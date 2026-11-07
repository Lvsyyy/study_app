"""Answer and solution views for the practice page.

One widget per answer shape (code family, calculation tables, reference
solution), so the page only has to orchestrate a round.
"""
import json
import re

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr
from ui.pap_editor import PapEditor
from ui.question_content import (
    BATCH,
    CSHARP,
    format_code_body,
    split_code_question,
)
from ui.widgets import action_button

MISSING_BATCH_OUTPUT = "Keine Zielausgabe hinterlegt."


def code_font():
    font = QFont("Cascadia Code")
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setPointSize(11)
    return font


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
            (r'"[^"\\]*(?:\\.[^"\\]*)*"', "#CE9178"),
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


class CodeAnswer(QWidget):
    """C# or batch editor plus the batch console beside it."""

    def __init__(self, on_run):
        super().__init__()
        font = code_font()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.editor_container = QWidget()
        self.editor_container.setObjectName("CodeEditorFrame")
        editor_layout = QVBoxLayout(self.editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        self.header = QLabel("  C#   |   Program.cs")
        self.header.setObjectName("CodeEditorHeader")
        self.header.setFixedHeight(34)
        editor_layout.addWidget(self.header)

        self.prefix = QLabel()
        self.prefix.setTextFormat(Qt.TextFormat.PlainText)
        self.prefix.setFont(font)
        self.prefix.setStyleSheet("color: #d4d4d4; padding: 10px 12px 0 12px;")
        editor_layout.addWidget(self.prefix)

        self.editor = AutoIndentCodeEditor()
        self.editor.auto_indent = True
        self.editor.setObjectName("CodeEditor")
        self.editor.setPlaceholderText(tr("// Write your code here"))
        self.editor.setMinimumHeight(210)
        self.editor.setMaximumHeight(340)
        self.editor.setFont(font)
        self.editor.setTabStopDistance(
            self.editor.fontMetrics().horizontalAdvance(" ") * 4
        )
        self.editor.setStyleSheet(
            "QPlainTextEdit#CodeEditor { background: #1e1e1e; color: #d4d4d4; "
            "border: none; border-radius: 0; padding: 12px; selection-background-color: #264f78; }"
        )
        self.highlighter = CSharpHighlighter(self.editor.document())
        editor_layout.addWidget(self.editor)

        self.suffix = QLabel()
        self.suffix.setTextFormat(Qt.TextFormat.PlainText)
        self.suffix.setFont(font)
        self.suffix.setStyleSheet("color: #d4d4d4; padding: 0 12px 10px 12px;")
        editor_layout.addWidget(self.suffix)

        self.editor_container.setStyleSheet(
            "QWidget#CodeEditorFrame { background: #1e1e1e; "
            "border: 1px solid #3c3c3c; border-radius: 7px; } "
            "QLabel#CodeEditorHeader { background: #252526; color: #cccccc; "
            "border: none; border-bottom: 1px solid #3c3c3c; "
            "font-size: 11px; font-weight: 600; }"
        )
        layout.addWidget(self.editor_container, 1)

        self.console_container = QWidget()
        self.console_container.setObjectName("BatchConsoleFrame")
        console_layout = QVBoxLayout(self.console_container)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)
        console_header = QHBoxLayout()
        self.console_title = QLabel(f"  {tr('CMD')}   |   {tr('Expected output')}")
        self.console_title.setObjectName("BatchConsoleHeader")
        self.console_title.setFixedHeight(34)
        console_header.addWidget(self.console_title, 1)
        self.run_button = action_button("Run")
        self.run_button.clicked.connect(on_run)
        console_header.addWidget(self.run_button)
        console_layout.addLayout(console_header)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(210)
        self.output.setMaximumHeight(340)
        self.output.setFont(font)
        self.output.setStyleSheet(
            "QPlainTextEdit { background: #101010; color: #d4d4d4; "
            "border: none; border-radius: 0; padding: 12px; }"
        )
        console_layout.addWidget(self.output)
        self.console_container.setStyleSheet(
            "QWidget#BatchConsoleFrame { background: #101010; "
            "border: 1px solid #3c3c3c; border-radius: 7px; } "
            "QLabel#BatchConsoleHeader { background: #252526; color: #cccccc; "
            "border: none; border-bottom: 1px solid #3c3c3c; "
            "font-size: 11px; font-weight: 600; }"
        )
        layout.addWidget(self.console_container, 1)
        self.hide()

    # -- lifecycle ---------------------------------------------------------

    def reset(self):
        self.editor.clear()
        self.prefix.clear()
        self.suffix.clear()
        self.output.clear()
        self.run_button.setEnabled(True)

    def show_question(self, question_text, mode, data):
        """Fill the editor for a code-family question and return the prompt."""
        self.console_container.setVisible(mode in (BATCH, CSHARP))
        self.run_button.setVisible(mode == BATCH)

        if mode == BATCH:
            self.header.setText(f"  {tr('Batch')}   |   {tr('Command prompt')}")
            self.editor.auto_indent = False
            self.prefix.setText(tr("C:\\Users\\ExampleUser>"))
            self.suffix.clear()
            self.editor.setPlainText("")
            self.output.setPlainText(self._expected_output(data))
            prompt = question_text
        else:
            prompt, prefix, body, suffix = split_code_question(question_text)
            self.header.setText("  C#   |   Program.cs")
            self.editor.auto_indent = True
            self.prefix.setText(prefix)
            self.suffix.setText(suffix)
            self.console_title.setText(f"  {tr('CONSOLE')}   |   {tr('Expected output')}")
            if mode == CSHARP:
                # Match the eight-space method-body indentation of the solution.
                body = format_code_body(body) or "        "
                self.output.setPlainText(self._console_output(data))
            self.editor.setPlainText(body)

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.editor.setTextCursor(cursor)
        return prompt

    @staticmethod
    def _expected_output(data):
        if isinstance(data, dict):
            output = data.get("expected_output", [])
            if isinstance(output, list) and output:
                return "\n".join(str(line) for line in output)
            if isinstance(output, str) and output:
                return output
        return MISSING_BATCH_OUTPUT

    @staticmethod
    def _console_output(data):
        output = data.get("output", "") if isinstance(data, dict) else ""
        return str(output) if output else MISSING_BATCH_OUTPUT

    def value(self):
        return self.editor.toPlainText()

    def focus(self):
        self.editor.setFocus()


