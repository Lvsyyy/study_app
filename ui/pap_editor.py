import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QInputDialog
)


class PapEditor(QWidget):
    """Simple visual PAP builder: create blocks, then connect selected blocks."""
    TYPES = ("Start/End", "Process", "Decision")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self.edges = []
        self._next_id = 1
        self._connect_source = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        tools = QHBoxLayout()
        self.type_box = QComboBox()
        self.type_box.addItems(self.TYPES)
        tools.addWidget(self.type_box)
        add = QPushButton("Add block")
        add.clicked.connect(self.add_node)
        tools.addWidget(add)
        self.edge_label = QComboBox()
        self.edge_label.addItems(["Normal", "Ja", "Nein"])
        tools.addWidget(self.edge_label)
        connect = QPushButton("Connect selected")
        connect.clicked.connect(self.connect_selected)
        tools.addWidget(connect)
        delete = QPushButton("Delete")
        delete.clicked.connect(self.delete_selected)
        tools.addWidget(delete)
        tools.addStretch()
        root.addLayout(tools)

        self.node_list = QListWidget()
        self.node_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.node_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.node_list.setMinimumHeight(220)
        self.node_list.itemDoubleClicked.connect(self.edit_node)
        root.addWidget(QLabel("Blocks — double-click to edit; select two blocks and connect them"))
        root.addWidget(self.node_list, 2)

        root.addWidget(QLabel("Connections"))
        self.edge_list = QListWidget()
        self.edge_list.setMinimumHeight(90)
        root.addWidget(self.edge_list, 1)

        self.setStyleSheet("""
            QListWidget { border: 1px solid #555; border-radius: 6px; padding: 5px; }
            QPushButton, QComboBox { padding: 6px 9px; }
        """)

    def load_config(self, config):
        self.nodes = [dict(n) for n in config.get("nodes", [])]
        self.edges = [dict(e) for e in config.get("edges", [])]
        self._next_id = max([n["id"] for n in self.nodes] + [0]) + 1
        self._connect_source = None
        self.refresh()

    def reset(self):
        self.nodes.clear()
        self.edges.clear()
        self._next_id = 1
        self._connect_source = None
        self.refresh()

    def add_node(self):
        kind = self.type_box.currentText()
        text, ok = QInputDialog.getText(self, "Add PAP block", "Block text:")
        if not ok or not text.strip():
            return
        node = {"id": self._next_id, "type": kind, "text": text.strip()}
        self._next_id += 1
        self.nodes.append(node)
        self.refresh()
        self.node_list.setCurrentRow(len(self.nodes) - 1)

    def edit_node(self, item):
        node = self._node_for_item(item)
        if node is None:
            return
        text, ok = QInputDialog.getText(self, "Edit PAP block", "Block text:", text=node["text"])
        if ok and text.strip():
            node["text"] = text.strip()
            self.refresh()

    def _node_for_item(self, item):
        if item is None:
            return None
        node_id = item.data(Qt.ItemDataRole.UserRole)
        return next((n for n in self.nodes if n["id"] == node_id), None)

    def connect_selected(self):
        item = self.node_list.currentItem()
        node = self._node_for_item(item)
        if node is None:
            return
        if self._connect_source is None:
            self._connect_source = node["id"]
            self.node_list.setToolTip("Now select the destination block and press Connect selected again.")
            return
        target = node["id"]
        source = self._connect_source
        self._connect_source = None
        if source == target:
            return
        label = self.edge_label.currentText()
        self.edges = [e for e in self.edges if not (e["from"] == source and e["label"] == label)]
        self.edges.append({"from": source, "to": target, "label": label})
        self.refresh()

    def delete_selected(self):
        node = self._node_for_item(self.node_list.currentItem())
        if node is None:
            return
        node_id = node["id"]
        self.nodes = [n for n in self.nodes if n["id"] != node_id]
        self.edges = [e for e in self.edges if e["from"] != node_id and e["to"] != node_id]
        self.refresh()

    def refresh(self):
        self.node_list.clear()
        for node in self.nodes:
            symbol = {"Start/End": "⬭", "Process": "▭", "Decision": "◇"}.get(node["type"], "□")
            item = QListWidgetItem(f'{symbol}  {node["type"]}: {node["text"]}')
            item.setData(Qt.ItemDataRole.UserRole, node["id"])
            self.node_list.addItem(item)
        self.edge_list.clear()
        lookup = {n["id"]: n["text"] for n in self.nodes}
        for edge in self.edges:
            source = lookup.get(edge["from"], "?")
            target = lookup.get(edge["to"], "?")
            self.edge_list.addItem(f'{source}  —[{edge["label"]}]→  {target}')

    def get_answer(self):
        return json.dumps({"nodes": self.nodes, "edges": self.edges}, ensure_ascii=False)

    def is_correct(self, expected):
        try:
            actual = json.loads(self.get_answer())
            wanted = json.loads(expected) if isinstance(expected, str) else expected
            norm_nodes = lambda nodes: sorted(
                (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                for n in nodes
            )
            node_ids = {n["id"]: (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                        for n in actual["nodes"]}
            actual_edges = sorted(
                (node_ids[e["from"]], node_ids[e["to"]], e["label"].casefold())
                for e in actual["edges"] if e["from"] in node_ids and e["to"] in node_ids
            )
            wanted_nodes = wanted["nodes"]
            wanted_edges = sorted(
                ((e["from"], e["to"], e["label"].casefold()) for e in wanted["edges"]),
                key=lambda e: (e[0], e[1], e[2])
            )
            expected_node_map = {n["id"]: (n["type"].casefold(), " ".join(n["text"].casefold().split()))
                                 for n in wanted_nodes}
            expected_edges = sorted(
                (expected_node_map[e["from"]], expected_node_map[e["to"]], e["label"].casefold())
                for e in wanted["edges"]
            )
            return norm_nodes(actual["nodes"]) == norm_nodes(wanted_nodes) and actual_edges == expected_edges
        except (KeyError, TypeError, ValueError):
            return False
