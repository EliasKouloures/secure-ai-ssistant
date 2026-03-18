from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from core.models import (
    AssistantRun,
    AuditEvent,
    Case,
    CaseBrief,
    CaseStatus,
    ClarifyingQuestion,
    ConfidenceLevel,
    DashboardCaseRow,
    ExtractedRecord,
    InputAsset,
    ParseMethod,
    QuestionPriority,
    ReplySet,
    SourceMode,
    StoredCaseBundle,
    TaskType,
    WorkflowCount,
)


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class Repository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        with self._managed_connection() as conn:
            conn.executescript(
                """
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    source_mode TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    reply_required INTEGER NOT NULL DEFAULT 0,
                    content_fingerprint TEXT,
                    source_summary TEXT NOT NULL DEFAULT '',
                    warnings_json TEXT NOT NULL DEFAULT '[]'
                );

                CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases (created_at);
                CREATE INDEX IF NOT EXISTS idx_cases_fingerprint ON cases (content_fingerprint);

                CREATE TABLE IF NOT EXISTS input_assets (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    asset_type TEXT NOT NULL,
                    filename TEXT,
                    parse_method TEXT NOT NULL,
                    parse_success INTEGER NOT NULL,
                    ocr_confidence REAL
                );

                CREATE TABLE IF NOT EXISTS extracted_records (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE CASCADE,
                    student_name TEXT,
                    class_name TEXT,
                    guardian_name TEXT,
                    date_from TEXT,
                    date_to TEXT,
                    reason TEXT,
                    request_type TEXT,
                    meeting_topic TEXT,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS reply_sets (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE CASCADE,
                    subject_lines_json TEXT NOT NULL,
                    variant_hemingway TEXT NOT NULL,
                    variant_corporate TEXT NOT NULL,
                    variant_educator TEXT NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS case_briefs (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL UNIQUE REFERENCES cases(id) ON DELETE CASCADE,
                    summary TEXT NOT NULL,
                    missing_fields_json TEXT NOT NULL,
                    recommended_action TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clarifying_questions (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                    question_text TEXT NOT NULL,
                    priority TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms INTEGER,
                    error_code TEXT,
                    metadata_json TEXT
                );

                CREATE TABLE IF NOT EXISTS assistant_runs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    context_text TEXT NOT NULL,
                    prompt_title TEXT NOT NULL,
                    prompt_body TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    source_files_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_assistant_runs_created_at ON assistant_runs (created_at DESC);
                """
            )

    def upsert_case(self, case: Case) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO cases (
                    id, task_type, source_mode, status, confidence, created_at,
                    completed_at, reply_required, content_fingerprint, source_summary, warnings_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    task_type=excluded.task_type,
                    source_mode=excluded.source_mode,
                    status=excluded.status,
                    confidence=excluded.confidence,
                    completed_at=excluded.completed_at,
                    reply_required=excluded.reply_required,
                    content_fingerprint=excluded.content_fingerprint,
                    source_summary=excluded.source_summary,
                    warnings_json=excluded.warnings_json
                """,
                (
                    case.id,
                    case.task_type.value,
                    case.source_mode.value,
                    case.status.value,
                    case.confidence.value if case.confidence else None,
                    case.created_at.isoformat(),
                    case.completed_at.isoformat() if case.completed_at else None,
                    int(case.reply_required),
                    case.content_fingerprint,
                    case.source_summary,
                    json.dumps(case.warnings),
                ),
            )

    def replace_input_assets(self, case_id: str, assets: list[InputAsset]) -> None:
        with self._managed_connection() as conn:
            conn.execute("DELETE FROM input_assets WHERE case_id = ?", (case_id,))
            conn.executemany(
                """
                INSERT INTO input_assets (
                    id, case_id, asset_type, filename, parse_method, parse_success, ocr_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        asset.id,
                        asset.case_id,
                        asset.asset_type.value,
                        asset.filename,
                        asset.parse_method.value,
                        int(asset.parse_success),
                        asset.ocr_confidence,
                    )
                    for asset in assets
                ],
            )

    def upsert_extracted_record(self, record: ExtractedRecord) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO extracted_records (
                    id, case_id, student_name, class_name, guardian_name, date_from,
                    date_to, reason, request_type, meeting_topic, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    id=excluded.id,
                    student_name=excluded.student_name,
                    class_name=excluded.class_name,
                    guardian_name=excluded.guardian_name,
                    date_from=excluded.date_from,
                    date_to=excluded.date_to,
                    reason=excluded.reason,
                    request_type=excluded.request_type,
                    meeting_topic=excluded.meeting_topic,
                    notes=excluded.notes
                """,
                (
                    record.id,
                    record.case_id,
                    record.student_name,
                    record.class_name,
                    record.guardian_name,
                    record.date_from,
                    record.date_to,
                    record.reason,
                    record.request_type,
                    record.meeting_topic,
                    record.notes,
                ),
            )

    def upsert_reply_set(self, reply_set: ReplySet) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO reply_sets (
                    id, case_id, subject_lines_json, variant_hemingway,
                    variant_corporate, variant_educator, approved
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    id=excluded.id,
                    subject_lines_json=excluded.subject_lines_json,
                    variant_hemingway=excluded.variant_hemingway,
                    variant_corporate=excluded.variant_corporate,
                    variant_educator=excluded.variant_educator,
                    approved=excluded.approved
                """,
                (
                    reply_set.id,
                    reply_set.case_id,
                    json.dumps(reply_set.subject_lines),
                    reply_set.variant_hemingway,
                    reply_set.variant_corporate,
                    reply_set.variant_educator,
                    int(reply_set.approved),
                ),
            )

    def upsert_case_brief(self, brief: CaseBrief) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO case_briefs (id, case_id, summary, missing_fields_json, recommended_action)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    id=excluded.id,
                    summary=excluded.summary,
                    missing_fields_json=excluded.missing_fields_json,
                    recommended_action=excluded.recommended_action
                """,
                (
                    brief.id,
                    brief.case_id,
                    brief.summary,
                    json.dumps(brief.missing_fields),
                    brief.recommended_action,
                ),
            )

    def replace_clarifying_questions(self, case_id: str, questions: list[ClarifyingQuestion]) -> None:
        with self._managed_connection() as conn:
            conn.execute("DELETE FROM clarifying_questions WHERE case_id = ?", (case_id,))
            conn.executemany(
                """
                INSERT INTO clarifying_questions (id, case_id, question_text, priority)
                VALUES (?, ?, ?, ?)
                """,
                [(question.id, question.case_id, question.question_text, question.priority.value) for question in questions],
            )

    def insert_audit_event(self, event: AuditEvent) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO audit_events (
                    id, case_id, event_type, timestamp, duration_ms, error_code, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.case_id,
                    event.event_type,
                    event.timestamp.isoformat(),
                    event.duration_ms,
                    event.error_code,
                    json.dumps(event.metadata_json or {}),
                ),
            )

    def insert_assistant_run(self, run: AssistantRun) -> None:
        with self._managed_connection() as conn:
            conn.execute(
                """
                INSERT INTO assistant_runs (
                    id, title, preview, context_text, prompt_title, prompt_body,
                    output_text, source_files_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.title,
                    run.preview,
                    run.context_text,
                    run.prompt_title,
                    run.prompt_body,
                    run.output_text,
                    json.dumps(run.source_files),
                    run.created_at.isoformat(),
                ),
            )

    def find_case_by_fingerprint(self, fingerprint: str) -> Case | None:
        with self._managed_connection() as conn:
            row = conn.execute(
                "SELECT * FROM cases WHERE content_fingerprint = ? ORDER BY created_at DESC LIMIT 1",
                (fingerprint,),
            ).fetchone()
        return self._row_to_case(row) if row else None

    def get_case_bundle(self, case_id: str) -> StoredCaseBundle | None:
        with self._managed_connection() as conn:
            case_row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
            if case_row is None:
                return None
            asset_rows = conn.execute("SELECT * FROM input_assets WHERE case_id = ?", (case_id,)).fetchall()
            record_row = conn.execute(
                "SELECT * FROM extracted_records WHERE case_id = ?",
                (case_id,),
            ).fetchone()
            reply_row = conn.execute("SELECT * FROM reply_sets WHERE case_id = ?", (case_id,)).fetchone()
            brief_row = conn.execute("SELECT * FROM case_briefs WHERE case_id = ?", (case_id,)).fetchone()
            question_rows = conn.execute(
                "SELECT * FROM clarifying_questions WHERE case_id = ? ORDER BY priority DESC",
                (case_id,),
            ).fetchall()
        return StoredCaseBundle(
            case=self._row_to_case(case_row),
            assets=[self._row_to_asset(row) for row in asset_rows],
            extracted_record=self._row_to_record(record_row) if record_row else None,
            reply_set=self._row_to_reply_set(reply_row) if reply_row else None,
            case_brief=self._row_to_case_brief(brief_row) if brief_row else None,
            clarifying_questions=[self._row_to_question(row) for row in question_rows],
        )

    def list_assistant_runs(self, limit: int = 50) -> list[AssistantRun]:
        with self._managed_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM assistant_runs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_assistant_run(row) for row in rows]

    def get_assistant_run(self, run_id: str) -> AssistantRun | None:
        with self._managed_connection() as conn:
            row = conn.execute(
                "SELECT * FROM assistant_runs WHERE id = ?",
                (run_id,),
            ).fetchone()
        return self._row_to_assistant_run(row) if row else None

    def list_recent_cases(self, limit: int = 7) -> list[DashboardCaseRow]:
        with self._managed_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, task_type, confidence, status
                FROM cases
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            DashboardCaseRow(
                id=row["id"],
                created_at=_dt(row["created_at"]) or datetime.now(UTC),
                task_type=TaskType(row["task_type"]),
                confidence=ConfidenceLevel(row["confidence"]) if row["confidence"] else None,
                status=CaseStatus(row["status"]),
            )
            for row in rows
        ]

    def count_cases_today(self) -> int:
        today = datetime.now(UTC).date().isoformat()
        with self._managed_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM cases WHERE substr(created_at, 1, 10) = ?",
                (today,),
            ).fetchone()
        return int(row["count"])

    def workflow_counts(self, days: int = 7) -> list[WorkflowCount]:
        start_day = (datetime.now(UTC).date() - timedelta(days=days - 1)).isoformat()
        with self._managed_connection() as conn:
            rows = conn.execute(
                """
                SELECT substr(created_at, 1, 10) AS day, task_type, COUNT(*) AS count
                FROM cases
                WHERE substr(created_at, 1, 10) >= ?
                GROUP BY day, task_type
                ORDER BY day ASC, task_type ASC
                """,
                (start_day,),
            ).fetchall()
        return [
            WorkflowCount(
                day=date.fromisoformat(row["day"]),
                task_type=TaskType(row["task_type"]),
                count=int(row["count"]),
            )
            for row in rows
        ]

    def recent_errors(self, limit: int = 5) -> list[dict[str, Any]]:
        with self._managed_connection() as conn:
            rows = conn.execute(
                """
                SELECT timestamp, error_code, metadata_json
                FROM audit_events
                WHERE error_code IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "timestamp": row["timestamp"],
                "error_code": row["error_code"],
                "metadata": json.loads(row["metadata_json"] or "{}"),
            }
            for row in rows
        ]

    def reset_case(self, case_id: str) -> bool:
        with self._managed_connection() as conn:
            cursor = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
            return bool(cursor.rowcount > 0)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _managed_connection(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _row_to_case(self, row: sqlite3.Row) -> Case:
        return Case(
            id=row["id"],
            task_type=TaskType(row["task_type"]),
            source_mode=SourceMode(row["source_mode"]),
            status=CaseStatus(row["status"]),
            confidence=ConfidenceLevel(row["confidence"]) if row["confidence"] else None,
            created_at=_dt(row["created_at"]) or datetime.now(UTC),
            completed_at=_dt(row["completed_at"]),
            reply_required=bool(row["reply_required"]),
            content_fingerprint=row["content_fingerprint"],
            source_summary=row["source_summary"],
            warnings=json.loads(row["warnings_json"] or "[]"),
        )

    def _row_to_asset(self, row: sqlite3.Row) -> InputAsset:
        from core.models import AssetType

        return InputAsset(
            id=row["id"],
            case_id=row["case_id"],
            asset_type=AssetType(row["asset_type"]),
            filename=row["filename"],
            parse_method=ParseMethod(row["parse_method"]),
            parse_success=bool(row["parse_success"]),
            ocr_confidence=row["ocr_confidence"],
        )

    def _row_to_record(self, row: sqlite3.Row) -> ExtractedRecord:
        return ExtractedRecord(**dict(row))

    def _row_to_reply_set(self, row: sqlite3.Row) -> ReplySet:
        return ReplySet(
            id=row["id"],
            case_id=row["case_id"],
            subject_lines=json.loads(row["subject_lines_json"]),
            variant_hemingway=row["variant_hemingway"],
            variant_corporate=row["variant_corporate"],
            variant_educator=row["variant_educator"],
            approved=bool(row["approved"]),
        )

    def _row_to_case_brief(self, row: sqlite3.Row) -> CaseBrief:
        return CaseBrief(
            id=row["id"],
            case_id=row["case_id"],
            summary=row["summary"],
            missing_fields=json.loads(row["missing_fields_json"]),
            recommended_action=row["recommended_action"],
        )

    def _row_to_question(self, row: sqlite3.Row) -> ClarifyingQuestion:
        return ClarifyingQuestion(
            id=row["id"],
            case_id=row["case_id"],
            question_text=row["question_text"],
            priority=QuestionPriority(row["priority"]),
        )

    def _row_to_assistant_run(self, row: sqlite3.Row) -> AssistantRun:
        return AssistantRun(
            id=row["id"],
            title=row["title"],
            preview=row["preview"],
            context_text=row["context_text"],
            prompt_title=row["prompt_title"],
            prompt_body=row["prompt_body"],
            output_text=row["output_text"],
            source_files=json.loads(row["source_files_json"] or "[]"),
            created_at=_dt(row["created_at"]) or datetime.now(UTC),
        )
