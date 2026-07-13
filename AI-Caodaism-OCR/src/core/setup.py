"""Project startup helpers."""

from src.config import PROJECT_DIRECTORIES


def ensure_directories() -> None:
    """Create all runtime directories before processing a document."""
    for directory in PROJECT_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)
