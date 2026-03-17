from __future__ import annotations

import re
from dataclasses import dataclass
from typing import cast
from uuid import uuid4

from core.errors import AppError
from core.models import (
    Case,
    CaseBrief,
    ClarifyingQuestion,
    ErrorCode,
    ExtractedRecord,
    GeneratedOutputs,
    QuestionPriority,
    ReplySet,
    TaskType,
)
from core.text import strip_hidden_reasoning
from services.backend import BackendClient

SALUTATION_RE = re.compile(r"^(?:hello|dear|hi)\b[^,\n]{0,80},?\s*", re.IGNORECASE)
SIGN_OFF_RE = re.compile(
    r"(?:kind regards|warm regards|best regards|regards|best|sincerely|many thanks|thanks),?"
    r"(?:\s+[A-Za-z][A-Za-z .'-]{1,80})?\s*$",
    re.IGNORECASE,
)
SUBJECT_PREFIX_RE = re.compile(
    r"^(?:\d+\.\s*version\s*:\s*|version\s*\d+\s*[:\-]\s*|\d+\s*[\).\:-]\s*)",
    re.IGNORECASE,
)
SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(slots=True)
class OutputContext:
    case: Case
    extracted_record: ExtractedRecord
    missing_fields: list[str]
    warnings: list[str]
    source_types: list[str]
    operator_note: str = ""


