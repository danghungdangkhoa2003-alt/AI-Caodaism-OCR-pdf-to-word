from pathlib import Path
from src.core.logger import log

class TextExporter:
    def __init__(self, output_dir="output"):
        """Khởi tạo thư mục đầu ra."""
        self.output_base = Path(output_dir)
        self.txt_dir = self.output_base / "raw_text"
        self.md_dir = self.output_base / "markdown"
        
        # Tự động tạo các thư mục nếu chưa có
        self.txt_dir.mkdir(parents=True, exist_ok=True)
        self.md_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"Thư mục lưu trữ đã sẵn sàng tại: {self.output_base}")

    def export_page(self, text, original_image_path):
        """Lưu văn bản OCR của từng trang vào file tương ứng."""
        # Lấy tên file không bao gồm phần mở rộng (ví dụ: clean_sample_page_001)
        page_name = Path(original_image_path).stem
        
        # 1. Xuất file TXT thuần túy
        txt_path = self.txt_dir / f"{page_name}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        # 2. Xuất file Markdown (để sau này tiện làm mục lục hoặc định dạng sách)
        md_path = self.md_dir / f"{page_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            md_content = f"# {page_name.upper()}\n\n{text}\n\n---\n*Trích xuất tự động bởi AI-Caodaism-OCR*"
            f.write(md_content)

        log.info(f"💾 Đã lưu dữ liệu trang [{page_name}] vào hệ thống lưu trữ.")
        return txt_path, md_path