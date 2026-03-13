from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from core.models import (
    Case,
    CaseStatus,
    ConfidenceLevel,
    ExtractedRecord,
    SourceMode,
    TaskType,
)
from core.storage import Repository


def test_repository_round_trip_and_reset(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "repo.db")
    case = Case(
        id="case_001",
        task_type=TaskType.REPLY,
        source_mode=SourceMode.TEXT,
        status=CaseStatus.READY,
        confidence=ConfidenceLevel.HIGH,
        created_at=datetime(2026, 3, 12, tzinfo=UTC),
    )
    record = ExtractedRecord(
        id="record_001",
        case_id="case_001",
        student_name="Leo Martin",
        request_type="reply_draft",
    )
    repository.upsert_case(case)
    repository.upsert_extracted_record(record)

    bundle = repository.get_case_bundle("case_001")
    assert bundle is not None
    assert bundle.extracted_record.student_name == "Leo Martin"
    assert repository.count_cases_today() >= 0
    assert repository.reset_case("case_001") is True
    assert repository.get_case_bundle("case_001") is None
