import calendar
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from core.formatting import format_duration, format_percent
from core.theme_manager import ThemeManager
from ui.widgets import clear_layout, muted_label, section_title, stat_card, title_label


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

        self.stat_numbers = {}
        self.stat_details = {}
        stats = QHBoxLayout()

        stat_definitions = [
            ("streak", "Day streak", "Consecutive study days"),
            ("correct", "Correct", "Correct answers"),
            ("wrong", "Wrong", "Incorrect answers"),
            ("total", "Total questions", "All recorded attempts"),
            ("time", "Study time", "Active time in the app"),
        ]

        for key, name, detail in stat_definitions:
            frame, number, detail_label = stat_card(name, detail)
            self.stat_numbers[key] = number
            self.stat_details[key] = detail_label
            stats.addWidget(frame)

        self.root.addLayout(stats)

        row = QHBoxLayout()

        weak_frame, weak_layout = card()
        weak_layout.addWidget(section_title("Weak points"))
        weak_layout.addWidget(
            muted_label("Topics with the lowest recorded accuracy")
        )
        self.weak_rows = QVBoxLayout()
        weak_layout.addLayout(self.weak_rows)
        weak_layout.addStretch()
        row.addWidget(weak_frame, 1)

        activity_frame, activity_layout = card()
        top = QHBoxLayout()
        top.addWidget(section_title("Study activity"))
        top.addStretch()

        self.month_label = QLabel()
        self.month_label.setMinimumWidth(110)
        self.month_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        top.addWidget(self.month_label)

        previous = QPushButton("‹")
        next_button = QPushButton("›")
        previous.setFixedWidth(32)
        next_button.setFixedWidth(32)
        previous.clicked.connect(lambda: self.shift_month(-1))
        next_button.clicked.connect(lambda: self.shift_month(1))
        top.addWidget(previous)
        top.addWidget(next_button)

        activity_layout.addLayout(top)
        activity_layout.addWidget(
            muted_label("Each square is one day. Brighter means more study.")
        )

        self.heat_grid = QGridLayout()
        self.heat_grid.setSpacing(5)
        activity_layout.addLayout(self.heat_grid)

        self.legend = QHBoxLayout()
        activity_layout.addLayout(self.legend)

        row.addWidget(activity_frame, 1)
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

        self.stat_numbers["streak"].setText(
            f"{streak} day" + ("" if streak == 1 else "s")
        )
        self.stat_numbers["correct"].setText(str(totals["correct"]))
        self.stat_numbers["wrong"].setText(str(totals["wrong"]))
        self.stat_numbers["total"].setText(str(totals["total"]))
        self.stat_numbers["time"].setText(format_duration(study["seconds"]))

        self.stat_details["correct"].setText(
            f"{format_percent(totals['accuracy'])} accuracy"
            if totals["total"]
            else "No attempts yet"
        )

        average_time = totals["avg_time"]
        self.stat_details["total"].setText(
            f"Avg {average_time:.1f}s per question"
            if average_time
            else "All recorded attempts"
        )

        clear_layout(self.weak_rows)
        weak_points = self.attempts.weak_points()

        if not weak_points:
            self.weak_rows.addWidget(
                muted_label("Not enough attempt data yet.")
            )
        else:
            for item in weak_points:
                line = QHBoxLayout()
                line.addWidget(
                    QLabel(
                        f"{item['subject_name']} · {item['topic_name']}"
                    )
                )
                line.addStretch()
                line.addWidget(
                    muted_label(f"{item['accuracy']}% accuracy")
                )
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
            swatch.setStyleSheet(
                f"background: {color}; border-radius: 3px;"
            )
            self.legend.addWidget(swatch)

        self.legend.addWidget(muted_label("More"))

    def _render_heatmap(self):
        clear_layout(self.heat_grid)

        today = date.today()
        month_index = today.month - 1 + self.month_offset
        year = today.year + month_index // 12
        month = month_index % 12 + 1

        self.month_label.setText(f"{calendar.month_name[month]} {year}")
        palette = ThemeManager.palette(self.theme_name)

        activity = {
            date.fromisoformat(row["day"]): row
            for row in self.statistics.monthly_activity(year, month)
        }

        def score(record):
            duration = record["duration"] or 0
            questions = record["questions"] or 0
            return max(duration, questions * 20)

        peak = max(
            (score(record) for record in activity.values()),
            default=0,
        )

        for column, weekday in enumerate(WEEKDAYS):
            label = muted_label(weekday)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.heat_grid.addWidget(label, 0, column)

        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(
            year, month
        )

        for week_row, week in enumerate(weeks, start=1):
            for column, day in enumerate(week):
                square = QLabel()
                square.setFixedSize(24, 24)

                if day.month != month:
                    self.heat_grid.addWidget(square, week_row, column)
                    continue

                record = activity.get(day)
                value = score(record) if record else 0

                if value == 0 or peak == 0:
                    level = 0
                else:
                    level = min(4, max(1, round(value / peak * 4)))

                edge = (
                    palette["accent"]
                    if day == today
                    else palette["border"]
                )
                square.setStyleSheet(
                    f"background: {palette['heat'][level]}; "
                    f"border: 1px solid {edge}; "
                    "border-radius: 4px;"
                )

                minutes = (
                    int((record["duration"] or 0) // 60)
                    if record
                    else 0
                )
                questions = (
                    int(record["questions"] or 0)
                    if record
                    else 0
                )

                square.setToolTip(
                    f"{day:%A, %d %B %Y}\n"
                    f"Study time: {minutes} min\n"
                    f"Questions: {questions}"
                )
                self.heat_grid.addWidget(square, week_row, column)
