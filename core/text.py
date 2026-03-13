from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from typing import cast

WHITESPACE_RE = re.compile(r"[ \t]+")
LINEBREAK_RE = re.compile(r"\n{3,}")
THINK_TAG_RE = re.compile(
    r"<think>.*?</think>|<analysis>.*?</analysis>|<reasoning>.*?</reasoning>",
    re.IGNORECASE | re.DOTALL,
)
CODE_FENCE_RE = re.compile(r"```(?:json|markdown|text)?|```", re.IGNORECASE)
XML_TAG_RE = re.compile(r"</?(?:assistant|final|scratchpad|internal)[^>]*>", re.IGNORECASE)


def normalise_whitespace(text: str) -> str:
    compact = WHITESPACE_RE.sub(" ", text.replace("\r\n", "\n").replace("\r", "\n"))
    compact = re.sub(r"[ \t]+\n", "\n", compact)
    compact = LINEBREAK_RE.sub("\n\n", compact)
    return compact.strip()


def strip_hidden_reasoning(text: str) -> str:
    cleaned = THINK_TAG_RE.sub("", text)
    cleaned = XML_TAG_RE.sub("", cleaned)
    cleaned = CODE_FENCE_RE.sub("", cleaned)
    cleaned = re.sub(r"\[\[(?:analysis|reasoning)[^\]]*\]\]", "", cleaned, flags=re.IGNORECASE)
    return normalise_whitespace(cleaned)


def clean_json_block(text: str) -> str:
    stripped = strip_hidden_reasoning(text)
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    return match.group(0) if match else stripped


def parse_json(text: str) -> dict[str, object]:
    return cast(dict[str, object], json.loads(clean_json_block(text)))


def detect_relative_date_terms(text: str) -> list[str]:
    hits: list[str] = []
    lowered = text.lower()
    for term in ("today", "tomorrow", "yesterday", "next week", "next monday", "next tuesday"):
        if term in lowered:
            hits.append(term)
    return hits


def parse_dates(text: str, anchor: date) -> tuple[list[str], list[str]]:
    explicit: list[str] = []
    warnings: list[str] = []

    numeric_patterns = [
        r"\b(\d{4})-(\d{2})-(\d{2})\b",
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b",
    ]
    for pattern in numeric_patterns:
        for match in re.finditer(pattern, text):
            groups = match.groups()
            try:
                if pattern.startswith(r"\b(\d{4})"):
                    parsed = date(int(groups[0]), int(groups[1]), int(groups[2]))
                else:
                    parsed = date(int(groups[2]), int(groups[1]), int(groups[0]))
            except ValueError:
                continue
            value = parsed.isoformat()
            if value not in explicit:
                explicit.append(value)

    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    for match in re.finditer(
        r"\b(\d{1,2})\s+(" + "|".join(month_names) + r")(?:\s+(\d{4}))?\b",
        text,
        flags=re.IGNORECASE,
    ):
        day_value = int(match.group(1))
        month_value = month_names[match.group(2).lower()]
        year_value = int(match.group(3)) if match.group(3) else anchor.year
        try:
            parsed = date(year_value, month_value, day_value)
        except ValueError:
            continue
        value = parsed.isoformat()
        if value not in explicit:
            explicit.append(value)

    for term in detect_relative_date_terms(text):
        warnings.append(f"Relative date '{term}' needs an absolute anchor.")
        if term == "today":
            explicit.append(anchor.isoformat())
        elif term == "tomorrow":
            explicit.append((anchor + timedelta(days=1)).isoformat())
        elif term == "yesterday":
            explicit.append((anchor - timedelta(days=1)).isoformat())

    return explicit, warnings


def title_case_name(value: str | None) -> str | None:
    if not value:
        return None
    words = [part.capitalize() for part in re.split(r"\s+", value.strip()) if part]
    return " ".join(words) if words else None


def iso_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
