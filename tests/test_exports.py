from __future__ import annotations

import json
from datetime import UTC, datetime

from core.models import (
    Case,
    CaseBrief,
    CaseStatus,
    ClarifyingQuestion,
    ConfidenceLevel,
    ExtractedRecord,
    QuestionPriority,
    ReplySet,
    SourceMode,
    StoredCaseBundle,
    TaskType,
)
from services.exports import ExportService


def build_bundle() -> StoredCaseBundle:
    case = Case(
        id="case_001",
        task_type=TaskType.ABSENCE,
        source_mode=SourceMode.TEXT,
        status=CaseStatus.READY,
        confidence=ConfidenceLevel.HIGH,
        created_at=datetime(2026, 3, 12, tzinfo=UTC),
    )
    record = ExtractedRecord(
        id="record_001",
        case_id="case_001",
        student_name="Leo Martin",
        class_name="Year 4B",
        date_from="2026-03-12",
        reason="stomach illness",
        request_type="absence_notice",
    )
    reply = ReplySet(
        id="reply_001",
        case_id="case_001",
        subject_lines=["A", "B", "C"],
        variant_hemingway="One",
        variant_corporate="Two",
        variant_educator="Three",
    )
    brief = CaseBrief(
        id="brief_001",
        case_id="case_001",
        summary="Brief",
        missing_fields=[],
        recommended_action="Review and copy.",
    )
    question = ClarifyingQuestion(
        id="question_001",
        case_id="case_001",
        question_text="Please confirm the date.",
        priority=QuestionPriority.HIGH,
    )
    return StoredCaseBundle(case, [], record, reply, brief, [question])


def test_json_export_uses_stable_field_names() -> None:
    payload, filename = ExportService().export(build_bundle(), "json")
    parsed = json.loads(payload)

    assert filename == "case_001.json"
    assert parsed["case"]["task_type"] == "absence"
    assert parsed["extracted_record"]["student_name"] == "Leo Martin"
    assert parsed["reply_set"]["variant_educator"] == "Three"


def test_csv_export_contains_expected_header() -> None:
    payload, filename = ExportService().export(build_bundle(), "csv")

    assert filename == "case_001.csv"
    assert payload.splitlines()[0].startswith("case_id,task_type,source_mode,status,confidence")
    assert "Leo Martin" in payload
