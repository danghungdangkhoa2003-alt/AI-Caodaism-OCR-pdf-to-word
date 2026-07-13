import sqlite3
from src.config import DB_FILE
from src.core.logger import log

class DatabaseManager:
    def __init__(self):
        self.db_path = DB_FILE
        self._init_db()

    def _get_connection(self):
        """Tạo kết nối an toàn đến SQLite."""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Khởi tạo cấu trúc bảng nếu chưa có."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ocr_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        page_name TEXT UNIQUE,
                        raw_text TEXT,
                        ai_text TEXT,
                        status TEXT DEFAULT 'PENDING',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            log.error(f"Lỗi khởi tạo database: {e}")

    def save_raw_text(self, page_name, raw_text):
        """Lưu kết quả văn bản thô do OCR đọc được."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Dùng UPSERT: Nếu trang này đã có thì cập nhật, chưa có thì chèn mới
                cursor.execute('''
                    INSERT INTO ocr_results (page_name, raw_text, status)
                    VALUES (?, ?, 'OCR_DONE')
                    ON CONFLICT(page_name) DO UPDATE SET 
                        raw_text=excluded.raw_text,
                        status='OCR_DONE',
                        updated_at=CURRENT_TIMESTAMP
                ''', (page_name, raw_text))
                conn.commit()
                log.info(f"Đã lưu RAW text cho {page_name}")
        except Exception as e:
            log.error(f"Lỗi lưu raw text cho {page_name}: {e}")

    def save_ai_text(self, page_name, ai_text):
        """Lưu kết quả văn bản sau khi đã được AI chỉnh sửa, làm mượt."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE ocr_results 
                    SET ai_text=?, status='AI_DONE', updated_at=CURRENT_TIMESTAMP
                    WHERE page_name=?
                ''', (ai_text, page_name))
                conn.commit()
                log.info(f"Đã lưu AI text cho {page_name}")
        except Exception as e:
            log.error(f"Lỗi lưu AI text cho {page_name}: {e}")

    def get_page_data(self, page_name):
        """Lấy toàn bộ dữ liệu của một trang."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT raw_text, ai_text, status FROM ocr_results WHERE page_name=?", (page_name,))
                row = cursor.fetchone()
                if row:
                    return {"raw_text": row[0], "ai_text": row[1], "status": row[2]}
                return None
        except Exception as e:
            log.error(f"Lỗi lấy dữ liệu cho {page_name}: {e}")
            return None