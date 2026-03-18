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


def test_manual_note_guides_output_without_overwriting_source_analysis(case_service) -> None:
    payload = AnalysisPayload(
        text_input=(
            'Hello School Board,\n\n'
            'This is the mother of student named "Johnny Knoxville" from class 8b.\n\n'
            "I demand an explanation for the unfair homework and grading.\n\n"
            "Regards,\nKaren Miller"
        ),
        note_input=(
            "Reply with a friendly message. Ask Karen Miller to call teacher Mr. Nice "
            "after 14:00 CET on 0160-123456789."
        ),
        locale="en-GB",
    )

    analysis = case_service.analyse_case(payload)
    outputs = case_service.generate_outputs(analysis.case.id, operator_note=payload.note_input)

    assert analysis.case.task_type == __import__("core.models", fromlist=["TaskType"]).TaskType.REPLY
    assert analysis.extracted_record.student_name == "Johnny Knoxville"
    assert analysis.extracted_record.guardian_name == "Karen Miller"
    assert "Operator note" in (analysis.extracted_record.notes or "")
    assert outputs.reply_set is not None
    assert "Mr. Nice" in outputs.reply_set.variant_corporate


def test_run_prompt_stores_history_and_output(case_service) -> None:
    saved_prompt = case_service.save_prompt_template(
        "Draft a short reply in British English.",
        selected_title="Draft a short reply",
    )

    run = case_service.run_prompt(
        context_text="Parent wants a calm reply about lateness.",
        prompt_title=saved_prompt.title,
        prompt_body=saved_prompt.body,
        files=[],
    )

    history = case_service.list_history()

    assert run.title.startswith("Draft a short reply")
    assert "Parent wants a calm reply" in run.output_text
    assert history[0].id == run.id


def test_run_prompt_requires_prompt_body(case_service) -> None:
    with pytest.raises(AppError) as exc_info:
        case_service.run_prompt(
            context_text="Parent wants a reply.",
            prompt_title="",
            prompt_body="",
            files=[],
        )

    assert exc_info.value.code == ErrorCode.INSUFFICIENT_CONTEXT
