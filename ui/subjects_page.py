from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget

from core.formatting import format_percent
from ui.widgets import (
    action_button,
    card,
    clear_layout,
    muted_label,
    progress_bar,
    section_title,
    title_label,
)

COLUMNS = 3


class SubjectsPage(QWidget):
    subject_requested = Signal(str)

    def __init__(self, statistics):
        super().__init__()
        self.statistics = statistics
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)
        root.addWidget(title_label("Subjects"))
        root.addWidget(muted_label("Pick a subject to practise"))
        self.grid = QGridLayout()
        self.grid.setSpacing(14)
        root.addLayout(self.grid)
        root.addStretch()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        clear_layout(self.grid)
        for index, subject in enumerate(self.statistics.subject_stats()):
            frame, box = card()
            box.addWidget(section_title(subject["name"]))
            attempts, correct = subject["attempts"], subject["correct"]
            accuracy = 100.0 * correct / attempts if attempts else None
            box.addWidget(muted_label(
                f"{subject['questions']} question(s)  ·  {attempts} attempt(s)"))
            box.addWidget(muted_label(f"Accuracy: {format_percent(accuracy)}"))
            box.addWidget(progress_bar(accuracy or 0))
            button = action_button("Practice", primary=True)
            button.setEnabled(subject["questions"] > 0)
            button.clicked.connect(lambda _=False, n=subject["name"]: self.subject_requested.emit(n))
            box.addWidget(button)
            self.grid.addWidget(frame, index // COLUMNS, index % COLUMNS)
