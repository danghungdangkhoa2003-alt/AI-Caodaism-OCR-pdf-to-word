"""Command line entry point for AI Caodaism OCR Pro.

Run ``python main.py sample.pdf`` from the VS Code terminal.  With no
argument the program asks for a PDF path, so no paths or API keys are kept in
source code.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from src.config import INPUT_DIR, OUTPUT_DIR
from src.core.logger import configure_logging, log
from src.core.setup import ensure_directories
from src.exporter.docx_exporter import DocumentExporter
from src.pdf.pdf_processor import PDFProcessor, PageContent

if TYPE_CHECKING:
    from src.ocr.paddle_engine import PaddleOCREngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chuyển PDF Cao Đài sang Word Unicode (Times New Roman, 13pt)."
    )
    parser.add_argument("pdf", nargs="?", type=Path, help="Đường dẫn PDF đầu vào")
    parser.add_argument("--output", type=Path, help="Đường dẫn file DOCX đầu ra")
    parser.add_argument("--dpi", type=int, default=250, help="DPI khi OCR PDF scan (mặc định: 250)")
    parser.add_argument("--force-ocr", action="store_true", help="OCR cả PDF đã có lớp văn bản")
    parser.add_argument(
        "--page-reference", action="store_true",
        help="Chèn ảnh trang gốc ở cuối mỗi trang Word để tiện đối chiếu bản scan",
    )
    return parser.parse_args()


def choose_pdf(argument: Path | None) -> Path:
    if argument:
        return argument.expanduser().resolve()
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askopenfilename(
            title="Chọn file PDF cần chuyển sang Word",
            initialdir=str(INPUT_DIR),
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        root.destroy()
    except Exception as exc:
        log.warning("Không mở được hộp chọn file (%s); chuyển sang nhập đường dẫn.", exc)
        selected = input("Nhập đường dẫn file PDF: ").strip().strip('"')
    if not selected:
        raise ValueError("Bạn chưa chọn file PDF.")
    return Path(selected).expanduser().resolve()


def main() -> int:
    args = parse_args()
    ensure_directories()
    configure_logging()
    try:
        pdf_path = choose_pdf(args.pdf)
        if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
            raise FileNotFoundError(f"Không tìm thấy PDF hợp lệ: {pdf_path}")

        output_path = args.output or OUTPUT_DIR / f"{pdf_path.stem}_unicode_tnr13.docx"
        output_path = output_path.expanduser().resolve()
        processor = PDFProcessor(pdf_path, dpi=args.dpi)
        ocr_engine: PaddleOCREngine | None = None
        pages: list[PageContent] = []

        for page_index in range(processor.page_count):
            content = processor.read_page(page_index, force_ocr=args.force_ocr)
            if content.needs_ocr:
                if ocr_engine is None:
                    from src.ocr.paddle_engine import PaddleOCREngine

                    ocr_engine = PaddleOCREngine()
                content = processor.ocr_page(page_index, ocr_engine)
            pages.append(content)
            log.info("Đã xử lý trang %s/%s (%s)", page_index + 1, processor.page_count, content.source)

        DocumentExporter().export(pages, output_path, include_page_reference=args.page_reference)
        processor.close()
        log.info("Hoàn thành. File Word: %s", output_path)
        return 0
    except Exception as exc:
        log.exception("Chuyển đổi thất bại: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
