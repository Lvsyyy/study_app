import json
import random

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsObject,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.i18n import tr


def _node_key(node):
    """Node identity for grading: type plus normalized text, ignoring position."""
    return (
        str(node.get("type", "")).casefold(),
        " ".join(str(node.get("text", "")).casefold().split()),
    )


def _edge_key(edge, nodes):
    return (
        nodes.get(edge.get("from")),
        nodes.get(edge.get("to")),
        str(edge.get("label", "Normal")).casefold(),
    )


class ConnectionPort(QGraphicsEllipseItem):
    def __init__(self, node, side):
        super().__init__(-6, -6, 12, 12, node)
        self.node = node
        self.side = side
        self.setBrush(QBrush(QColor("#54a6e8")))
        self.setPen(QPen(QColor("#dceeff"), 1.5))
        self.setZValue(5)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setVisible(False)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.node.editor.begin_connection(self.node.node_id, self.side, self.scenePos())
            event.accept()

    def mouseMoveEvent(self, event):
        self.node.editor.move_connection(event.scenePos())
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.node.editor.finish_connection(event.scenePos())
            event.accept()


class ConnectionLine(QGraphicsLineItem):
    def __init__(self, editor, edge, key):
        super().__init__()
        self.editor, self.edge, self.key = editor, edge, key
        self.setPen(QPen(QColor("#9bb8d4"), 2))
        self.setZValue(1)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseDoubleClickEvent(self, event):
        choices = ["Normal", "Ja", "Nein"]
        current = self.edge.get("label", "Normal")
        selected, ok = QInputDialog.getItem(
            self.editor, tr("Edit connection"), tr("Line type:"), choices,
            choices.index(current) if current in choices else 0, False,
        )
        if ok:
            self.edge["label"] = selected
            self.editor.refresh()
        event.accept()

