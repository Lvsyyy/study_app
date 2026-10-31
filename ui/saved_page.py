from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ui.widgets import (
    action_button,
    card,
    clear_layout,
    muted_label,
    section_title,
    title_label,
)


class SavedPage(QWidget):
    practice_requested = Signal(list)  # list of question ids

    def __init__(self, question_repository):
        super().__init__()
        self.questions = question_repository
        outer = QVBoxLayout(self)
        outer.setContentsMargins(34, 30, 34, 0)
        outer.setSpacing(14)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.addWidget(title_label("Saved questions"))
        titles.addWidget(muted_label("Questions you starred while practising"))
        header.addLayout(titles)
        header.addStretch()
        self.practice_all = action_button("Practice all saved", primary=True)
        self.practice_all.clicked.connect(self._practice_all)
        header.addWidget(self.practice_all)
        outer.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)
        content = QWidget()
        scroll.setWidget(content)
        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 20)
        self.list_layout.setSpacing(10)
        self.ids = []
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        clear_layout(self.list_layout)
        saved = self.questions.list_saved()
        self.ids = [row["id"] for row in saved]
        self.practice_all.setEnabled(bool(saved))
        if not saved:
            frame, box = card()
            box.addWidget(muted_label("Nothing saved yet. Press “☆ Save” on a question to keep it here."))
            self.list_layout.addWidget(frame)
        for row in saved:
            frame, box = card()
            box.addWidget(section_title(f"{row['subject_name']} · {row['topic_name']}"))
            text = QLabel(row["question_text"])
            text.setWordWrap(True)
            box.addWidget(text)
            buttons = QHBoxLayout()
            practice = action_button("Practice")
            practice.clicked.connect(lambda _=False, i=row["id"]: self.practice_requested.emit([i]))
            remove = action_button("Remove")
            remove.clicked.connect(lambda _=False, i=row["id"]: self._remove(i))
            buttons.addStretch()
            buttons.addWidget(practice)
            buttons.addWidget(remove)
            box.addLayout(buttons)
            self.list_layout.addWidget(frame)
        self.list_layout.addStretch()

    def _remove(self, question_id):
        self.questions.set_saved(question_id, False)
        self.refresh()

    def _practice_all(self):
        if self.ids:
            self.practice_requested.emit(list(self.ids))
