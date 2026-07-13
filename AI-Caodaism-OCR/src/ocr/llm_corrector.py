import os
import google.generativeai as genai
from src.core.logger import log

class LLMCorrector:
    def __init__(self, api_key=None):
        log.info("Đang khởi tạo Module 08: AI Text Corrector...")
        
        # Lấy API Key từ tham số truyền vào hoặc từ biến môi trường hệ thống
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            log.warning("⚠ Chưa cấu hình GEMINI_API_KEY. Module 08 sẽ chạy ở chế độ BYPASS (Giữ nguyên bản thô).")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Sử dụng gemini-1.5-flash tối ưu tuyệt đối cho việc xử lý text nhanh
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                log.info("🤖 Kết nối AI Gemini thành công! Hệ thống sẵn sàng sửa lỗi chính tả.")
            except Exception as e:
                log.error(f"❌ Lỗi kết nối API Gemini: {str(e)}")
                self.model = None

    def correct_text(self, raw_text, context_hint="Tài liệu, kinh sách, nội san thuộc tôn giáo Cao Đài"):
        """Sử dụng trí tuệ nhân tạo để sửa lỗi chính tả và khôi phục dấu tiếng Việt theo ngữ cảnh."""
        if not self.model or not raw_text.strip():
            return raw_text

        log.info("🧠 AI đang phân tích ngữ cảnh để sửa lỗi và khôi phục dấu...")
        
        # Prompt kỹ thuật chuyên dụng ép AI sửa lỗi chính xác, không bịa chữ
        system_prompt = f"""
        Bạn là một chuyên gia hiệu đính văn bản cổ chuyên nghiệp. 
        Nhiệm vụ của bạn là sửa toàn bộ lỗi chính tả, lỗi nhận diện sai ký tự do quét OCR từ hình ảnh sách cũ sang văn bản thô.
        
        Ngữ cảnh của tài liệu này: {context_hint}.
        
        Các quy tắc nghiêm ngặt phải tuân thủ:
        1. Khôi phục hoàn toàn dấu tiếng Việt bị mất hoặc bị biến dạng (Ví dụ các ký tự lỗi hệ thống như 'c6' thành 'có', 'th@' thành 'thể', 'ngui' thành 'người').
        2. Sửa các từ bị méo mó âm tiết dựa trên ngữ cảnh toàn câu (Ví dụ: 'keiblet laengooi khon' sửa thành 'biết là người khôn').
        3. GIỮ NGUYÊN cấu trúc xuống dòng, các mốc thời gian, số thứ tự, các đoạn thơ lines, và các ký hiệu đóng mở ngoặc đơn.
        4. TUYỆT ĐỐI KHÔNG tự ý tóm tắt, không viết thêm lời bình luận, không giải thích dông dài. Chỉ trả về duy nhất văn bản đã được sửa lỗi hoàn chỉnh.

        Văn bản thô lỗi cần sửa:
        \"\"\"
        {raw_text}
        \"\"\"
        """

        try:
            response = self.model.generate_content(system_prompt)
            cleaned_text = response.text.strip()
            
            # Khử bỏ các ký tự bọc markdown văn bản nếu AI vô tình thêm vào
            if cleaned_text.startswith("```"):
                cleaned_text = "\n".join(cleaned_text.split("\n")[1:-1])
                
            log.info("✨ Đã hoàn thành hiệu đính văn bản bằng AI.")
            return cleaned_text
        except Exception as e:
            log.error(f"⚠ Lỗi trong quá trình gọi AI sửa bài: {str(e)}. Trả về văn bản gốc.")
            return raw_text