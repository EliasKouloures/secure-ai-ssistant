from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaskType(StrEnum):
    ABSENCE = "absence"
    REPLY = "reply"
    SCHEDULE = "schedule"
    TRIAGE = "triage"


class SourceMode(StrEnum):
    TEXT = "text"
    NOTE = "note"
    IMAGE = "image"
    PDF = "pdf"
    MIXED = "mixed"


class CaseStatus(StrEnum):
    NEW = "new"
    PROCESSING = "processing"
    NEEDS_REVIEW = "needs_review"
    READY = "ready"
    BLOCKED = "blocked"
    ERROR = "error"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AssetType(StrEnum):
    TEXT = "text"
    NOTE = "note"
    IMAGE = "image"
    PDF = "pdf"


class ParseMethod(StrEnum):
    DIRECT_TEXT = "direct_text"
    OCR = "ocr"
    MIXED = "mixed"
    MANUAL = "manual"


class QuestionPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExportFormat(StrEnum):
    TEXT = "text"
    JSON = "json"
    CSV = "csv"


class ErrorCode(StrEnum):
    BACKEND_UNREACHABLE = "BACKEND_UNREACHABLE"
    CASE_NOT_FOUND = "CASE_NOT_FOUND"
    EMPTY_INPUT = "EMPTY_INPUT"
    EXPORT_FAILED = "EXPORT_FAILED"
    FILE_PARSE_FAILED = "FILE_PARSE_FAILED"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    OCR_LOW_CONFIDENCE = "OCR_LOW_CONFIDENCE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    UNSUPPORTED_MULTI_CHILD = "UNSUPPORTED_MULTI_CHILD"


@dataclass(slots=True)
class FileUpload:
    name: str
    content: bytes
    content_type: str | None = None

    @property
    def size_bytes(self) -> int:
        return len(self.content)

    @property
    def suffix(self) -> str:
        suffix = self.name.rsplit(".", 1)
        return f".{suffix[-1].lower()}" if len(suffix) > 1 else ""


@dataclass(slots=True)
class Case:
    id: str
    task_type: TaskType
    source_mode: SourceMode
    status: CaseStatus
    confidence: ConfidenceLevel | None
    created_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None
    reply_required: bool = False
    content_fingerprint: str | None = None
    source_summary: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class InputAsset:
    id: str
    case_id: str
    asset_type: AssetType
    filename: str | None
    parse_method: ParseMethod
    parse_success: bool
    ocr_confidence: float | None = None


@dataclass(slots=True)
class ExtractedRecord:
    id: str
    case_id: str
    student_name: str | None = None
    class_name: str | None = None
    guardian_name: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    reason: str | None = None
    request_type: str | None = None
    meeting_topic: str | None = None
    notes: str | None = None

    def as_display_dict(self) -> dict[str, str]:
        return {
            "student_name": self.student_name or "[Not provided]",
            "class_name": self.class_name or "[Not provided]",
            "guardian_name": self.guardian_name or "[Not provided]",
            "date_from": self.date_from or "[Not provided]",
            "date_to": self.date_to or "[Not provided]",
            "reason": self.reason or "[Not provided]",
            "request_type": self.request_type or "[Not provided]",
            "meeting_topic": self.meeting_topic or "[Not provided]",
            "notes": self.notes or "[Not provided]",
        }


@dataclass(slots=True)
class ReplySet:
    id: str
    case_id: str
    subject_lines: list[str]
    variant_hemingway: str
    variant_corporate: str
    variant_educator: str
    approved: bool = False


@dataclass(slots=True)
class CaseBrief:
    id: str
    case_id: str
    summary: str
    missing_fields: list[str]
    recommended_action: str


@dataclass(slots=True)
class ClarifyingQuestion:
    id: str
    case_id: str
    question_text: str
    priority: QuestionPriority


@dataclass(slots=True)
class AuditEvent:
    id: str
    case_id: str | None
    event_type: str
    timestamp: datetime
    duration_ms: int | None = None
    error_code: str | None = None
    metadata_json: dict[str, Any] | None = None


@dataclass(slots=True)
class AnalysisPayload:
    workflow_hint: str | None = None
    text_input: str | None = None
    note_input: str | None = None
    files: list[FileUpload] = field(default_factory=list)
    locale: str = "en-GB"


@dataclass(slots=True)
class AnalysisResult:
    case: Case
    extracted_record: ExtractedRecord
    input_assets: list[InputAsset]
    warnings: list[str]
    confidence_score: int
    missing_fields: list[str]
    clarifying_questions: list[str]
    source_summary: str


@dataclass(slots=True)
class GeneratedOutputs:
    case_brief: CaseBrief
    reply_set: ReplySet | None
    clarifying_questions: list[ClarifyingQuestion]
    copy_blocks: dict[str, str]
    export_payloads: dict[str, str]
    warnings: list[str]


@dataclass(slots=True)
class HealthCheckResult:
    status: str
    backend_name: str
    base_url: str
    model_id: str
    reachable: bool
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DashboardCaseRow:
    id: str
    created_at: datetime
    task_type: TaskType
    confidence: ConfidenceLevel | None
    status: CaseStatus


@dataclass(slots=True)
class WorkflowCount:
    day: date
    task_type: TaskType
    count: int


@dataclass(slots=True)
class StoredCaseBundle:
    case: Case
    assets: list[InputAsset]
    extracted_record: ExtractedRecord | None
    reply_set: ReplySet | None
    case_brief: CaseBrief | None
    clarifying_questions: list[ClarifyingQuestion]


@dataclass(slots=True)
class PromptTemplate:
    title: str
    body: str
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class AssistantRun:
    id: str
    title: str
    preview: str
    context_text: str
    prompt_title: str
    prompt_body: str
    output_text: str
    source_files: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
