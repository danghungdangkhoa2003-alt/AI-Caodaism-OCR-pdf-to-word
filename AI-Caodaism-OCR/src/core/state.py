import json
from src.config import STATE_FILE
from src.core.logger import log

class StateManager:
    def __init__(self, job_name="default_job"):
        self.job_name = job_name
        self.state_file = STATE_FILE
        self.state = self._load_state()

    def _load_state(self):
        """Đọc trạng thái đã lưu từ file JSON, nếu chưa có thì tạo mới."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Lỗi đọc state.json: {e}")
                return {}
        return {}

    def is_completed(self, item_id):
        """Kiểm tra xem một trang/file đã được xử lý xong chưa."""
        job_state = self.state.get(self.job_name, [])
        return item_id in job_state

    def mark_completed(self, item_id):
        """Đánh dấu trang/file đã hoàn thành và lưu ngay xuống ổ cứng."""
        if self.job_name not in self.state:
            self.state[self.job_name] = []
            
        if item_id not in self.state[self.job_name]:
            self.state[self.job_name].append(item_id)
            self._save_state()
            log.info(f"Đã lưu trạng thái hoàn thành: {item_id}")

    def _save_state(self):
        """Ghi dữ liệu trạng thái xuống file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=4)