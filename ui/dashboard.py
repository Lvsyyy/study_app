import calendar
from datetime import date, datetime

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.formatting import format_duration, format_percent
from core.i18n import month_name, tr, weekday_long, weekday_short
from core.theme_manager import ThemeManager
from ui.widgets import card, clear_layout, muted_label, section_title, stat_card, title_label


class Dashboard(QWidget):
    study_exam_requested = Signal(str)

    def __init__(self, statistics, attempts, theme_name="Rose Pine"):
        super().__init__()
        self.statistics = statistics
        self.attempts = attempts
        self.theme_name = theme_name
        self.month_offset = 0
        self.exams = []
        self.exam_error = ""
        self.timetable = []
        self.timetable_error = ""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.page_scroll = QScrollArea()
        self.page_scroll.setWidgetResizable(True)
        self.page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.page_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.page_content = QWidget()
        self.root = QVBoxLayout(self.page_content)
        self.root.setContentsMargins(30, 26, 30, 26)
        self.root.setSpacing(18)
        self.root.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
        self.page_scroll.setWidget(self.page_content)
        outer_layout.addWidget(self.page_scroll)
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
        definitions = (
            ("streak", "Day streak", "Consecutive study days"),
            ("correct", "Correct", "Correct answers"),
            ("wrong", "Wrong", "Incorrect answers"),
            ("total", "Total questions", "All recorded attempts"),
            ("time", "Study time", "Active time in the app"),
        )
        for key, name, detail in definitions:
            frame, number, detail_label = stat_card(name, detail)
            self.stat_numbers[key] = number
            self.stat_details[key] = detail_label
            stats.addWidget(frame)
        self.root.addLayout(stats)
        self._build_exams()

        row = QHBoxLayout()
        row.setSpacing(18)
        weak_frame, weak_layout = card()
        weak_layout.addWidget(section_title("Weak points"))
        weak_layout.addWidget(muted_label("Topics with the lowest recorded accuracy"))
        self.weak_rows = QVBoxLayout()
        weak_layout.addLayout(self.weak_rows)
        weak_layout.addStretch()
        weak_frame.setMinimumHeight(300)
        weak_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        row.addWidget(weak_frame, 1)

        activity_frame, activity_layout = card()
        top = QHBoxLayout()
        top.addWidget(section_title("Study activity"))
        top.addStretch()
        self.month_label = QLabel()
        self.month_label.setMinimumWidth(110)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        activity_layout.addWidget(muted_label("Each cell is one day. Brighter means more study."))
        self.heat_grid = QVBoxLayout()
        self.heat_grid.setContentsMargins(0, 2, 0, 2)
        self.heat_grid.setSpacing(8)
        activity_layout.addLayout(self.heat_grid)
        self.legend = QHBoxLayout()
        activity_layout.addLayout(self.legend)
        activity_frame.setMinimumHeight(360)
        activity_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        row.addWidget(activity_frame, 1)
        row.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        self.root.addLayout(row)
        self._build_timetable()

    def _build_exams(self):
        heading = QHBoxLayout()
        heading.addWidget(section_title("Upcoming Exams"))
        heading.addStretch()
        self.exam_count = muted_label("Loading…")
        heading.addWidget(self.exam_count)
        self.root.addLayout(heading)

        self.exam_scroll = QScrollArea()
        self.exam_scroll.setWidgetResizable(True)
        self.exam_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.exam_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.exam_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.exam_container = QWidget()
        self.exam_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.exam_row = QHBoxLayout(self.exam_container)
        self.exam_row.setContentsMargins(0, 0, 8, 0)
        self.exam_row.setSpacing(10)
        self.exam_row.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)
        self.exam_scroll.setWidget(self.exam_container)
        self.exam_scroll.setFixedHeight(132)
        self.root.addWidget(self.exam_scroll)

    def _build_timetable(self):
        heading = QHBoxLayout()
        heading.addWidget(section_title("School schedule"))
        heading.addStretch()
        self.timetable_count = muted_label("Loading…")
        heading.addWidget(self.timetable_count)
        self.root.addLayout(heading)
        self.timetable_scroll = QScrollArea()
        self.timetable_scroll.setWidgetResizable(True)
        self.timetable_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.timetable_container = QWidget()
        self.timetable_layout = QVBoxLayout(self.timetable_container)
        self.timetable_layout.setContentsMargins(0, 0, 8, 0)
        self.timetable_layout.setSpacing(8)
        self.timetable_scroll.setWidget(self.timetable_container)
        self.timetable_scroll.setMinimumHeight(180)
        self.timetable_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.root.addWidget(self.timetable_scroll, 1)

    def set_timetable(self, entries, error=""):
        self.timetable = entries
        self.timetable_error = error
        self._render_timetable()

    def set_exams(self, exams, error=""):
        self.exams = exams
        self.exam_error = error
        self._render_exams()

    def _render_exams(self):
        clear_layout(self.exam_row)
        if self.exam_error:
            self.exam_count.setText(tr("Unavailable"))
            self.exam_row.addWidget(
                muted_label(tr("Could not load exams: {error}", error=self.exam_error))
            )
            return
        self.exam_count.setText(str(len(self.exams)))
        if not self.exams:
            self.exam_row.addWidget(muted_label("No upcoming exams found."))
            return

        today = date.today()
        palette = ThemeManager.palette(self.theme_name)
        exam_cards = []
        for exam in self.exams:
            start = datetime.fromisoformat(exam["start"]).astimezone()
            exam_day = start.date()
            days_left = (exam_day - today).days
            date_label = QLabel(start.strftime("%d.%m"))
            date_label.setStyleSheet(
                f"font-size: 19px; font-weight: 700; color: {palette['text']};"
            )
            weekday_label = muted_label(weekday_long(start.weekday()))
            countdown_text = (
                tr("Today") if days_left == 0
                else tr("In {days} days", days=days_left) if days_left > 0
                else tr("{days} days ago", days=abs(days_left))
            )
            countdown = QLabel(countdown_text)
            countdown.setStyleSheet(f"color: {palette['muted']};")
            subject = QLabel(exam["subject"])
            subject.setStyleSheet(
                f"color: {palette['text']}; font-weight: 600;"
            )
            subject.setWordWrap(True)
            subject.setMinimumWidth(0)
            subject.ensurePolished()
            subject_height = subject.fontMetrics().boundingRect(
                QRect(0, 0, 190, 10000),
                Qt.TextFlag.TextWordWrap,
                subject.text(),
            ).height()
            subject.setMinimumHeight(subject_height)
            subject.setMaximumHeight(subject_height)
            subject.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
            )
            time_text = start.strftime("%H:%M")
            if exam.get("end"):
                end = datetime.fromisoformat(exam["end"]).astimezone()
                time_text += f"–{end:%H:%M}"
            time_label = muted_label(time_text)
            card_button = QPushButton()
            card_button.setCursor(Qt.CursorShape.PointingHandCursor)
            card_button.setMinimumWidth(230)
            card_button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            card_button.setStyleSheet(
                f"QPushButton {{ text-align: left; padding: 3px; color: {palette['text']}; "
                f"background: {palette['panel']}; border: 1px solid {palette['border']}; "
                "border-radius: 10px; } "
                f"QPushButton:hover {{ border: 1px solid {palette['accent']}; }}"
            )
            card_layout = QVBoxLayout(card_button)
            card_layout.setContentsMargins(12, 9, 12, 9)
            card_layout.setSpacing(4)
            card_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)
            top = QHBoxLayout()
            top.addWidget(date_label)
            top.addStretch()
            if exam.get("is_new"):
                new_label = QLabel(tr("NEW"))
                new_label.setStyleSheet(
                    f"font-size: 10px; font-weight: 700; padding: 3px 6px; "
                    f"border-radius: 5px; background: {palette['accent']}; color: {palette['bg']};"
                )
                top.addWidget(new_label)
            card_layout.addLayout(top)
            card_layout.addWidget(weekday_label)
            card_layout.addWidget(countdown)
            card_layout.addWidget(subject)
            card_layout.addWidget(time_label)
            card_button.clicked.connect(lambda _checked=False, item=exam: self._show_exam(item))
            self.exam_row.addWidget(card_button, 1)
            exam_cards.append(card_button)

        # Measure cards after their subjects have been wrapped to the card width.
        # Give every card the tallest required height so their bottoms align.
        for exam_card in exam_cards:
            exam_card.ensurePolished()
            exam_card.layout().activate()
        tallest_height = max(
            exam_card.layout().sizeHint().height() + 6
            for exam_card in exam_cards
        )
        for exam_card in exam_cards:
            exam_card.setFixedHeight(tallest_height)

        scrollbar_height = self.exam_scroll.horizontalScrollBar().sizeHint().height()
        self.exam_scroll.setFixedHeight(tallest_height + scrollbar_height + 8)


    def _render_timetable(self):
        clear_layout(self.timetable_layout)
        if self.timetable_error:
            self.timetable_count.setText(tr("Unavailable"))
            self.timetable_layout.addWidget(
                muted_label(
                    tr(
                        "Could not load school schedule: {error}",
                        error=self.timetable_error,
                    )
                )
            )
            return
        entries = sorted(self.timetable, key=lambda item: item["start"])
        self.timetable_count.setText(tr("{entries} entries", entries=len(entries)))
        if not entries:
            self.timetable_layout.addWidget(muted_label("No schedule entries found."))
            return
        palette = ThemeManager.palette(self.theme_name)
        grouped = {}
        for entry in entries:
            start = datetime.fromisoformat(entry["start"]).astimezone()
            grouped.setdefault(start.date(), []).append((entry, start))
        for day, day_entries in grouped.items():
            day_title = QLabel(
                tr(
                    "{weekday}, {day} {month} {year}",
                    weekday=weekday_long(day.weekday()),
                    day=day.day,
                    month=month_name(day.month),
                    year=day.year,
                )
            )
            day_title.setStyleSheet(
                f"font-weight: 700; color: {palette['text']}; padding: 8px 2px 2px;"
            )
            self.timetable_layout.addWidget(day_title)
            for entry, start in day_entries:
                end_text = ""
                if entry.get("end"):
                    end_text = datetime.fromisoformat(entry["end"]).astimezone().strftime("–%H:%M")
                time_label = QLabel(start.strftime("%H:%M") + end_text)
                time_label.setFixedWidth(112)
                time_label.setStyleSheet(f"color: {palette['accent']}; font-weight: 700;")
                subject_label = QLabel(entry.get("subject") or tr("Unspecified"))
                subject_label.setStyleSheet(f"color: {palette['text']}; font-weight: 600;")
                details = [value for value in (
                    entry.get("room"), entry.get("teacher"), entry.get("description")
                ) if value]
                detail_label = QLabel(" · ".join(details) if details else entry.get("type", ""))
                detail_label.setWordWrap(True)
                detail_label.setStyleSheet(f"color: {palette['muted']}; font-size: 11px;")
                text_layout = QVBoxLayout()
                text_layout.setSpacing(2)
                text_layout.addWidget(subject_label)
                text_layout.addWidget(detail_label)
                line = QHBoxLayout()
                line.setContentsMargins(10, 7, 10, 7)
                line.addWidget(time_label)
                line.addLayout(text_layout, 1)
                frame = QFrame()
                frame.setStyleSheet(
                    f"QFrame {{ background: {palette['panel']}; "
                    f"border: 1px solid {palette['border']}; border-radius: 8px; }}"
                )
                frame.setLayout(line)
                self.timetable_layout.addWidget(frame)
        self.timetable_layout.addStretch()

    def _show_exam(self, exam):
        start = datetime.fromisoformat(exam["start"]).astimezone()
        details = [
            exam["subject"],
            tr(
                "{weekday}, {day} {month} {year}",
                weekday=weekday_long(start.weekday()),
                day=start.day,
                month=month_name(start.month),
                year=start.year,
            ),
            start.strftime("%H:%M") + (
                "–" + datetime.fromisoformat(exam["end"]).astimezone().strftime("%H:%M")
                if exam.get("end") else ""
            ),
        ]
        if exam.get("description"):
            details.append(exam["description"])
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Exam details"))
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("\n".join(details)))
        buttons = QDialogButtonBox()
        study_button = buttons.addButton(
            tr("Study for exam"), QDialogButtonBox.ButtonRole.ActionRole
        )
        close_button = buttons.addButton(QDialogButtonBox.StandardButton.Close)
        close_button.setText(tr("Close"))
        study_button.clicked.connect(
            lambda: (dialog.accept(), self.study_exam_requested.emit(
                exam.get("subject_short") or exam["subject"]
            ))
        )
        close_button.clicked.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def _render_all(self):
        self._render_legend()
        self._render_heatmap()
        self._render_exams()
        self._render_timetable()

    def apply_theme(self, name):
        self.theme_name = name
        self._render_all()

    def refresh(self):
        totals = self.attempts.totals()
        study = self.statistics.study_totals()
        streak = self.statistics.current_streak()
        self.stat_numbers["streak"].setText(
            tr("{streak} day", streak=streak) if streak == 1
            else tr("{streak} days", streak=streak)
        )
        for key in ("correct", "wrong", "total"):
            self.stat_numbers[key].setText(str(totals[key]))
        self.stat_numbers["time"].setText(format_duration(study["seconds"]))
        self.stat_details["correct"].setText(
            tr("{percent} accuracy", percent=format_percent(totals["accuracy"]))
            if totals["total"] else tr("No attempts yet")
        )
        average = totals["avg_time"]
        self.stat_details["total"].setText(
            tr("Avg {seconds:.1f}s per question", seconds=average)
            if average is not None else tr("All recorded attempts")
        )
        clear_layout(self.weak_rows)
        weak_points = self.attempts.weak_points()
        if not weak_points:
            self.weak_rows.addWidget(muted_label("Not enough attempt data yet."))
        else:
            for item in weak_points:
                line = QHBoxLayout()
                line.addWidget(QLabel(f"{item['subject_name']} · {item['topic_name']}"))
                line.addStretch()
                line.addWidget(
                    muted_label(tr("{accuracy}% accuracy", accuracy=item["accuracy"]))
                )
                self.weak_rows.addLayout(line)
        self._render_all()

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
        year = today.year + month_index // 12
        month = month_index % 12 + 1
        self.month_label.setText(f"{month_name(month)} {year}")
        palette = ThemeManager.palette(self.theme_name)
        activity = {
            date.fromisoformat(row["day"]): row
            for row in self.statistics.monthly_activity(year, month)
        }

        def score(record):
            return max(record["duration"] or 0, (record["questions"] or 0) * 20)

        peak = max((score(record) for record in activity.values()), default=0)

        header = QHBoxLayout()
        header.setSpacing(5)
        for index in range(7):
            label = muted_label(weekday_short(index))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(label, 1)
        self.heat_grid.addLayout(header)

        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
        for week in weeks:
            week_widget = QWidget()
            week_widget.setFixedHeight(22)
            week_layout = QHBoxLayout(week_widget)
            week_layout.setContentsMargins(0, 0, 0, 0)
            week_layout.setSpacing(5)
            for day in week:
                cell = QLabel()
                cell.setMinimumWidth(0)
                cell.setFixedHeight(22)
                cell.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                if day.month == month:
                    record = activity.get(day)
                    value = score(record) if record else 0
                    level = (
                        0 if value == 0 or peak == 0
                        else min(4, max(1, round(value / peak * 4)))
                    )
                    edge = palette["accent"] if day == today else palette["border"]
                    cell.setStyleSheet(
                        f"background: {palette['heat'][level]}; "
                        f"border: 1px solid {edge}; border-radius: 4px;"
                    )
                    minutes = int((record["duration"] or 0) // 60) if record else 0
                    questions = int(record["questions"] or 0) if record else 0
                    cell.setToolTip(
                        tr(
                            "{weekday}, {day} {month} {year}",
                            weekday=weekday_long(day.weekday()),
                            day=day.day,
                            month=month_name(day.month),
                            year=day.year,
                        )
                        + "\n"
                        + tr("Study time: {minutes} min", minutes=minutes)
                        + "\n"
                        + tr("Questions: {questions}", questions=questions)
                    )
                else:
                    cell.setStyleSheet("background: transparent; border: none;")
                week_layout.addWidget(cell, 1)
            self.heat_grid.addWidget(week_widget)
