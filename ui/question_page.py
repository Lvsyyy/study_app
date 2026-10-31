from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from ui.widgets import card, muted_label, action_button


class QuestionPage(QWidget):
    def __init__(self, question_repository, attempt_repository):
        super().__init__()
        self.questions = question_repository
        self.attempts = attempt_repository
        self.subject = "Math"
        self.offset = 0
        self.current = None
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(34, 30, 34, 30)
        self.root.setSpacing(18)
        self._build()

    def _build(self):
        header = QHBoxLayout()
        back = action_button("←  Back")
        back.clicked.connect(lambda: self.window().show_page("Home"))
        header.addWidget(back)
        header.addStretch()
        self.subject_label = muted_label(self.subject)
        header.addWidget(self.subject_label)
        self.root.addLayout(header)

        title = QLabel("Practice")
        title.setStyleSheet("font-size: 27px; font-weight: 800;")
        self.root.addWidget(title)
        self.topic = muted_label("")
        self.root.addWidget(self.topic)

        self.question_frame, self.question_layout = card(padding=24)
        self.question_text = QLabel()
        self.question_text.setWordWrap(True)
        self.question_text.setStyleSheet("font-size: 19px; font-weight: 600;")
        self.question_layout.addWidget(self.question_text)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMaximumHeight(300)
        self.question_layout.addWidget(self.image_label)
        self.hint_text = muted_label("")
        self.hint_text.setWordWrap(True)
        self.question_layout.addWidget(self.hint_text)
        self.feedback = QLabel("")
        self.question_layout.addWidget(self.feedback)
        self.root.addWidget(self.question_frame)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Type your answer…")
        self.answer.returnPressed.connect(self.check_answer)
        self.root.addWidget(self.answer)

        meta = QHBoxLayout()
        self.number_label = muted_label("Question")
        meta.addWidget(self.number_label)
        meta.addStretch()
        meta.addWidget(muted_label("Type accuracy: calculated from attempts"))
        self.root.addLayout(meta)

        buttons = QHBoxLayout()
        skip = action_button("Skip")
        hint = action_button("Hint")
        check = action_button("Check answer", primary=True)
        check.clicked.connect(self.check_answer)
        skip.clicked.connect(self.next_question)
        hint.clicked.connect(self.show_hint)
        buttons.addWidget(skip)
        buttons.addWidget(hint)
        buttons.addStretch()
        buttons.addWidget(check)
        self.root.addLayout(buttons)
        self.root.addStretch()
        self._load_question()

    def set_subject(self, subject):
        self.subject = subject
        self.offset = 0
        self.subject_label.setText(subject)
        self._load_question()

    def _load_question(self):
        self.current = self.questions.get_next_question(self.subject, self.offset)
        self.hint_text.setText("")
        self.feedback.setText("")
        self.answer.clear()
        if not self.current:
            self.topic.setText("")
            self.question_text.setText(
                f"No questions have been added for {self.subject} yet."
            )
            self.image_label.clear()
            self.number_label.setText("No question loaded")
            return

        self.topic.setText(f"TOPIC  /  {self.current['topic_name']}")
        self.question_text.setText(self.current["question_text"])
        self.number_label.setText(f"Question ID: #{self.current['id']}")
        image_path = self.current["question_image"]
        if image_path and Path(image_path).is_file():
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(
                pixmap.scaled(640, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.image_label.show()
        else:
            self.image_label.clear()
            self.image_label.hide()

    def show_hint(self):
        if self.current and self.current["hint"]:
            self.hint_text.setText(f"Hint: {self.current['hint']}")

    def check_answer(self):
        if not self.current:
            return
        entered = self.answer.text().strip()
        if not entered:
            self.feedback.setText("Enter an answer first.")
            return
        expected = self.current["answer"].strip().casefold()
        correct = entered.casefold() == expected
        self.attempts.record(self.current["id"], entered, correct)
        self.feedback.setText("Correct." if correct else "Incorrect. Try again or skip.")
        self.feedback.setStyleSheet("font-weight: 700;")

    def next_question(self):
        self.offset += 1
        self._load_question()
