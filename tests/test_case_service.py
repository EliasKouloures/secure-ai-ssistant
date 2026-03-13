from __future__ import annotations

import pytest

from core.errors import AppError
from core.models import AnalysisPayload, ErrorCode


def test_end_to_end_text_case(case_service, simple_payload) -> None:
    analysis = case_service.analyse_case(simple_payload)
    outputs = case_service.generate_outputs(analysis.case.id)
    content, filename = case_service.export_case(analysis.case.id, "json")

    assert analysis.case.id.startswith("case_")
    assert analysis.extracted_record.student_name == "Leo Martin"
    assert outputs.reply_set is not None
    assert len(outputs.reply_set.subject_lines) == 3
    assert filename.endswith(".json")
    assert '"task_type": "absence"' in content


def test_backend_error_bubbles_for_output_generation(app_config) -> None:
    class BrokenBackend:
        def health_check(self):
            from core.models import HealthCheckResult

            return HealthCheckResult(
                status="offline",
                backend_name="broken",
                base_url="http://127.0.0.1:1234/v1",
                model_id="none",
                reachable=False,
            )

        def generate_reply_payload(self, context):
            raise AppError(ErrorCode.BACKEND_UNREACHABLE, "backend down")

        def ocr_image(self, image_bytes, mime_type, filename):
            raise AppError(ErrorCode.BACKEND_UNREACHABLE, "backend down")

    service = __import__("services.case_service", fromlist=["CaseService"]).CaseService(
        config=app_config,
        backend=BrokenBackend(),
    )
    analysis = service.analyse_case(
        AnalysisPayload(
            text_input="Leo Martin will be absent on 2026-03-12.",
            locale="en-GB",
        )
    )

    with pytest.raises(AppError) as exc_info:
        service.generate_outputs(analysis.case.id)

    assert exc_info.value.code == ErrorCode.BACKEND_UNREACHABLE


def test_empty_input_is_rejected(case_service) -> None:
    with pytest.raises(AppError) as exc_info:
        case_service.analyse_case(AnalysisPayload(locale="en-GB"))

    assert exc_info.value.code == ErrorCode.EMPTY_INPUT
