"""UTF-8 file and terminal logging."""

import logging

from src.config import LOG_DIR

log = logging.getLogger("ai_caodaism_ocr")


def configure_logging() -> None:
    """Configure logging once, after runtime folders have been created."""
    if log.handlers:
        return
    log.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    log.addHandler(console_handler)
