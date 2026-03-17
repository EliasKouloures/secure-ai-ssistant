from __future__ import annotations

from core.models import Case, CaseStatus, ConfidenceLevel, ExtractedRecord, SourceMode, TaskType
from services.outputs import OutputContext, OutputService


class ThinBackend:
    def generate_reply_payload(self, context: dict[str, object]) -> dict[str, object]:
        return {
            "subject_lines": [
                "<think>ignore</think>1. Version: Absence noted",
                "Attendance update received",
                "3. Version: Thank you for your message",
            ],
            "message_variants": {
                "hemingway": (
                    "<think>ignore</think>Hello Sarah Martin, "
                    "We have noted Leo Martin's absence for 12 March. "
                    "We will update the register today. Best, School Office"
                ),
                "corporate": (
                    "Dear Sarah Martin, Thank you for your message. "
                    "We have recorded Leo Martin's absence for 12 March 2026. "
                    "Please let us know if anything changes. Kind regards, School Office"
                ),
                "educator_first": (
                    "Hello Sarah Martin, Thank you for letting us know about Leo Martin. "
                    "We hope he feels better soon. Please keep us updated if needed. "
                    "Warm regards, School Office"
                ),
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
        guardian_name="Sarah Martin",
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
    assert outputs.copy_blocks["Subject lines"].startswith("1. Version: Absence noted")
    assert "2. Version: Attendance update received" in outputs.copy_blocks["Subject lines"]
    assert "3. Version: Thank you for your message" in outputs.copy_blocks["Subject lines"]
    assert outputs.reply_set.variant_hemingway.startswith("Hello Sarah Martin,\n\n")
    assert "\n\nBest," in outputs.reply_set.variant_hemingway
    assert "\n\nKind regards," in outputs.reply_set.variant_corporate
    assert "\n\nWarm regards," in outputs.reply_set.variant_educator
    assert "Corporate response" in outputs.copy_blocks
    assert "Empathic response" in outputs.copy_blocks
