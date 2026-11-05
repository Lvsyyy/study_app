import json
import random

from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QListWidget, QWidget, QVBoxLayout, QGridLayout, QFrame, QApplication

from core.theme_manager import ThemeManager


class _SortCard(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setMinimumHeight(76)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setStyleSheet("border: 1px solid palette(mid); border-radius: 8px; padding: 12px; background: palette(base);")

    def mousePressEvent(self, event):
        self._start = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self._start).manhattanLength() < QApplication.startDragDistance():
            return
        from PySide6.QtGui import QDrag
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.text())
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)


class _SortDropZone(QFrame):
    dropped = Signal(str, str)

    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category = category
        self.setAcceptDrops(True)
        self.setMinimumHeight(110)
        self.setStyleSheet("QFrame { border: 2px dashed palette(mid); border-radius: 8px; }")
        self.label = QLabel("Hier ablegen")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.dropped.emit(event.mimeData().text(), self.category)
        event.acceptProposedAction()


class _TableSort(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.cards = list(data.get("cards", []))
        random.shuffle(self.cards)
        self.index = 0
        self.completed = False
        self.zones = {}
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        for column, category in enumerate(data.get("categories", [])):
            header = QLabel(str(category))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet("font-weight: 700; padding: 8px;")
            zone = _SortDropZone(str(category))
            zone.dropped.connect(self._drop)
            self.zones[str(category)] = zone
            grid.addWidget(header, 0, column)
            grid.addWidget(zone, 1, column)
        layout.addLayout(grid)
        self.feedback = QLabel()
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback)
        self.card_host = QWidget()
        self.card_layout = QVBoxLayout(self.card_host)
        self.card_layout.setContentsMargins(0, 8, 0, 0)
        layout.addWidget(self.card_host)
        self._show_card()

    def _show_card(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self.index >= len(self.cards):
            self.completed = True
            self.feedback.setText("Alle Karten richtig zugeordnet.")
            return
        self.card_layout.addWidget(_SortCard(str(self.cards[self.index].get("text", ""))))

    def _drop(self, text, category):
        if self.completed or self.index >= len(self.cards):
            return
        current = self.cards[self.index]
        if text != str(current.get("text", "")):
            return
        if category == str(current.get("category", "")):
            zone = self.zones[category]
            existing = zone.label.text()
            zone.label.setText(text if existing == "Hier ablegen" else existing + "\n" + text)
            self.feedback.setText("Richtig")
            self.index += 1
            self._show_card()
        else:
            self.feedback.setText("Falsch – versuche es erneut.")

    def get_answer(self):
        return json.dumps({"completed": self.completed, "placed": self.index}, ensure_ascii=False)

    def is_correct(self):
        return self.completed

    def reveal_solution(self):
        for category, zone in self.zones.items():
            assigned = [str(card.get("text", "")) for card in self.cards if str(card.get("category", "")) == category]
            zone.label.setText("\n".join(assigned) if assigned else "—")
        self.index = len(self.cards)
        self.completed = True
        self._show_card()


class InteractiveQuestion(QWidget):
    """Multi-select, drag ordering and term-to-definition matching."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.kind = None
        self.data = {}
        self.controls = []
        self.order_list = None
        self.match_options = []
        self.table_sort = None
        self.apply_theme("Rose Pine")

    def apply_theme(self, theme):
        p = ThemeManager.palette(theme)
        self.setStyleSheet(f"""
            QCheckBox {{
                background: {p['card']};
                color: {p['text']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                padding: 11px 12px;
                spacing: 10px;
            }}
            QCheckBox:hover {{ border-color: {p['accent']}; }}
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border: 1px solid {p['muted']};
                border-radius: 4px;
                background: {p['panel']};
            }}
            QCheckBox::indicator:checked {{
                background: {p['accent']};
                border-color: {p['accent']};
            }}
            QListWidget {{
                background: {p['panel']};
                alternate-background-color: {p['card']};
                color: {p['text']};
                border: 1px solid {p['border']};
                border-radius: 8px;
                padding: 6px;
                outline: 0;
            }}
            QListWidget::item {{
                background: {p['card']};
                border: 1px solid {p['border']};
                border-radius: 6px;
                padding: 10px;
                margin: 3px;
            }}
            QListWidget::item:selected {{
                background: {p['raised']};
                color: {p['text']};
                border-color: {p['accent']};
            }}
            QListWidget::item:hover {{ border-color: {p['accent']}; }}
            QComboBox {{
                background: {p['panel']};
                color: {p['text']};
                border: 1px solid {p['border']};
                border-radius: 7px;
                padding: 8px;
                min-height: 22px;
            }}
            QComboBox QAbstractItemView {{
                background: {p['panel']};
                color: {p['text']};
                selection-background-color: {p['raised']};
                selection-color: {p['text']};
                border: 1px solid {p['border']};
            }}
            QLabel {{ background: transparent; color: {p['text']}; }}
        """)

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.controls = []
        self.order_list = None
        self.match_options = []
        self.table_sort = None

    def load(self, kind, raw_answer):
        self._clear()
        self.kind = kind
        try:
            self.data = json.loads(raw_answer)
        except (TypeError, json.JSONDecodeError):
            self.data = {}

        if kind == "multi_select":
            for option in self.data.get("options", []):
                control = QCheckBox(str(option))
                self.controls.append(control)
                self.layout.addWidget(control)
        elif kind == "ordering":
            self.layout.addWidget(QLabel("Drag the items into the correct order:"))
            self.order_list = QListWidget()
            self.order_list.setAlternatingRowColors(True)
            values = list(self.data.get("items", []))
            item_count = len(values)
            self.order_list.setMinimumHeight(min(560, max(280, item_count * 58 + 20)))
            self.order_list.setMaximumHeight(560)
            self.order_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
            self.order_list.setDefaultDropAction(Qt.DropAction.MoveAction)
            self.order_list.setDragEnabled(True)
            self.order_list.setAcceptDrops(True)
            self.order_list.setDropIndicatorShown(True)
            random.shuffle(values)
            for value in values:
                self.order_list.addItem(str(value))
            self.layout.addWidget(self.order_list)
        elif kind == "table_sort":
            self.table_sort = _TableSort(self.data)
            self.layout.addWidget(self.table_sort)
        elif kind == "matching":
            definitions = [str(pair.get("right", "")) for pair in self.data.get("pairs", [])]
            shuffled = definitions[:]
            random.shuffle(shuffled)
            for pair in self.data.get("pairs", []):
                row = QWidget()
                row_layout = QVBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.addWidget(QLabel(str(pair.get("left", ""))))
                combo = QComboBox()
                combo.addItem("Select a definition…", None)
                for definition in shuffled:
                    combo.addItem(definition, definition)
                row_layout.addWidget(combo)
                self.match_options.append(combo)
                self.layout.addWidget(row)
        self.setEnabled(True)

    def set_answer_locked(self, locked):
        if self.kind == "ordering" and self.order_list:
            self.order_list.setDragEnabled(not locked)
            self.order_list.setDragDropMode(
                QListWidget.DragDropMode.NoDragDrop if locked
                else QListWidget.DragDropMode.InternalMove
            )
        if self.table_sort:
            self.table_sort.setEnabled(not locked)
        for control in self.controls:
            control.setEnabled(not locked)
        for combo in self.match_options:
            combo.setEnabled(not locked)

    def get_answer(self):
        if self.kind == "multi_select":
            return json.dumps([i for i, control in enumerate(self.controls) if control.isChecked()])
        if self.kind == "ordering" and self.order_list:
            return json.dumps([self.order_list.item(i).text() for i in range(self.order_list.count())], ensure_ascii=False)
        if self.kind == "matching":
            return json.dumps([combo.currentData() for combo in self.match_options], ensure_ascii=False)
        if self.kind == "table_sort" and self.table_sort:
            return self.table_sort.get_answer()
        return ""

    def is_correct(self):
        try:
            entered = json.loads(self.get_answer())
        except json.JSONDecodeError:
            return False
        if self.kind == "multi_select":
            return sorted(entered) == sorted(self.data.get("correct", []))
        if self.kind == "ordering":
            return entered == self.data.get("items", [])
        if self.kind == "matching":
            return entered == [pair.get("right") for pair in self.data.get("pairs", [])]
        if self.kind == "table_sort" and self.table_sort:
            return self.table_sort.is_correct()
        return False

    def reveal_solution(self):
        if self.kind == "multi_select":
            correct = set(self.data.get("correct", []))
            for index, control in enumerate(self.controls):
                control.setChecked(index in correct)
        elif self.kind == "ordering" and self.order_list:
            self.order_list.clear()
            for value in self.data.get("items", []):
                self.order_list.addItem(str(value))
        elif self.kind == "table_sort" and self.table_sort:
            self.table_sort.reveal_solution()
        elif self.kind == "matching":
            for combo, pair in zip(self.match_options, self.data.get("pairs", [])):
                index = combo.findData(pair.get("right"))
                if index >= 0:
                    combo.setCurrentIndex(index)
