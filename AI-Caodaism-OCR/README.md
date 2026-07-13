# AI Caodaism OCR Pro

Ứng dụng Python chạy trong VS Code để chuyển PDF Cao Đài (PDF có lớp chữ hoặc PDF scan) sang Word `.docx` Unicode. Mọi phần văn bản xuất ra được đặt về **Times New Roman, 13pt**. Ảnh nhúng trong PDF được giữ lại; với bản scan, tùy chọn đối chiếu giữ ảnh trang gốc.

## Chạy trong VS Code

1. Mở thư mục dự án bằng VS Code và chọn Python 3.11.
2. Mở Terminal trong VS Code rồi tạo môi trường ảo:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Chuyển đổi một PDF:

   ```powershell
   python main.py "D:\du-lieu\tai-lieu-cao-dai.pdf"
   ```

   Kết quả mặc định nằm tại `output/<ten-pdf>_unicode_tnr13.docx`.

## Tuỳ chọn

```powershell
# Buộc OCR cả PDF đã có lớp chữ
python main.py input\sach.pdf --force-ocr

# Chèn ảnh trang scan gốc sau nội dung Word để đối chiếu thủ công
python main.py input\sach.pdf --page-reference

# Chọn tên/nơi lưu file đầu ra
python main.py input\sach.pdf --output output\sach-da-chuyen.docx
```

Không truyền tham số: chương trình tự dùng PDF duy nhất trong thư mục `input`; nếu có nhiều file, chương trình sẽ hỏi đường dẫn. Chỉ cần chạy `python main.py`.

## Lưu ý chất lượng

PDF có lớp chữ thường cho bố cục tốt nhất vì chương trình đọc các khối chữ/ảnh theo thứ tự và phong cách gốc. PDF scan cần PaddleOCR; chất lượng phụ thuộc độ rõ của bản scan và nên dùng `--page-reference` khi cần soát lại. Word là định dạng dòng chảy, vì vậy không thể bảo đảm vị trí tuyệt đối từng ký tự như phần mềm DTP; tài liệu tạo ra giữ thứ tự đọc, trang, ảnh và định dạng đậm/nghiêng ở mức thực tế của DOCX.
