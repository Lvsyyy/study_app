import json
import os
from datetime import datetime, timedelta

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from core.webuntis import WebUntisExamManager


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_new_exam_badge_expires_and_does_not_reappear(app, tmp_path):
    manager = WebUntisExamManager()
    manager.state_path = tmp_path / "exams.json"
    exam = {
        "id": "exam-1",
        "start": (datetime.now().astimezone() + timedelta(days=5)).isoformat(),
        "end": "",
        "subject": "Netzwerktechnik",
        "description": "Schulaufgabe",
    }

    manager._handle_result([exam.copy()], "")
    assert manager._new_until["exam-1"]
    assert json.loads(manager.state_path.read_text())["known_ids"] == ["exam-1"]

    manager._new_until["exam-1"] = (
        datetime.now().astimezone() - timedelta(seconds=1)
    ).isoformat()
    manager._handle_result([exam.copy()], "")

    assert manager._new_until == {}
    assert manager._known_ids == {"exam-1"}
