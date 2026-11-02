import json
import re
import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QPixmap, QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget)

from core.answer_checker import is_correct
from core.formatting import format_duration
from ui.widgets import action_button, card, muted_label, set_state, title_label


class AutoIndentCodeEditor(QPlainTextEdit):
    """Code editor that keeps method-body indentation consistent."""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers() & (
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
        box.addWidget(self.code_editor_container)

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
        for widget in (self.answer, self.calculation_answer, self.code_editor, self.calculation_table_container, self.skip_button, self.hint_button, self.reveal_button, self.save_button):
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
        self._code_mode = False
        self.question_text.show()
        self.calculation_answer.clear()
        self.calculation_answer.hide()
        self._clear_calculation_tables()
        self.calculation_table_container.hide()
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
        self.calculation_table_container.hide()
        self.calculation_answer.hide()
        self.code_editor_container.hide()
        question_text = question["question_text"]
        question_type = question["question_type"] if "question_type" in question.keys() else "text"
        self._code_mode = question_type == "code" or (
            question["subject_name"] == "AE"
            and bool(re.search(r"\b(?:static\s+void\s+Main|Console\.|using\s+System|class\s+\w+)\b", question_text))
        )
        if self._code_mode:
            prompt, code_prefix, editable_body, code_suffix = self._split_code_question(question_text)
            self.question_text.setText(prompt)
            self.question_text.setVisible(bool(prompt))
            self.answer.hide()
            self.calculation_answer.hide()
            self.code_prefix.setText(code_prefix)
            self.code_suffix.setText(code_suffix)
            self.code_editor.setPlainText(editable_body)
            cursor = self.code_editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.code_editor.setTextCursor(cursor)
            self.code_editor_container.show()
            self.code_editor.setEnabled(True)
            self.code_editor.setFocus()
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
        self._set_saved_button(self.questions.is_saved(question["id"]))
        stats = self.attempts.topic_accuracy(question["topic_id"])
        self.accuracy_label.setText(
            f"Topic accuracy: {stats['accuracy']}% over {stats['attempts']} attempts"
            if stats else "No attempts in this topic yet"
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
    def _code_answer_matches(entered, expected, alternatives=()):
        """Compare code exactly, including indentation and whitespace."""
        submitted = (entered or "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
        if not submitted:
            return False

        for candidate in (expected, *alternatives):
            target = QuestionPage._format_code_body(candidate)
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
                item = QTableWidgetItem("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_index, 0, item)
                table.setSpan(row_index, 0, 1, len(headers))
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
            if binary_layout and first and first.text().startswith("━"):
                rows.append(["__SEPARATOR__", *[""] * (table.columnCount() - 1)])
                continue
            rows.append([
                table.item(row, column).text() if table.item(row, column) else ""
                for column in range(table.columnCount())
            ])
        return {"headers": headers, "rows": rows}

    def _input_text(self):
        if self._code_mode:
            return self.code_editor.toPlainText()
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
        entered = self._input_text().strip()
        if not entered:
            self.feedback.setText("Enter an answer first.")
            set_state(self.feedback, None)
            return
        alternatives = self.questions.alternatives(self.current)
        correct = (
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
            self.calculation_answer.setEnabled(False)
            self.calculation_table_container.setEnabled(False)
            self.primary_button.setText("Next  →")
        else:
            note = "Only your first attempt counts. " if first else ""
            self.feedback.setText(f"Incorrect. {note}Try again or show the answer.")
            set_state(self.feedback, "bad")
            if self._code_mode:
                self.code_editor.selectAll()
            elif not self.calculation_answer.isHidden():
                self.calculation_answer.selectAll()
            else:
                self.answer.selectAll()

    def reveal_answer(self):
        if self.current is None or self._solved:
            return
        self._record_first_attempt(self._input_text().strip(), False)
        self._solved = True
        if self._code_mode:
            self.code_editor.setPlainText(self._format_code_body(self.current["answer"]))
            self.feedback.setText("Correct solution shown in the code editor.")
        elif not self.calculation_table_container.isHidden():
            try:
                answer_data = json.loads(self.current["answer"])
                if isinstance(answer_data, dict) and (
                    ("headers" in answer_data and "rows" in answer_data)
                    or isinstance(answer_data.get("tables"), list)
                ):
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
        self.code_editor.setEnabled(False)
        self.calculation_answer.setEnabled(False)
        self.calculation_table_container.setEnabled(False)
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
