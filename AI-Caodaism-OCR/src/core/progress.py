"""Progress tracking and status reporting."""

from __future__ import annotations

from typing import Optional

from src.core.logger import log


class ProgressTracker:
    """Track and report processing progress."""

    def __init__(self, total_steps: int, task_name: str = "Processing") -> None:
        self.total_steps = total_steps
        self.current_step = 0
        self.task_name = task_name
        self.step_messages = []

    def step(self, message: Optional[str] = None) -> None:
        """Advance to next step and optionally log a message."""
        self.current_step += 1
        progress_pct = int((self.current_step / self.total_steps) * 100)
        if message:
            log.info("%s [%d%%] %s", self.task_name, progress_pct, message)
            self.step_messages.append(message)
        else:
            log.info("%s: %d/%d steps", self.task_name, self.current_step, self.total_steps)

    def reset(self) -> None:
        """Reset progress tracker."""
        self.current_step = 0
        self.step_messages.clear()
