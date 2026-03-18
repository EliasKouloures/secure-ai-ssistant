from __future__ import annotations

import json
from pathlib import Path

from core.models import PromptTemplate, utc_now


class PromptLibraryService:
    def __init__(
        self,
        library_path: str | Path = "data/prompt_library.json",
        seed_path: str | Path = "prompts/default_library.json",
    ) -> None:
        self.library_path = Path(library_path)
        self.seed_path = Path(seed_path)
        self.library_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_library()

    def list_prompts(self) -> list[PromptTemplate]:
        items = self._read_library()
        prompts = [
            PromptTemplate(
                title=str(item["title"]),
                body=str(item["body"]),
                updated_at=utc_now(),
            )
            for item in items
        ]
        return sorted(prompts, key=lambda item: item.title.lower())

    def get_prompt(self, title: str) -> PromptTemplate | None:
        for prompt in self.list_prompts():
            if prompt.title == title:
                return prompt
        return None

    def save_prompt(self, prompt_body: str, selected_title: str | None = None) -> PromptTemplate:
        title = selected_title or self.derive_title(prompt_body)
        items = self._read_library()
        stored = {"title": title, "body": prompt_body.strip()}
        replaced = False
        for index, item in enumerate(items):
            if str(item["title"]) == title:
                items[index] = stored
                replaced = True
                break
        if not replaced:
            items.append(stored)
        self._write_library(items)
        return PromptTemplate(title=title, body=prompt_body.strip(), updated_at=utc_now())

    def derive_title(self, prompt_body: str) -> str:
        for line in prompt_body.splitlines():
            cleaned = line.strip().strip("#").strip()
            if cleaned:
                return cleaned.rstrip(":.")[:48] or "Untitled Prompt"
        return "Untitled Prompt"

    def _ensure_library(self) -> None:
        if self.library_path.exists():
            return
        if self.seed_path.exists():
            self.library_path.write_text(self.seed_path.read_text(encoding="utf-8"), encoding="utf-8")
            return
        self._write_library([])

    def _read_library(self) -> list[dict[str, str]]:
        try:
            raw_items = json.loads(self.library_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self._ensure_library()
            raw_items = json.loads(self.library_path.read_text(encoding="utf-8"))
        return [
            {"title": str(item["title"]), "body": str(item["body"])}
            for item in raw_items
            if isinstance(item, dict) and "title" in item and "body" in item
        ]

    def _write_library(self, items: list[dict[str, str]]) -> None:
        self.library_path.write_text(json.dumps(items, indent=2), encoding="utf-8")
