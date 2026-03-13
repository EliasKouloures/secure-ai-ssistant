from __future__ import annotations

import pytest

from core.config import InputLimits
from core.errors import AppError
from core.models import ErrorCode, FileUpload
from services.files import FileIngestService


def test_pdf_direct_text_extraction(fake_backend) -> None:
    fitz = pytest.importorskip("fitz")
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Leo Martin will be absent on 2026-03-12.")
    pdf_bytes = document.tobytes()

    service = FileIngestService(InputLimits())
    parsed = service.ingest([FileUpload(name="absence.pdf", content=pdf_bytes)], fake_backend, supports_vision=True)

    assert "Leo Martin" in parsed.combined_text
    assert parsed.assets[0].parse_method.value == "direct_text"


def test_image_low_confidence_is_rejected(app_config) -> None:
    from tests.conftest import FakeBackend

    service = FileIngestService(app_config.limits)
    with pytest.raises(AppError) as exc_info:
        service.ingest(
            [FileUpload(name="blurred.png", content=b"fake-image", content_type="image/png")],
            backend=FakeBackend(ocr_confidence=0.2),
            supports_vision=True,
        )

    assert exc_info.value.code == ErrorCode.OCR_LOW_CONFIDENCE

