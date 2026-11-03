import json

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QComboBox, QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem,
    QGraphicsObject, QGraphicsScene, QGraphicsTextItem, QGraphicsView,
    QHBoxLayout, QInputDialog, QLabel, QPushButton, QVBoxLayout, QWidget,
)


class ConnectionPort(QGraphicsEllipseItem):
    def __init__(self, node, output):
        super().__init__(-6, -6, 12, 12, node)
        self.node = node
        self.output = output
        self.setBrush(QBrush(QColor("#54a6e8")))
        self.setPen(QPen(QColor("#dceeff"), 1.5))
        self.setZValue(5)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setVisible(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.node.editor.handle_port_click(self.node.node_id, self.output)
            event.accept()
            return
        super().mousePressEvent(event)


class FlowNode(QGraphicsObject):
    WIDTH = 190
    HEIGHT = 76

    def __init__(self, editor, data):
        super().__init__()
        self.editor = editor
        self.node_id = data["id"]
        self.kind = data.get("type", "Process")
        self.label = data.get("text", "")
        self.setPos(float(data.get("x", 0)), float(data.get("y", 0)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setZValue(2)
        self.input_port = ConnectionPort(self, False)
        self.output_port = ConnectionPort(self, True)
        self.input_port.setPos(0, self.HEIGHT / 2)
        self.output_port.setPos(self.WIDTH, self.HEIGHT / 2)

    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.HEIGHT)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#70b7f0") if self.isSelected() else QColor("#718096"), 2))
        painter.setBrush(QBrush(QColor("#263449")))
        rect = self.boundingRect().adjusted(1, 1, -1, -1)
        if self.kind == "Start/End":
            painter.drawRoundedRect(rect, 25, 25)
        elif self.kind == "Decision":
            path = QPainterPath()
            path.moveTo(self.WIDTH / 2, 1)
            path.lineTo(self.WIDTH - 1, self.HEIGHT / 2)
            path.lineTo(self.WIDTH / 2, self.HEIGHT - 1)
            path.lineTo(1, self.HEIGHT / 2)
            path.closeSubpath()
            painter.drawPath(path)
        else:
            painter.drawRoundedRect(rect, 8, 8)
        painter.setPen(QColor("#f1f5f9"))
        painter.drawText(
            rect.adjusted(18, 10, -18, -10),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.label,
        )

    def hoverEnterEvent(self, event):
        self.input_port.setVisible(True)
        self.output_port.setVisible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.input_port.setVisible(False)
        self.output_port.setVisible(False)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.editor.update_connections()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getText(
            self.editor, "PAP-Block bearbeiten", "Blocktext:", text=self.label
        )
        if ok and text.strip():
            self.label = text.strip()
            self.update()
            self.editor.sync_node(self.node_id)
        super().mouseDoubleClickEvent(event)


class PapView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setSceneRect(-100000, -100000, 200000, 200000)
        self.setMinimumHeight(440)
        self.setStyleSheet(
            "QGraphicsView { background: #141c29; border: 1px solid #465366; border-radius: 8px; }"
        )
        self._zoom = 1.0
        self._panning = False
        self._pan_pos = None

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        target = max(0.25, min(2.5, self._zoom * factor))
        self.scale(target / self._zoom, target / self._zoom)
        self._zoom = target

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._panning = True
            self._pan_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            current = event.position().toPoint()
            delta = current - self._pan_pos
            self._pan_pos = current
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning and event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self._panning = False
            self._pan_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class PapEditor(QWidget):
    TYPES = ("Start/End", "Process", "Decision")
    GRID = 24

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self.edges = []
        self._next_id = 1
        self._connect_source = None
        self._graphics_nodes = {}
        self._graphics_edges = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)
        tools = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(self.TYPES)
        tools.addWidget(self.type_box)
        add = QPushButton("Block hinzufügen")
        add.clicked.connect(self.add_node)
        tools.addWidget(add)
        self.edge_label = QComboBox()
        self.edge_label.addItems(["Normal", "Ja", "Nein"])
        tools.addWidget(self.edge_label)
        delete = QPushButton("Ausgewählten Block löschen")
        delete.clicked.connect(self.delete_selected)
        tools.addWidget(delete)
        tools.addStretch()
        root.addLayout(tools)
        self.status = QLabel(
            "Blöcke ziehen · Mausrad: Zoom · Mittlere/rechte Maustaste: Arbeitsfläche bewegen · Kreise anklicken: verbinden"
        )
        root.addWidget(self.status)
        self.scene = QGraphicsScene(self)
        self.view = PapView(self.scene, self)
        root.addWidget(self.view, 1)
        self.setStyleSheet("QPushButton, QComboBox { padding: 6px 9px; }")

    def _ensure_positions(self):
        for i, node in enumerate(self.nodes):
            node.setdefault("x", (i % 4) * 250)
            node.setdefault("y", (i // 4) * 150)

    def load_config(self, config):
        self.nodes = [dict(n) for n in config.get("nodes", [])]
        self.edges = [dict(e) for e in config.get("edges", [])]
        self._next_id = max([n["id"] for n in self.nodes] + [0]) + 1
        self._connect_source = None
        self._ensure_positions()
        self.refresh()

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self._next_id = 1
        self._connect_source = None
        self.refresh()

    def add_node(self):
        text, ok = QInputDialog.getText(self, "PAP-Block hinzufügen", "Blocktext:")
        if not ok or not text.strip():
            return
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.nodes.append({
            "id": self._next_id,
            "type": self.type_box.currentText(),
            "text": text.strip(),
            "x": round(center.x() / self.GRID) * self.GRID,
            "y": round(center.y() / self.GRID) * self.GRID,
        })
        self._next_id += 1
        self.refresh()
        self._graphics_nodes[self._next_id - 1].setSelected(True)

    def sync_node(self, node_id):
        item = self._graphics_nodes.get(node_id)
        data = next((n for n in self.nodes if n["id"] == node_id), None)
        if item and data:
            data["text"] = item.label

    def update_connections(self):
        for edge in self.edges:
            key = (edge["from"], edge["to"], edge.get("label", "Normal"))
            line = self._graphics_edges.get(key)
            source = self._graphics_nodes.get(edge["from"])
            target = self._graphics_nodes.get(edge["to"])
            if line and source and target:
                a = source.mapToScene(QPointF(source.WIDTH, source.HEIGHT / 2))
                b = target.mapToScene(QPointF(0, target.HEIGHT / 2))
                line.setLine(a.x(), a.y(), b.x(), b.y())
                label = self._graphics_edges.get(("label",) + key)
                if label:
                    label.setPos((a.x() + b.x()) / 2, (a.y() + b.y()) / 2 - 20)

    def handle_port_click(self, node_id, output):
        if output:
            self._connect_source = node_id
            self.status.setText("Jetzt den Eingabekreis des Zielblocks anklicken.")
            return
        if self._connect_source is None:
            self.status.setText("Zuerst den Ausgabekreis des Startblocks anklicken.")
            return
        source = self._connect_source
        self._connect_source = None
        if source == node_id:
            self.status.setText("Ein Block kann nicht mit sich selbst verbunden werden.")
            return
        label = self.edge_label.currentText()
        self.edges = [
            e for e in self.edges
            if not (e["from"] == source and e.get("label", "Normal") == label)
        ]
        self.edges.append({"from": source, "to": node_id, "label": label})
        self.refresh()
        self.status.setText("Verbindung erstellt.")

    def delete_selected(self):
        selected = next((n for n in self._graphics_nodes.values() if n.isSelected()), None)
        if selected is None:
            return
        node_id = selected.node_id
        self.nodes = [n for n in self.nodes if n["id"] != node_id]
        self.edges = [e for e in self.edges if e["from"] != node_id and e["to"] != node_id]
        self._connect_source = None
        self.refresh()

    def refresh(self):
        self.scene.clear()
        self._graphics_nodes.clear()
        self._graphics_edges.clear()
        for node in self.nodes:
            item = FlowNode(self, node)
            self.scene.addItem(item)
            self._graphics_nodes[node["id"]] = item
        for edge in self.edges:
            source = self._graphics_nodes.get(edge["from"])
            target = self._graphics_nodes.get(edge["to"])
            if not source or not target:
                continue
            key = (edge["from"], edge["to"], edge.get("label", "Normal"))
            line = QGraphicsLineItem()
            line.setPen(QPen(QColor("#9bb8d4"), 2))
            line.setZValue(1)
            self.scene.addItem(line)
            self._graphics_edges[key] = line
            label = QGraphicsTextItem(edge.get("label", "Normal"))
            label.setDefaultTextColor(QColor("#e6edf5"))
            label.setZValue(3)
            self.scene.addItem(label)
            self._graphics_edges[("label",) + key] = label
        self.update_connections()

    def get_answer(self):
        for node in self.nodes:
            item = self._graphics_nodes.get(node["id"])
            if item:
                node["x"] = round(item.pos().x() / self.GRID) * self.GRID
                node["y"] = round(item.pos().y() / self.GRID) * self.GRID
                node["text"] = item.label
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, ensure_ascii=False)

    def is_correct(self, expected):
        try:
            actual = json.loads(self.get_answer())
            wanted = json.loads(expected) if isinstance(expected, str) else expected
            normalize = lambda nodes: sorted(
                (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                for n in nodes
            )
            actual_ids = {
                n["id"]: (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                for n in actual["nodes"]
            }
            expected_ids = {
                n["id"]: (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                for n in wanted["nodes"]
            }
            actual_edges = sorted(
                (actual_ids[e["from"]], actual_ids[e["to"]], e.get("label", "Normal").casefold())
                for e in actual["edges"]
                if e["from"] in actual_ids and e["to"] in actual_ids
            )
            expected_edges = sorted(
                (expected_ids[e["from"]], expected_ids[e["to"]], e.get("label", "Normal").casefold())
                for e in wanted["edges"]
            )
            return normalize(actual["nodes"]) == normalize(wanted["nodes"]) and actual_edges == expected_edges
        except (KeyError, TypeError, ValueError):
            return False
