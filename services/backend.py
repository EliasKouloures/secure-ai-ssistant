from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol, cast

from core.config import BackendProfile
from core.errors import AppError
from core.models import ErrorCode, HealthCheckResult
from core.text import parse_json, strip_hidden_reasoning
from services.prompt_loader import PromptLoader


@dataclass(slots=True)
class VisionOCRResult:
    text: str
    ocr_confidence: float
    is_handwritten: bool = False
    warnings: list[str] | None = None


class BackendClient(Protocol):
    def health_check(self) -> HealthCheckResult: ...

    def generate_reply_payload(self, context: dict[str, Any]) -> dict[str, Any]: ...

    def ocr_image(self, image_bytes: bytes, mime_type: str, filename: str) -> VisionOCRResult: ...


class OpenAICompatibleBackend:
    def __init__(self, profile: BackendProfile, prompt_loader: PromptLoader | None = None) -> None:
        self.profile = profile
        self.prompt_loader = prompt_loader or PromptLoader()

    def health_check(self) -> HealthCheckResult:
        url = f"{self.profile.base_url.rstrip('/')}/models"
        request = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.profile.api_key}"},
        )
        warnings: list[str] = []
        try:
            with urllib.request.urlopen(request, timeout=self.profile.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return HealthCheckResult(
                status="offline",
                backend_name=self.profile.provider_name,
                base_url=self.profile.base_url,
                model_id=self.profile.model_id,
                reachable=False,
                warnings=[str(exc)],
            )

        models = [item.get("id", "") for item in payload.get("data", []) if isinstance(item, dict)]
        if models and self.profile.model_id not in models:
            warnings.append(
                f"Configured model '{self.profile.model_id}' is not reported by the backend. "
                f"Available: {', '.join(models[:3])}."
            )
        return HealthCheckResult(
            status="ok",
            backend_name=self.profile.provider_name,
            base_url=self.profile.base_url,
            model_id=self.profile.model_id,
            reachable=True,
            warnings=warnings,
        )

    def generate_reply_payload(self, context: dict[str, Any]) -> dict[str, Any]:
        system_prompt = self.prompt_loader.load("output_system.txt")
        user_prompt = self.prompt_loader.load("output_user.txt").format(**context)
        payload = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        try:
            return parse_json(payload)
        except json.JSONDecodeError as exc:
            raise AppError(
                ErrorCode.MODEL_TIMEOUT, f"Backend returned invalid JSON: {exc}"
            ) from exc

    def ocr_image(self, image_bytes: bytes, mime_type: str, filename: str) -> VisionOCRResult:
        system_prompt = self.prompt_loader.load("vision_system.txt")
        user_prompt = self.prompt_loader.load("vision_user.txt").format(filename=filename)
        encoded = base64.b64encode(image_bytes).decode("ascii")
        payload = self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                        },
                    ],
                },
            ]
        )
        try:
            parsed = parse_json(payload)
        except json.JSONDecodeError as exc:
            raise AppError(
                ErrorCode.FILE_PARSE_FAILED, f"Vision output was not valid JSON: {exc}"
            ) from exc
        raw_warnings = parsed.get("warnings", [])
        warning_items = raw_warnings if isinstance(raw_warnings, list) else []
        return VisionOCRResult(
            text=strip_hidden_reasoning(str(parsed.get("text", ""))),
            ocr_confidence=float(cast(float | int | str, parsed.get("ocr_confidence", 0.0))),
            is_handwritten=bool(parsed.get("is_handwritten", False)),
            warnings=[str(item) for item in warning_items if isinstance(item, str)],
        )

    def _chat(self, messages: list[dict[str, Any]]) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise AppError(
                ErrorCode.BACKEND_UNREACHABLE,
                "OpenAI Python SDK is not installed. Install dependencies first.",
            ) from exc

        client = OpenAI(
            base_url=self.profile.base_url,
            api_key=self.profile.api_key,
            timeout=self.profile.timeout_seconds,
        )
        try:
            response = client.chat.completions.create(
                model=self.profile.model_id,
                temperature=self.profile.temperature,
                max_tokens=self.profile.max_tokens,
                messages=messages,  # type: ignore[arg-type]
            )
        except Exception as exc:  # pragma: no cover - backend exceptions vary by provider
            raise AppError(
                ErrorCode.BACKEND_UNREACHABLE, f"Local model backend request failed: {exc}"
            ) from exc

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise AppError(ErrorCode.MODEL_TIMEOUT, "Local model backend returned no content.")
        return str(message)