class OutputService:
    def __init__(self, backend: BackendClient | None = None) -> None:
        self.backend = backend

    def generate(self, context: OutputContext) -> GeneratedOutputs:
        questions = self._build_questions(context)
        brief = self._build_case_brief(context)
        reply_set = None
        if context.case.reply_required and context.case.status != "blocked":
            reply_set = self._build_reply_set(context, brief, questions)
        copy_blocks = self._copy_blocks(context, brief, reply_set, questions)
        export_payloads = {
            "case_brief": brief.summary,
            "facts": self._facts_block(context.extracted_record),
            "clarifying_questions": "\n".join(
                f"- {question.question_text}" for question in questions
            ),
        }
        return GeneratedOutputs(
            case_brief=brief,
            reply_set=reply_set,
            clarifying_questions=questions,
            copy_blocks=copy_blocks,
            export_payloads=export_payloads,
            warnings=context.warnings,
        )

    def _build_case_brief(self, context: OutputContext) -> CaseBrief:
        recommended_action = self._recommended_action(context)
        summary = (
            f"Task type: {context.case.task_type.value}. "
            f"Source types used: {', '.join(context.source_types) or context.case.source_mode.value}. "
            f"Extracted fields: {self._present_fields(context.extracted_record)}. "
            f"Missing fields: {', '.join(context.missing_fields) if context.missing_fields else 'None'}. "
            f"Recommended next action: {recommended_action}. "
            f"Confidence: {context.case.confidence.value if context.case.confidence else 'unknown'}."
        )
        return CaseBrief(
            id=f"brief_{uuid4().hex[:12]}",
            case_id=context.case.id,
            summary=summary,
            missing_fields=context.missing_fields,
            recommended_action=recommended_action,
        )

    def _build_reply_set(
        self,
        context: OutputContext,
        brief: CaseBrief,
        questions: list[ClarifyingQuestion],
    ) -> ReplySet:
        if self.backend is None:
            raise AppError(ErrorCode.BACKEND_UNREACHABLE, "The local model backend is unavailable.")

        payload = self.backend.generate_reply_payload(
            {
                "task_type": context.case.task_type.value,
                "source_summary": context.case.source_summary,
                "facts_block": self._facts_block(context.extracted_record),
                "warnings": "\n".join(context.warnings) or "None",
                "missing_fields": ", ".join(context.missing_fields) or "None",
                "recommended_action": brief.recommended_action,
                "clarifying_questions": "\n".join(question.question_text for question in questions)
                or "None",
                "operator_note": context.operator_note or "None",
            }
        )
        reply_set = self._normalise_reply_payload(payload, context)
        return reply_set

    def _normalise_reply_payload(
        self, payload: dict[str, object], context: OutputContext
    ) -> ReplySet:
        subject_values = payload.get("subject_lines", [])
        subject_items = cast(list[object], subject_values if isinstance(subject_values, list) else [])
        subject_lines = [
            self._clean_subject_line(str(item))
            for item in subject_items
            if self._clean_subject_line(str(item))
        ][:3]
        while len(subject_lines) < 3:
            subject_lines.append(self._fallback_subject_line(context, len(subject_lines)))

        variants = payload.get("message_variants", {})
        if not isinstance(variants, dict):
            variants = {}
        hemingway = self._format_email_variant(
            context,
            "hemingway",
            str(variants.get("hemingway", self._fallback_variant(context, "hemingway"))),
        )
        corporate = self._format_email_variant(
            context,
            "corporate",
            str(variants.get("corporate", self._fallback_variant(context, "corporate"))),
        )
        educator = self._format_email_variant(
            context,
            "educator_first",
            str(
                variants.get(
                    "educator_first", self._fallback_variant(context, "educator_first")
                )
            ),
        )

        return ReplySet(
            id=f"reply_{uuid4().hex[:12]}",
            case_id=context.case.id,
            subject_lines=subject_lines,
            variant_hemingway=hemingway,
            variant_corporate=corporate,
            variant_educator=educator,
        )

    def _fallback_subject_line(self, context: OutputContext, index: int) -> str:
        student = context.extracted_record.student_name or "the pupil"
        fallbacks = [
            f"Update received for {student}",
            f"School office update for {student}",
            "Thank you for your message",
        ]
        return fallbacks[index]

    def _fallback_variant(self, context: OutputContext, tone: str) -> str:
        student = context.extracted_record.student_name or "[Not provided]"
        reason = context.extracted_record.reason or "the information you shared"
        if tone == "hemingway":
            return f"Thank you. We have noted the update for {student}. We will proceed based on {reason}."
        if tone == "corporate":
            return (
                f"Thank you for your message. We have recorded the update regarding {student}. "
                f"We will now proceed in line with the information provided about {reason}."
            )
        return (
            f"Thank you for letting us know about {student}. We have noted the information about {reason}, "
            "and we will take the next appropriate step."
        )

    def _facts_block(self, record: ExtractedRecord) -> str:
        return "\n".join(
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in record.as_display_dict().items()
        )

    def _copy_blocks(
        self,
        context: OutputContext,
        brief: CaseBrief,
        reply_set: ReplySet | None,
        questions: list[ClarifyingQuestion],
    ) -> dict[str, str]:
        blocks = {
            "Structured facts": self._facts_block(context.extracted_record),
            "Internal case brief": brief.summary,
        }
        if reply_set:
            blocks["Subject lines"] = self._format_subject_versions(reply_set.subject_lines)
            blocks["Hemingway response"] = reply_set.variant_hemingway
            blocks["Corporate response"] = reply_set.variant_corporate
            blocks["Empathic response"] = reply_set.variant_educator
        if questions:
            blocks["Clarifying questions"] = "\n".join(
                f"- {item.question_text}" for item in questions
            )
        return blocks

    def _build_questions(self, context: OutputContext) -> list[ClarifyingQuestion]:
        prompts = {
            "student_name": "Please confirm the pupil's full name.",
            "date_from": "Please confirm the relevant date or date range.",
            "meeting_topic": "Please confirm the meeting topic.",
            "request_type": "Please confirm what action is being requested.",
        }
        items: list[ClarifyingQuestion] = []
        for field_name in context.missing_fields[:3]:
            items.append(
                ClarifyingQuestion(
                    id=f"question_{uuid4().hex[:12]}",
                    case_id=context.case.id,
                    question_text=prompts.get(
                        field_name, f"Please confirm the {field_name.replace('_', ' ')}."
                    ),
                    priority=QuestionPriority.HIGH,
                )
            )
        return items

    def _present_fields(self, record: ExtractedRecord) -> str:
        present = [
            key.replace("_", " ")
            for key, value in record.as_display_dict().items()
            if value != "[Not provided]"
        ]
        return ", ".join(present) if present else "None"

    def _recommended_action(self, context: OutputContext) -> str:
        if context.case.status == "blocked":
            return "Stop and ask for a single-child message or typed clarification."
        if context.missing_fields:
            return "Send a short clarification request before taking further action."
        if context.case.task_type == TaskType.SCHEDULE:
            return "Review the summary and confirm the meeting details."
        if context.case.reply_required:
            return "Review the drafts, edit if needed, and copy the preferred version into the school system."
        return "Review the brief and file the case without sending a reply."

    def _clean_subject_line(self, value: str) -> str:
        cleaned = strip_hidden_reasoning(value).strip()
        cleaned = SUBJECT_PREFIX_RE.sub("", cleaned).strip()
        return cleaned

    def _format_subject_versions(self, subject_lines: list[str]) -> str:
        return "\n".join(
            f"{index}. Version: {line}"
            for index, line in enumerate(subject_lines[:3], start=1)
            if line.strip()
        )

    def _format_email_variant(self, context: OutputContext, tone: str, raw_text: str) -> str:
        cleaned = strip_hidden_reasoning(raw_text)
        body = self._strip_email_wrapping(cleaned)
        if not body:
            body = self._fallback_variant(context, tone)
        paragraphs = self._body_paragraphs(body)
        greeting = self._greeting(context)
        closing = self._closing(tone)
        parts = [greeting, *paragraphs, closing]
        return "\n\n".join(part for part in parts if part.strip())

    def _strip_email_wrapping(self, text: str) -> str:
        cleaned = strip_hidden_reasoning(text)
        cleaned = SALUTATION_RE.sub("", cleaned, count=1).strip()
        cleaned = SIGN_OFF_RE.sub("", cleaned).strip(" ,")
        cleaned = re.sub(r"\s+(?:School Office|Office Team|Administration Team)\s*$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _body_paragraphs(self, body: str) -> list[str]:
        flat_body = " ".join(part.strip() for part in body.splitlines() if part.strip())
        flat_body = re.sub(r"\s+", " ", flat_body).strip()
        if not flat_body:
            return []

        sentences = [
            sentence.strip()
            for sentence in SENTENCE_BREAK_RE.split(flat_body)
            if sentence.strip()
        ]
        if not sentences:
            return [self._ensure_sentence(flat_body)]

        first_paragraph = self._ensure_sentence(sentences[0])
        remainder = " ".join(self._ensure_sentence(sentence) for sentence in sentences[1:])
        if remainder:
            return [first_paragraph, remainder]
        return [first_paragraph]

    def _ensure_sentence(self, value: str) -> str:
        sentence = value.strip()
        if not sentence:
            return ""
        if sentence[-1] not in ".!?":
            sentence += "."
        return sentence

    def _greeting(self, context: OutputContext) -> str:
        recipient = context.extracted_record.guardian_name or ""
        if recipient and recipient != "[Not provided]":
            return f"Hello {recipient},"
        return "Hello,"

    def _closing(self, tone: str) -> str:
        mapping = {
            "hemingway": "Best,",
            "corporate": "Kind regards,",
            "educator_first": "Warm regards,",
        }
        return mapping.get(tone, "Kind regards,")
