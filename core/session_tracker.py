"""Records how long the app is actively used and how many questions were answered."""
import time

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QApplication


class SessionTracker(QObject):
    """Counts only time the app is the active window and saves progress periodically,
    so a crash loses at most SAVE_INTERVAL_S seconds."""

    TICK_MS = 5000
    SAVE_INTERVAL_S = 30

    def __init__(self, session_repository, parent=None):
        super().__init__(parent)
        self.repo = session_repository
        self.session_id = None
        self.active_seconds = 0.0
        self.questions = 0
        self._last_tick = None
        self._last_save = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(self.TICK_MS)
        self._timer.timeout.connect(self.tick)

    def start(self):
        self.session_id = self.repo.start()
        self._last_tick = time.monotonic()
        self._timer.start()

    def record_question(self):
        self.questions += 1

    def tick(self):
        now = time.monotonic()
        if self._last_tick is not None and self._is_active():
            self.active_seconds += now - self._last_tick
        self._last_tick = now
        if self.active_seconds - self._last_save >= self.SAVE_INTERVAL_S:
            self._save()

    @staticmethod
    def _is_active() -> bool:
        app = QApplication.instance()
        return app is None or app.applicationState() == Qt.ApplicationState.ApplicationActive

    def _save(self):
        if self.session_id is not None:
            self.repo.update(self.session_id, self.active_seconds, self.questions)
            self._last_save = self.active_seconds

    def stop(self):
        if self.session_id is None:
            return
        self._timer.stop()
        self.tick()
        self.repo.finish(self.session_id, self.active_seconds, self.questions)
        self.session_id = None
