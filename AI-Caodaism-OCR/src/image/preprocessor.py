import cv2
import numpy as np
from pathlib import Path
from src.config import PROCESSED_DIR
from src.core.logger import log

class ImagePreprocessor:
    def __init__(self):
        pass

    def process_image(self, image_path):
        """
        Thực hiện chuỗi xử lý: Ảnh màu -> Ảnh xám -> Khử nhiễu -> Trắng/Đen.
        """
        img_path = Path(image_path)
        if not img_path.exists():
            log.error(f"Không tìm thấy ảnh để xử lý: {img_path}")
            raise FileNotFoundError(f"Không tìm thấy: {img_path}")
            
        # 1. Đọc ảnh bằng OpenCV
        img = cv2.imread(str(img_path))
        if img is None:
            raise ValueError(f"OpenCV không thể đọc được file: {img_path}")

        # 2. Chuyển đổi sang thang độ xám (Grayscale)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Khử nhiễu nhẹ (Median Blur) để làm sạch các lấm tấm trên giấy scan
        blurred = cv2.medianBlur(gray, 3)
        
        # 4. Phân ngưỡng thích nghi (Adaptive Thresholding)
        # Thuật toán này sẽ tính toán độ sáng của từng vùng nhỏ để tẩy nền, 
        # rất hiệu quả cho sách bị đổ bóng gáy hoặc sáng tối không đều.
        binary = cv2.adaptiveThreshold(
            blurred, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Lưu file đã xử lý
        out_filename = f"clean_{img_path.name}"
        out_path = PROCESSED_DIR / out_filename
        
        cv2.imwrite(str(out_path), binary)
        log.info(f"Đã làm sạch ảnh và lưu tại: {out_path.name}")
        
        return out_path