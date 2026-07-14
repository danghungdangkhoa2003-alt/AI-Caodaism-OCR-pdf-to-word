"""Command line entry point for AI Caodaism OCR Pro.

Run ``python main.py sample.pdf`` from the VS Code terminal.  With no
argument the program asks for a PDF path, so no paths or API keys are kept in
source code.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from src.config import INPUT_DIR, OUTPUT_DIR
from src.core.logger import configure_logging, log
from src.core.progress import ProgressTracker
from src.core.setup import ensure_directories
from src.exporter.docx_exporter import DocumentExporter
from src.pdf.pdf_processor import PDFProcessor, PageContent

if TYPE_CHECKING:
    from src.ocr.paddle_engine import PaddleOCREngine


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Chuyển PDF Cao Đài sang Word Unicode (Times New Roman, 13pt).",
        epilog="Ví dụ: python main.py input/sample.pdf --output output/result.docx"
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
    """Choose a PDF file: from argument, file dialog, or prompt."""
    if argument:
        pdf_path = argument.expanduser().resolve()
        if pdf_path.is_file() and pdf_path.suffix.lower() == ".pdf":
            return pdf_path
        log.error("Invalid PDF path: %s", argument)
        raise FileNotFoundError(f"Không tìm thấy PDF hợp lệ: {argument}")
    
    # Try file dialog first
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
        if selected:
            return Path(selected).expanduser().resolve()
    except Exception as exc:
        log.warning("Cannot open file dialog (%s); switching to text input.", exc)
    
    # Fallback to text prompt
    selected = input("Nhập đường dẫn file PDF: ").strip().strip('"')
    if not selected:
        raise ValueError("Bạn chưa chọn file PDF.")
    
    pdf_path = Path(selected).expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"File không tồn tại: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"File phải là PDF, không phải: {pdf_path.suffix}")
    return pdf_path


def main() -> int:
    """Main entry point."""
    args = parse_args()
    ensure_directories()
    configure_logging()
    
    try:
        log.info("=" * 60)
        log.info("AI Caodaism OCR Pro - Chuyển PDF sang Word Unicode")
        log.info("=" * 60)
        
        pdf_path = choose_pdf(args.pdf)
        log.info("Input PDF: %s", pdf_path)
        
        output_path = args.output or OUTPUT_DIR / f"{pdf_path.stem}_unicode_tnr13.docx"
        output_path = output_path.expanduser().resolve()
        log.info("Output DOCX: %s", output_path)
        
        # Initialize PDF processor
        log.info("Opening PDF...")
        processor = PDFProcessor(pdf_path, dpi=args.dpi)
        log.info("PDF has %d pages", processor.page_count)
        
        ocr_engine: PaddleOCREngine | None = None
        pages: list[PageContent] = []
        
        # Process each page
        progress = ProgressTracker(processor.page_count, "Processing pages")
        for page_index in range(processor.page_count):
            try:
                content = processor.read_page(page_index, force_ocr=args.force_ocr)
                if content.needs_ocr:
                    if ocr_engine is None:
                        log.info("Initializing PaddleOCR engine...")
                        from src.ocr.paddle_engine import PaddleOCREngine
                        ocr_engine = PaddleOCREngine()
                    content = processor.ocr_page(page_index, ocr_engine)
                pages.append(content)
                progress.step(f"Processed page {page_index + 1} ({content.source})")
            except Exception as exc:
                log.error("Error processing page %d: %s", page_index + 1, exc)
                raise
        
        # Export to DOCX
        log.info("Exporting to DOCX...")
        DocumentExporter().export(pages, output_path, include_page_reference=args.page_reference)
        processor.close()
        
        log.info("=" * 60)
        log.info("SUCCESS! Converted PDF to: %s", output_path)
        log.info("=" * 60)
        return 0
        
    except FileNotFoundError as exc:
        log.error("File error: %s", exc)
        return 1
    except ValueError as exc:
        log.error("Input error: %s", exc)
        return 1
    except Exception as exc:
        log.exception("Conversion failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
