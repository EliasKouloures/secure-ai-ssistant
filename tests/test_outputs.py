from __future__ import annotations

from core.models import Case, CaseStatus, ConfidenceLevel, ExtractedRecord, SourceMode, TaskType
from services.outputs import OutputContext, OutputService


class ThinBackend:
    def generate_reply_payload(self, context: dict[str, object]) -> dict[str, object]:
        return {
            "subject_lines": ["<think>ignore</think>Absence noted"],
            "message_variants": {
                "hemingway": "<think>ignore</think>Thank you. We have noted the absence.",
                "corporate": "Thank you for your message. We have recorded the absence.",
                "educator_first": "Thank you for letting us know. We have noted the absence.",
            },
        }


def test_output_service_normalises_counts_and_strips_reasoning() -> None:
    case = Case(
        id="case_001",
        task_type=TaskType.ABSENCE,
        source_mode=SourceMode.TEXT,
        status=CaseStatus.READY,
        confidence=ConfidenceLevel.HIGH,
        reply_required=True,
        source_summary="Pasted text",
    )
    record = ExtractedRecord(
        id="record_001",
        case_id="case_001",
        student_name="Leo Martin",
        date_from="2026-03-12",
        request_type="absence_notice",
    )
    service = OutputService(backend=ThinBackend())

    outputs = service.generate(
        OutputContext(
            case=case,
            extracted_record=record,
            missing_fields=[],
            warnings=[],
            source_types=["text"],
        )
    )

    assert len(outputs.reply_set.subject_lines) == 3
    assert outputs.reply_set.subject_lines[0] == "Absence noted"
    assert outputs.reply_set.variant_hemingway == "Thank you. We have noted the absence."
    assert "Corporate" in outputs.copy_blocks
    assert "Educator-first" in outputs.copy_blocks
