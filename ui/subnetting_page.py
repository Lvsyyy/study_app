import ipaddress
import random

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)

from ui.widgets import action_button, card, muted_label, title_label


class SubnetCanvas(QWidget):
    """Interactive CIDR split diagram. Each edge control splits only its own room."""

    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 500)
        self.setMouseTracking(True)
        self.rooms = []
        self.selected_id = None
        self.next_id = 0
        self.base_splits_done = 0
        self.extra_splits_done = 0
        self.reset_exercise()

    def reset_exercise(self):
        prefix = random.randint(21, 23)
        block_size = 1 << (32 - prefix)
        base = random.randint(1, 254) * 256
        base = (base // block_size) * block_size
        self.network = base
        self.prefix = prefix
        self.broadcast = base + block_size - 1
        self.ip = random.randint(base + 1, self.broadcast - 1)
        self.initial_rooms = random.randint(2, 4)
        self.extra_splits = random.randint(2, 4)
        self.base_splits_done = 0
        self.extra_splits_done = 0
        self.selected_id = None
        self.allowed_extra_ids = set()
        self.next_id = 1
        self.rooms = [{
            "id": 0, "x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0,
            "network": base, "prefix": prefix,
        }]
        self.update()

    @property
    def phase(self):
        if self.base_splits_done < self.initial_rooms - 1:
            return "base"
        if self.extra_splits_done < self.extra_splits:
            return "extra"
        return "done"

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
        if room["prefix"] >= 30:
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

        was_extra = self.phase == "extra"
        self.rooms.remove(room)
        self.rooms.extend((first, second))
        if was_extra:
            self.extra_splits_done += 1
            self.allowed_extra_ids = {first["id"], second["id"]}
            self.selected_id = None
        else:
            self.base_splits_done += 1
        self.update()
        self.changed.emit()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        point = event.position()
        if self.phase == "done":
            return

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

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self.palette().window())
        bounds = self._bounds()

        painter.setPen(QPen(QColor("#a00088"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(bounds)

        for room in self.rooms:
            rect = self._room_rect(room)
            selected = room["id"] == self.selected_id
            painter.setPen(QPen(QColor("#a00088") if not selected else QColor("#1685d5"), 2))
            if selected:
                painter.setBrush(QColor(22, 133, 213, 28))
                painter.drawRect(rect)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(self.palette().text().color()))
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            broadcast = room["network"] + (1 << (32 - room["prefix"])) - 1
            painter.drawText(rect.adjusted(5, 4, -5, -4), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                             f"{self._ip(room['network'])}/{room['prefix']}")
            painter.drawText(rect.adjusted(5, 4, -5, -4), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                             self._ip(broadcast))

            if self.phase == "base" or (self.phase == "extra" and room["id"] == self.selected_id):
                for edge_point, _edge in self._edge_points(room):
                    painter.setPen(QPen(QColor("#ffffff"), 1))
                    painter.setBrush(QBrush(QColor("#a00088")))
                    painter.drawEllipse(edge_point, 7, 7)

        painter.end()


class SubnettingPage(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 30, 34, 30)
        root.setSpacing(14)

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

        self.network_info = QLabel()
        self.network_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(self.network_info)

        frame, layout = card(padding=12)
        self.canvas = SubnetCanvas()
        layout.addWidget(self.canvas)
        root.addWidget(frame, 1)

        controls = QHBoxLayout()
        self.reset_button = action_button("New exercise")
        self.reset_button.clicked.connect(self.new_exercise)
        controls.addWidget(self.reset_button)
        controls.addStretch()
        root.addLayout(controls)
        self.canvas.changed.connect(self.refresh_text)
        self.refresh_text()

    def new_exercise(self):
        self.canvas.reset_exercise()
        self.refresh_text()

    def refresh_text(self):
        canvas = self.canvas
        ip = canvas._ip(canvas.ip)
        mask = canvas._mask(canvas.prefix)
        binary_ip = ".".join(f"{int(part):08b}" for part in ip.split("."))
        binary_mask = ".".join(f"{int(part):08b}" for part in mask.split("."))
        self.network_info.setText(
            f"<b>IP-Adresse:</b> {ip} &nbsp; <b>Subnetzmaske:</b> {mask} "
            f"(/ {canvas.prefix})<br>"
            f"<span style='font-family:monospace'>{binary_ip}<br>{binary_mask}</span><br>"
            f"<b>Netzwerk:</b> {canvas._ip(canvas.network)} "
            f"&nbsp; <b>Broadcast:</b> {canvas._ip(canvas.broadcast)}"
        )
        if canvas.phase == "base":
            remaining = canvas.initial_rooms - 1 - canvas.base_splits_done
            self.instructions.setText(
                f"Teile das Netzwerk in {canvas.initial_rooms} Räume auf. "
                f"Noch {remaining} Teilung(en). Klicke auf einen Randpunkt des Raums, "
                "den du teilen möchtest."
            )
        elif canvas.phase == "extra":
            if canvas.selected_id is None:
                self.instructions.setText(
                    f"Wähle einen Raum aus und unterteile diesen Zweig anschließend "
                    f"noch {canvas.extra_splits - canvas.extra_splits_done} Mal."
                )
            else:
                self.instructions.setText(
                    f"Teile den markierten Raum. Noch "
                    f"{canvas.extra_splits - canvas.extra_splits_done} weitere Teilung(en)."
                )
        else:
            self.instructions.setText(
                f"Aufteilung abgeschlossen: {len(canvas.rooms)} Subnetze."
            )
