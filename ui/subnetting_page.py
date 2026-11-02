import ipaddress
import random

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPalette
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QScrollArea, QTableWidget,
    QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget
)

from ui.widgets import action_button, card, muted_label, title_label


class SubnetCanvas(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 500)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)
        self.setStyleSheet("background: transparent;")
        self.rooms = []
        self.inputs = {}
        self.selected_id = None
        self.next_id = 0
        self.reset_exercise()

    def reset_exercise(self):
        self.initial_rooms = 4
        self.extra_splits = random.randint(2, 4)
        room_depth = 2
        self.prefix = random.randint(10, 30 - room_depth - self.extra_splits)
        block_size = 1 << (32 - self.prefix)
        base_network = int(ipaddress.IPv4Address("10.0.0.0"))
        base = base_network + random.randrange(1 << (self.prefix - 8)) * block_size
        self.network = base
        self.broadcast = base + block_size - 1
        self.ip = random.randint(base + 1, self.broadcast - 1)
        self.extra_splits_done = 0
        self.selected_id = None
        self.next_id = 0
        for pair in self.inputs.values():
            for edit in pair:
                edit.deleteLater()
        self.inputs.clear()
        self.rooms = []
        room_size = block_size // self.initial_rooms
        for row in range(2):
            for column in range(2):
                index = row * 2 + column
                self.rooms.append({
                    "id": self.next_id, "x": column / 2, "y": row / 2,
                    "w": 0.5, "h": 0.5,
                    "network": base + index * room_size, "prefix": self.prefix + room_depth,
                })
                self.next_id += 1
        self.allowed_extra_ids = {room["id"] for room in self.rooms}
        for room in self.rooms:
            self._create_inputs(room)
        self.update()

    @property
    def phase(self):
        return "extra" if self.extra_splits_done < self.extra_splits else "done"

    def _create_inputs(self, room):
        network = QLineEdit(self)
        broadcast = QLineEdit(self)
        network.setPlaceholderText("Netzwerkadresse")
        broadcast.setPlaceholderText("Broadcastadresse")
        network.setAlignment(Qt.AlignmentFlag.AlignLeft)
        broadcast.setAlignment(Qt.AlignmentFlag.AlignRight)
        for edit in (network, broadcast):
            edit.setMaxLength(15)
            edit.setToolTip("IPv4-Adresse eingeben")
            edit.setProperty("answerState", "")
            edit.setFrame(False)
            edit.setStyleSheet(
                "QLineEdit { background: transparent; border: none; padding: 0px; }"
                "QLineEdit:focus { background: rgba(0, 0, 0, 35); border: 1px solid palette(highlight); }"
            )
        self.inputs[room["id"]] = (network, broadcast)
        self._position_inputs(room)

    def _bounds(self):
        side = max(300, min(self.width() - 64, self.height() - 64))
        return QRectF((self.width() - side) / 2, (self.height() - side) / 2, side, side)

    def _room_rect(self, room):
        bounds = self._bounds()
        return QRectF(
            bounds.x() + room["x"] * bounds.width(),
            bounds.y() + room["y"] * bounds.height(),
            room["w"] * bounds.width(),
            room["h"] * bounds.height(),
        )

    def _position_inputs(self, room):
        pair = self.inputs.get(room["id"])
        if not pair:
            return
        rect = self._room_rect(room).toRect()
        width = max(24, int(rect.width() * 0.44))
        height = min(20, max(15, int(rect.height() * 0.22)))
        pair[0].setGeometry(rect.left() + 4, rect.top() + 4, width, height)
        pair[1].setGeometry(rect.right() - width - 4, rect.bottom() - height - 4, width, height)
        font = QFont()
        font.setPointSize(6 if rect.width() < 110 or rect.height() < 110 else 8)
        for edit in pair:
            edit.setFont(font)
            edit.setVisible(True)

    def _edge_points(self, room):
        rect = self._room_rect(room)
        return [
            (QPointF(rect.center().x(), rect.top()), "top"),
            (QPointF(rect.right(), rect.center().y()), "right"),
            (QPointF(rect.center().x(), rect.bottom()), "bottom"),
            (QPointF(rect.left(), rect.center().y()), "left"),
        ]

    @staticmethod
    def _ip(value):
        return str(ipaddress.IPv4Address(value))

    @staticmethod
    def _mask(prefix):
        return str(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)

    def _split(self, room, edge):
        if room["prefix"] >= 29:
            return
        half_size = 1 << (31 - room["prefix"])
        first = dict(room)
        second = dict(room)
        first["id"] = self.next_id
        self.next_id += 1
        second["id"] = self.next_id
        self.next_id += 1
        first["prefix"] += 1
        second["prefix"] += 1
        second["network"] += half_size
        if edge in ("top", "bottom"):
            first["w"] /= 2
            second["x"] += first["w"]
            second["w"] /= 2
        else:
            first["h"] /= 2
            second["y"] += first["h"]
            second["h"] /= 2

        self.rooms.remove(room)
        for edit in self.inputs.pop(room["id"], ()):
            edit.deleteLater()
        self.rooms.extend((first, second))
        self._create_inputs(first)
        self._create_inputs(second)
        self.extra_splits_done += 1
        self.allowed_extra_ids = {first["id"], second["id"]}
        self.selected_id = None
        self.update()
        self.changed.emit()

    def check_answers(self):
        incorrect = []
        for room in self.rooms:
            network_edit, broadcast_edit = self.inputs[room["id"]]
            expected_network = self._ip(room["network"])
            expected_broadcast = self._ip(room["network"] + (1 << (32 - room["prefix"])) - 1)
            try:
                given_network = str(ipaddress.IPv4Address(network_edit.text().strip()))
            except ipaddress.AddressValueError:
                given_network = ""
            try:
                given_broadcast = str(ipaddress.IPv4Address(broadcast_edit.text().strip()))
            except ipaddress.AddressValueError:
                given_broadcast = ""
            if given_network != expected_network or given_broadcast != expected_broadcast:
                incorrect.append(room["id"])
        for room in self.rooms:
            for edit in self.inputs[room["id"]]:
                edit.setProperty("answerState", "wrong" if room["id"] in incorrect else "correct")
                edit.style().unpolish(edit)
                edit.style().polish(edit)
        return not incorrect

    def reveal_answers(self):
        for room in self.rooms:
            network_edit, broadcast_edit = self.inputs[room["id"]]
            network_edit.setText(self._ip(room["network"]))
            broadcast_edit.setText(
                self._ip(room["network"] + (1 << (32 - room["prefix"])) - 1)
            )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self.phase == "done":
            return
        point = event.position()
        if self.phase == "extra" and self.selected_id is None:
            if not self.allowed_extra_ids:
                self.allowed_extra_ids = {room["id"] for room in self.rooms}
            for room in self.rooms:
                if room["id"] in self.allowed_extra_ids and self._room_rect(room).contains(point):
                    self.selected_id = room["id"]
                    self.update()
                    return
        for room in self.rooms:
            if self.phase == "extra" and room["id"] != self.selected_id:
                continue
            for edge_point, edge in self._edge_points(room):
                if (point - edge_point).manhattanLength() <= 17:
                    self._split(room, edge)
                    return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for room in self.rooms:
            self._position_inputs(room)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        background = palette.color(QPalette.ColorRole.Window)
        bounds = self._bounds()
        accent = palette.color(QPalette.ColorRole.Highlight)
        border = accent
        painter.setPen(QPen(accent, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(bounds)
        for room in self.rooms:
            rect = self._room_rect(room)
            selected = room["id"] == self.selected_id
            painter.setPen(QPen(accent if selected else border, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
            if selected:
                painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 24))
                painter.drawRect(rect)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            if self.phase == "base" or (self.phase == "extra" and selected):
                for edge_point, _edge in self._edge_points(room):
                    painter.setPen(QPen(background, 1))
                    painter.setBrush(QBrush(accent))
                    painter.drawEllipse(edge_point, 7, 7)
        painter.end()


class SubnettingPage(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(18)
        self.scroll_area.setWidget(content)
        outer.addWidget(self.scroll_area)

        header = QHBoxLayout()
        back = action_button("←  Back")
        back.clicked.connect(self.back_requested)
        header.addWidget(back)
        header.addStretch()
        root.addLayout(header)
        root.addWidget(title_label("Subnetting"))
        self.instructions = muted_label("")
        self.instructions.setWordWrap(True)
        root.addWidget(self.instructions)

        frame, table_layout = card(padding=12)
        self.info_table = QTableWidget(4, 3)
        self.info_table.setHorizontalHeaderLabels(["", "Decimal", "Binary"])
        self.info_table.verticalHeader().setVisible(False)
        self.info_table.setAlternatingRowColors(True)
        self.info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.info_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.info_table.verticalHeader().setDefaultSectionSize(42)
        self.info_table.setMinimumHeight(212)
        self.info_table.setStyleSheet(
            "QTableWidget QLineEdit { background: transparent; "
            "border: 1px solid palette(highlight); padding: 2px; }"
        )
        self.info_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
        self.info_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
        self.info_table.setWordWrap(False)
        table_layout.addWidget(self.info_table)
        root.addWidget(frame)

        canvas_frame, canvas_layout = card(padding=12)
        self.canvas = SubnetCanvas()
        canvas_layout.addWidget(self.canvas)
        root.addWidget(canvas_frame)

        self.feedback = muted_label("")
        root.addWidget(self.feedback)

        buttons = QHBoxLayout()
        self.skip_button = action_button("Skip")
        self.hint_button = action_button("Hint")
        self.reveal_button = action_button("Show answer")
        self.save_button = action_button("☆  Save")
        self.primary_button = action_button("Check answer", primary=True)
        self.skip_button.clicked.connect(self.new_exercise)
        self.hint_button.clicked.connect(self.show_hint)
        self.reveal_button.clicked.connect(self.reveal_answer)
        self.save_button.clicked.connect(self.toggle_saved)
        self.primary_button.clicked.connect(self.check_answers)
        for button in (self.skip_button, self.hint_button, self.reveal_button, self.save_button):
            buttons.addWidget(button)
        buttons.addStretch()
        buttons.addWidget(self.primary_button)
        root.addLayout(buttons)
        root.addStretch()
        self._saved = False

        self.canvas.changed.connect(self.refresh_text)
        self.refresh_text()

    def toggle_saved(self):
        self._saved = not self._saved
        self.save_button.setText("★  Saved" if self._saved else "☆  Save")

    def new_exercise(self):
        self.canvas.reset_exercise()
        self._saved = False
        self.save_button.setText("☆  Save")
        self.feedback.setText("")
        self.info_table.clearContents()
        self.refresh_text()

    def show_hint(self):
        self.feedback.setText("Tipp: Berechne zuerst die Netzwerkadresse mit der IP-Adresse und Subnetzmaske. Jede Teilung erhöht den Präfix um 1.")

    @staticmethod
    def _binary_ip(value):
        return ".".join(f"{int(part):08b}" for part in value.split("."))

    def reveal_answer(self):
        self.canvas.reveal_answers()
        ip_value = self.canvas._ip(self.canvas.ip)
        mask_value = self.canvas._mask(self.canvas.prefix)
        network_value = self.canvas._ip(self.canvas.network)
        broadcast_value = self.canvas._ip(self.canvas.broadcast)
        values = {
            0: (f"{ip_value}/{self.canvas.prefix}", self._binary_ip(ip_value)),
            1: (mask_value, self._binary_ip(mask_value)),
            2: (network_value, self._binary_ip(network_value)),
            3: (broadcast_value, self._binary_ip(broadcast_value)),
        }
        for row, (decimal_value, binary_value) in values.items():
            self.info_table.item(row, 1).setText(decimal_value)
            self.info_table.item(row, 2).setText(binary_value)
        self.feedback.setText("Lösungen wurden eingetragen.")

    def check_answers(self):
        if self.canvas.phase != "done":
            self.feedback.setText("Schließe zuerst die Aufteilung ab.")
            return
        expected = (self.canvas._ip(self.canvas.network), self.canvas._ip(self.canvas.broadcast))
        table_ok = True
        for row, decimal_value in zip((2, 3), expected):
            binary_value = ".".join(f"{int(part):08b}" for part in decimal_value.split("."))
            decimal_item = self.info_table.item(row, 1)
            binary_item = self.info_table.item(row, 2)
            decimal_ok = bool(decimal_item and decimal_item.text().strip() == decimal_value)
            binary_ok = bool(binary_item and binary_item.text().strip() == binary_value)
            for item, correct in ((decimal_item, decimal_ok), (binary_item, binary_ok)):
                if item:
                    item.setBackground(self.palette().color(
                        QPalette.ColorRole.AlternateBase if correct else QPalette.ColorRole.Base
                    ))
            table_ok = table_ok and decimal_ok and binary_ok

        rooms_ok = self.canvas.check_answers()
        if table_ok and rooms_ok:
            self.feedback.setText("Alle Netzwerk- und Broadcastadressen sind korrekt.")
        else:
            self.feedback.setText("Einige Adressen sind falsch oder fehlen. Prüfe die markierten Felder.")

    def refresh_text(self):
        canvas = self.canvas
        if canvas.phase == "extra":
            detail = (
                f"Wähle einen der vorgeteilten Räume und teile ihn weiter. "
                f"Noch {canvas.extra_splits - canvas.extra_splits_done} Teilung(en)."
                if canvas.selected_id is None else
                f"Teile den markierten Raum. Noch {canvas.extra_splits - canvas.extra_splits_done} Teilung(en)."
            )
            self.instructions.setText(f"Berechne und beschrifte das Netzwerk. {detail}")
        else:
            self.instructions.setText(
                "Berechne und beschrifte das Netzwerk. Trage die Netzwerk- und "
                "Broadcastadressen aller Teilnetze in die Felder im Quadrat ein."
            )

        ip_item = QTableWidgetItem(f"{canvas._ip(canvas.ip)}/{canvas.prefix}")
        ip_item.setFlags(ip_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        ip_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_table.setItem(0, 1, ip_item)
        for row, label in enumerate(("IP Adresse", "Subnetzmaske", "Netzwerkadresse", "Broadcastadresse")):
            label_item = QTableWidgetItem(label)
            label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            label_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_table.setItem(row, 0, label_item)
        for row in (0, 1, 2, 3):
            for column in (1, 2):
                if row == 0 and column == 1:
                    continue
                item = self.info_table.item(row, column)
                if item is None or row in (0, 1):
                    item = QTableWidgetItem("")
                    self.info_table.setItem(row, column, item)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
