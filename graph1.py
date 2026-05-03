"""
GraphAlgo Pro — PySide6 Graph Editor (FRONTEND ONLY)
Features:
- Drag-and-drop nodes, weighted/directed edges
- Export graph JSON to backend
- Import algorithm results JSON from backend
- Visualize shortest paths, spanning trees, node coloring, etc.
"""
import sys
import json
import math
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem, QGraphicsPathItem,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QInputDialog, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QGroupBox, QGridLayout, QSpacerItem, QSizePolicy, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QAbstractItemView, QFileDialog, QProgressBar
)
from PySide6.QtCore import (
    Qt, QPointF, QRectF, QLineF, Signal, QObject, QTimer, QThread
)
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainter, QPainterPath, QFont, QFontMetrics,
    QRadialGradient, QLinearGradient, QPolygonF, QPalette, QIcon,
    QTransform, QCursor
)

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_DARK = "#0f1117"
BG_PANEL = "#1a1d27"
BG_CARD = "#22263a"
BG_CARD2 = "#1e2130"
ACCENT_BLUE = "#4f8ef7"
ACCENT_CYAN = "#3dd6c8"
ACCENT_PINK = "#f76f8e"
ACCENT_AMBER = "#f7c94f"
ACCENT_GREEN = "#50fa7b"
NODE_DEFAULT = "#3a4a7a"
NODE_HOVER = "#5068c0"
NODE_SEL = "#4f8ef7"
EDGE_COLOR = "#6272a4"
EDGE_PATH_COLOR = "#ff79c6"  # For shortest path
GRID_COLOR = "#1e2236"
TEXT_MAIN = "#e8ecf7"
TEXT_DIM = "#6272a4"
TEXT_LABEL = "#a0aac8"
BORDER = "#2d3352"

ALGO_DEFS = [
    ("Bellman-Ford", "shortest_path", "#4f8ef7"),
    ("Dijkstra", "shortest_path", "#4f8ef7"),
    ("Bellman", "shortest_path", "#4f8ef7"),
    ("Kruskal", "spanning_tree", "#3dd6c8"),
    ("Prim", "spanning_tree", "#3dd6c8"),
    ("Composantes Connexes", "connectivity", "#f7c94f"),
    ("Chemin Eulérien", "euler", "#f76f8e"),
    ("Welsh-Powell", "coloring", "#bd93f9"),
]

# ─── Result Data Classes ───────────────────────────────────────────────────────
class AlgorithmResult:
    """Container for algorithm results from backend"""
    def __init__(self, algo_name: str, result_json: dict):
        self.algo_name = algo_name
        self.result_type = result_json.get("type", "unknown")  # shortest_path, coloring, etc.
        self.data = result_json
        self.path = result_json.get("path", [])  # For shortest path
        self.distance = result_json.get("distance", None)
        self.coloring = result_json.get("coloring", {})  # {node_id: color}
        self.mst_edges = result_json.get("mst_edges", [])  # For spanning tree
        self.components = result_json.get("components", [])  # For connectivity

