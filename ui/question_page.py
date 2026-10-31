import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from core.answer_checker import is_correct
from core.formatting import format_duration
from ui.widgets import action_button, card, muted_label, set_state, title_label


class QuestionPage(QWidget):
    back_requested = Signal()
    answered = Signal(bool)  # emitted once per question, on the first answer (or reveal)

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
        self.heading = "Practice"
        self.queue = []
        self.index = 0
        self.current = None
        self._started = time.monotonic()
        self._attempted = False
        self._solved = False
        self._finished = False
        self._rebuild = None  # callable returning a fresh queue for "Practice again"
        self._round_correct = 0
        self._round_answered = 0
        self.subject = "Math"
        self.offset = 0
        self.current = None
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(34, 30, 34, 30)
        self.root.setSpacing(18)
        self._build()

    # -- layout ----------------------------------------------------------
    def _build(self):
        header = QHBoxLayout()
        back = action_button("←  Back")
        back.clicked.connect(self.back_requested)
        header.addWidget(back)
        header.addStretch()
        self.subject_label = muted_label()
        header.addWidget(self.subject_label)
        self.root.addLayout(header)

        self.title = title_label("Practice")
        self.root.addWidget(self.title)
        self.topic = muted_label()
        self.root.addWidget(self.topic)

        frame, box = card(padding=24)
        self.question_text = QLabel()
        self.question_text.setProperty("role", "question")
        self.question_text.setWordWrap(True)
        box.addWidget(self.question_text)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMaximumHeight(300)
        box.addWidget(self.image_label)
        self.hint_text = muted_label()
        self.hint_text.setWordWrap(True)
        box.addWidget(self.hint_text)
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        box.addWidget(self.feedback)
        self.root.addWidget(frame)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("Type your answer…")
        self.answer.returnPressed.connect(self._primary_action)
        self.root.addWidget(self.answer)

        meta = QHBoxLayout()
        self.number_label = muted_label()
        meta.addWidget(self.number_label)
        meta.addStretch()
        self.accuracy_label = muted_label()
        meta.addWidget(self.accuracy_label)
        self.root.addLayout(meta)

        buttons = QHBoxLayout()
        self.skip_button = action_button("Skip")
        self.hint_button = action_button("Hint")
        self.reveal_button = action_button("Show answer")
        self.save_button = action_button("☆  Save")
        self.primary_button = action_button("Check answer", primary=True)
        self.skip_button.clicked.connect(self.next_question)
        self.hint_button.clicked.connect(self.show_hint)
        self.reveal_button.clicked.connect(self.reveal_answer)
        self.save_button.clicked.connect(self.toggle_saved)
        self.primary_button.clicked.connect(self._primary_action)
        for widget in (self.skip_button, self.hint_button, self.reveal_button, self.save_button):
            buttons.addWidget(widget)
        buttons.addStretch()
        buttons.addWidget(self.primary_button)
        self.root.addLayout(buttons)
        self.root.addStretch()
        self._show_empty("Choose a subject from the sidebar to start practising.")

    # -- queue -----------------------------------------------------------
    def set_subject(self, subject):
        self.set_queue(subject, self.questions.get_study_queue(subject),
                       rebuild=lambda: self.questions.get_study_queue(subject))

    def set_queue(self, heading, ids, rebuild=None):
        self.heading = heading
        self._rebuild = rebuild
        self.title.setText("Practice")
        self.subject_label.setText(heading)
        self.queue = list(ids)
        self.index = 0
        self._round_correct = self._round_answered = 0
        if not self.queue:
            self._show_empty(f"No questions for {heading} yet.")
        else:
            self._load_current()

    def _controls_enabled(self, enabled):
        for widget in (self.answer, self.skip_button, self.hint_button,
                       self.reveal_button, self.save_button):
            widget.setEnabled(enabled)

    def _show_empty(self, message):
        self.current = None
        self._finished = False
        self.topic.setText("")
        self.question_text.setText(message)
        self.image_label.hide()
        self.hint_text.setText("")
        self.feedback.setText("")
        self.number_label.setText("")
        self.accuracy_label.setText("")
        self.answer.clear()
        self._controls_enabled(False)
        self.primary_button.setEnabled(False)
        self.primary_button.setText("Check answer")

    def _show_finished(self):
        self._show_empty("Round complete 🎉")
        self.topic.setText(self.heading)
        self.feedback.setText(
            f"You answered {self._round_answered} question(s): "
            f"{self._round_correct} correct.")
        set_state(self.feedback, None)
        self.primary_button.setEnabled(True)
        self.primary_button.setText("Practice again")
        self._finished = True

    # -- loading ---------------------------------------------------------
    def _load_current(self):
        question = None
        while self.index < len(self.queue) and question is None:
            question = self.questions.get_question(self.queue[self.index])
            if question is None:  # deleted since the queue was built
                self.index += 1
        if question is None:
            self._show_finished()
            return
        self.current = question
        self._finished = False
        self._attempted = self._solved = False
        self._started = time.monotonic()
        self._controls_enabled(True)
        self.primary_button.setEnabled(True)
        self.primary_button.setText("Check answer")
        self.hint_text.setText("")
        self.feedback.setText("")
        set_state(self.feedback, None)
        self.answer.clear()
        self.answer.setFocus()
        self.hint_button.setEnabled(bool(question["hint"]))

        self.topic.setText(
            f"{question['subject_name']}  /  {question['topic_name']}  ·  "
            f"difficulty {'●' * question['difficulty']}{'○' * (5 - question['difficulty'])}")
        self.question_text.setText(question["question_text"])
        self.number_label.setText(f"Question {self.index + 1} of {len(self.queue)}")
        self._set_saved_button(self.questions.is_saved(question["id"]))
        stats = self.attempts.topic_accuracy(question["topic_id"])
        self.accuracy_label.setText(
            f"Topic accuracy: {stats['accuracy']}% over {stats['attempts']} attempts"
            if stats else "No attempts in this topic yet")
        self._load_image(question["question_image"])

    def _load_image(self, path):
        self.image_label.clear()
        if path and Path(path).is_file():
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.image_label.setPixmap(
                    pixmap.scaled(640, 280, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))
                self.image_label.show()
                return
        if path:
            self.feedback.setText("(The question image could not be loaded.)")
        self.image_label.hide()

    # -- actions ---------------------------------------------------------
    def _primary_action(self):
        if self.current is None:
            if self._finished:
                ids = self._rebuild() if self._rebuild else self.queue
                self.set_queue(self.heading, ids, self._rebuild)
            return
        if self._solved:
            self.next_question()
        else:
            self.check_answer()

    def _record_first_attempt(self, text, correct):
        if self._attempted:
            return None
        self._attempted = True
        elapsed = time.monotonic() - self._started
        self.attempts.record(self.current["id"], text, correct, elapsed)
        self._round_answered += 1
        self._round_correct += int(correct)
        self.answered.emit(correct)
        return elapsed

    def check_answer(self):
        if self.current is None or self._solved:
            return
        entered = self.answer.text().strip()
        if not entered:
            self.feedback.setText("Enter an answer first.")
            set_state(self.feedback, None)
            return
        alternatives = self.questions.alternatives(self.current)
        correct = is_correct(entered, self.current["answer"], alternatives)
        first = not self._attempted
        elapsed = self._record_first_attempt(entered, correct)
        if correct:
            self._solved = True
            took = f" · {format_duration(round(elapsed))}" if first and elapsed else ""
            self.feedback.setText(f"Correct ✓{took}" if first else "Correct ✓ (first try counted)")
            set_state(self.feedback, "good")
            self.answer.setEnabled(False)
            self.primary_button.setText("Next  →")
        else:
            note = "Only your first attempt counts. " if first else ""
            self.feedback.setText(f"Incorrect. {note}Try again or show the answer.")
            set_state(self.feedback, "bad")
            self.answer.selectAll()

    def reveal_answer(self):
        if self.current is None or self._solved:
            return
        self._record_first_attempt(self.answer.text().strip(), False)
        self._solved = True
        self.feedback.setText(f"Answer: {self.current['answer']}")
        set_state(self.feedback, "bad")
        self.answer.setEnabled(False)
        self.primary_button.setText("Next  →")
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

    def toggle_saved(self):
        if self.current is None:
            return
        saved = not self.questions.is_saved(self.current["id"])
        self.questions.set_saved(self.current["id"], saved)
        self._set_saved_button(saved)

    def _set_saved_button(self, saved):
        self.save_button.setText("★  Saved" if saved else "☆  Save")

    def next_question(self):
        self.index += 1
        self._load_current()
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
