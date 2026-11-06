import random
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.answer_checker import is_correct
from core.batch_simulator import BatchSimulationError, simulate_batch
from core.formatting import format_duration
from core.i18n import tr
from ui.interactive_questions import InteractiveQuestion
from ui.pap_editor import PapEditor
from ui.question_content import (
    BATCH,
    CODE,
    CODE_MODES,
    CSHARP,
    INTERACTIVE,
    PAP,
    TABLE,
    TEXT,
    code_answer_matches,
    condition_answer_matches,
    format_solution_text,
    has_tables,
    normalize_console,
    parse_answer,
    question_mode,
)
from ui.question_forms import CodeAnswer, SolutionPanel, TableAnswer
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
        self.mode = TEXT
        self._started = time.monotonic()
        self._attempted = False
        self._solved = False
        self._finished = False
        self._rebuild = None
        self._generator = None
        self._round_correct = 0
        self._round_answered = 0
        self._batch_result = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(self.scroll_area)
        content = QWidget()
        self.root = QVBoxLayout(content)
        self.root.setContentsMargins(34, 30, 34, 30)
        self.root.setSpacing(18)
        self.scroll_area.setWidget(content)
        self._build()

    # -- construction ------------------------------------------------------

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

        self.code_answer = CodeAnswer(self.run_batch)
        box.addWidget(self.code_answer)

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
        self.answer.setPlaceholderText(tr("Type your answer…"))
        self.answer.returnPressed.connect(self._primary_action)
        self.root.addWidget(self.answer)

        self.calculation_answer = QPlainTextEdit()
        self.calculation_answer.setPlaceholderText(tr("Complete the calculation…"))
        self.calculation_answer.setMinimumHeight(150)
        self.calculation_answer.setMaximumHeight(230)
        self.calculation_answer.hide()
        self.root.addWidget(self.calculation_answer)

        self.table_answer = TableAnswer()
        self.root.addWidget(self.table_answer)

        self.interactive_question = InteractiveQuestion()
        self.interactive_question.hide()
        self.root.addWidget(self.interactive_question)

        self.pap_editor = PapEditor()
        self.pap_editor.hide()
        self.root.addWidget(self.pap_editor)

        self.solution_panel = SolutionPanel()
        self.root.addWidget(self.solution_panel)

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
        self._show_empty(tr("Choose a subject from the sidebar to start practising."))

    def apply_theme(self, theme):
        self.interactive_question.apply_theme(theme)

    # -- rounds ------------------------------------------------------------

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
        # Queues rebuilt from SQL already come back in a random order; only the
        # fixed id lists (saved questions, practice again) need shuffling here.
        self.queue = list(dict.fromkeys(ids))
        if rebuild is None:
            random.shuffle(self.queue)
        self.index = 0
        self._round_correct = 0
        self._round_answered = 0
        if self.queue:
            self._load_current()
        else:
            self._show_empty(tr("No questions for {heading} yet.", heading=heading))

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
        self.primary_button.setText(tr("Check answer"))
        self.hint_text.clear()
        self.feedback.clear()
        set_state(self.feedback, None)
        self._reset_answer_views()

        template = question["answer_template"] if "answer_template" in question.keys() else None
        data = parse_answer(question["answer"])
        question_type = question["question_type"] if "question_type" in question.keys() else "text"
        self.mode = question_mode(
            question_type,
            question["subject_name"],
            question["question_text"],
            parse_answer(template) if template else None,
        )
        self._batch_result = None
        self._apply_view(question, question_type, template, data)

        self.hint_button.setEnabled(bool(question["hint"]))
        difficulty = question["difficulty"]
        self.topic.setText(
            f"{question['subject_name']} / {question['topic_name']} · "
            f"{tr('difficulty')} {'●' * difficulty}{'○' * (5 - difficulty)}"
        )
        self.number_label.setText(
            tr("Question {number}", number=self.index + 1)
            if self._generator is not None
            else tr(
                "Question {number} of {total}",
                number=self.index + 1,
                total=len(self.queue),
            )
        )
        self._set_saved_button(bool(question["is_saved"]))
        self.accuracy_label.setText(
            tr(
                "Topic accuracy: {accuracy}% over {attempts} attempts",
                accuracy=question["topic_accuracy"],
                attempts=question["topic_attempts"],
            )
            if question["topic_attempts"] else tr("No attempts in this topic yet")
        )
        self._load_image(question["question_image"])

    def _apply_view(self, question, question_type, template, data):
        """Show only the answer view that belongs to this question type."""
        question_text = question["question_text"]

        if self.mode == PAP:
            self.question_text.setText(question_text)
            self.question_text.show()
            self.answer.hide()
            self.calculation_answer.hide()
            self.code_answer.hide()
            self.table_answer.hide()
            try:
                self.pap_editor.load_config(data or {})
            except (AttributeError, TypeError, ValueError):
                self.pap_editor.reset()
            self.pap_editor.show()
            return

        if self.mode in CODE_MODES:
            prompt = self.code_answer.show_question(question_text, self.mode, data)
            self.question_text.setText(prompt)
            self.question_text.setVisible(bool(prompt))
            self.answer.hide()
            self.calculation_answer.hide()
            self.table_answer.hide()
            self.interactive_question.hide()
            self.pap_editor.hide()
            self.code_answer.show()
            self.code_answer.focus()
            return

        if self.mode == INTERACTIVE:
            self.question_text.setText(question_text)
            self.question_text.show()
            self.answer.hide()
            self.calculation_answer.hide()
            self.code_answer.hide()
            self.table_answer.hide()
            self.pap_editor.hide()
            self.interactive_question.load(question_type, question["answer"])
            self.interactive_question.show()
            self.interactive_question.setEnabled(True)
            return

        if self.mode == TABLE:
            self.question_text.setText(question_text)
            self.question_text.show()
            self.answer.hide()
            self.calculation_answer.hide()
            self.code_answer.hide()
            self.pap_editor.hide()
            self.table_answer.show_data(parse_answer(template))
            self.table_answer.show()
            self.table_answer.focus_first()
            return

        self.question_text.setText(question_text)
        self.question_text.show()
        self.code_answer.hide()
        self.table_answer.hide()
        self.interactive_question.hide()
        self.pap_editor.hide()
        if template:
            self.answer.hide()
            self.calculation_answer.setPlainText(template)
            self.calculation_answer.show()
            self.calculation_answer.setFocus()
        else:
            self.calculation_answer.hide()
            self.answer.show()
            self.answer.clear()
            self.answer.setFocus()

    def _reset_answer_views(self):
        self.solution_panel.reset()
        self.answer.clear()
        self.answer.hide()
        self.calculation_answer.clear()
        self.calculation_answer.hide()
        self.table_answer.clear()
        self.table_answer.hide()
        self.interactive_question.hide()
        self.interactive_question.set_answer_locked(False)
        self.pap_editor.hide()
        self.pap_editor.reset()
        self.code_answer.reset()
        self.code_answer.hide()

    def _controls_enabled(self, enabled):
        for widget in (
            self.answer,
            self.calculation_answer,
            self.code_answer.editor,
            self.table_answer,
            self.interactive_question,
            self.pap_editor,
            self.code_answer.run_button,
            self.skip_button,
            self.hint_button,
            self.reveal_button,
            self.save_button,
        ):
            widget.setEnabled(enabled)

    def _lock_controls(self):
        """Freeze the answer controls after a correct answer or a reveal."""
        for widget in (
            self.answer,
            self.code_answer.editor,
            self.code_answer.run_button,
            self.calculation_answer,
            self.table_answer,
        ):
            widget.setEnabled(False)
        self.interactive_question.set_answer_locked(True)
        self.pap_editor.set_editing_enabled(False)
        self.primary_button.setText(tr("Next  →"))

    def _show_empty(self, message):
        self.current = None
        self._finished = False
        self.mode = TEXT
        self.topic.setText("")
        self.question_text.setText(message)
        self.question_text.show()
        self.image_label.clear()
        self.image_label.hide()
        self.hint_text.clear()
        self.feedback.clear()
        self.number_label.clear()
        self.accuracy_label.clear()
        self._reset_answer_views()
        self.answer.show()
        self._controls_enabled(False)
        self.primary_button.setEnabled(False)
        self.primary_button.setText(tr("Check answer"))

    def _show_finished(self):
        self._show_empty(tr("Round complete"))
        self.topic.setText(self.heading)
        self.feedback.setText(
            tr(
                "You answered {answered} question(s): {correct} correct.",
                answered=self._round_answered,
                correct=self._round_correct,
            )
        )
        set_state(self.feedback, None)
        self.primary_button.setEnabled(True)
        self.primary_button.setText(tr("Practice again"))
        self._finished = True

    # -- answers -----------------------------------------------------------

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
            self.feedback.setText(tr("The question image could not be loaded."))
        self.image_label.hide()

    def _answer_data(self):
        return parse_answer(self.current["answer"]) if self.current is not None else None

    def _input_text(self):
        if self.mode == PAP:
            return self.pap_editor.get_answer()
        if self.mode in CODE_MODES:
            return self.code_answer.value()
        if self.mode == INTERACTIVE:
            return self.interactive_question.get_answer()
        if self.mode == TABLE:
            return self.table_answer.value()
        if not self.calculation_answer.isHidden():
            return self.calculation_answer.toPlainText()
        return self.answer.text()

    def _answer_is_correct(self, entered, alternatives):
        data = self._answer_data()
        if self.mode == PAP:
            return self.pap_editor.is_correct(self.current["answer"])
        if self.mode == INTERACTIVE:
            return self.interactive_question.is_correct()
        if self.mode == BATCH:
            return self._batch_answer_matches()
        if self.mode == CSHARP:
            solution = data.get("solution", "") if isinstance(data, dict) else ""
            if "if (________________)" in self.current["question_text"]:
                return condition_answer_matches(entered, solution)
            extra = data.get("alternatives", ()) if isinstance(data, dict) else ()
            return code_answer_matches(entered, solution, extra)
        if self.mode == CODE:
            return code_answer_matches(entered, self.current["answer"], alternatives)
        return is_correct(entered, self.current["answer"], alternatives)

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
        raw_entered = self._input_text()
        # Preserve leading indentation in code: stripping it here makes the
        # first line differ from later auto-indented lines during comparison.
        entered = raw_entered if self.mode in CODE_MODES else raw_entered.strip()
        if not entered.strip():
            self.feedback.setText(tr("Enter an answer first."))
            set_state(self.feedback, None)
            return

        alternatives = self.questions.alternatives(self.current)
        correct = self._answer_is_correct(entered, alternatives)
        first = not self._attempted
        elapsed = self._record_first_attempt(entered, correct)
        if correct:
            self._solved = True
            took = f" · {format_duration(round(elapsed))}" if first and elapsed is not None else ""
            self.feedback.setText(
                tr("Correct ✓{took}", took=took) if first
                else tr("Correct ✓ (first try counted)")
            )
            set_state(self.feedback, "good")
            self._lock_controls()
        else:
            note = tr("Only your first attempt counts. ") if first else ""
            self.feedback.setText(
                tr("Incorrect. {note}Try again or show the answer.", note=note)
            )
            set_state(self.feedback, "bad")
            if self.mode not in CODE_MODES and not self.calculation_answer.isHidden():
                self.calculation_answer.selectAll()
            elif self.mode not in CODE_MODES:
                self.answer.selectAll()

    def run_batch(self):
        if self.mode != BATCH or self.current is None:
            return
        try:
            config = parse_answer(self.current["answer"]) or {}
            self._batch_result = simulate_batch(
                self.code_answer.value(), config.get("inputs", [])
            )
            matches = self._batch_output_matches()
            self.feedback.setText(
                "Ausgabe stimmt mit der Vorgabe überein." if matches
                else "Die Ausgabe stimmt noch nicht mit der Vorgabe überein."
            )
            set_state(self.feedback, "good" if matches else None)
        except (BatchSimulationError, TypeError, ValueError, SyntaxError) as exc:
            self._batch_result = None
            self.feedback.setText(f"Batch-Fehler: {exc}")
            set_state(self.feedback, "bad")

    def _batch_output_matches(self):
        """Compare the last simulated run with the task's expected console output."""
        if self.current is None or self._batch_result is None:
            return False
        config = parse_answer(self.current["answer"])
        if not isinstance(config, dict):
            return False
        expected = "\n".join(config.get("expected_output", []))
        return (
            normalize_console(self._batch_result["output"])
            == normalize_console(expected)
        )

    def _batch_answer_matches(self):
        if self._batch_result is None:
            self.run_batch()
        return self._batch_output_matches()

    def reveal_answer(self):
        if self.current is None or self._solved:
            return
        self._record_first_attempt(self._input_text(), False)
        self._solved = True
        data = self._answer_data()

        if self.mode == PAP:
            self.solution_panel.show_diagram(data or {})
        elif has_tables(data):
            # Calculation answers are shown as real tables instead of ASCII text.
            self.solution_panel.show_tables(data)
        else:
            kind = self.interactive_question.kind if self.mode == INTERACTIVE else None
            self.solution_panel.show_text(
                format_solution_text(self.current, data, self.mode, kind)
            )

        self.feedback.setText(tr("Correct solution shown below your answer."))
        set_state(self.feedback, "bad")
        self._lock_controls()

    def next_question(self):
        if self.current is None:
            return
        self.index += 1
        self._load_current()

    def show_hint(self):
        if self.current is not None and self.current["hint"]:
            self.hint_text.setText(tr("Hint: {hint}", hint=self.current["hint"]))

    def toggle_saved(self):
        if self.current is None:
            return
        saved = not self.questions.is_saved(self.current["id"])
        self.questions.set_saved(self.current["id"], saved)
        self._set_saved_button(saved)

    def _set_saved_button(self, saved):
        self.save_button.setText(tr("★  Saved") if saved else tr("☆  Save"))
