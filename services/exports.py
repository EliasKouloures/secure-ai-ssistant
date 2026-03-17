from __future__ import annotations

import csv
import io
import json

from core.errors import AppError
from core.models import ErrorCode, ExportFormat, StoredCaseBundle


class ExportService:
    def export(
        self, bundle: StoredCaseBundle, export_format: ExportFormat | str
    ) -> tuple[str, str]:
        if isinstance(export_format, str):
            export_format = ExportFormat(export_format)
        if export_format == ExportFormat.TEXT:
            return self._export_text(bundle), f"{bundle.case.id}.txt"
        if export_format == ExportFormat.JSON:
            return self._export_json(bundle), f"{bundle.case.id}.json"
        if export_format == ExportFormat.CSV:
            return self._export_csv(bundle), f"{bundle.case.id}.csv"
        raise AppError(ErrorCode.EXPORT_FAILED, f"Unsupported export format: {export_format}")

    def _export_text(self, bundle: StoredCaseBundle) -> str:
        sections = [
            f"Case ID: {bundle.case.id}",
            f"Task type: {bundle.case.task_type.value}",
            f"Status: {bundle.case.status.value}",
            f"Confidence: {bundle.case.confidence.value if bundle.case.confidence else 'unknown'}",
        ]
        if bundle.extracted_record:
            sections.append("Structured facts:")
            sections.extend(
                f"- {key}: {value}"
                for key, value in bundle.extracted_record.as_display_dict().items()
            )
        if bundle.case_brief:
            sections.append(f"Internal brief: {bundle.case_brief.summary}")
        if bundle.reply_set:
            sections.append("Subject lines:")
            sections.extend(
                f"{index}. Version: {line}"
                for index, line in enumerate(bundle.reply_set.subject_lines, start=1)
            )
            sections.append("Hemingway response:")
            sections.append(bundle.reply_set.variant_hemingway)
            sections.append("Corporate response:")
            sections.append(bundle.reply_set.variant_corporate)
            sections.append("Empathic response:")
            sections.append(bundle.reply_set.variant_educator)
        if bundle.clarifying_questions:
            sections.append("Clarifying questions:")
            sections.extend(f"- {item.question_text}" for item in bundle.clarifying_questions)
        return "\n".join(sections)

    def _export_json(self, bundle: StoredCaseBundle) -> str:
        payload = {
            "case": {
                "id": bundle.case.id,
                "task_type": bundle.case.task_type.value,
                "source_mode": bundle.case.source_mode.value,
                "status": bundle.case.status.value,
                "confidence": bundle.case.confidence.value if bundle.case.confidence else None,
                "reply_required": bundle.case.reply_required,
                "created_at": bundle.case.created_at.isoformat(),
                "completed_at": bundle.case.completed_at.isoformat()
                if bundle.case.completed_at
                else None,
            },
            "assets": [
                {
                    "asset_type": asset.asset_type.value,
                    "filename": asset.filename,
                    "parse_method": asset.parse_method.value,
                    "parse_success": asset.parse_success,
                    "ocr_confidence": asset.ocr_confidence,
                }
                for asset in bundle.assets
            ],
            "extracted_record": bundle.extracted_record.as_display_dict()
            if bundle.extracted_record
            else None,
            "case_brief": {
                "summary": bundle.case_brief.summary,
                "missing_fields": bundle.case_brief.missing_fields,
                "recommended_action": bundle.case_brief.recommended_action,
            }
            if bundle.case_brief
            else None,
            "reply_set": {
                "subject_lines": bundle.reply_set.subject_lines,
                "variant_hemingway": bundle.reply_set.variant_hemingway,
                "variant_corporate": bundle.reply_set.variant_corporate,
                "variant_educator": bundle.reply_set.variant_educator,
            }
            if bundle.reply_set
            else None,
            "clarifying_questions": [item.question_text for item in bundle.clarifying_questions],
        }
        return json.dumps(payload, indent=2)

    def _export_csv(self, bundle: StoredCaseBundle) -> str:
        output = io.StringIO()
        fieldnames = [
            "case_id",
            "task_type",
            "source_mode",
            "status",
            "confidence",
            "student_name",
            "class_name",
            "guardian_name",
            "date_from",
            "date_to",
            "reason",
            "request_type",
            "meeting_topic",
            "notes",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        record = bundle.extracted_record
        writer.writerow(
            {
                "case_id": bundle.case.id,
                "task_type": bundle.case.task_type.value,
                "source_mode": bundle.case.source_mode.value,
                "status": bundle.case.status.value,
                "confidence": bundle.case.confidence.value if bundle.case.confidence else None,
                "student_name": record.student_name if record else None,
                "class_name": record.class_name if record else None,
                "guardian_name": record.guardian_name if record else None,
                "date_from": record.date_from if record else None,
                "date_to": record.date_to if record else None,
                "reason": record.reason if record else None,
                "request_type": record.request_type if record else None,
                "meeting_topic": record.meeting_topic if record else None,
                "notes": record.notes if record else None,
            }
        )
        return output.getvalue()
