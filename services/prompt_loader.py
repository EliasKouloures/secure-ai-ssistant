from __future__ import annotations

from pathlib import Path


class PromptLoader:
    def __init__(self, prompt_dir: str | Path = "prompts") -> None:
        self.prompt_dir = Path(prompt_dir)

    def load(self, name: str) -> str:
        return (self.prompt_dir / name).read_text(encoding="utf-8").strip()
