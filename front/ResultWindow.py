"""
GraphAlgo Pro — PySide6 Graph Editor
Full frontend: drag-and-drop nodes, weighted/directed edges,
adjacency matrix, graph properties, algorithm buttons, JSON export.
"""

import sys
import json
import math
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QGraphicsPathItem,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QInputDialog, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QGroupBox, QGridLayout, QSpacerItem, QSizePolicy, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QAbstractItemView, QPlainTextEdit, QTabWidget
)
from PySide6.QtCore import (
    Qt, QPointF, QRectF, QLineF, Signal, QObject, QTimer
)
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont, QFontMetrics,
    QRadialGradient, QLinearGradient, QPolygonF, QPalette, QIcon,
    QTransform, QCursor
)

from front.EdgeItem import EdgeItem
from front.GraphScene import GraphScene
from front.GraphView import GraphView
from front.NodeItem import NodeItem
from front.theme.colors import *
class ResultWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graph Result Viewer")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.scene = GraphScene()
        self.view = GraphView(self.scene)

        layout.addWidget(self.view)

        btn_load = QPushButton("Load JSON")
        btn_load.clicked.connect(self.load_json)
        layout.addWidget(btn_load)

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON (*.json)")
        if not path:
            return

        import json
        with open(path, "r") as f:
            data = json.load(f)

        self.draw_graph(data)
        self.apply_result(data)

    def draw_graph(self, data):
        self.scene.clear()
        self.scene._nodes.clear()
        self.scene._edges.clear()

        positions = data["graph"]["node_positions"]

        # create nodes
        for i, label in enumerate(data["graph"]["nodes"]):
            pos = positions[label]
            node = NodeItem(i, label, pos["x"], pos["y"], self.scene)
            self.scene.addItem(node)
            self.scene._nodes[i] = node

        # helper map
        label_to_node = {n.label: n for n in self.scene._nodes.values()}

        # create edges
        for e in data["graph"]["edges"]:
            edge = EdgeItem(
                label_to_node[e["from"]],
                label_to_node[e["to"]],
                e.get("weight", 1),
                e.get("capacity", 1),
                data["graph"]["directed"]
            )
            self.scene.addItem(edge)
            edge.update_path()
            self.scene._edges.append(edge)

    def apply_result(self, data):
        result = data.get("result", {})

        # ✅ 1. MST
        mst = result.get("mst_edges", [])
        mst_set = {(e["from"], e["to"]) for e in mst}

        for e in self.scene._edges:
            if (e.src.label, e.dst.label) in mst_set or (e.dst.label, e.src.label) in mst_set:
                e.setPen(QPen(QColor("#00ff00"), 4))

        # ✅ 2. COLORING (THIS WAS MISSING)
        coloring = result.get("coloring", {})
        node_colors = coloring.get("node_colors", {})

        for node in self.scene._nodes.values():
            if node.label in node_colors:
                node.setBrush(QBrush(QColor(node_colors[node.label])))  