from __future__ import annotations

import json
from pathlib import Path

from services.prompt_library import PromptLibraryService


def test_prompt_library_seeds_and_sorts_titles(tmp_path: Path) -> None:
    seed_path = tmp_path / "seed.json"
    seed_path.write_text(
        json.dumps(
            [
                {"title": "Z Prompt", "body": "Last"},
                {"title": "A Prompt", "body": "First"},
            ]
        ),
        encoding="utf-8",
    )

    service = PromptLibraryService(
        library_path=tmp_path / "library.json",
        seed_path=seed_path,
    )

    prompts = service.list_prompts()

    assert [item.title for item in prompts] == ["A Prompt", "Z Prompt"]


def test_prompt_library_derives_title_for_new_prompt(tmp_path: Path) -> None:
    service = PromptLibraryService(
        library_path=tmp_path / "library.json",
        seed_path=tmp_path / "missing-seed.json",
    )

    saved = service.save_prompt("Write a calm school reply.\nUse British English.")

    assert saved.title == "Write a calm school reply"
    assert service.get_prompt(saved.title).body.startswith("Write a calm school reply")
