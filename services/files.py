from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from core.config import InputLimits
from core.errors import AppError
from core.models import AssetType, ErrorCode, FileUpload, InputAsset, ParseMethod, SourceMode
from core.text import normalise_whitespace
from services.backend import BackendClient

ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg"}


@dataclass(slots=True)
class ParsedInputs:
    combined_text: str
    assets: list[InputAsset]
    source_mode: SourceMode
    warnings: list[str]
    ocr_used: bool
    low_quality: bool


class FileIngestService:
    def __init__(self, limits: InputLimits) -> None:
        self.limits = limits

    def ingest(self, files: list[FileUpload], backend: BackendClient | None = None, supports_vision: bool = False) -> ParsedInputs:
        if len(files) > self.limits.max_assets:
            raise AppError(ErrorCode.FILE_PARSE_FAILED, f"Only {self.limits.max_assets} files are supported per case.")

        texts: list[str] = []
        assets: list[InputAsset] = []
        warnings: list[str] = []
        ocr_used = False
        low_quality = False
        source_mode = SourceMode.TEXT

        for upload in files:
            self._validate(upload)
            if upload.suffix == ".pdf":
                pdf_text, asset, pdf_warnings, used_ocr, weak_signal = self._parse_pdf(upload, backend, supports_vision)
                texts.append(pdf_text)
                assets.append(asset)
                warnings.extend(pdf_warnings)
                ocr_used = ocr_used or used_ocr
                low_quality = low_quality or weak_signal
                source_mode = SourceMode.PDF if source_mode == SourceMode.TEXT and not texts[:-1] else SourceMode.MIXED
            else:
                image_text, asset, image_warnings, weak_signal = self._parse_image(upload, backend, supports_vision)
                texts.append(image_text)
                assets.append(asset)
                warnings.extend(image_warnings)
                ocr_used = True
                low_quality = low_quality or weak_signal
                source_mode = SourceMode.IMAGE if source_mode == SourceMode.TEXT and not texts[:-1] else SourceMode.MIXED

        return ParsedInputs(
            combined_text=normalise_whitespace("\n\n".join(item for item in texts if item)),
            assets=assets,
            source_mode=source_mode if files else SourceMode.TEXT,
            warnings=warnings,
            ocr_used=ocr_used,
            low_quality=low_quality,
        )

    def _validate(self, upload: FileUpload) -> None:
        if upload.suffix not in ALLOWED_SUFFIXES:
            raise AppError(ErrorCode.UNSUPPORTED_FILE_TYPE, f"{upload.name} is not a supported file type.")
        if upload.size_bytes > self.limits.max_file_mb * 1024 * 1024:
            raise AppError(ErrorCode.FILE_PARSE_FAILED, f"{upload.name} exceeds the file size limit.")

    def _parse_pdf(
        self,
        upload: FileUpload,
        backend: BackendClient | None,
        supports_vision: bool,
    ) -> tuple[str, InputAsset, list[str], bool, bool]:
        try:
            import fitz
        except ImportError as exc:
            raise AppError(ErrorCode.FILE_PARSE_FAILED, "PyMuPDF is not installed.") from exc

        try:
            document = fitz.open(stream=upload.content, filetype="pdf")
        except Exception as exc:
            raise AppError(ErrorCode.FILE_PARSE_FAILED, f"{upload.name} could not be parsed as a PDF.") from exc

        if document.page_count > self.limits.max_pdf_pages:
            raise AppError(ErrorCode.FILE_PARSE_FAILED, f"{upload.name} exceeds the PDF page limit.")

        direct_text_parts: list[str] = []
        for page in document:
            page_text = normalise_whitespace(page.get_text())
            if page_text:
                direct_text_parts.append(page_text)
        direct_text = normalise_whitespace("\n\n".join(direct_text_parts))
        if len(direct_text) >= 40:
            return (
                direct_text,
                InputAsset(
                    id=f"asset_{uuid4().hex[:12]}",
                    case_id="",
                    asset_type=AssetType.PDF,
                    filename=upload.name,
                    parse_method=ParseMethod.DIRECT_TEXT,
                    parse_success=True,
                ),
                [],
                False,
                False,
            )

        if not supports_vision or backend is None:
            raise AppError(
                ErrorCode.OCR_LOW_CONFIDENCE,
                "The PDF did not contain enough direct text and local vision OCR is unavailable.",
            )

        image_text_parts: list[str] = []
        confidences: list[float] = []
        warnings: list[str] = []
        for page in document:
            pixmap = page.get_pixmap(dpi=150)
            result = backend.ocr_image(pixmap.tobytes("png"), "image/png", f"{upload.name}:{page.number + 1}")
            if result.is_handwritten:
                raise AppError(ErrorCode.OCR_LOW_CONFIDENCE, "Handwritten documents are not supported in the MVP.")
            image_text_parts.append(result.text)
            confidences.append(result.ocr_confidence)
            warnings.extend(result.warnings or [])
        average = sum(confidences) / len(confidences) if confidences else 0.0
        if average < 0.6:
            raise AppError(ErrorCode.OCR_LOW_CONFIDENCE, "OCR confidence is too low. Please paste clearer text instead.")

        return (
            normalise_whitespace("\n\n".join(image_text_parts)),
            InputAsset(
                id=f"asset_{uuid4().hex[:12]}",
                case_id="",
                asset_type=AssetType.PDF,
                filename=upload.name,
                parse_method=ParseMethod.OCR,
                parse_success=True,
                ocr_confidence=round(average, 2),
            ),
            warnings,
            True,
            average < 0.75,
        )

    def _parse_image(
        self,
        upload: FileUpload,
        backend: BackendClient | None,
        supports_vision: bool,
    ) -> tuple[str, InputAsset, list[str], bool]:
        if not supports_vision or backend is None:
            raise AppError(ErrorCode.OCR_LOW_CONFIDENCE, "Vision OCR unavailable locally for image files.")
        result = backend.ocr_image(upload.content, upload.content_type or "image/png", upload.name)
        if result.is_handwritten:
            raise AppError(ErrorCode.OCR_LOW_CONFIDENCE, "Handwritten uploads are not supported in the MVP.")
        if result.ocr_confidence < 0.6:
            raise AppError(ErrorCode.OCR_LOW_CONFIDENCE, "The image was too unclear to read confidently.")
        return (
            normalise_whitespace(result.text),
            InputAsset(
                id=f"asset_{uuid4().hex[:12]}",
                case_id="",
                asset_type=AssetType.IMAGE,
                filename=upload.name,
                parse_method=ParseMethod.OCR,
                parse_success=True,
                ocr_confidence=round(result.ocr_confidence, 2),
            ),
            result.warnings or [],
            result.ocr_confidence < 0.75,
        )