# ─── Edge Weight Dialog ────────────────────────────────────────────────────────
class WeightDialog(QDialog):
    def __init__(self, parent=None, default=1, is_directed=False):
        super().__init__(parent)
        self.setWindowTitle("Edge Properties")
        self.setFixedWidth(300)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG_PANEL}; border: 1px solid {BORDER}; 
            border-radius: 8px; }}
            QLabel {{ color: {TEXT_MAIN}; font-size: 13px; }}
            QLineEdit {{ background: {BG_CARD}; color: {TEXT_MAIN}; border: 1px 
            solid {BORDER};
            border-radius: 4px; padding: 6px; font-size: 13px; }}
            QPushButton {{ background: {ACCENT_BLUE}; color: white; border: none;
            border-radius: 5px; padding: 8px 20px; font-size: 13px; }}
            QPushButton:hover {{ background: #6aa0ff; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("Weight:"))
        self.weight_edit = QLineEdit(str(default))
        self.weight_edit.setPlaceholderText("Enter weight (number)")
        layout.addWidget(self.weight_edit)
        
        if is_directed:
            self.dir_check = QCheckBox("Directed (one-way)")
            self.dir_check.setChecked(True)
            self.dir_check.setStyleSheet(f"color: {TEXT_MAIN};")
            layout.addWidget(self.dir_check)
        else:
            self.dir_check = None
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def get_weight(self):
        try:
            return float(self.weight_edit.text())
        except:
            return 1.0
    
    def get_directed(self):
        return self.dir_check.isChecked() if self.dir_check else True

# ─── Node ─────────────────────────────────────────────────────────────────────
class NodeItem(QGraphicsEllipseItem):
    RADIUS = 22
    
    def __init__(self, node_id, label, x, y, scene_ref):
        r = self.RADIUS
        super().__init__(-r, -r, 2*r, 2*r)
        self.node_id = node_id
        self.label = label
        self._scene = scene_ref
        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setZValue(10)
        self.node_color = None  # For result coloring
        self._update_appearance()
        
        self._label_item = QGraphicsTextItem(label, self)
        self._label_item.setDefaultTextColor(QColor(TEXT_MAIN))
        self._label_item.setFont(QFont("Consolas", 11, QFont.Bold))
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)
        self._label_item.setZValue(11)
    
    def _update_appearance(self):
        grad = QRadialGradient(0, -5, self.RADIUS*1.2)
        
        if self.node_color:  # Result coloring takes precedence
            grad.setColorAt(0, QColor(self.node_color).lighter(130))
            grad.setColorAt(1, QColor(self.node_color))
            pen_c = QColor(self.node_color).darker()
        elif self.isSelected():
            grad.setColorAt(0, QColor("#7aa8ff"))
            grad.setColorAt(1, QColor(NODE_SEL))
            pen_c = QColor(ACCENT_BLUE)
        else:
            grad.setColorAt(0, QColor("#4a5a8a"))
            grad.setColorAt(1, QColor(NODE_DEFAULT))
            pen_c = QColor(BORDER)
        
        self.setBrush(QBrush(grad))
        self.setPen(QPen(pen_c, 2))
    
    def set_result_color(self, hex_color):
        """Set node color from algorithm result"""
        self.node_color = hex_color
        self._update_appearance()
    
    def clear_result_color(self):
        """Clear result coloring"""
        self.node_color = None
        self._update_appearance()
    
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._scene.node_moved(self)
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self._update_appearance()
        return super().itemChange(change, value)
    
    def hoverEnterEvent(self, event):
        if not self.node_color:
            grad = QRadialGradient(0, -5, self.RADIUS*1.2)
            grad.setColorAt(0, QColor("#8090d0"))
            grad.setColorAt(1, QColor(NODE_HOVER))
            self.setBrush(QBrush(grad))
            self.setPen(QPen(QColor(ACCENT_CYAN), 2))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self._update_appearance()
        super().hoverLeaveEvent(event)
    
    def set_label(self, lbl):
        self.label = lbl
        self._label_item.setPlainText(lbl)
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)

# ─── Edge ─────────────────────────────────────────────────────────────────────
class EdgeItem(QGraphicsPathItem):
    def __init__(self, src: NodeItem, dst: NodeItem, weight=1.0, directed=True):
        super().__init__()
        self.src = src
        self.dst = dst
        self.weight = weight
        self.directed = directed
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        
        self._pen = QPen(QColor(EDGE_COLOR), 2.5, Qt.SolidLine, Qt.RoundCap)
        self._arrow_tip = None
        self._arrow_nx = 0.0
        self._arrow_ny = 0.0
        
        self._weight_item = QGraphicsTextItem(self)
        self._weight_item.setDefaultTextColor(QColor(ACCENT_AMBER))
        self._weight_item.setFont(QFont("Consolas", 9, QFont.Bold))
        self._weight_item.setZValue(5)
        
        self.is_in_path = False  # Highlight for shortest path results
        self.setPen(self._pen)
    
    def update_path(self):
        p1 = self.src.scenePos()
        p2 = self.dst.scenePos()
        
        if p1 == p2 and self.src is not self.dst:
            return
        
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist
        
        r = NodeItem.RADIUS
        sp = QPointF(p1.x() + nx * r, p1.y() + ny * r)
        ep = QPointF(p2.x() - nx * r, p2.y() - ny * r)
        
        self.prepareGeometryChange()
        path = QPainterPath(sp)
        
        if self.src is self.dst:
            path.cubicTo(
                QPointF(sp.x() + 50, sp.y() - 70),
                QPointF(ep.x() - 50, ep.y() - 70),
                ep,
            )
        else:
            mid = QPointF((sp.x() + ep.x()) / 2, (sp.y() + ep.y()) / 2)
            ctrl = QPointF(mid.x() - ny * 18, mid.y() + nx * 18)
            path.quadTo(ctrl, ep)
        
        self.setPath(path)
        self._arrow_tip = ep
        self._arrow_nx = nx
        self._arrow_ny = ny
        
        # Weight label
        mid_pt = path.pointAtPercent(0.5)
        w = self.weight
        w_txt = str(int(w)) 