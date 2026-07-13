"""PDF reading, embedded-image extraction, and OCR fallback."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import fitz

from src.config import CACHE_DIR
from src.core.logger import log
from src.core.vietnamese_encoding import to_unicode

if TYPE_CHECKING:
    from src.ocr.paddle_engine import PaddleOCREngine


@dataclass(slots=True)
class TextSpan:
    text: str
    bold: bool = False
    italic: bool = False


@dataclass(slots=True)
class ContentBlock:
    kind: str  # text or image
    bbox: tuple[float, float, float, float]
    spans: list[TextSpan] = field(default_factory=list)
    image_path: Path | None = None


@dataclass(slots=True)
class PageContent:
    number: int
    width: float
    height: float
    blocks: list[ContentBlock]
    source: str
    needs_ocr: bool = False
    rendered_page: Path | None = None


class PDFProcessor:
    """Read text PDFs directly and use OCR only for scan-like pages."""

    def __init__(self, pdf_path: Path, dpi: int = 250) -> None:
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.document = fitz.open(pdf_path)
        self.asset_dir = CACHE_DIR / pdf_path.stem
        self.asset_dir.mkdir(parents=True, exist_ok=True)

    @property
    def page_count(self) -> int:
        return len(self.document)

    def read_page(self, page_index: int, force_ocr: bool = False) -> PageContent:
        """Return positioned text/image blocks from an existing PDF text layer."""
        page = self.document.load_page(page_index)
        page_dict = page.get_text("dict", sort=True)
        blocks: list[ContentBlock] = []
        text_characters = 0
        for index, block in enumerate(page_dict["blocks"]):
            bbox = tuple(float(value) for value in block["bbox"])
            if block["type"] == 0:
                spans: list[TextSpan] = []
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        value = to_unicode(span.get("text", ""))
                        text_characters += len(value.strip())
                        if value:
                            flags = int(span.get("flags", 0))
                            spans.append(TextSpan(value, bold=bool(flags & 16), italic=bool(flags & 2)))
                    spans.append(TextSpan("\n"))
                if spans:
                    blocks.append(ContentBlock("text", bbox, spans=spans))
            elif block["type"] == 1 and block.get("image"):
                image_path = self.asset_dir / f"page_{page_index + 1:04}_{index}.png"
                try:
                    pixmap = fitz.Pixmap(block["image"])
                    if pixmap.n - pixmap.alpha > 3:
                        pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                    pixmap.save(image_path)
                    blocks.append(ContentBlock("image", bbox, image_path=image_path))
                except Exception as exc:
                    log.warning("Không thể chuyển ảnh nhúng trang %s, khối %s sang PNG: %s", page_index + 1, index, exc)
        return PageContent(
            number=page_index + 1,
            width=page.rect.width,
            height=page.rect.height,
            blocks=blocks,
            source="PDF text layer",
            needs_ocr=force_ocr or text_characters < 20,
        )

    def render_page(self, page_index: int) -> Path:
        """Render an OCR-quality image while retaining the original PDF page ratio."""
        output = self.asset_dir / f"page_{page_index + 1:04}_render.png"
        if not output.exists():
            page = self.document.load_page(page_index)
            scale = self.dpi / 72
            page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(output)
        return output

    def ocr_page(self, page_index: int, engine: PaddleOCREngine) -> PageContent:
        """OCR a rendered page and return text blocks in reading order."""
        page = self.document.load_page(page_index)
        rendered = self.render_page(page_index)
        blocks = engine.extract_blocks(rendered, page.rect.width, page.rect.height)
        return PageContent(
            number=page_index + 1,
            width=page.rect.width,
            height=page.rect.height,
            blocks=blocks,
            source="PaddleOCR",
            rendered_page=rendered,
        )

    def close(self) -> None:
        self.document.close()
