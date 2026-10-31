import calendar
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.formatting import format_duration, format_percent
from core.theme_manager import ThemeManager
from ui.widgets import card, clear_layout, muted_label, section_title, stat_card, title_label

WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


class Dashboard(QWidget):
    def __init__(self, statistics, attempts, theme_name="Rose Pine"):
        super().__init__()
        self.statistics = statistics
        self.attempts = attempts
        self.theme_name = theme_name
        self.month_offset = 0
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(30, 26, 30, 26)
        self.root.setSpacing(18)
        self._build()
        self.refresh()

    def _build(self):
        titles = QVBoxLayout()
        titles.addWidget(title_label("Dashboard"))
        titles.addWidget(muted_label("Your learning overview"))
        self.root.addLayout(titles)

        self.stat_numbers, self.stat_details = {}, {}
        stats = QHBoxLayout()
        for key, name, detail in (
            ("streak", "Day streak", "Consecutive study days"),
            ("correct", "Correct", "Correct answers"),
            ("wrong", "Wrong", "Incorrect answers"),
            ("total", "Total questions", "All recorded attempts"),
            ("time", "Study time", "Active time in the app"),
        ):
            frame, number, detail_label = stat_card(name, detail)
            self.stat_numbers[key], self.stat_details[key] = number, detail_label
            stats.addWidget(frame)
        self.root.addLayout(stats)

        row = QHBoxLayout()
        weak, weak_box = card()
        weak_box.addWidget(section_title("Weak points"))
        weak_box.addWidget(muted_label("Topics with the lowest recorded accuracy"))
        self.weak_rows = QVBoxLayout()
        weak_box.addLayout(self.weak_rows)
        weak_box.addStretch()
        row.addWidget(weak, 1)

        activity, activity_box = card()
        top = QHBoxLayout()
        top.addWidget(section_title("Study activity"))
        top.addStretch()
        self.month_label = QLabel()
        self.month_label.setMinimumWidth(110)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top.addWidget(self.month_label)
        for text, delta in (("‹", -1), ("›", 1)):
            button = QPushButton(text)
            button.setFixedWidth(32)
            button.clicked.connect(lambda _=False, d=delta: self.shift_month(d))
            top.addWidget(button)
        activity_box.addLayout(top)
        activity_box.addWidget(muted_label("Each square is one day. Brighter means more study."))
        self.heat_grid = QGridLayout()
        self.heat_grid.setSpacing(5)
        activity_box.addLayout(self.heat_grid)
        self.legend = QHBoxLayout()
        activity_box.addLayout(self.legend)
        row.addWidget(activity, 1)
        self.root.addLayout(row)

        self.root.addStretch()

    # -- data ------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def apply_theme(self, name):
        self.theme_name = name
        self._render_legend()
        self._render_heatmap()

    def refresh(self):
        totals = self.attempts.totals()
        study = self.statistics.study_totals()
        streak = self.statistics.current_streak()
        self.stat_numbers["streak"].setText(f"{streak} day" + ("" if streak == 1 else "s"))
        self.stat_numbers["correct"].setText(str(totals["correct"]))
        self.stat_numbers["wrong"].setText(str(totals["wrong"]))
        self.stat_numbers["total"].setText(str(totals["total"]))
        self.stat_numbers["time"].setText(format_duration(study["seconds"]))
        self.stat_details["correct"].setText(
            f"{format_percent(totals['accuracy'])} accuracy" if totals["total"] else "No attempts yet")
        avg = totals["avg_time"]
        self.stat_details["total"].setText(
            f"Avg {avg:.1f}s per question" if avg else "All recorded attempts")

        clear_layout(self.weak_rows)
        weak_points = self.attempts.weak_points()
        if not weak_points:
            self.weak_rows.addWidget(muted_label("Not enough attempt data yet."))
        for item in weak_points:
            line = QHBoxLayout()
            line.addWidget(QLabel(f"{item['subject_name']} · {item['topic_name']}"))
            line.addStretch()
            line.addWidget(muted_label(f"{item['accuracy']}% accuracy"))
            self.weak_rows.addLayout(line)

        self._render_legend()
        self._render_heatmap()

    def shift_month(self, amount):
        self.month_offset += amount
        self._render_heatmap()

    def _render_legend(self):
        clear_layout(self.legend)
        self.legend.addWidget(muted_label("Less"))
        self.legend.addStretch()
        for color in ThemeManager.palette(self.theme_name)["heat"]:
            swatch = QLabel()
            swatch.setFixedSize(13, 13)
            swatch.setStyleSheet(f"background: {color}; border-radius: 3px;")
            self.legend.addWidget(swatch)
        self.legend.addWidget(muted_label("More"))

    def _render_heatmap(self):
        clear_layout(self.heat_grid)
        today = date.today()
        month_index = today.month - 1 + self.month_offset
        year, month = today.year + month_index // 12, month_index % 12 + 1
        self.month_label.setText(f"{calendar.month_name[month]} {year}")
        palette = ThemeManager.palette(self.theme_name)

        activity = {date.fromisoformat(r["day"]): r for r in self.statistics.monthly_activity(year, month)}

        def score(record):  # sessions give seconds; answered questions count ~20s each
            return max(record["duration"] or 0, (record["questions"] or 0) * 20)

        peak = max((score(r) for r in activity.values()), default=0)

        for col, name in enumerate(WEEKDAYS):
            label = muted_label(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.heat_grid.addWidget(label, 0, col)

        for week_row, week in enumerate(calendar.Calendar(0).monthdatescalendar(year, month), 1):
            for col, day in enumerate(week):
                square = QLabel()
                square.setFixedSize(24, 24)
                if day.month != month:
                    self.heat_grid.addWidget(square, week_row, col)
                    continue
                record = activity.get(day)
                value = score(record) if record else 0
                level = 0 if value == 0 else min(4, max(1, round(value / peak * 4)))
                edge = palette["accent"] if day == today else palette["border"]
                border = f"border: 1px solid {edge};"
                square.setStyleSheet(
                    f"background: {palette['heat'][level]}; border-radius: 4px; {border}")
                minutes = int((record["duration"] or 0) // 60) if record else 0
                count = int(record["questions"] or 0) if record else 0
                square.setToolTip(
                    f"{day:%A, %d %B %Y}\nStudy time: {minutes} min\nQuestions: {count}")
                self.heat_grid.addWidget(square, week_row, col)
