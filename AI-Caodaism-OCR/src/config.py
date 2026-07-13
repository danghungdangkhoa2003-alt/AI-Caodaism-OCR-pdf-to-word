"""Centralized, environment-based project configuration."""

from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Lets text-layer conversion report missing optional packages clearly.
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
REVIEW_DIR = BASE_DIR / "review"
IMAGE_DIR = OUTPUT_DIR / "images"
PROCESSED_DIR = OUTPUT_DIR / "processed"
STATE_FILE = OUTPUT_DIR / "state.json"
DB_FILE = OUTPUT_DIR / "caodaism_ocr.db"

PROJECT_DIRECTORIES = (INPUT_DIR, OUTPUT_DIR, LOG_DIR, CACHE_DIR, REVIEW_DIR, IMAGE_DIR, PROCESSED_DIR)