class TableAnswer(QWidget):
    """Editable calculation tables for questions with a table template."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(14)
        self.tables = []
        self.titles = []
        self.hide()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.tables = []
        self.titles = []

    def show_data(self, data):
        self.clear()
        tables = data.get("tables") if isinstance(data, dict) else None
        entries = tables if isinstance(tables, list) else [data]
        for entry in entries:
            self.titles.append(entry.get("title", ""))
            if entry.get("title"):
                heading = QLabel(entry["title"])
                heading.setWordWrap(True)
                heading.setProperty("role", "question")
                self.layout.addWidget(heading)
            table = QTableWidget()
            self._populate(table, entry)
            self.tables.append(table)
            self.layout.addWidget(table)

    def focus_first(self):
        if self.tables:
            self.tables[0].setFocus()

    def value(self):
        tables = [self._table_data(table) for table in self.tables]
        if len(tables) > 1:
            return json.dumps({
                "tables": [
                    {"title": title, **table}
                    for title, table in zip(self.titles, tables, strict=True)
                ]
            }, ensure_ascii=False)
        return json.dumps(tables[0], ensure_ascii=False)

    @staticmethod
    def _populate(table, data, show_answer=False):
        headers, rows = data["headers"], data["rows"]
        binary_layout = bool(headers and headers[0] == "__binary_layout__")
        table.setProperty("binary_layout", binary_layout)
        if binary_layout:
            headers = headers[1:]
            table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )
            for column in range(1, len(headers)):
                table.horizontalHeader().setSectionResizeMode(
                    column, QHeaderView.ResizeMode.Stretch
                )
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

    @staticmethod
    def _table_data(table):
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


class SolutionPanel(QFrame):
    """Reference solution: text, real tables, or a read-only flowchart."""

    def __init__(self):
        super().__init__()
        self.setProperty("role", "card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        self.title = QLabel(tr("Correct solution"))
        self.title.setProperty("role", "question")
        layout.addWidget(self.title)

        self.content = QPlainTextEdit()
        self.content.setReadOnly(True)
        self.content.setMinimumHeight(110)
        self.content.setMaximumHeight(300)
        self.content.setFont(code_font())
        self.content.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.highlighter = CSharpHighlighter(self.content.document())
        layout.addWidget(self.content)

        self.tables_container = QWidget()
        self.tables_layout = QVBoxLayout(self.tables_container)
        self.tables_layout.setContentsMargins(0, 0, 0, 0)
        self.tables_layout.setSpacing(12)
        self.tables = []
        self.tables_container.hide()
        layout.addWidget(self.tables_container)

        self.diagram = PapEditor()
        self.diagram.hide()
        layout.addWidget(self.diagram)
        self.hide()

    def reset(self):
        self.hide()
        self.content.clear()
        self._clear_tables()
        self.tables_container.hide()
        self.diagram.hide()
        self.diagram.reset()

    def _clear_tables(self):
        while self.tables_layout.count():
            item = self.tables_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.tables = []

    def show_text(self, text):
        self._clear_tables()
        self.tables_container.hide()
        self.diagram.hide()
        self.content.setPlainText(text)
        self.content.show()
        self.show()

    def show_tables(self, data):
        self.content.clear()
        self.content.hide()
        self.diagram.hide()
        self._clear_tables()
        tables = data.get("tables") if isinstance(data, dict) else None
        entries = tables if isinstance(tables, list) else [data]
        for entry in entries:
            if entry.get("title"):
                heading = QLabel(str(entry["title"]))
                heading.setWordWrap(True)
                heading.setProperty("role", "question")
                self.tables_layout.addWidget(heading)
            table = QTableWidget()
            TableAnswer._populate(table, entry, show_answer=True)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.tables.append(table)
            self.tables_layout.addWidget(table)
        self.tables_container.show()
        self.show()

    def show_diagram(self, data):
        """Show a read-only flowchart; returns False when it cannot load."""
        try:
            self.diagram.load_config(data or {}, show_solution=True)
            self.diagram.set_editing_enabled(False)
        except (AttributeError, TypeError, ValueError):
            self.show_text(tr("The flowchart solution could not be loaded."))
            return False
        self._clear_tables()
        self.tables_container.hide()
        self.content.hide()
        self.diagram.show()
        self.show()
        return True
