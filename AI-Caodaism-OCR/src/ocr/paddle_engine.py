"""PaddleOCR adapter with layout coordinates and confidence data."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("GLOG_minloglevel", "3")

try:
    from paddleocr import PaddleOCR
except ModuleNotFoundError as exc:
    PaddleOCR = None  # type: ignore[assignment]
    _PADDLE_IMPORT_ERROR = exc

from src.core.logger import log

if TYPE_CHECKING:
    from src.pdf.pdf_processor import ContentBlock


class PaddleOCREngine:
    def __init__(self) -> None:
        if PaddleOCR is None:
            raise RuntimeError(
                "PaddleOCR chưa được cài. Hãy dùng Python 3.11, tạo .venv rồi chạy "
                "`python -m pip install -r requirements.txt`."
            ) from _PADDLE_IMPORT_ERROR
        log.info("Đang khởi tạo PaddleOCR tiếng Việt…")
        self.ocr = PaddleOCR(lang="vi", show_log=False, use_angle_cls=True)

    def extract_blocks(self, image_path: Path, pdf_width: float, pdf_height: float) -> list[ContentBlock]:
        """Recognize text and map pixel bounding boxes back into PDF points."""
        from PIL import Image
        from src.pdf.pdf_processor import ContentBlock, TextSpan

        with Image.open(image_path) as image:
            image_width, image_height = image.size
        result = self.ocr.ocr(str(image_path), cls=True)
        blocks: list[ContentBlock] = []
        for row in result[0] if result else []:
            if not row or not row[1]:
                continue
            points, (text, confidence) = row
            if float(confidence) < 0.15 or not str(text).strip():
                continue
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            bbox = (
                min(xs) * pdf_width / image_width,
                min(ys) * pdf_height / image_height,
                max(xs) * pdf_width / image_width,
                max(ys) * pdf_height / image_height,
            )
            blocks.append(ContentBlock("text", bbox, [TextSpan(str(text))]))
        blocks.sort(key=lambda item: (round(item.bbox[1] / 12), item.bbox[0]))
        return blocks
