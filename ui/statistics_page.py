from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from core.formatting import format_duration, format_percent
from ui.widgets import (
    card,
    clear_layout,
    muted_label,
    progress_bar,
    section_title,
    stat_card,
    title_label,
)


class StatisticsPage(QWidget):
    def __init__(self, statistics, attempts):
        super().__init__()
        self.statistics = statistics
        self.attempts = attempts
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        root = QVBoxLayout(content)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)

        root.addWidget(title_label("Statistics"))
        root.addWidget(muted_label("Calculated from your answers and study sessions"))

        self.numbers = {}
        row = QHBoxLayout()
        for key, name, detail in (
            ("accuracy", "Accuracy", "Correct / all attempts"),
            ("time", "Study time", "Total active time"),
            ("avg", "Avg. per question", "Time to answer"),
            ("sessions", "Sessions", "Times you studied"),
            ("longest", "Longest streak", "Consecutive days"),
        ):
            frame, number, _ = stat_card(name, detail)
            self.numbers[key] = number
            row.addWidget(frame)
        root.addLayout(row)

        subjects, subjects_box = card()
        subjects_box.addWidget(section_title("Accuracy by subject"))
        self.subject_rows = QVBoxLayout()
        subjects_box.addLayout(self.subject_rows)
        root.addWidget(subjects)

        weak, weak_box = card()
        weak_box.addWidget(section_title("Weakest topics"))
        self.weak_rows = QVBoxLayout()
        weak_box.addLayout(self.weak_rows)
        root.addWidget(weak)
        root.addStretch()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        totals = self.attempts.totals()
        study = self.statistics.study_totals()
        self.numbers["accuracy"].setText(format_percent(totals["accuracy"]))
        self.numbers["time"].setText(format_duration(study["seconds"]))
        avg = totals["avg_time"]
        self.numbers["avg"].setText(f"{avg:.1f}s" if avg else "–")
        self.numbers["sessions"].setText(str(study["sessions"]))
        self.numbers["longest"].setText(f"{self.statistics.longest_streak()} d")

        clear_layout(self.subject_rows)
        rows = [s for s in self.statistics.subject_stats() if s["attempts"] > 0]
        if not rows:
            self.subject_rows.addWidget(muted_label("No attempts recorded yet."))
        for subject in rows:
            accuracy = 100.0 * subject["correct"] / subject["attempts"]
            line = QHBoxLayout()
            name = QLabel(subject["name"])
            name.setMinimumWidth(80)
            line.addWidget(name)
            line.addWidget(progress_bar(accuracy), 1)
            detail = muted_label(f"{format_percent(accuracy)}  ({subject['attempts']} attempts)")
            detail.setMinimumWidth(130)
            line.addWidget(detail)
            self.subject_rows.addLayout(line)

        clear_layout(self.weak_rows)
        weak = self.attempts.weak_points(limit=8)
        if not weak:
            self.weak_rows.addWidget(muted_label("Not enough attempt data yet (needs 2+ per topic)."))
        for item in weak:
            line = QHBoxLayout()
            line.addWidget(QLabel(f"{item['subject_name']} · {item['topic_name']}"))
            line.addStretch()
            line.addWidget(muted_label(f"{item['accuracy']}%  ({item['attempts']} attempts)"))
            self.weak_rows.addLayout(line)
