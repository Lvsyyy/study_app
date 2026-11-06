import json
import re
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QPixmap, QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QFrame)
from ui.interactive_questions import InteractiveQuestion
from ui.pap_editor import PapEditor

from core.answer_checker import is_correct
from core.formatting import format_duration
from ui.widgets import action_button, card, muted_label, set_state, title_label


class AutoIndentCodeEditor(QPlainTextEdit):
    """Code editor that keeps method-body indentation consistent."""

    def keyPressEvent(self, event):
        if getattr(self, "auto_indent", True) and event.key() == Qt.Key.Key_Return and not event.modifiers() & (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier
        ):
            line = self.textCursor().block().text()
            indent = re.match(r"[ \t]*", line).group()
            stripped = line.strip()
            if stripped.endswith("{"):
                indent += "    "
            elif stripped.startswith("}") and len(indent) >= 4:
                indent = indent[:-4]
            super().keyPressEvent(event)
            self.textCursor().insertText(indent)
            return
        super().keyPressEvent(event)


class CSharpHighlighter(QSyntaxHighlighter):
    """Small C# syntax highlighter for the embedded practice editor."""

    def __init__(self, document):
        super().__init__(document)
        self.rules = []
        for word in (
            "using", "namespace", "class", "public", "private", "protected",
            "static", "void", "int", "string", "bool", "var", "new", "return",
            "if", "else", "for", "foreach", "while", "true", "false", "null",
        ):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor("#569CD6"))
            fmt.setFontWeight(QFont.Weight.Bold)
            self.rules.append((QRegularExpression(r"\b" + word + r"\b"), fmt))

        for pattern, color in (
            (r'"[^"\\]*(?:\.[^"\\]*)*"', "#CE9178"),
            (r"//[^\n]*", "#6A9955"),
            (r"\b\d+\b", "#B5CEA8"),
            (r"\bConsole\b", "#4EC9B0"),
            (r"\b(WriteLine|ReadLine|Write)\b", "#DCDCAA"),
        ):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            self.rules.append((QRegularExpression(pattern), fmt))

    def highlightBlock(self, text):
        for expression, fmt in self.rules:
            matches = expression.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


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
        self._code_mode = False
        self._review_subject = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        self.root = QVBoxLayout(content)
        self.root.setContentsMargins(34, 30, 34, 30)
        self.root.setSpacing(18)
        self.scroll_area.setWidget(content)
        outer.addWidget(self.scroll_area)
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

        self.code_editor_container = QWidget()
        self.code_editor_container.setObjectName("CodeEditorFrame")
        code_layout = QVBoxLayout(self.code_editor_container)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(0)
        self.code_editor_header = QLabel("  C#   |   Program.cs")
        self.code_editor_header.setObjectName("CodeEditorHeader")
        self.code_editor_header.setFixedHeight(34)
        code_layout.addWidget(self.code_editor_header)

        code_font = QFont("Cascadia Code")
        code_font.setStyleHint(QFont.StyleHint.Monospace)
        code_font.setPointSize(11)
        self.code_prefix = QLabel()
        self.code_prefix.setTextFormat(Qt.TextFormat.PlainText)
        self.code_prefix.setFont(code_font)
        self.code_prefix.setStyleSheet("color: #d4d4d4; padding: 10px 12px 0 12px;")
        code_layout.addWidget(self.code_prefix)

        self.code_editor = AutoIndentCodeEditor()
        self.code_editor.auto_indent = True
        self.code_editor.setObjectName("CodeEditor")
        self.code_editor.setPlaceholderText("// Write your code here")
        self.code_editor.setMinimumHeight(210)
        self.code_editor.setMaximumHeight(340)
        self.code_editor.setFont(code_font)
        self.code_editor.setTabStopDistance(
            self.code_editor.fontMetrics().horizontalAdvance(" ") * 4
        )
        self.code_editor.setStyleSheet(
            "QPlainTextEdit#CodeEditor { background: #1e1e1e; color: #d4d4d4; "
            "border: none; border-radius: 0; padding: 12px; selection-background-color: #264f78; }"
        )
        self.code_highlighter = CSharpHighlighter(self.code_editor.document())
        code_layout.addWidget(self.code_editor)

        self.code_suffix = QLabel()
        self.code_suffix.setTextFormat(Qt.TextFormat.PlainText)
        self.code_suffix.setFont(code_font)
        self.code_suffix.setStyleSheet("color: #d4d4d4; padding: 0 12px 10px 12px;")
        code_layout.addWidget(self.code_suffix)

        self.code_editor_container.setStyleSheet(
            "QWidget#CodeEditorFrame { background: #1e1e1e; "
            "border: 1px solid #3c3c3c; border-radius: 7px; } "
            "QLabel#CodeEditorHeader { background: #252526; color: #cccccc; "
            "border: none; border-bottom: 1px solid #3c3c3c; "
            "font-size: 11px; font-weight: 600; }"
        )
        self.code_editor_container.hide()

        self.batch_workspace = QWidget()
        batch_layout = QHBoxLayout(self.batch_workspace)
        batch_layout.setContentsMargins(0, 0, 0, 0)
        batch_layout.setSpacing(12)
        batch_layout.addWidget(self.code_editor_container, 1)

        self.batch_console_container = QWidget()
        self.batch_console_container.setObjectName("BatchConsoleFrame")
        console_layout = QVBoxLayout(self.batch_console_container)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)
        console_header = QHBoxLayout()
        self.batch_console_title = QLabel("  CMD   |   Vorgegebene Ausgabe")
        self.batch_console_title.setObjectName("BatchConsoleHeader")
        self.batch_console_title.setFixedHeight(34)
        console_header.addWidget(self.batch_console_title, 1)
        self.batch_run_button = action_button("Run")
        self.batch_run_button.clicked.connect(self.run_batch)
        console_header.addWidget(self.batch_run_button)
        console_layout.addLayout(console_header)
        self.batch_output = QPlainTextEdit()
        self.batch_output.setReadOnly(True)
        self.batch_output.setMinimumHeight(210)
        self.batch_output.setMaximumHeight(340)
        self.batch_output.setFont(code_font)
        self.batch_output.setStyleSheet(
            "QPlainTextEdit { background: #101010; color: #d4d4d4; "
            "border: none; border-radius: 0; padding: 12px; }"
        )
        console_layout.addWidget(self.batch_output)
        self.batch_console_container.setStyleSheet(
            "QWidget#BatchConsoleFrame { background: #101010; "
            "border: 1px solid #3c3c3c; border-radius: 7px; } "
            "QLabel#BatchConsoleHeader { background: #252526; color: #cccccc; "
            "border: none; border-bottom: 1px solid #3c3c3c; "
            "font-size: 11px; font-weight: 600; }"
        )
        batch_layout.addWidget(self.batch_console_container, 1)
        self.batch_workspace.hide()
        box.addWidget(self.batch_workspace)

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

        self.calculation_table_container = QWidget()
        self.calculation_tables_layout = QVBoxLayout(self.calculation_table_container)
        self.calculation_tables_layout.setContentsMargins(0, 0, 0, 0)
        self.calculation_tables_layout.setSpacing(14)
        self.calculation_tables = []
        self.calculation_table_titles = []
        self.calculation_table = None
        self.calculation_table_container.hide()
        self.root.addWidget(self.calculation_table_container)

        self.interactive_question = InteractiveQuestion()
        self.interactive_question.hide()
        self.root.addWidget(self.interactive_question)

        self.pap_editor = PapEditor()
        self.pap_editor.hide()
        self.root.addWidget(self.pap_editor)

        self.solution_panel = QFrame()
        self.solution_panel.setObjectName("SolutionPanel")
        solution_layout = QVBoxLayout(self.solution_panel)
        solution_layout.setContentsMargins(16, 14, 16, 14)
        solution_layout.setSpacing(8)
        self.solution_title = QLabel("Correct solution")
        self.solution_title.setProperty("role", "question")
        solution_layout.addWidget(self.solution_title)
        self.solution_content = QPlainTextEdit()
        self.solution_content.setReadOnly(True)
        self.solution_content.setMinimumHeight(110)
        self.solution_content.setMaximumHeight(300)
        self.solution_content.setFont(code_font)
        self.solution_content.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.solution_content.setStyleSheet(
            "QPlainTextEdit { background: #101820; color: #d4dce8; "
            "border: 1px solid #3c4b5c; border-radius: 6px; padding: 10px; }"
        )
        self.solution_highlighter = CSharpHighlighter(self.solution_content.document())
        solution_layout.addWidget(self.solution_content)
        self.solution_panel.setStyleSheet(
            "QFrame#SolutionPanel { background: palette(alternate-base); "
            "border: 1px solid palette(mid); border-radius: 9px; }"
        )
        self.solution_panel.hide()
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
        self._show_empty("Choose a subject from the sidebar to start practising.")

    def apply_theme(self, theme):
        self.interactive_question.apply_theme(theme)

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
        # Normal subject/topic rounds are finite and randomized.
        # Adaptive review belongs in a separate review mode, not at the end
        # of every topic queue.
        self._review_subject = None
        self.heading = heading
        self._rebuild = rebuild
        self.subject_label.setText(heading)
        self.queue = list(dict.fromkeys(ids))
        self.index = 0
        self._round_correct = 0
        self._round_answered = 0
        if self.queue:
            self._load_current()
        else:
            self._show_empty(f"No questions for {heading} yet.")

    def _controls_enabled(self, enabled):
        for widget in (self.answer, self.calculation_answer, self.code_editor, self.calculation_table_container, self.interactive_question, self.pap_editor, self.batch_run_button, self.skip_button, self.hint_button, self.reveal_button, self.save_button):
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
        self.code_editor.clear()
        self.code_editor_container.hide()
        self.batch_workspace.hide()
        self.batch_output.clear()
        self._code_mode = False
        self.question_text.show()
        self.calculation_answer.clear()
        self.calculation_answer.hide()
        self._clear_calculation_tables()
        self.calculation_table_container.hide()
        self.interactive_question.hide()
        self.pap_editor.hide()
        self.pap_editor.reset()
        self.solution_panel.hide()
        self.solution_content.clear()
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
        elif self._generator is None and self.index >= len(self.queue) and self._review_subject:
            previous_id = self.current["id"] if self.current is not None else None
            review_id = self.questions.get_review_question(self._review_subject, previous_id)
            if review_id is None:
                review_id = self.questions.get_review_question(self._review_subject)
            if review_id is not None:
                self.queue.append(review_id)
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
        self.calculation_table_container.hide()
        self.interactive_question.hide()
        self.interactive_question.set_answer_locked(False)
        self.pap_editor.hide()
        self.pap_editor.reset()
        self.solution_panel.hide()
        self.solution_content.clear()
        self.calculation_answer.hide()
        self.code_editor_container.hide()
        self.batch_workspace.hide()
        self.batch_run_button.show()
        question_text = question["question_text"]
        question_type = question["question_type"] if "question_type" in question.keys() else "text"
        self._batch_mode = question_type == "batch"
        self._csharp_practice_mode = question_type == "csharp_practice"
        self._pap_mode = question_type == "pap"
        self._batch_result = None
        self.batch_output.clear()
        self.batch_run_button.setEnabled(True)
        if self._batch_mode:
            try:
                batch_config = json.loads(question["answer"])
                self.batch_output.setPlainText("\n".join(batch_config.get("expected_output", [])))
            except (json.JSONDecodeError, TypeError):
                self.batch_output.setPlainText("Keine Zielausgabe hinterlegt.")
        elif self._csharp_practice_mode:
            try:
                practice_config = json.loads(question["answer"])
                self.batch_output.setPlainText(practice_config.get("output", ""))
            except (json.JSONDecodeError, TypeError):
                self.batch_output.setPlainText("Keine Zielausgabe hinterlegt.")
        self._code_mode = question_type in ("code", "batch", "csharp_practice") or (
            question["subject_name"] == "AE"
            and bool(re.search(r"\b(?:static\s+void\s+Main|Console\.|using\s+System|class\s+\w+)\b", question_text))
        )
        if self._pap_mode:
            self.question_text.setText(question_text)
            self.question_text.show()
            self.answer.hide()
            try:
                self.pap_editor.load_config(json.loads(question["answer"]))
            except (json.JSONDecodeError, TypeError):
                self.pap_editor.reset()
            self.pap_editor.show()
        elif self._code_mode:
            if self._batch_mode:
                prompt = question_text
                code_prefix = r"C:\Users\Supercoolerbenutzer>"
                editable_body = ""
                code_suffix = ""
                self.code_editor_header.setText("  Batch   |   Eingabeaufforderung")
                self.code_editor.auto_indent = False
            else:
                prompt, code_prefix, editable_body, code_suffix = self._split_code_question(question_text)
                self.code_editor_header.setText("  C#   |   Program.cs")
                self.code_editor.auto_indent = True
            self.question_text.setText(prompt)
            self.question_text.setVisible(bool(prompt))
            self.answer.hide()
            self.calculation_answer.hide()
            self.code_prefix.setText(code_prefix)
            self.code_suffix.setText(code_suffix)
            if self._csharp_practice_mode:
                # Match the eight-space method-body indentation used by revealed solutions.
                editable_body = self._format_code_body(editable_body) or "        "
            self.code_editor.setPlainText(editable_body)
            cursor = self.code_editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.code_editor.setTextCursor(cursor)
            if self._batch_mode:
                self.code_editor_container.show()
                self.batch_workspace.show()
            elif self._csharp_practice_mode:
                self.code_editor_header.setText("  C#   |   Program.cs")
                self.batch_console_title.setText("  CONSOLE   |   Vorgegebene Ausgabe")
                self.batch_run_button.hide()
                self.code_editor_container.show()
                self.batch_workspace.show()
            else:
                self.code_editor_container.show()
            self.code_editor.setEnabled(True)
            self.code_editor.setFocus()
        elif question_type in ("multi_select", "ordering", "matching", "table_sort"):
            self.question_text.setText(question_text)
            self.question_text.show()
            self.answer.hide()
            self.calculation_answer.hide()
            self.interactive_question.load(question_type, question["answer"])
            self.interactive_question.show()
            self.interactive_question.setEnabled(True)
        elif template:
            self.question_text.setText(question_text)
            self.question_text.show()
            try:
                table = json.loads(template)
                if isinstance(table, dict) and (
                    ("headers" in table and "rows" in table)
                    or isinstance(table.get("tables"), list)
                ):
                    self._show_calculation_table(table)
                    self.answer.hide()
                    self.calculation_answer.hide()
                    self.calculation_table_container.show()
                    self.calculation_tables[0].setFocus()
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
            self.question_text.setText(question_text)
            self.question_text.show()
            self.code_editor_container.hide()
            self.answer.show()
            self.answer.clear()
            self.answer.setFocus()
        self.hint_button.setEnabled(bool(question["hint"]))
        difficulty = question["difficulty"]
        self.topic.setText(
            f"{question['subject_name']} / {question['topic_name']} · "
            f"difficulty {'●' * difficulty}{'○' * (5 - difficulty)}"
        )
        self.number_label.setText(
            f"Question {self.index + 1}" if self._generator is not None
            else f"Question {self.index + 1} of {len(self.queue)}"
        )
        self._set_saved_button(bool(question["is_saved"]))
        self.accuracy_label.setText(
            f"Topic accuracy: {question['topic_accuracy']}% over "
            f"{question['topic_attempts']} attempts"
            if question["topic_attempts"] else "No attempts in this topic yet"
        )
        self._load_image(question["question_image"])

    @staticmethod
    def _split_code_question(question_text):
        """Separate the fixed Main method shell from its editable body."""
        lines = question_text.splitlines()
        main_index = next(
            (
                index for index, line in enumerate(lines)
                if re.search(r"\bstatic\s+void\s+Main\s*\(", line)
            ),
            None,
        )
        if main_index is None:
            return question_text.strip(), "", "", ""

        prompt = "\n".join(lines[:main_index]).strip()
        signature = lines[main_index].strip()
        opening_index = next(
            (index for index in range(main_index + 1, len(lines)) if "{" in lines[index]),
            None,
        )
        if opening_index is None:
            return prompt, signature, "", ""

        prefix = signature + "\n" + lines[opening_index].strip()
        depth = lines[opening_index].count("{") - lines[opening_index].count("}")
        closing_index = None
        for index in range(opening_index + 1, len(lines)):
            depth += lines[index].count("{") - lines[index].count("}")
            if depth <= 0:
                closing_index = index
                break

        if closing_index is None:
            body_lines = lines[opening_index + 1:]
            suffix = ""
        else:
            body_lines = lines[opening_index + 1:closing_index]
            suffix = lines[closing_index].strip()

        body = "\n".join(body_lines).strip("\n")
        return prompt, prefix, body, suffix

    @staticmethod
    def _format_code_body(code):
        """Indent a solution as a body inside the fixed Main method."""
        import textwrap

        body = textwrap.dedent((code or "").strip("\n"))
        if not body:
            return ""
        return "\n".join(
            ("        " + line if line.strip() else "")
            for line in body.splitlines()
        )

    @staticmethod
    @staticmethod
    def _condition_answer_matches(entered, expected):
        """Check the condition entered into the supplied if-statement scaffold."""
        match = re.search(r"\bif\s*\(\s*(.*?)\s*\)", entered or "", re.DOTALL)
        if not match:
            return False
        normalize = lambda value: re.sub(r"\s+", "", value or "")
        return normalize(match.group(1)) == normalize(expected)

    @staticmethod
    def _code_answer_matches(entered, expected, alternatives=()):
        """Compare code while ignoring indentation differences."""
        import textwrap

        submitted = textwrap.dedent(
            (entered or "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
        ).rstrip()
        if not submitted:
            return False

        for candidate in (expected, *alternatives):
            target = textwrap.dedent(
                QuestionPage._format_code_body(candidate)
            ).rstrip()
            if target and submitted == target:
                return True
        return False

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

    def _clear_calculation_tables(self):
        while self.calculation_tables_layout.count():
            item = self.calculation_tables_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.calculation_tables = []
        self.calculation_table_titles = []
        self.calculation_table = None

    def _populate_calculation_table(self, table, data, show_answer=False):
        headers, rows = data["headers"], data["rows"]
        binary_layout = bool(headers and headers[0] == "__binary_layout__")
        table.setProperty("binary_layout", binary_layout)
        if binary_layout:
            headers = headers[1:]
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for column in range(1, len(headers)):
                table.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        else:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if not show_answer and headers == ["Rechnung", "R", "GQ"]:
            rows = [["", "", ""] for _ in rows]

        table.clear()
        table.setColumnCount(len(headers))
        table.setRowCount(len(rows))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setVisible(not binary_layout)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setStyleSheet(
            "QLineEdit { background: transparent; border: none; "
            "border-radius: 0; padding: 0; margin: 0; }"
        )
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for row_index, row in enumerate(rows):
            separator = binary_layout and row and row[0] == "__SEPARATOR__"
            if separator:
                for column_index in range(len(headers)):
                    item = QTableWidgetItem("")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if column_index == 0:
                        item.setData(Qt.ItemDataRole.UserRole, "__SEPARATOR__")
                    table.setItem(row_index, column_index, item)

                    divider = QFrame()
                    divider.setFrameShape(QFrame.Shape.HLine)
                    divider.setFrameShadow(QFrame.Shadow.Plain)
                    divider.setLineWidth(2)
                    divider.setMidLineWidth(0)
                    table.setCellWidget(row_index, column_index, divider)
                continue
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value or ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if value not in (None, "") and "____" not in str(value):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_index, column_index, item)
        table.resizeRowsToContents()
        table_height = (
            table.horizontalHeader().height()
            + sum(table.rowHeight(row) for row in range(table.rowCount()))
            + table.frameWidth() * 2
            + 4
        )
        table.setFixedHeight(max(170, table_height))

    def _show_calculation_table(self, data, show_answer=False):
        self._clear_calculation_tables()
        tables = data.get("tables") if isinstance(data, dict) else None
        multi_table = isinstance(tables, list)
        entries = tables if multi_table else [data]
        for entry in entries:
            self.calculation_table_titles.append(entry.get("title", ""))
            if entry.get("title"):
                heading = QLabel(entry["title"])
                heading.setWordWrap(True)
                heading.setProperty("role", "question")
                self.calculation_tables_layout.addWidget(heading)
            table = QTableWidget()
            self._populate_calculation_table(table, entry, show_answer)
            self.calculation_tables.append(table)
            self.calculation_tables_layout.addWidget(table)
        if self.calculation_tables:
            self.calculation_table = self.calculation_tables[0]

    def _table_input_data(self, table):
        headers = [
            table.horizontalHeaderItem(i).text()
            for i in range(table.columnCount())
        ]
        binary_layout = bool(table.property("binary_layout"))
        if binary_layout:
            headers.insert(0, "__binary_layout__")
        rows = []
        for row in range(table.rowCount()):
            first = table.item(row, 0)
            if (
                binary_layout
                and first
                and first.data(Qt.ItemDataRole.UserRole) == "__SEPARATOR__"
            ):
                rows.append(["__SEPARATOR__", *[""] * (table.columnCount() - 1)])
                continue
            rows.append([
                table.item(row, column).text() if table.item(row, column) else ""
                for column in range(table.columnCount())
            ])
        return {"headers": headers, "rows": rows}

    def _input_text(self):
        if self._pap_mode:
            return self.pap_editor.get_answer()
        if self._code_mode:
            return self.code_editor.toPlainText()
        if not self.interactive_question.isHidden():
            return self.interactive_question.get_answer()
        if not self.calculation_table_container.isHidden():
            tables = [self._table_input_data(table) for table in self.calculation_tables]
            if len(tables) > 1:
                titles = self.calculation_table_titles
                return json.dumps({
                    "tables": [
                        {"title": title, **table}
                        for title, table in zip(titles, tables)
                    ]
                }, ensure_ascii=False)
            return json.dumps(tables[0], ensure_ascii=False)
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
        raw_entered = self._input_text()
        # Preserve leading indentation in code: stripping it here makes the
        # first line differ from later auto-indented lines during comparison.
        entered = raw_entered if self._code_mode else raw_entered.strip()
        if not entered.strip():
            self.feedback.setText("Enter an answer first.")
            set_state(self.feedback, None)
            return
        alternatives = self.questions.alternatives(self.current)
        correct = (
            self.pap_editor.is_correct(self.current["answer"]) if self._pap_mode else
            self.interactive_question.is_correct() if not self.interactive_question.isHidden() else
            self._batch_answer_matches() if self._batch_mode else
            (
                self._condition_answer_matches(
                    entered, json.loads(self.current["answer"]).get("solution", "")
                )
                if "if (________________)" in self.current["question_text"]
                else self._code_answer_matches(
                    entered,
                    json.loads(self.current["answer"]).get("solution", ""),
                    json.loads(self.current["answer"]).get("alternatives", ()),
                )
            )
            if self._csharp_practice_mode else
            self._code_answer_matches(entered, self.current["answer"], alternatives)
            if self._code_mode else is_correct(entered, self.current["answer"], alternatives)
        )
        first = not self._attempted
        elapsed = self._record_first_attempt(entered, correct)
        if correct:
            self._solved = True
            took = f" · {format_duration(round(elapsed))}" if first and elapsed is not None else ""
            self.feedback.setText(f"Correct ✓{took}" if first else "Correct ✓ (first try counted)")
            set_state(self.feedback, "good")
            self.answer.setEnabled(False)
            self.code_editor.setEnabled(False)
            self.batch_run_button.setEnabled(False)
            self.calculation_answer.setEnabled(False)
            self.calculation_table_container.setEnabled(False)
            self.interactive_question.set_answer_locked(True)
            self.pap_editor.set_editing_enabled(False)
            self.primary_button.setText("Next  →")
        else:
            note = "Only your first attempt counts. " if first else ""
            self.feedback.setText(f"Incorrect. {note}Try again or show the answer.")
            set_state(self.feedback, "bad")
            if self._code_mode:
                pass
            elif not self.calculation_answer.isHidden():
                self.calculation_answer.selectAll()
            else:
                self.answer.selectAll()

    def run_batch(self):
        if not self._batch_mode or self.current is None:
            return
        from core.batch_simulator import simulate_batch, BatchSimulationError

        try:
            config = json.loads(self.current["answer"])
            inputs = config.get("inputs", [])
            result = simulate_batch(self.code_editor.toPlainText(), inputs)
            self._batch_result = result
            expected = "\n".join(config.get("expected_output", []))
            normalize = lambda value: "\n".join(
                line.rstrip() for line in value.replace("\r", "").strip().splitlines()
            )
            matches = normalize(result["output"]) == normalize(expected)
            self.feedback.setText(
                "Ausgabe stimmt mit der Vorgabe überein." if matches
                else "Die Ausgabe stimmt noch nicht mit der Vorgabe überein."
            )
            set_state(self.feedback, "good" if matches else None)
        except (json.JSONDecodeError, BatchSimulationError, TypeError, ValueError, SyntaxError) as exc:
            self._batch_result = None
            self.feedback.setText(f"Batch-Fehler: {exc}")
            set_state(self.feedback, "bad")

    def _batch_answer_matches(self):
        if self._batch_result is None:
            self.run_batch()
        if self._batch_result is None:
            return False
        try:
            config = json.loads(self.current["answer"])
            expected = "\n".join(config.get("expected_output", []))
            actual = self._batch_result["output"]
            normalize = lambda value: "\n".join(
                line.rstrip() for line in value.replace("\r", "").strip().splitlines()
            )
            return normalize(actual) == normalize(expected)
        except (json.JSONDecodeError, TypeError):
            return False

    def _format_solution_data(self):
        """Build a readable reference answer without modifying submitted controls."""
        raw = self.current["answer"]
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            data = None

        if self._pap_mode and isinstance(data, dict):
            nodes = {node.get("id"): node for node in data.get("nodes", [])}
            lines = ["Flowchart blocks:"]
            for node in data.get("nodes", []):
                lines.append(f'- {node.get("type", "Block")}: {node.get("text", "")}')
            lines.extend(("", "Connections:"))
            for edge in data.get("edges", []):
                source = nodes.get(edge.get("from"), {})
                target = nodes.get(edge.get("to"), {})
                lines.append(
                    f'- {source.get("text", edge.get("from"))} '
                    f'--[{edge.get("label", "Normal")}]--> '
                    f'{target.get("text", edge.get("to"))}'
                )
            return "\n".join(lines)

        if not self.interactive_question.isHidden() and isinstance(data, dict):
            kind = self.interactive_question.kind
            if kind == "multi_select":
                options, correct = data.get("options", []), data.get("correct", [])
                return "Correct options:\n" + "\n".join(
                    f'✓ {options[index]}'
                    for index in correct
                    if isinstance(index, int) and 0 <= index < len(options)
                )
            if kind == "ordering":
                return "Correct order:\n" + "\n".join(
                    f'{index + 1}. {value}'
                    for index, value in enumerate(data.get("items", []))
                )
            if kind == "matching":
                return "Correct matches:\n" + "\n".join(
                    f'{pair.get("left", "")}  →  {pair.get("right", "")}'
                    for pair in data.get("pairs", [])
                )
            if kind == "table_sort":
                categories, cards = data.get("categories", []), data.get("cards", [])
                return "Correct categories:\n" + "\n".join(
                    f'{category}: ' + ", ".join(
                        str(card.get("text", ""))
                        for card in cards
                        if str(card.get("category", "")) == str(category)
                    )
                    for category in categories
                )

        if isinstance(data, dict) and (
            ("headers" in data and "rows" in data)
            or isinstance(data.get("tables"), list)
        ):
            tables = data.get("tables", [data])
            sections = []
            for table_data in tables:
                headers, rows = table_data.get("headers", []), table_data.get("rows", [])
                if table_data.get("title"):
                    sections.append(str(table_data["title"]))
                sections.append(" | ".join(str(value) for value in headers))
                sections.extend(
                    " | ".join(str(value or "") for value in row) for row in rows
                )
                sections.append("")
            return "\n".join(sections).strip()

        if self._batch_mode and isinstance(data, dict):
            solution = data.get("solution", "")
            output = data.get("expected_output", [])
            output_text = "\n".join(output) if isinstance(output, list) else str(output)
            return f"Solution:\n{solution}\n\nExpected output:\n{output_text}".strip()

        if self._csharp_practice_mode and isinstance(data, dict):
            solution = self._format_code_body(data.get("solution", ""))
            output = data.get("output", "")
            return f"Solution:\n{solution}\n\nConsole output:\n{output}".strip()

        if self._code_mode:
            solution = data.get("solution", raw) if isinstance(data, dict) else raw
            return self._format_code_body(solution)
        if isinstance(data, dict) and "solution" in data:
            return str(data["solution"])
        return str(raw)

    def reveal_answer(self):
        if self.current is None or self._solved:
            return
        self._record_first_attempt(self._input_text(), False)
        self._solved = True
        self.solution_content.setPlainText(self._format_solution_data())
        self.solution_panel.show()
        self.feedback.setText("Correct solution shown below your answer.")
        set_state(self.feedback, "bad")
        self.answer.setEnabled(False)
        self.code_editor.setEnabled(False)
        self.batch_run_button.setEnabled(False)
        self.calculation_answer.setEnabled(False)
        self.calculation_table_container.setEnabled(False)
        self.interactive_question.set_answer_locked(True)
        self.pap_editor.set_editing_enabled(False)
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
