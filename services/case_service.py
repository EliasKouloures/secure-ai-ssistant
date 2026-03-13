from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from time import perf_counter

from core.config import AppConfig
from core.errors import AppError
from core.models import (
    AnalysisPayload,
    AnalysisResult,
    AuditEvent,
    ErrorCode,
    ExportFormat,
    GeneratedOutputs,
    HealthCheckResult,
    SourceMode,
    utc_now,
)
from core.storage import Repository
from core.text import normalise_whitespace
from services.analysis import AnalysisContext, AnalysisService
from services.backend import BackendClient, OpenAICompatibleBackend
from services.exports import ExportService
from services.files import FileIngestService
from services.outputs import OutputContext, OutputService
from services.prompt_loader import PromptLoader


class CaseService:
    def __init__(
        self,
        config: AppConfig,
        repository: Repository | None = None,
        backend: BackendClient | None = None,
    ) -> None:
        self.config = config
        self.repository = repository or Repository(config.storage.database_path)
        self.backend = backend or OpenAICompatibleBackend(config.backend, PromptLoader())
        self.analysis_service = AnalysisService()
        self.file_service = FileIngestService(config.limits)
        self.output_service = OutputService(self.backend)
        self.export_service = ExportService()

    def health_check(self) -> HealthCheckResult:
        return self.backend.health_check()

    def analyse_case(self, payload: AnalysisPayload) -> AnalysisResult:
        start = perf_counter()
        combined_text = normalise_whitespace("\n\n".join(filter(None, [payload.text_input, payload.note_input])))
        source_mode = self._source_mode(payload)
        parsed_files = self.file_service.ingest(
            payload.files,
            backend=self.backend,
            supports_vision=self.config.backend.supports_vision,
        ) if payload.files else None
        if parsed_files:
            combined_text = normalise_whitespace("\n\n".join(filter(None, [combined_text, parsed_files.combined_text])))
            source_mode = parsed_files.source_mode if source_mode == SourceMode.TEXT else SourceMode.MIXED
        if not combined_text:
            self._audit_error(None, ErrorCode.EMPTY_INPUT, start, {"workflow_hint": payload.workflow_hint})
            raise AppError(ErrorCode.EMPTY_INPUT, "Please provide text, a note, or a supported file.")

        fingerprint = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()
        duplicate_case = self.repository.find_case_by_fingerprint(fingerprint)
        extra_warnings = list(parsed_files.warnings if parsed_files else [])
        if duplicate_case:
            extra_warnings.append(f"This looks similar to recent case {duplicate_case.id}.")

        context = AnalysisContext(
            combined_text=combined_text,
            source_mode=source_mode,
            assets=parsed_files.assets if parsed_files else [],
            workflow_hint=payload.workflow_hint,
            ocr_used=parsed_files.ocr_used if parsed_files else False,
            low_quality=parsed_files.low_quality if parsed_files else False,
            extra_warnings=extra_warnings,
            anchor_date=datetime.now(UTC).date(),
        )
        result = self.analysis_service.analyse(context)
        result.case.content_fingerprint = fingerprint
        result.case.completed_at = utc_now()
        self.repository.upsert_case(result.case)
        self.repository.replace_input_assets(result.case.id, result.input_assets)
        self.repository.upsert_extracted_record(result.extracted_record)
        self.repository.insert_audit_event(
            AuditEvent(
                id=f"audit_{hashlib.md5(result.case.id.encode(), usedforsecurity=False).hexdigest()[:12]}",
                case_id=result.case.id,
                event_type="analyse_case",
                timestamp=utc_now(),
                duration_ms=int((perf_counter() - start) * 1000),
                metadata_json={
                    "task_type": result.case.task_type.value,
                    "confidence": result.case.confidence.value if result.case.confidence else None,
                    "status": result.case.status.value,
                },
            )
        )
        return result

    def generate_outputs(self, case_id: str) -> GeneratedOutputs:
        start = perf_counter()
        bundle = self.repository.get_case_bundle(case_id)
        if bundle is None or bundle.extracted_record is None:
            self._audit_error(case_id, ErrorCode.CASE_NOT_FOUND, start, {})
            raise AppError(ErrorCode.CASE_NOT_FOUND, "The requested case could not be found.")

        missing_fields = self.analysis_service.missing_fields(bundle.case.task_type, bundle.extracted_record)
        output_context = OutputContext(
            case=bundle.case,
            extracted_record=bundle.extracted_record,
            missing_fields=missing_fields,
            warnings=bundle.case.warnings,
            source_types=[asset.asset_type.value for asset in bundle.assets] or [bundle.case.source_mode.value],
        )
        outputs = self.output_service.generate(output_context)
        self.repository.upsert_case_brief(outputs.case_brief)
        if outputs.reply_set is not None:
            self.repository.upsert_reply_set(outputs.reply_set)
        self.repository.replace_clarifying_questions(case_id, outputs.clarifying_questions)
        self.repository.insert_audit_event(
            AuditEvent(
                id=f"audit_{hashlib.sha1((case_id + 'generate').encode(), usedforsecurity=False).hexdigest()[:12]}",
                case_id=case_id,
                event_type="generate_outputs",
                timestamp=utc_now(),
                duration_ms=int((perf_counter() - start) * 1000),
                metadata_json={"reply_required": bundle.case.reply_required},
            )
        )
        return outputs

    def export_case(self, case_id: str, export_format: str) -> tuple[str, str]:
        bundle = self.repository.get_case_bundle(case_id)
        if bundle is None:
            raise AppError(ErrorCode.CASE_NOT_FOUND, "The requested case could not be found.")
        try:
            return self.export_service.export(bundle, ExportFormat(export_format))
        except ValueError as exc:
            raise AppError(ErrorCode.EXPORT_FAILED, f"Unsupported export format: {export_format}") from exc

    def reset_case(self, case_id: str) -> dict[str, bool]:
        if not self.repository.reset_case(case_id):
            raise AppError(ErrorCode.CASE_NOT_FOUND, "The requested case could not be found.")
        return {"reset": True}

    def _audit_error(self, case_id: str | None, code: str, start: float, metadata: dict[str, object]) -> None:
        self.repository.insert_audit_event(
            AuditEvent(
                id=f"audit_{hashlib.sha1((str(case_id) + code).encode(), usedforsecurity=False).hexdigest()[:12]}",
                case_id=case_id,
                event_type="error",
                timestamp=utc_now(),
                duration_ms=int((perf_counter() - start) * 1000),
                error_code=code,
                metadata_json=metadata,
            )
        )

    def _source_mode(self, payload: AnalysisPayload) -> SourceMode:
        if payload.files and (payload.text_input or payload.note_input):
            return SourceMode.MIXED
        if payload.files:
            return SourceMode.TEXT
        if payload.note_input:
            return SourceMode.NOTE
        return SourceMode.TEXT
