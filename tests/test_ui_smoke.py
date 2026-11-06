import json
import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings, Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core.math_question_generator import binary_arithmetic_table  # noqa: E402
from core.settings_store import SettingsStore  # noqa: E402
from core.theme_manager import ThemeManager  # noqa: E402
from database.database import Database  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def window(app, tmp_path):
    settings = SettingsStore(QSettings(str(tmp_path / "s.ini"), QSettings.Format.IniFormat))
    ThemeManager.apply(app, settings.theme)
    win = MainWindow(app, settings, Database(":memory:"))
    win.show()
    yield win
    win.close()


def test_full_practice_flow_records_time_and_refreshes(window):
    repo = window.question_repository
    repo.add_question("Math", "Binary", "Convert 101101 to decimal.", "45",
                      hint="place values", alt_answers=["forty five"])
    window.show_page("Math")
    page = window.question_page
    assert page.current["answer"] == "45"

    page.answer.setText("46")
    page.check_answer()
    assert page.feedback.property("state") == "bad"
    page.answer.setText("45.0")
    page.check_answer()
    assert page.feedback.property("state") == "good"

    rows = window.db.fetch_all("SELECT * FROM attempts")
    assert len(rows) == 1 and rows[0]["is_correct"] == 0 and rows[0]["time_taken"] is not None
    assert window.session.questions == 1

    page.next_question()
    assert "Round complete" in page.question_text.text()
    window.show_page("Home")
    assert window.dashboard.stat_numbers["total"].text() == "1"


def test_weak_point_rows_do_not_accumulate(window):
    repo = window.question_repository
    qid = repo.add_question("Math", "Binary", "Q", "1")
    for _ in range(2):
        window.attempt_repository.record(qid, "x", False)
    for _ in range(3):
        window.dashboard.refresh()
    assert window.dashboard.weak_rows.count() == 1


def test_reveal_counts_as_wrong_once(window):
    window.question_repository.add_question("CS", "T", "Q", "A")
    window.show_page("CS")
    window.question_page.reveal_answer()
    window.question_page.reveal_answer()
    rows = window.db.fetch_all("SELECT is_correct FROM attempts")
    assert [r[0] for r in rows] == [0]


def test_reveal_preserves_answer_and_shows_separate_solution(window):
    window.question_repository.add_question("CS", "T", "Question", "Correct answer")
    window.show_page("CS")
    page = window.question_page
    page.answer.setText("My submitted answer")

    page.reveal_answer()

    assert page.answer.text() == "My submitted answer"
    assert page.solution_panel.isVisible()
    assert page.solution_content.toPlainText() == "Correct answer"
    assert page.primary_button.text() == "Next  →"


def test_saved_flow_and_theme_switch(window, app):
    qid = window.question_repository.add_question("Math", "T", "Q", "A")
    window.show_page("Math")
    window.question_page.toggle_saved()
    window.saved_page.refresh()
    assert window.saved_page.ids == [qid]
    ThemeManager.apply(app, "Dracula")
    window.theme_changed.emit("Dracula")
    window.sidebar.set_icon_pack("Catppuccin Icons")
    for name in ("Home", "Subjects", "Statistics", "Saved", "Math", "bogus"):
        window.show_page(name)


def test_session_is_saved_on_close(app, tmp_path):
    settings = SettingsStore(QSettings(str(tmp_path / "s.ini"), QSettings.Format.IniFormat))
    db = Database(tmp_path / "d.sqlite3")
    win = MainWindow(app, settings, db)
    win.session.active_seconds = 90
    win.session.record_question()
    win.close()
    import sqlite3
    row = sqlite3.connect(tmp_path / "d.sqlite3").execute(
        "SELECT duration, questions_completed, ended_at FROM study_sessions").fetchone()
    assert row[0] >= 90 and row[1] == 1 and row[2] is not None


def test_subnet_canvas_can_split_a_slash_29_room(window):
    canvas = window.subnetting_page.canvas
    room = canvas.rooms[0]
    room["network"] = 167772160  # 10.0.0.0
    room["prefix"] = 29

    canvas._split(room, "top")

    children = [item for item in canvas.rooms if item["id"] in canvas.allowed_extra_ids]
    assert len(children) == 2
    assert {item["prefix"] for item in children} == {30}
    assert sorted(item["network"] for item in children) == [167772160, 167772164]


def test_correct_subnet_answer_changes_primary_action_to_next(window):
    page = window.subnetting_page
    canvas = page.canvas
    canvas.extra_splits_done = canvas.extra_splits

    for room in canvas.rooms:
        network_edit, broadcast_edit = canvas.inputs[room["id"]]
        network_edit.setText(canvas._ip(room["network"]))
        broadcast_edit.setText(
            canvas._ip(room["network"] + (1 << (32 - room["prefix"])) - 1)
        )

    network = canvas._ip(canvas.network)
    broadcast = canvas._ip(canvas.broadcast)
    for row, value in ((2, network), (3, broadcast)):
        page.info_table.item(row, 1).setText(value)
        page.info_table.item(row, 2).setText(
            ".".join(f"{int(part):08b}" for part in value.split("."))
        )

    page.check_answers()

    assert page.primary_button.text() == "Next  →"
    page._primary_action()
    assert page.primary_button.text() == "Check answer"


def test_statistics_displays_zero_second_average(window):
    qid = window.question_repository.add_question("Math", "Binary", "Q", "A")
    window.attempt_repository.record(qid, "A", True, 0)
    window.statistics_page.refresh()
    assert window.statistics_page.numbers["avg"].text() == "0.0s"

def test_pug_subject_includes_arbeitsvertrag(window):
    window.show_page("PuG")
    assert "Arbeitsvertrag" in window.question_repository.list_topics("PuG")
    assert window.subject_menu_page.title.text() == "PuG"



def test_binary_dividers_fit_each_table_cell(window):
    _, template = binary_arithmetic_table("10101", "00110", "+")
    page = window.question_page
    page._show_calculation_table(json.loads(template))
    table = page.calculation_tables[0]

    separator_rows = [
        row for row in range(table.rowCount())
        if table.item(row, 0).data(Qt.ItemDataRole.UserRole) == "__SEPARATOR__"
    ]
    assert separator_rows

    for row in separator_rows:
        assert table.columnSpan(row, 0) == 1
        assert all(table.cellWidget(row, column) is not None
                   for column in range(table.columnCount()))
        assert page._table_input_data(table)["rows"][row][0] == "__SEPARATOR__"
