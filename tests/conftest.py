from __future__ import annotations

from pathlib import Path

import pytest

from core.config import AppConfig, BackendProfile, FeatureFlags, InputLimits, StorageConfig
from core.models import HealthCheckResult
from services.backend import VisionOCRResult
from services.case_service import CaseService


class FakeBackend:
    def __init__(self, *, ocr_confidence: float = 0.92, handwritten: bool = False) -> None:
        self.ocr_confidence = ocr_confidence
        self.handwritten = handwritten

    def health_check(self) -> HealthCheckResult:
        return HealthCheckResult(
            status="ok",
            backend_name="fake",
            base_url="http://127.0.0.1:1234/v1",
            model_id="fake-local-model",
            reachable=True,
        )

    def generate_reply_payload(self, context: dict[str, object]) -> dict[str, object]:
        student = "the pupil"
        facts_block = str(context.get("facts_block", ""))
        operator_note = str(context.get("operator_note", "")).strip()
        for line in facts_block.splitlines():
            if line.lower().startswith("student name:"):
                student = line.split(":", 1)[1].strip()
                break
        suffix = f" Operator note: {operator_note}" if operator_note else ""
        return {
            "subject_lines": [
                f"Absence noted for {student}",
                "Attendance update received",
                "Thank you for your message",
            ],
            "message_variants": {
                "hemingway": f"Thank you. We have noted the update for {student}.{suffix}",
                "corporate": f"Thank you for your message. We have recorded the update concerning {student}.{suffix}",
                "educator_first": f"Thank you for letting us know about {student}. We have noted the update.{suffix}",
            },
        }

    def generate_assistant_text(self, context: dict[str, object]) -> str:
        prompt_title = str(context.get("prompt_title", "Prompt")).strip() or "Prompt"
        context_text = str(context.get("context_text", "")).strip()
        file_context = str(context.get("file_context", "")).strip()
        lines = [f"{prompt_title}"]
        if context_text:
            lines.append(context_text)
        if file_context and file_context != "No uploaded file context provided.":
            lines.append(f"File context: {file_context}")
        lines.append("Prepared locally.")
        return "\n\n".join(lines)

    def ocr_image(self, image_bytes: bytes, mime_type: str, filename: str) -> VisionOCRResult:
        text = "Student: Leo Martin\nYear 4B\nAbsent on 2026-03-12 because of stomach illness."
        return VisionOCRResult(
            text=text,
            ocr_confidence=self.ocr_confidence,
            is_handwritten=self.handwritten,
            warnings=[],
        )


@pytest.fixture()
def app_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        title="Secure Secr-AI-tery",
        locale="en-GB",
        bind_host="127.0.0.1",
        bind_port=8501,
        backend=BackendProfile(
            provider_name="fake",
            base_url="http://127.0.0.1:1234/v1",
            model_id="fake-local-model",
            supports_vision=True,
        ),
        storage=StorageConfig(database_path=str(tmp_path / "secure-secr-ai-tery.db")),
        limits=InputLimits(),
        features=FeatureFlags(),
    )


@pytest.fixture()
def fake_backend() -> FakeBackend:
    return FakeBackend()


@pytest.fixture()
def case_service(app_config: AppConfig, fake_backend: FakeBackend) -> CaseService:
    return CaseService(config=app_config, backend=fake_backend)


@pytest.fixture()
def simple_payload():
    from core.models import AnalysisPayload

    return AnalysisPayload(
        text_input="Leo Martin in Year 4B will be absent on 2026-03-12 because of stomach illness.\nKind regards,\nSarah Martin",
        locale="en-GB",
    )
