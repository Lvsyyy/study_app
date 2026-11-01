import json
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget)

from core.answer_checker import is_correct
from core.formatting import format_duration
from ui.widgets import action_button, card, muted_label, set_state, title_label


class QuestionPage(QWidget):
    back_requested = Signal()
    answered = Signal(bool)

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
        self._rebuild = None
        self._generator = None
        self._round_correct = 0
        self._round_answered = 0

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(34, 30, 34, 30)
        self.root.setSpacing(18)
        self._build()

    def _build(self):
        header = QHBoxLayout()
        back = action_button("←  Back")
        back.clicked.connect(self.back_requested)
        header.addWidget(back)
        header.addStretch()
        self.subject_label = muted_label("")
        header.addWidget(self.subject_label)
        self.root.addLayout(header)

        self.title = title_label("Practice")
        self.root.addWidget(self.title)
        self.topic = muted_label("")
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
        self.hint_text = muted_label("")
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

        self.calculation_answer = QPlainTextEdit()
        self.calculation_answer.setPlaceholderText("Complete the calculation…")
        self.calculation_answer.setMinimumHeight(150)
        self.calculation_answer.setMaximumHeight(230)
        self.calculation_answer.hide()
        self.root.addWidget(self.calculation_answer)

        self.calculation_table = QTableWidget()
        self.calculation_table.setMinimumHeight(170)
        self.calculation_table.setAlternatingRowColors(True)
        self.calculation_table.setShowGrid(True)
        self.calculation_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.calculation_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.calculation_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.calculation_table.verticalHeader().setVisible(False)
        self.calculation_table.hide()
        self.root.addWidget(self.calculation_table)

        meta = QHBoxLayout()
        self.number_label = muted_label("")
        meta.addWidget(self.number_label)
        meta.addStretch()
        self.accuracy_label = muted_label("")
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
        for button in (self.skip_button, self.hint_button, self.reveal_button, self.save_button):
            buttons.addWidget(button)
        buttons.addStretch()
        buttons.addWidget(self.primary_button)
        self.root.addLayout(buttons)
        self.root.addStretch()
        self._show_empty("Choose a subject from the sidebar to start practising.")

    def set_subject(self, subject):
        self.set_queue(
            subject,
            self.questions.get_study_queue(subject),
            rebuild=lambda: self.questions.get_study_queue(subject),
        )

    def set_generator(self, heading, generator):
        self.heading = heading
        self._rebuild = None
        self._generator = generator
        self.subject_label.setText(heading)
        self.queue = []
        self.index = 0
        self._round_correct = 0
        self._round_answered = 0
        self._load_current()

    def set_queue(self, heading, ids, rebuild=None):
        self._generator = None
        self.heading = heading
        self._rebuild = rebuild
        self.subject_label.setText(heading)
        self.queue = list(ids)
        self.index = 0
        self._round_correct = 0
        self._round_answered = 0
        if self.queue:
            self._load_current()
        else:
            self._show_empty(f"No questions for {heading} yet.")

    def _controls_enabled(self, enabled):
        for widget in (self.answer, self.calculation_answer, self.calculation_table, self.skip_button, self.hint_button, self.reveal_button, self.save_button):
            widget.setEnabled(enabled)

    def _show_empty(self, message):
        self.current = None
        self._finished = False
        self.topic.setText("")
        self.question_text.setText(message)
        self.image_label.clear()
        self.image_label.hide()
        self.hint_text.clear()
        self.feedback.clear()
        self.number_label.clear()
        self.accuracy_label.clear()
        self.answer.clear()
        self.calculation_answer.clear()
        self.calculation_answer.hide()
        self.calculation_table.clear()
        self.calculation_table.hide()
        self.answer.show()
        self._controls_enabled(False)
        self.primary_button.setEnabled(False)
        self.primary_button.setText("Check answer")

    def _show_finished(self):
        self._show_empty("Round complete")
        self.topic.setText(self.heading)
        self.feedback.setText(
            f"You answered {self._round_answered} question(s): {self._round_correct} correct."
        )
        set_state(self.feedback, None)
        self.primary_button.setEnabled(True)
        self.primary_button.setText("Practice again")
        self._finished = True

    def _load_current(self):
        if self._generator is not None and self.index >= len(self.queue):
            self.queue.append(self._generator())
        question = None
        while self.index < len(self.queue) and question is None:
            question = self.questions.get_question(self.queue[self.index])
            if question is None:
                self.index += 1
        if question is None:
            self._show_finished()
            return

        self.current = question
        self._finished = False
        self._attempted = False
        self._solved = False
        self._started = time.monotonic()
        self._controls_enabled(True)
        self.primary_button.setEnabled(True)
        self.primary_button.setText("Check answer")
        self.hint_text.clear()
        self.feedback.clear()
        set_state(self.feedback, None)
        template = question["answer_template"] if "answer_template" in question.keys() else None
        self.calculation_table.hide()
        self.calculation_answer.hide()
        if template:
            try:
                table = json.loads(template)
                if isinstance(table, dict) and "headers" in table and "rows" in table:
                    self._show_calculation_table(table)
                    self.answer.hide()
                    self.calculation_answer.hide()
                    self.calculation_table.show()
                    self.calculation_table.setFocus()
                else:
                    self.answer.hide()
                    self.calculation_answer.show()
                    self.calculation_answer.setPlainText(template)
                    self.calculation_answer.setFocus()
            except (json.JSONDecodeError, TypeError):
                self.answer.hide()
                self.calculation_answer.show()
                self.calculation_answer.setPlainText(template)
                self.calculation_answer.setFocus()
        else:
            self.answer.show()
            self.answer.clear()
            self.answer.setFocus()
        self.hint_button.setEnabled(bool(question["hint"]))
        difficulty = question["difficulty"]
        self.topic.setText(
            f"{question['subject_name']} / {question['topic_name']} · "
            f"difficulty {'●' * difficulty}{'○' * (5 - difficulty)}"
        )
        self.question_text.setText(question["question_text"])
        self.number_label.setText(
            f"Question {self.index + 1}" if self._generator is not None
            else f"Question {self.index + 1} of {len(self.queue)}"
        )
        self._set_saved_button(self.questions.is_saved(question["id"]))
        stats = self.attempts.topic_accuracy(question["topic_id"])
        self.accuracy_label.setText(
            f"Topic accuracy: {stats['accuracy']}% over {stats['attempts']} attempts"
            if stats else "No attempts in this topic yet"
        )
        self._load_image(question["question_image"])

    def _load_image(self, path):
        self.image_label.clear()
        if path and Path(path).is_file():
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.image_label.setPixmap(
                    pixmap.scaled(
                        640, 280, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                self.image_label.show()
                return
        if path:
            self.feedback.setText("The question image could not be loaded.")
        self.image_label.hide()

    def _show_calculation_table(self, data, show_answer=False):
        headers, rows = data["headers"], data["rows"]
        binary_layout = bool(headers and headers[0] == "__binary_layout__")
        if binary_layout:
            headers = headers[1:]
        # Decimal division tables are intentionally blank while practising.
        if not show_answer and headers == ["Rechnung", "R", "GQ"]:
            rows = [["", "", ""] for _ in rows]

        self.calculation_table.clear()
        self.calculation_table.setColumnCount(len(headers))
        self.calculation_table.setRowCount(len(rows))
        self.calculation_table.setHorizontalHeaderLabels(headers)
        self.calculation_table.horizontalHeader().setVisible(not binary_layout)
        for row_index, row in enumerate(rows):
            separator = binary_layout and row and row[0] == "__SEPARATOR__"
            if separator:
                item = QTableWidgetItem("────────────────────────────────")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.calculation_table.setItem(row_index, 0, item)
                self.calculation_table.setSpan(row_index, 0, 1, len(headers))
                continue
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value or ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if value not in (None, "") and "____" not in str(value):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.calculation_table.setItem(row_index, column_index, item)
        self.calculation_table.resizeRowsToContents()
        table_height = (
            self.calculation_table.horizontalHeader().height()
            + sum(self.calculation_table.rowHeight(row) for row in range(self.calculation_table.rowCount()))
            + self.calculation_table.frameWidth() * 2
            + 4
        )
        self.calculation_table.setFixedHeight(table_height)

    def _input_text(self):
        if not self.calculation_table.isHidden():
            headers = [
                self.calculation_table.horizontalHeaderItem(i).text()
                for i in range(self.calculation_table.columnCount())
            ]
            rows = []
            for row in range(self.calculation_table.rowCount()):
                rows.append([
                    self.calculation_table.item(row, column).text()
                    if self.calculation_table.item(row, column) else ""
                    for column in range(self.calculation_table.columnCount())
                ])
            return json.dumps({"headers": headers, "rows": rows}, ensure_ascii=False)
        if not self.calculation_answer.isHidden():
            return self.calculation_answer.toPlainText()
        return self.answer.text()

    def _primary_action(self):
        if self.current is None:
            if self._finished:
                if self._generator is not None:
                    self.queue = []
                    self.index = 0
                    self._round_correct = 0
                    self._round_answered = 0
                    self._load_current()
                else:
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
        self.answered.emit(bool(correct))
        return elapsed

    def check_answer(self):
        if self.current is None or self._solved:
            return
        entered = self._input_text().strip()
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
            took = f" · {format_duration(round(elapsed))}" if first and elapsed is not None else ""
            self.feedback.setText(f"Correct ✓{took}" if first else "Correct ✓ (first try counted)")
            set_state(self.feedback, "good")
            self.answer.setEnabled(False)
            self.calculation_answer.setEnabled(False)
            self.calculation_table.setEnabled(False)
            self.primary_button.setText("Next  →")
        else:
            note = "Only your first attempt counts. " if first else ""
            self.feedback.setText(f"Incorrect. {note}Try again or show the answer.")
            set_state(self.feedback, "bad")
            if not self.calculation_answer.isHidden():
                self.calculation_answer.selectAll()
            else:
                self.answer.selectAll()

    def reveal_answer(self):
        if self.current is None or self._solved:
            return
        self._record_first_attempt(self._input_text().strip(), False)
        self._solved = True
        if not self.calculation_table.isHidden():
            try:
                answer_data = json.loads(self.current["answer"])
                if isinstance(answer_data, dict) and "headers" in answer_data and "rows" in answer_data:
                    self._show_calculation_table(answer_data, show_answer=True)
                    self.feedback.setText("Correct solution shown in the table.")
                else:
                    self.feedback.setText(f"Answer: {self.current['answer']}")
            except (json.JSONDecodeError, TypeError):
                self.feedback.setText(f"Answer: {self.current['answer']}")
        else:
            self.feedback.setText(f"Answer: {self.current['answer']}")
        set_state(self.feedback, "bad")
        self.answer.setEnabled(False)
        self.calculation_answer.setEnabled(False)
        self.calculation_table.setEnabled(False)
        self.primary_button.setText("Next  →")

    def next_question(self):
        if self.current is None:
            return
        self.index += 1
        self._load_current()

    def show_hint(self):
        if self.current is not None and self.current["hint"]:
            self.hint_text.setText(f"Hint: {self.current['hint']}")

    def toggle_saved(self):
        if self.current is None:
            return
        saved = not self.questions.is_saved(self.current["id"])
        self.questions.set_saved(self.current["id"], saved)
        self._set_saved_button(saved)

    def _set_saved_button(self, saved):
        self.save_button.setText("★  Saved" if saved else "☆  Save")