class FlowNode(QGraphicsObject):
    WIDTH = 190
    HEIGHT = 76

    def __init__(self, editor, data):
        super().__init__()
        self.editor = editor
        self.node_id = data["id"]
        self.data = data
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
        self.ports = {}
        positions = {
            "left": QPointF(0, self.HEIGHT / 2),
            "right": QPointF(self.WIDTH, self.HEIGHT / 2),
            "top": QPointF(self.WIDTH / 2, 0),
            "bottom": QPointF(self.WIDTH / 2, self.HEIGHT),
        }
        for side, pos in positions.items():
            port = ConnectionPort(self, side)
            port.setPos(pos)
            self.ports[side] = port

    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.HEIGHT)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#70b7f0") if self.isSelected() else QColor("#718096"), 2))
        painter.setBrush(QBrush(QColor("#263449")))
        rect = self.boundingRect().adjusted(1, 1, -1, -1)
        if self.editor.is_endpoint_node(self.node_id):
            painter.drawRoundedRect(rect, 38, 38)
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
        for port in self.ports.values():
            port.setVisible(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        for port in self.ports.values():
            port.setVisible(False)
        super().hoverLeaveEvent(event)

    def port_scene_pos(self, side):
        return self.mapToScene(self.ports[side].pos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            grid = self.editor.GRID
            return QPointF(round(value.x() / grid) * grid, round(value.y() / grid) * grid)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.data["x"], self.data["y"] = value.x(), value.y()
            self.editor.update_connections()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getText(
            self.editor, tr("Edit flowchart block"), tr("Block text:"), text=self.label
        )
        if ok and text.strip():
            self.label = text.strip()
            self.update()
            self.editor.sync_node(self.node_id)
        super().mouseDoubleClickEvent(event)


class PapView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setSceneRect(-1200, -800, 2400, 1600)
        self.setMinimumHeight(300)
        self.setMaximumHeight(390)
        self.setStyleSheet(
            "QGraphicsView { background: #141c29; border: 1px solid #465366; border-radius: 8px; }"
        )
        self._zoom = 1.0
        self._panning = False
        self._pan_pos = None

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        target = max(0.3, min(2.2, self._zoom * factor))
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
        self._graphics_nodes = {}
        self._graphics_edges = {}
        self._preview_line = None
        self._connection_source = None
        self._editing_enabled = True

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)
        tools = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(self.TYPES)
        self.add_button = None
        self.delete_button = None
        tools.addWidget(self.type_box)
        add = QPushButton(tr("Add block"))
        add.clicked.connect(self.add_node)
        tools.addWidget(add)
        delete = QPushButton(tr("Delete selected block"))
        delete.clicked.connect(self.delete_selected)
        tools.addWidget(delete)
        self.add_button = add
        self.delete_button = delete
        tools.addStretch()
        root.addLayout(tools)
        self.status = QLabel(
            tr(
                "Drag blocks · Mouse wheel: zoom · Middle/right mouse button: move "
                "canvas · Connection: drag a circle"
            )
        )
        root.addWidget(self.status)
        self.scene = QGraphicsScene(self)
        self.view = PapView(self.scene, self)
        root.addWidget(self.view, 1)
        self.setStyleSheet("QPushButton, QComboBox { padding: 6px 9px; }")

    def _scatter_positions(self, count):
        # Keep the exercise in a compact, consistent grid while shuffling
        # positions on every load. Slot spacing exceeds the block dimensions.
        columns = 4
        rows = (count + columns - 1) // columns
        slots = [
            (x * 240, y * 132)
            for y in range(rows)
            for x in range(columns)
        ]
        random.shuffle(slots)
        # Center the complete grid around the canvas origin.
        x_offset = ((columns - 1) * 240 + FlowNode.WIDTH) / 2
        y_offset = ((rows - 1) * 132 + FlowNode.HEIGHT) / 2
        return [
            (round((x - x_offset) / self.GRID) * self.GRID,
             round((y - y_offset) / self.GRID) * self.GRID)
            for x, y in slots[:count]
        ]

    def is_endpoint_node(self, node_id):
        node = next((n for n in self.nodes if n["id"] == node_id), None)
        if not node:
            return False
        label = " ".join(node.get("text", "").casefold().split())
        return label.startswith("start des bootvorgangs") or label == "betriebssystem geladen"

    def set_editing_enabled(self, enabled):
        """Lock editing without disabling canvas navigation (zoom and pan)."""
        self._editing_enabled = bool(enabled)
        self.type_box.setEnabled(self._editing_enabled)
        self.add_button.setEnabled(self._editing_enabled)
        self.delete_button.setEnabled(self._editing_enabled)
        for node in self._graphics_nodes.values():
            movable = QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            node.setFlag(movable, self._editing_enabled)
            for port in node.ports.values():
                port.setAcceptedMouseButtons(
                    Qt.MouseButton.LeftButton if self._editing_enabled
                    else Qt.MouseButton.NoButton
                )
        for line in self._graphics_edges.values():
            if isinstance(line, ConnectionLine):
                line.setAcceptedMouseButtons(
                    Qt.MouseButton.LeftButton if self._editing_enabled
                    else Qt.MouseButton.NoButton
                )

    def load_config(self, config, show_solution=False):
        self.set_editing_enabled(True)
        self.nodes = [dict(n) for n in config.get("nodes", [])]
        self._next_id = max([n["id"] for n in self.nodes] + [0]) + 1
        if show_solution:
            self.edges = [dict(e) for e in config.get("edges", [])]
            self._arrange_solution()
        else:
            self.edges = []
            for node, (x, y) in zip(
                self.nodes, self._scatter_positions(len(self.nodes)), strict=True
            ):
                node["x"], node["y"] = x, y
        self._connection_source = None
        self.refresh()
        self.center_on_nodes()

    def center_on_nodes(self):
        """Center the current complete layout in the visible canvas."""
        if not self._graphics_nodes:
            self.view.centerOn(0, 0)
            return
        bounds = QRectF()
        first = True
        for node in self._graphics_nodes.values():
            rect = node.sceneBoundingRect()
            bounds = rect if first else bounds.united(rect)
            first = False
        self.view.centerOn(bounds.center())

    def _arrange_solution(self):
        """Arrange the main path vertically and error branches beside it."""
        if not self.nodes:
            return
        by_id = {node["id"]: node for node in self.nodes}
        outgoing = {node_id: [] for node_id in by_id}
        incoming = {node_id: 0 for node_id in by_id}
        for edge in self.edges:
            source, target = edge.get("from"), edge.get("to")
            if source in by_id and target in by_id:
                outgoing[source].append(edge)
                incoming[target] += 1
        starts = [
            n["id"] for n in self.nodes
            if incoming[n["id"]] == 0
            and " ".join(n.get("text", "").casefold().split()).startswith("start des bootvorgangs")
        ]
        if not starts:
            starts = [
                n["id"] for n in self.nodes
                if n.get("type") == "Start/End" and incoming[n["id"]] == 0
            ]
        start = starts[0] if starts else self.nodes[0]["id"]
        main, branches, seen = [], [], set()
        current = start
        while current in by_id and current not in seen:
            seen.add(current)
            main.append(current)
            next_edges = [e for e in outgoing[current] if e.get("label", "Normal") != "Nein"]
            if not next_edges:
                break
            current = next_edges[0]["to"]
        for node_id in main:
            for edge in outgoing[node_id]:
                branch_start = edge.get("to")
                if edge.get("label") != "Nein" or branch_start in seen:
                    continue
                branch, cursor = [], branch_start
                while cursor in by_id and cursor not in seen and cursor not in branch:
                    branch.append(cursor)
                    next_edges = [e for e in outgoing[cursor] if e.get("label", "Normal") != "Nein"]
                    if not next_edges:
                        break
                    cursor = next_edges[0]["to"]
                branches.extend(branch)
                seen.update(branch)
        remaining = [n["id"] for n in self.nodes if n["id"] not in seen]
        main.extend(remaining)
        for index, node_id in enumerate(main):
            by_id[node_id]["x"], by_id[node_id]["y"] = 0, index * 132
        for index, node_id in enumerate(branches):
            by_id[node_id]["x"], by_id[node_id]["y"] = 300, index * 132

        # Center the whole solution (main path and branches) around the
        # canvas origin so long answers do not start above the visible area.
        min_x = min(node["x"] for node in self.nodes)
        max_x = max(node["x"] + FlowNode.WIDTH for node in self.nodes)
        min_y = min(node["y"] for node in self.nodes)
        max_y = max(node["y"] + FlowNode.HEIGHT for node in self.nodes)
        offset_x = (min_x + max_x) / 2
        offset_y = (min_y + max_y) / 2
        for node in self.nodes:
            node["x"] = round((node["x"] - offset_x) / self.GRID) * self.GRID
            node["y"] = round((node["y"] - offset_y) / self.GRID) * self.GRID

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self._next_id = 1
        self._connection_source = None
        self.refresh()

    def add_node(self):
        text, ok = QInputDialog.getText(self, tr("Add flowchart block"), tr("Block text:"))
        if not ok or not text.strip():
            return
        center = self.view.mapToScene(self.view.viewport().rect().center())
        self.nodes.append({
            "id": self._next_id, "type": self.type_box.currentText(),
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

    def begin_connection(self, node_id, side, pos):
        self._connection_source = (node_id, side)
        self._preview_line = QGraphicsLineItem(pos.x(), pos.y(), pos.x(), pos.y())
        self._preview_line.setPen(QPen(QColor(110, 190, 255, 145), 3, Qt.PenStyle.DashLine))
        self._preview_line.setZValue(8)
        self.scene.addItem(self._preview_line)
        self.status.setText(tr("Drag a connection and release it on another circle."))

    def move_connection(self, pos):
        if self._preview_line:
            line = self._preview_line.line()
            self._preview_line.setLine(line.x1(), line.y1(), pos.x(), pos.y())

    def _nearest_port(self, pos, radius=22):
        best = None
        best_distance = radius
        for node_id, node in self._graphics_nodes.items():
            for side in ("left", "right", "top", "bottom"):
                point = node.port_scene_pos(side)
                distance = (point - pos).manhattanLength()
                if distance <= best_distance:
                    best, best_distance = (node_id, side), distance
        return best

    def finish_connection(self, pos):
        target = self._nearest_port(pos)
        source = self._connection_source
        if self._preview_line:
            self.scene.removeItem(self._preview_line)
            self._preview_line = None
        self._connection_source = None
        if not source or not target or source[0] == target[0]:
            self.status.setText(tr("No connection created."))
            return
        edge = {
            "from": source[0], "from_port": source[1],
            "to": target[0], "to_port": target[1],
            "label": "Normal",
        }
        self.edges = [
            e for e in self.edges
            if not (e["from"] == edge["from"] and e.get("from_port", "right") == edge["from_port"]
                    and e.get("label", "Normal") == edge["label"])
        ]
        self.edges.append(edge)
        self.refresh()
        self.status.setText(tr("Connection created."))

    def update_connections(self):
        for edge in self.edges:
            key = (edge["from"], edge["to"], edge.get("label", "Normal"))
            line = self._graphics_edges.get(key)
            source = self._graphics_nodes.get(edge["from"])
            target = self._graphics_nodes.get(edge["to"])
            if line and source and target:
                a = source.port_scene_pos(edge.get("from_port", "right"))
                b = target.port_scene_pos(edge.get("to_port", "left"))
                line.setLine(a.x(), a.y(), b.x(), b.y())
                label = self._graphics_edges.get(("label",) + key)
                if label:
                    label.setPos((a.x() + b.x()) / 2, (a.y() + b.y()) / 2 - 20)

    def delete_selected(self):
        selected = next((n for n in self._graphics_nodes.values() if n.isSelected()), None)
        if selected is None:
            return
        node_id = selected.node_id
        self.nodes = [n for n in self.nodes if n["id"] != node_id]
        self.edges = [e for e in self.edges if e["from"] != node_id and e["to"] != node_id]
        self._connection_source = None
        self.refresh()

    def refresh(self):
        # FlowNode writes positions back to its model while being dragged, so
        # rebuilding the scene never restores stale coordinates.
        self.scene.clear()
        self._graphics_nodes.clear()
        self._graphics_edges.clear()
        self._preview_line = None
        for node in self.nodes:
            item = FlowNode(self, node)
            self.scene.addItem(item)
            self._graphics_nodes[node["id"]] = item
        for edge in self.edges:
            if edge["from"] not in self._graphics_nodes or edge["to"] not in self._graphics_nodes:
                continue
            key = (edge["from"], edge["to"], edge.get("label", "Normal"))
            line = ConnectionLine(self, edge, key)
            self.scene.addItem(line)
            self._graphics_edges[key] = line
            edge_type = edge.get("label", "Normal")
            if edge_type in ("Ja", "Nein"):
                label = QGraphicsTextItem(edge_type)
                label.setDefaultTextColor(QColor("#e6edf5"))
                label.setZValue(3)
                self.scene.addItem(label)
                self._graphics_edges[("label",) + key] = label
        self.update_connections()
        self.set_editing_enabled(self._editing_enabled)

    def get_answer(self):
        for node in self.nodes:
            item = self._graphics_nodes.get(node["id"])
            if item:
                node["x"], node["y"] = item.pos().x(), item.pos().y()
                node["text"] = item.label
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, ensure_ascii=False)

    def is_correct(self, expected):
        try:
            actual = json.loads(self.get_answer())
            wanted = json.loads(expected) if isinstance(expected, str) else expected
            actual_ids = {node["id"]: _node_key(node) for node in actual["nodes"]}
            expected_ids = {node["id"]: _node_key(node) for node in wanted["nodes"]}
            actual_edges = sorted(
                _edge_key(edge, actual_ids)
                for edge in actual["edges"]
                if edge["from"] in actual_ids and edge["to"] in actual_ids
            )
            expected_edges = sorted(
                _edge_key(edge, expected_ids) for edge in wanted["edges"]
            )
            return (
                sorted(actual_ids.values()) == sorted(expected_ids.values())
                and actual_edges == expected_edges
            )
        except (KeyError, TypeError, ValueError):
            return False
