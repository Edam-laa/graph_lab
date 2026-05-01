"""
GraphAlgo Pro — PySide6 Graph Editor
Full frontend: drag-and-drop nodes, weighted/directed edges,
adjacency matrix, graph properties, algorithm buttons, JSON export.
"""

import sys
import json
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
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

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_DARK      = "#0f1117"
BG_PANEL     = "#1a1d27"
BG_CARD      = "#22263a"
BG_CARD2     = "#1e2130"
ACCENT_BLUE  = "#4f8ef7"
ACCENT_CYAN  = "#3dd6c8"
ACCENT_PINK  = "#f76f8e"
ACCENT_AMBER = "#f7c94f"
NODE_DEFAULT = "#3a4a7a"
NODE_HOVER   = "#5068c0"
NODE_SEL     = "#4f8ef7"
EDGE_COLOR   = "#6272a4"
GRID_COLOR   = "#1e2236"
TEXT_MAIN    = "#e8ecf7"
TEXT_DIM     = "#6272a4"
TEXT_LABEL   = "#a0aac8"
BORDER       = "#2d3352"

ALGO_DEFS = [
    ("Bellman-Ford",       "shortest_path",  "#4f8ef7"),
    ("Dijkstra",           "shortest_path",  "#4f8ef7"),
    ("Bellman",            "shortest_path",  "#4f8ef7"),
    ("Kruskal",            "spanning_tree",  "#3dd6c8"),
    ("Prim",               "spanning_tree",  "#3dd6c8"),
    ("Composantes Connexes","connectivity",  "#f7c94f"),
    ("Chemin Eulérien",    "euler",          "#f76f8e"),
    ("Welsh-Powell",       "coloring",       "#bd93f9"),
]
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QFileDialog

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
# ─── Edge Properties Dialog ───────────────────────────────────────────────────
class WeightDialog(QDialog):
    def __init__(self, parent=None, default_weight=1, default_capacity=1, is_directed=False, weighted=True, capacity_enabled=True):
        super().__init__(parent)
        self.setWindowTitle("Edge Properties")
        self.setFixedWidth(320)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG_PANEL}; border: 1px solid {BORDER}; border-radius: 8px; }}
            QLabel {{ color: {TEXT_MAIN}; font-size: 12px; }}
            QLineEdit {{ background: {BG_CARD}; color: {TEXT_MAIN}; border: 1px solid {BORDER};
                         border-radius: 4px; padding: 6px; font-size: 13px; }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_BLUE}; }}
            QPushButton {{ background: {ACCENT_BLUE}; color: white; border: none;
                           border-radius: 5px; padding: 8px 20px; font-size: 13px; }}
            QPushButton:hover {{ background: #6aa0ff; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("⟶  Edge Properties")
        title.setFont(QFont("Consolas", 12, QFont.Bold))
        title.setStyleSheet(f"color: {ACCENT_CYAN};")
        layout.addWidget(title)

        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {BORDER};"); layout.addWidget(line)

        if weighted:
            layout.addWidget(QLabel("Weight  (poids):"))
            self.weight_edit = QLineEdit(str(default_weight))
            self.weight_edit.setPlaceholderText("ex: 5, 3.14 ...")
            layout.addWidget(self.weight_edit)
        else:
            self.weight_edit = None

        if capacity_enabled:
            layout.addWidget(QLabel("Capacity  (capacité):"))
            self.capacity_edit = QLineEdit(str(default_capacity))
            self.capacity_edit.setPlaceholderText("ex: 10, 100 ...")
            layout.addWidget(self.capacity_edit)
        else:
            self.capacity_edit = None

        if is_directed:
            self.dir_check = QCheckBox("Directed edge  (arc orienté)")
            self.dir_check.setChecked(True)
            self.dir_check.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px;")
            layout.addWidget(self.dir_check)
        else:
            self.dir_check = None

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.setStyleSheet(f"""
            QPushButton {{ background: {ACCENT_BLUE}; color: white; border-radius: 5px; padding: 7px 18px; }}
        """)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_weight(self):
        if self.weight_edit is None:
            return 1.0
        try:
            return float(self.weight_edit.text())
        except:
            return 1.0

    def get_capacity(self):
        if self.capacity_edit is None:
            return 1
        try:
            v = float(self.capacity_edit.text())
            return int(v) if v == int(v) else v
        except:
            return 1

    def get_directed(self):
        return self.dir_check.isChecked() if self.dir_check else True


# ─── Node ─────────────────────────────────────────────────────────────────────
class NodeItem(QGraphicsEllipseItem):
    RADIUS = 22

    def __init__(self, node_id, label, x, y, scene_ref):
        r = self.RADIUS
        super().__init__(-r, -r, 2*r, 2*r)
        self.node_id = node_id
        self.label   = label
        self._scene  = scene_ref
        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setZValue(10)
        self._update_appearance()

        self._label_item = QGraphicsTextItem(label, self)
        self._label_item.setDefaultTextColor(QColor(TEXT_MAIN))
        self._label_item.setFont(QFont("Consolas", 11, QFont.Bold))
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)
        self._label_item.setZValue(11)

    def _update_appearance(self):
        grad = QRadialGradient(0, -5, self.RADIUS*1.2)
        if self.isSelected():
            grad.setColorAt(0, QColor("#7aa8ff"))
            grad.setColorAt(1, QColor(NODE_SEL))
            pen_c = QColor(ACCENT_BLUE)
        else:
            grad.setColorAt(0, QColor("#4a5a8a"))
            grad.setColorAt(1, QColor(NODE_DEFAULT))
            pen_c = QColor(BORDER)
        self.setBrush(QBrush(grad))
        self.setPen(QPen(pen_c, 2))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._scene.node_moved(self)
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self._update_appearance()
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        grad = QRadialGradient(0, -5, self.RADIUS*1.2)
        grad.setColorAt(0, QColor("#8090d0"))
        grad.setColorAt(1, QColor(NODE_HOVER))
        self.setBrush(QBrush(grad))
        self.setPen(QPen(QColor(ACCENT_CYAN), 2))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._update_appearance()
        super().hoverLeaveEvent(event)

    def setAcceptHoverEvents(self, b):
        super().setAcceptHoverEvents(b)

    def set_label(self, lbl):
        self.label = lbl
        self._label_item.setPlainText(lbl)
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)


# ─── Edge ─────────────────────────────────────────────────────────────────────
class EdgeItem(QGraphicsPathItem):
    def __init__(self, src: NodeItem, dst: NodeItem, weight=1.0, capacity=1, directed=True):
        super().__init__()
        self.src      = src
        self.dst      = dst
        self.weight   = weight
        self.capacity = capacity
        self.directed = directed
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._pen = QPen(QColor(EDGE_COLOR), 2.5, Qt.SolidLine, Qt.RoundCap)
        self._arrow_tip  = None
        self._arrow_nx   = 0.0
        self._arrow_ny   = 0.0

        self._weight_item = QGraphicsTextItem(self)
        self._weight_item.setDefaultTextColor(QColor(ACCENT_AMBER))
        self._weight_item.setFont(QFont("Consolas", 9, QFont.Bold))
        self._weight_item.setZValue(5)

        self.setPen(self._pen)
        # update_path() is called by the scene AFTER addItem()

    def update_path(self):
        # All coordinates in scene space; EdgeItem sits at scene origin (pos = 0,0)
        p1 = self.src.scenePos()
        p2 = self.dst.scenePos()

        # Safety: if nodes not in scene yet, skip
        if p1 == p2 and self.src is not self.dst:
            return

        dx   = p2.x() - p1.x()
        dy   = p2.y() - p1.y()
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist

        r  = NodeItem.RADIUS
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
            mid  = QPointF((sp.x() + ep.x()) / 2, (sp.y() + ep.y()) / 2)
            ctrl = QPointF(mid.x() - ny * 18, mid.y() + nx * 18)
            path.quadTo(ctrl, ep)

        self.setPath(path)

        # Arrow data stored for paint()
        self._arrow_tip = ep
        self._arrow_nx  = nx
        self._arrow_ny  = ny

        # Weight / capacity label
        mid_pt = path.pointAtPercent(0.5)
        w = self.weight
        c = self.capacity
        w_txt = str(int(w)) if w == int(w) else str(w)
        c_txt = str(int(c)) if c == int(c) else str(c)
        
        # Show based on scene settings
        scene = self.scene()
        show_w = getattr(scene, '_weighted_graph', True) if scene else True
        show_c = getattr(scene, '_capacity_graph', True) if scene else True
        
        if show_w and show_c:
            label_txt = f"{w_txt}/{c_txt}" if c != 1 else w_txt
        elif show_w:
            label_txt = w_txt
        elif show_c:
            label_txt = c_txt
        else:
            label_txt = ""
        
        self._weight_item.setPlainText(label_txt)
        wr = self._weight_item.boundingRect()
        self._weight_item.setPos(
            mid_pt.x() - wr.width() / 2 - ny * 16,
            mid_pt.y() - wr.height() / 2 + nx * 16,
        )
        self.update()

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        self.setPen(self._pen)
        super().paint(painter, option, widget)
        if self.directed and self._arrow_tip is not None:
            self._paint_arrow(painter)

    def _paint_arrow(self, painter):
        tip = self._arrow_tip
        nx, ny = self._arrow_nx, self._arrow_ny
        sz = 12
        left  = QPointF(tip.x() - nx*sz + ny*sz*0.5,
                        tip.y() - ny*sz - nx*sz*0.5)
        right = QPointF(tip.x() - nx*sz - ny*sz*0.5,
                        tip.y() - ny*sz + nx*sz*0.5)
        painter.setBrush(QBrush(QColor(EDGE_COLOR)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(QPolygonF([tip, left, right]))

    def reverse(self):
        """Reverse the direction of the edge (swap src and dst)."""
        self.src, self.dst = self.dst, self.src
        self.update_path()


# ─── Graph Scene ──────────────────────────────────────────────────────────────
class GraphScene(QGraphicsScene):
    graph_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-1000, -1000, 2000, 2000)
        self._nodes: dict[int, NodeItem] = {}
        self._edges: list[EdgeItem]      = []
        self._node_counter = 0
        self._mode   = "select"   # select | add_node | add_edge
        self._directed_graph = True
        self._weighted_graph = True
        self._capacity_graph = True
        self._history = []  # Undo stack
        self._edge_src: NodeItem | None = None
        self._temp_line: QGraphicsLineItem | None = None
        self._drag_pos = None
        self._node_labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    def _edit_edge(self, edge: EdgeItem):
        parent_widget = self.views()[0].window() if self.views() else None

        dlg = WeightDialog(
            parent=parent_widget,
            default_weight=edge.weight,
            default_capacity=edge.capacity,
            is_directed=self._directed_graph,
            weighted=self._weighted_graph
        )

        if dlg.exec():
            # ✅ poids
            if self._weighted_graph:
                edge.weight = dlg.get_weight()

            # ✅ capacité
            edge.capacity = dlg.get_capacity()

            # ✅ direction (si activé)
            if dlg.dir_check:
                edge.directed = dlg.get_directed()

            edge.update_path()
            self.graph_changed.emit()
    # ── Mode control
    def set_mode(self, mode):
        self._mode = mode
        self._edge_src = None
        if self._temp_line:
            self.removeItem(self._temp_line)
            self._temp_line = None
        for node in self._nodes.values():
            node.setFlag(QGraphicsItem.ItemIsMovable,   mode == "select")
            node.setFlag(QGraphicsItem.ItemIsSelectable, mode == "select")
            node.setAcceptHoverEvents(True)

    def set_directed(self, v): self._directed_graph = v; self._refresh_edges()
    def set_weighted(self, v): self._weighted_graph = v
    def set_capacity(self, v): self._capacity_graph = v; self.graph_changed.emit()

    def undo(self):
        """Undo last action (add node, add edge, or delete)."""
        if not self._history:
            return

        action, obj = self._history.pop()

        if action == "add_node":
            # Remove the node and all connected edges
            to_remove = [e for e in self._edges if e.src is obj or e.dst is obj]
            for e in to_remove:
                self.removeItem(e)
                self._edges.remove(e)
            self.removeItem(obj)
            del self._nodes[obj.node_id]

        elif action == "add_edge":
            if obj in self._edges:
                self.removeItem(obj)
                self._edges.remove(obj)

        elif action == "delete_node":
            # Restore node
            self.addItem(obj)
            self._nodes[obj.node_id] = obj

        elif action == "delete_edge":
            # Restore edge
            self.addItem(obj)
            self._edges.append(obj)

        self.graph_changed.emit()

    def _refresh_edges(self):
        for e in self._edges:
            e.directed = self._directed_graph
            e.update_path()
        self.graph_changed.emit()

    # ── Mouse events
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._mode == "add_node":
                self._add_node(event.scenePos())
            elif self._mode == "add_edge":
                node = self._node_at(event.scenePos())
                if node:
                    if self._edge_src is None:
                        self._edge_src = node
                        self._temp_line = QGraphicsLineItem()
                        self._temp_line.setPen(QPen(QColor(ACCENT_CYAN), 1.5, Qt.DashLine))
                        self._temp_line.setZValue(20)
                        self.addItem(self._temp_line)
                    else:
                        self._finalize_edge(node)
                # Don't call super() in add_edge mode — it interferes with selection
                return
            elif self._mode == "delete":
                node = self._node_at(event.scenePos())
                if node:
                    self._delete_item(node)
                else:
                    item = self.itemAt(event.scenePos(), QTransform())
                    self._delete_item(item)
            else:
                super().mousePressEvent(event)
        elif event.button() == Qt.RightButton:
            # Right-click to reverse edge direction
            item = self.itemAt(event.scenePos(), QTransform())
            if isinstance(item, EdgeItem):
                item.reverse()
                self.graph_changed.emit()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._mode == "add_edge" and self._edge_src and self._temp_line:
            p1 = self._edge_src.scenePos()
            self._temp_line.setLine(QLineF(p1, event.scenePos()))
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.scenePos(), QTransform())

        # 🔥 1. PRIORITÉ : EDIT EDGE
        if isinstance(item, EdgeItem):
            self._edit_edge(item)
            return

        # 🔥 2. ENSUITE : NODE
        node = self._get_node(item)
        if node and self._mode == "select":
            lbl, ok = QInputDialog.getText(None, "Rename Node", "Label:", text=node.label)
            if ok and lbl.strip():
                node.set_label(lbl.strip())
                self.graph_changed.emit()
            return

        super().mouseDoubleClickEvent(event)


    # ── Helpers
    def _node_at(self, scene_pos):
        """Return the NodeItem under scene_pos, checking all items at that point."""
        for item in self.items(scene_pos):
            node = self._get_node(item)
            if node:
                return node
        return None

    def _get_node(self, item):
        """Walk up the item parent chain to find a NodeItem."""
        cur = item
        while cur is not None:
            if isinstance(cur, NodeItem):
                return cur
            cur = cur.parentItem()
        return None

    def _add_node(self, pos):
        nid = self._node_counter
        lbl = self._node_labels[nid % 26]
        if nid >= 26:
            lbl = self._node_labels[(nid // 26) - 1] + lbl
        node = NodeItem(nid, lbl, pos.x(), pos.y(), self)
        node.setAcceptHoverEvents(True)
        node.setFlag(QGraphicsItem.ItemIsMovable,    self._mode == "select")
        node.setFlag(QGraphicsItem.ItemIsSelectable, self._mode == "select")
        self.addItem(node)
        self._nodes[nid] = node
        self._node_counter += 1
        # Save to history for undo
        self._history.append(("add_node", node))
        self.graph_changed.emit()

    def _finalize_edge(self, dst: NodeItem):
        src = self._edge_src
        self._edge_src = None
        if self._temp_line:
            self.removeItem(self._temp_line)
            self._temp_line = None

        parent_widget = self.views()[0].window() if self.views() else None
        dlg = WeightDialog(
            parent=parent_widget,
            is_directed=self._directed_graph,
            weighted=self._weighted_graph,
            capacity_enabled=self._capacity_graph,
        )
        if dlg.exec():   # non-zero == Accepted in PySide6
            weight   = dlg.get_weight()
            capacity = dlg.get_capacity()
        else:
            return

        edge = EdgeItem(src, dst, weight, capacity, self._directed_graph)
        self.addItem(edge)      # must be in scene before update_path() reads scenePos()
        edge.update_path()
        self._edges.append(edge)
        # Save to history for undo
        self._history.append(("add_edge", edge))
        self.graph_changed.emit()

    def _delete_item(self, item):
        node = self._get_node(item)
        if node:
            # Remove all connected edges
            to_remove = [e for e in self._edges if e.src is node or e.dst is node]
            for e in to_remove:
                self.removeItem(e)
                self._edges.remove(e)
            # Save to history for undo
            self._history.append(("delete_node", node))
            self.removeItem(node)
            del self._nodes[node.node_id]
            self.graph_changed.emit()
            return
        if isinstance(item, EdgeItem):
            # Save to history for undo
            self._history.append(("delete_edge", item))
            self.removeItem(item)
            self._edges.remove(item)
            self.graph_changed.emit()
        elif isinstance(item, QGraphicsTextItem):
            parent = item.parentItem()
            if isinstance(parent, EdgeItem):
                # Save to history for undo
                self._history.append(("delete_edge", parent))
                self.removeItem(parent)
                self._edges.remove(parent)
                self.graph_changed.emit()

    def node_moved(self, node):
        for e in self._edges:
            if e.src is node or e.dst is node:
                e.update_path()
        self.graph_changed.emit()

    # ── Graph data
    def get_graph_data(self, algo_name="", algo_category="", algo_params=None) -> dict:
        props = self.get_properties()
        nodes_list = [n.label for n in self._nodes.values()]
        edges_list = []
        for e in self._edges:
            entry = {
                "from":     e.src.label,
                "to":       e.dst.label,
                "capacity": e.capacity,
            }
            if self._weighted_graph:
                entry["weight"] = e.weight
            edges_list.append(entry)

        # node positions for visualisation
        node_positions = {
            n.label: {"x": round(n.scenePos().x(), 2), "y": round(n.scenePos().y(), 2)}
            for n in self._nodes.values()
        }

        # algo constraints defaults
        cat = algo_category or "shortest_path"
        constraints = {
            "shortest_path":  {"requires_positive_weights": True,  "requires_positive_capacity": False, "requires_connected": True,  "requires_dag": False},
            "spanning_tree":  {"requires_positive_weights": False, "requires_positive_capacity": False, "requires_connected": True,  "requires_dag": False},
            "connectivity":   {"requires_positive_weights": False, "requires_positive_capacity": False, "requires_connected": False, "requires_dag": False},
            "euler":          {"requires_positive_weights": False, "requires_positive_capacity": False, "requires_connected": True,  "requires_dag": False},
            "coloring":       {"requires_positive_weights": False, "requires_positive_capacity": False, "requires_connected": False, "requires_dag": False},
            "max_flow":       {"requires_positive_weights": False, "requires_positive_capacity": True,  "requires_connected": True,  "requires_dag": False},
        }.get(cat, {"requires_positive_weights": False, "requires_positive_capacity": False, "requires_connected": False, "requires_dag": False})

        return {
            "graph": {
                "nodes": nodes_list,
                "node_positions": node_positions,
                "edges": edges_list,
                "directed": self._directed_graph,
                "metadata": {
                    "name": "",
                    "description": "",
                    "allow_negative_weights": True,
                    "weighted": self._weighted_graph,
                },
            },
            "algorithm": {
                "name":     algo_name or "",
                "category": cat,
                "params":   algo_params or {},
                "constraints_check": constraints,
            },
            "execution": {
                "execution_time": None,
                "complexity":     None,
                "status":         "not_started",
                "message":        "",
                "warnings":       [],
            },
            "result": {
                "type": None,
                "distances": {},
                "path": [],
                "paths": {},
                "mst_edges": [],
                "components": [],
                "cycles": [],
                "eulerian_path": [],
                "eulerian_circuit": [],
                "coloring": {"node_colors": {}, "edge_colors": {}},
                "flow": {"value": None, "augmenting_paths": [], "edge_flows": {}},
                "traversal": {"order": [], "tree_edges": []},
                "graph_properties": {
                    "is_connected":         props.get("connected"),
                    "is_strongly_connected": None,
                    "is_tree":              props.get("is_tree"),
                    "is_bipartite":         props.get("bipartite"),
                    "is_eulerian":          props.get("eulerian_circuit"),
                    "has_cycle":            None,
                    "is_weighted":          self._weighted_graph,
                },
                "steps": [],
            },
            "options": {
                "return_path":    True,
                "return_steps":   True,
                "measure_time":   True,
                "visualize":      False,
            },
        }

    def get_adjacency_matrix(self):
        ids   = sorted(self._nodes.keys())
        labels = [self._nodes[i].label for i in ids]
        n = len(ids)
        idx = {nid: i for i, nid in enumerate(ids)}
        mat = [[None]*n for _ in range(n)]
        for e in self._edges:
            i = idx[e.src.node_id]
            j = idx[e.dst.node_id]
            w = e.weight
            mat[i][j] = w
            if not e.directed:
                mat[j][i] = w
        return labels, mat

    def get_properties(self) -> dict:
        n = len(self._nodes)
        m = len(self._edges)
        if n == 0:
            return {}

        # Build adjacency
        ids = list(self._nodes.keys())
        adj  = {i: set() for i in ids}
        adj_in = {i: set() for i in ids}
        deg  = {i: 0 for i in ids}
        deg_in  = {i: 0 for i in ids}
        deg_out = {i: 0 for i in ids}
        for e in self._edges:
            s, d = e.src.node_id, e.dst.node_id
            adj[s].add(d)
            adj_in[d].add(s)
            deg_out[s] += 1
            deg_in[d]  += 1
            deg[s] += 1
            deg[d] += 1
            adj_undir = {i: set() for i in ids}
            for e in self._edges:
                s, d = e.src.node_id, e.dst.node_id
                adj_undir[s].add(d)
                adj_undir[d].add(s)
            if not e.directed:
                adj[d].add(s)
                adj_in[s].add(d)
                deg_out[d] += 1
                deg_in[s]  += 1
                deg[d] += 1  # counted twice for undirected in deg list

        # Connectivity (BFS undirected)

        components = 0
        all_ids = set(ids)
        temp = set()
        for i in ids:
            if i not in temp:
                components += 1
                q = [i]; temp.add(i)
                while q:
                    c = q.pop(0)
                    for nb in adj_undir[c]:
                        if nb not in temp:
                            temp.add(nb); q.append(nb)

        connected = components == 1

        # Complete check
        complete = all(len(adj_undir[i]) >= n-1 for i in ids)

        # Eulerian (undirected: all even degree; directed: in==out for all)
        if self._directed_graph:
            eulerian_circuit  = connected and all(deg_in[i]==deg_out[i] for i in ids)
            eulerian_path     = connected and sum(1 for i in ids if deg_out[i]-deg_in[i]==1)==1 \
                                          and sum(1 for i in ids if deg_in[i]-deg_out[i]==1)==1
        else:
            odd_deg = sum(1 for i in ids if deg[i] % 2 != 0)
            eulerian_circuit = connected and odd_deg == 0
            eulerian_path    = connected and odd_deg == 2

        # Regular
        all_degs = [deg[i] for i in ids]
        regular = len(set(all_degs)) == 1
        reg_degree = all_degs[0] if regular else None

        # Bipartite (BFS 2-coloring)
        color = {}
        bipartite = True
        for start in ids:
            if start not in color:
                color[start] = 0
                q = [start]
                while q and bipartite:
                    cur = q.pop(0)
                    for nb in adj_undir[cur]:
                        if nb not in color:
                            color[nb] = 1 - color[cur]
                            q.append(nb)
                        elif color[nb] == color[cur]:
                            bipartite = False

        # Tree check
        is_tree = connected and m == n - 1

        # Density
        max_edges = n*(n-1) if self._directed_graph else n*(n-1)//2
        density = round(m/max_edges, 3) if max_edges > 0 else 0

        return {
            "nodes": n, "edges": m,
            "connected": connected,
            "components": components,
            "complete": complete,
            "eulerian_circuit": eulerian_circuit,
            "eulerian_path": eulerian_path,
            "regular": regular,
            "reg_degree": reg_degree,
            "bipartite": bipartite,
            "is_tree": is_tree,
            "density": density,
        }


# ─── Graph View ───────────────────────────────────────────────────────────────
class GraphView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setStyleSheet(f"background: {BG_DARK}; border: none;")
        self._draw_grid = True

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(BG_DARK))
        if not self._draw_grid:
            return
        painter.setPen(QPen(QColor(GRID_COLOR), 0.5))
        step = 40
        l, r = int(rect.left())//step*step, int(rect.right())//step*step+step
        t, b = int(rect.top())//step*step, int(rect.bottom())//step*step+step
        for x in range(l, r, step):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(t, b, step):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = event
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)


# ─── Tool Button ──────────────────────────────────────────────────────────────
class ToolBtn(QPushButton):
    def __init__(self, text, icon_char="", active_color=ACCENT_BLUE, parent=None):
        super().__init__(parent)
        self.icon_char    = icon_char
        self.active_color = active_color
        self.setCheckable(True)
        self.setText(f"  {icon_char}  {text}")
        self.setFont(QFont("Consolas", 11))
        self.setFixedHeight(38)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.toggled.connect(lambda _: self._update_style())

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{ background: {self.active_color}22;
                               color: {self.active_color}; border: 1px solid {self.active_color};
                               border-radius: 6px; padding: 0 12px; text-align: left; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {TEXT_DIM};
                               border: 1px solid transparent; border-radius: 6px;
                               padding: 0 12px; text-align: left; }}
                QPushButton:hover {{ background: {BG_CARD}; color: {TEXT_LABEL}; }}
            """)


# ─── Algorithm Button ─────────────────────────────────────────────────────────
class AlgoBtn(QPushButton):
    def __init__(self, name, color, parent=None):
        super().__init__(name, parent)
        self.algo_name = name
        self._color    = color
        self.setFont(QFont("Consolas", 10, QFont.Medium))
        self.setFixedHeight(34)
        self.setCursor(Qt.PointingHandCursor)
        self.set_available(True)

    def set_available(self, avail: bool):
        self._available = avail
        if avail:
            self.setEnabled(True)
            self.setStyleSheet(f"""
                QPushButton {{ background: {self._color}22; color: {self._color};
                               border: 1px solid {self._color}55; border-radius: 6px; }}
                QPushButton:hover {{ background: {self._color}44; border: 1px solid {self._color}; }}
                QPushButton:pressed {{ background: {self._color}66; }}
            """)
        else:
            self.setEnabled(False)
            self.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {TEXT_DIM}33;
                               border: 1px solid {BORDER}44; border-radius: 6px; }}
            """)


# ─── Section Label ────────────────────────────────────────────────────────────
def section_label(text):
    lbl = QLabel(text.upper())
    lbl.setFont(QFont("Consolas", 9, QFont.Bold))
    lbl.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 1px; padding: 4px 0;")
    return lbl


# ─── Main Window ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphAlgo Pro  —  Graph Editor")
        self.resize(1320, 820)
        self.setMinimumSize(900, 600)

        self._scene = GraphScene()
        self._scene.graph_changed.connect(self._on_graph_changed)

        self._build_ui()
        self._apply_global_style()
        self._on_graph_changed()
    def _open_result_window(self):
        self.result_window = ResultWindow(self)
        self.result_window.show()

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        # Center: canvas on top, log panel on bottom (splitter)
        center_wrap = QWidget()
        center_wrap.setObjectName("centerWrap")
        cv = QVBoxLayout(center_wrap)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)

        # Algo buttons bar
        bottom = self._build_bottom_bar()
        cv.addWidget(bottom)

        # Splitter: canvas / log
        self._center_splitter = QSplitter(Qt.Vertical)
        self._center_splitter.setStyleSheet(f"""
            QSplitter::handle {{ background: {BORDER}; height: 4px; }}
            QSplitter::handle:hover {{ background: {ACCENT_BLUE}; }}
        """)

        self._view = GraphView(self._scene)
        self._center_splitter.addWidget(self._view)

        log_panel = self._build_log_panel()
        self._center_splitter.addWidget(log_panel)

        self._center_splitter.setStretchFactor(0, 3)
        self._center_splitter.setStretchFactor(1, 1)
        self._center_splitter.setSizes([560, 200])

        cv.addWidget(self._center_splitter, 1)

        root.addWidget(center_wrap, 1)

        # Right panel
        right = self._build_right_panel()
        root.addWidget(right)

    def _build_sidebar(self):
        sb = QWidget()
        sb.setFixedWidth(200)
        sb.setObjectName("sidebar")
        layout = QVBoxLayout(sb)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Logo
        logo = QLabel("⬡ GraphAlgo Pro")
        logo.setFont(QFont("Consolas", 14, QFont.Bold))
        logo.setStyleSheet(f"color: {ACCENT_BLUE};")
        layout.addWidget(logo)

        sub = QLabel("v1.0  ·  Graph Editor")
        sub.setFont(QFont("Consolas", 9))
        sub.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(sub)

        layout.addSpacing(16)
        layout.addWidget(self._hdiv())
        layout.addSpacing(8)

        # Build tools
        layout.addWidget(section_label("Build Tools"))
        self._btn_select   = ToolBtn("Select / Move", "↖", ACCENT_BLUE)
        self._btn_add_node = ToolBtn("Add Node",      "◉", ACCENT_CYAN)
        self._btn_add_edge = ToolBtn("Add Edge",      "—", ACCENT_PINK)
        self._btn_delete   = ToolBtn("Delete",        "✕", "#f76f8e")
        self._btn_reverse  = ToolBtn("Reverse Edge",  "↻", ACCENT_AMBER)

        for btn in [self._btn_select, self._btn_add_node, self._btn_add_edge, self._btn_delete, self._btn_reverse]:

            layout.addWidget(btn)

        self._btn_select.setChecked(True)
        self._btn_select.clicked.connect(lambda: self._set_mode("select"))
        self._btn_add_node.clicked.connect(lambda: self._set_mode("add_node"))
        self._btn_add_edge.clicked.connect(lambda: self._set_mode("add_edge"))
        self._btn_delete.clicked.connect(lambda: self._set_mode("delete"))
        self._btn_reverse.clicked.connect(self._reverse_selected_edge)

        layout.addSpacing(12)
        layout.addWidget(self._hdiv())
        layout.addSpacing(8)

        # Graph options
        layout.addWidget(section_label("Graph Type"))

        self._chk_directed = QPushButton("⟶  Directed")
        self._chk_directed.setCheckable(True)
        self._chk_directed.setChecked(True)
        self._chk_directed.setFont(QFont("Consolas", 11))
        self._chk_directed.setFixedHeight(36)
        self._chk_directed.toggled.connect(self._on_directed_changed)
        self._style_toggle(self._chk_directed, ACCENT_CYAN)
        layout.addWidget(self._chk_directed)

        self._chk_weighted = QPushButton("⚖  Weighted")
        self._chk_weighted.setCheckable(True)
        self._chk_weighted.setChecked(True)
        self._chk_weighted.setFont(QFont("Consolas", 11))
        self._chk_weighted.setFixedHeight(36)
        self._chk_weighted.toggled.connect(self._on_weighted_changed)
        self._style_toggle(self._chk_weighted, ACCENT_AMBER)
        layout.addWidget(self._chk_weighted)

        self._chk_capacity = QPushButton("📦  Capacity")
        self._chk_capacity.setCheckable(True)
        self._chk_capacity.setChecked(True)
        self._chk_capacity.setFont(QFont("Consolas", 11))
        self._chk_capacity.setFixedHeight(36)
        self._chk_capacity.toggled.connect(self._on_capacity_changed)
        self._style_toggle(self._chk_capacity, "#3dd6c8")
        layout.addWidget(self._chk_capacity)

        layout.addSpacing(12)
        layout.addWidget(self._hdiv())
        layout.addSpacing(8)

        # Actions
        layout.addWidget(section_label("Actions"))

        self._btn_clear = self._action_btn("⌫  Clear Graph", "#f76f8e")
        self._btn_clear.clicked.connect(self._clear_graph)
        layout.addWidget(self._btn_clear)

        self._btn_export = self._action_btn("⬇  Export JSON", ACCENT_CYAN)
        self._btn_export.clicked.connect(self._export_json)
        layout.addWidget(self._btn_export)

        self._btn_undo = self._action_btn("↶ Undo", "#bd93f9")
        self._btn_undo.clicked.connect(self._scene.undo)
        layout.addWidget(self._btn_undo)

        self._btn_show_result = self._action_btn("🧠 Show Result JSON", "#bd93f9")
        self._btn_show_result.clicked.connect(self._open_result_window)
        layout.addWidget(self._btn_show_result)

        layout.addStretch()

        # Status
        self._status_lbl = QLabel("Ready")
        self._status_lbl.setFont(QFont("Consolas", 9))
        self._status_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        self._status_lbl.setWordWrap(True)
        layout.addWidget(self._status_lbl)

        return sb

    def _build_bottom_bar(self):
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setObjectName("bottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Algorithms:").setStyleSheet if False else QLabel("Algorithms:"))

        self._algo_btns: dict[str, AlgoBtn] = {}
        for name, cat, color in ALGO_DEFS:
            btn = AlgoBtn(name, color)
            btn.clicked.connect(lambda checked, n=name: self._run_algo(n))
            self._algo_btns[name] = btn
            layout.addWidget(btn)

        layout.addStretch()

        self._nodes_lbl = QLabel("Nodes: 0")
        self._edges_lbl = QLabel("Edges: 0")
        for lbl in [self._nodes_lbl, self._edges_lbl]:
            lbl.setFont(QFont("Consolas", 10))
            lbl.setStyleSheet(f"color: {TEXT_DIM};")
            layout.addWidget(lbl)

        return bar

    def _build_log_panel(self):
        """Execution log panel — shown below the canvas."""
        panel = QWidget()
        panel.setObjectName("logPanel")
        panel.setMinimumHeight(120)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(32)
        header.setObjectName("logHeader")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(12, 0, 8, 0)
        hlay.setSpacing(8)

        title = QLabel("⬛  Execution Log")
        title.setFont(QFont("Consolas", 10, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_DIM};")
        hlay.addWidget(title)

        self._log_algo_badge = QLabel("")
        self._log_algo_badge.setFont(QFont("Consolas", 9, QFont.Bold))
        self._log_algo_badge.setStyleSheet(
            f"color: {ACCENT_CYAN}; background: {ACCENT_CYAN}22; "
            f"border: 1px solid {ACCENT_CYAN}55; border-radius: 3px; padding: 1px 6px;"
        )
        self._log_algo_badge.hide()
        hlay.addWidget(self._log_algo_badge)

        hlay.addStretch()

        # Clear button
        btn_clear_log = QPushButton("✕ Clear")
        btn_clear_log.setFont(QFont("Consolas", 9))
        btn_clear_log.setFixedHeight(22)
        btn_clear_log.setCursor(Qt.PointingHandCursor)
        btn_clear_log.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_DIM};
                           border: 1px solid {BORDER}; border-radius: 3px; padding: 0 8px; }}
            QPushButton:hover {{ color: {ACCENT_PINK}; border-color: {ACCENT_PINK}; }}
        """)
        btn_clear_log.clicked.connect(self._clear_log)
        hlay.addWidget(btn_clear_log)

        layout.addWidget(header)

        # Divider
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(div)

        # The actual log text area — using QPlainTextEdit for performance with many lines
        self._log_text = QPlainTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("Consolas", 10))
        self._log_text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self._log_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {BG_DARK};
                color: {TEXT_MAIN};
                border: none;
                padding: 8px 12px;
                selection-background-color: {ACCENT_BLUE}44;
            }}
            QScrollBar:vertical {{
                background: {BG_PANEL}; width: 8px; border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 4px; min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {TEXT_DIM}; }}
            QScrollBar:horizontal {{
                background: {BG_PANEL}; height: 8px; border: none;
            }}
            QScrollBar::handle:horizontal {{
                background: {BORDER}; border-radius: 4px;
            }}
        """)
        self._log_text.setPlaceholderText(
            "Run an algorithm to see step-by-step execution details here…"
        )
        layout.addWidget(self._log_text, 1)

        return panel

    def _clear_log(self):
        self._log_text.clear()
        self._log_algo_badge.hide()

    def _log(self, text, kind="info"):
        """Append a styled line to the log. kind: info | step | result | warn | error | header"""
        colors = {
            "header": ACCENT_CYAN,
            "step":   TEXT_MAIN,
            "result": ACCENT_AMBER,
            "warn":   "#f7c94f",
            "error":  ACCENT_PINK,
            "info":   TEXT_DIM,
            "dim":    TEXT_DIM,
        }
        prefixes = {
            "header": "━━ ",
            "step":   "  › ",
            "result": "  ✔ ",
            "warn":   "  ⚠ ",
            "error":  "  ✖ ",
            "info":   "  · ",
            "dim":    "    ",
        }
        color  = colors.get(kind, TEXT_MAIN)
        prefix = prefixes.get(kind, "  ")
        # Use HTML for colored output
        safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = f'<span style="color:{color};">{prefix}{safe}</span>'
        self._log_text.appendHtml(html)

    def _log_separator(self):
        self._log_text.appendHtml(
            f'<span style="color:{BORDER};">{"─" * 60}</span>'
        )

    def _build_right_panel(self):
        panel = QWidget()
        panel.setFixedWidth(290)
        panel.setObjectName("rightPanel")

        # Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {BG_PANEL}; border: none;")

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)

        # ── Algorithm Parameters ─────────────────────────────────────────────
        algo_grp = QGroupBox("Algorithm Parameters")
        algo_grp.setObjectName("infoGroup")
        algo_layout = QVBoxLayout(algo_grp)
        algo_layout.setSpacing(6)

        # Algorithm selector
        algo_layout.addWidget(self._dim_label("Algorithm:"))
        self._algo_selector = QComboBox()
        self._algo_selector.addItems([name for name, _, _ in ALGO_DEFS])
        self._algo_selector.setFont(QFont("Consolas", 10))
        self._algo_selector.setStyleSheet(f"""
            QComboBox {{ background: {BG_CARD}; color: {TEXT_MAIN}; border: 1px solid {BORDER};
                         border-radius: 4px; padding: 4px 8px; }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{ background: {BG_CARD2}; color: {TEXT_MAIN};
                                           selection-background-color: {ACCENT_BLUE}44; }}
        """)
        algo_layout.addWidget(self._algo_selector)

        # Source node
        algo_layout.addWidget(self._dim_label("Source node:"))
        self._param_source = QLineEdit()
        self._param_source.setPlaceholderText("ex: A, S ...")
        self._param_source.setFont(QFont("Consolas", 10))
        self._param_source.setStyleSheet(self._field_style())
        algo_layout.addWidget(self._param_source)

        # Sink / target node
        algo_layout.addWidget(self._dim_label("Target / Sink node:"))
        self._param_sink = QLineEdit()
        self._param_sink.setPlaceholderText("ex: T, Z ... (optional)")
        self._param_sink.setFont(QFont("Consolas", 10))
        self._param_sink.setStyleSheet(self._field_style())
        algo_layout.addWidget(self._param_sink)

        layout.addWidget(algo_grp)

        # ── Execution Info ───────────────────────────────────────────────────
        exec_grp = QGroupBox("Execution Info")
        exec_grp.setObjectName("infoGroup")
        exec_layout = QVBoxLayout(exec_grp)
        exec_layout.setSpacing(4)

        exec_rows = [
            ("exec_status",     "Status"),
            ("exec_complexity", "Complexity"),
            ("exec_time",       "Exec. Time"),
        ]
        self._exec_labels: dict[str, QLabel] = {}
        for key, txt in exec_rows:
            row = QHBoxLayout()
            k = QLabel(txt + ":")
            k.setFont(QFont("Consolas", 10))
            k.setStyleSheet(f"color: {TEXT_DIM};")
            v = QLabel("—")
            v.setFont(QFont("Consolas", 10, QFont.Bold))
            v.setStyleSheet(f"color: {TEXT_MAIN};")
            v.setAlignment(Qt.AlignRight)
            row.addWidget(k)
            row.addWidget(v)
            exec_layout.addLayout(row)
            self._exec_labels[key] = v

        layout.addWidget(exec_grp)

        # ── Graph Information ────────────────────────────────────────────────
        info_grp = QGroupBox("Graph Information")
        info_grp.setObjectName("infoGroup")
        info_layout = QVBoxLayout(info_grp)
        info_layout.setSpacing(4)

        self._info_labels: dict[str, QLabel] = {}
        props = [
            ("nodes",       "Nodes"),
            ("edges",       "Edges"),
            ("connected",   "Connected"),
            ("components",  "Components"),
            ("complete",    "Complete"),
            ("regular",     "Regular"),
            ("bipartite",   "Bipartite"),
            ("is_tree",     "Is Tree"),
            ("density",     "Density"),
        ]
        for key, display in props:
            row = QHBoxLayout()
            k_lbl = QLabel(display + ":")
            k_lbl.setFont(QFont("Consolas", 10))
            k_lbl.setStyleSheet(f"color: {TEXT_DIM};")
            v_lbl = QLabel("—")
            v_lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            v_lbl.setStyleSheet(f"color: {TEXT_MAIN};")
            v_lbl.setAlignment(Qt.AlignRight)
            row.addWidget(k_lbl)
            row.addWidget(v_lbl)
            info_layout.addLayout(row)
            self._info_labels[key] = v_lbl

        layout.addWidget(info_grp)

        # ── Eulerian ─────────────────────────────────────────────────────────
        euler_grp = QGroupBox("Eulerian Properties")
        euler_grp.setObjectName("infoGroup")
        euler_layout = QVBoxLayout(euler_grp)
        euler_layout.setSpacing(4)
        self._euler_circuit_lbl = QLabel("—")
        self._euler_path_lbl    = QLabel("—")
        for lbl, text in [(self._euler_circuit_lbl, "Eulerian Circuit:"),
                          (self._euler_path_lbl,    "Eulerian Path:")]:
            row = QHBoxLayout()
            k = QLabel(text)
            k.setFont(QFont("Consolas", 10))
            k.setStyleSheet(f"color: {TEXT_DIM};")
            lbl.setFont(QFont("Consolas", 10, QFont.Bold))
            lbl.setAlignment(Qt.AlignRight)
            row.addWidget(k)
            row.addWidget(lbl)
            euler_layout.addLayout(row)
        layout.addWidget(euler_grp)

        # ── Adjacency Matrix ─────────────────────────────────────────────────
        mat_grp = QGroupBox("Adjacency Matrix")
        mat_grp.setObjectName("infoGroup")
        mat_layout = QVBoxLayout(mat_grp)
        mat_layout.setContentsMargins(4, 8, 4, 8)

        self._matrix_table = QTableWidget(0, 0)
        self._matrix_table.setFixedHeight(160)
        self._matrix_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._matrix_table.setStyleSheet(f"""
            QTableWidget {{ background: {BG_DARK}; color: {TEXT_MAIN};
                            border: none; gridline-color: {BORDER}; font-size: 10px; }}
            QHeaderView::section {{ background: {BG_CARD2}; color: {TEXT_DIM};
                                    border: 1px solid {BORDER}; padding: 2px; font-size: 10px; }}
            QTableWidget::item {{ padding: 2px; text-align: center; }}
            QTableWidget::item:selected {{ background: {ACCENT_BLUE}33; }}
        """)
        self._matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        mat_layout.addWidget(self._matrix_table)
        layout.addWidget(mat_grp)

        layout.addStretch()
        scroll.setWidget(inner)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return panel

    def _dim_label(self, text):
        l = QLabel(text)
        l.setFont(QFont("Consolas", 10))
        l.setStyleSheet(f"color: {TEXT_DIM};")
        return l

    def _field_style(self):
        return (f"QLineEdit {{ background: {BG_CARD}; color: {TEXT_MAIN}; "
                f"border: 1px solid {BORDER}; border-radius: 4px; padding: 5px 8px; }}"
                f"QLineEdit:focus {{ border: 1px solid {ACCENT_BLUE}; }}")

    def _hdiv(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {BORDER};")
        return line

    def _style_toggle(self, btn, color):
        btn.setCursor(Qt.PointingHandCursor)
        def _upd(checked):
            if checked:
                btn.setStyleSheet(f"""QPushButton {{ background: {color}22; color: {color};
                    border: 1px solid {color}88; border-radius: 6px; text-align: left; padding: 0 12px; }}
                    QPushButton:hover {{ background: {color}44; }}""")
            else:
                btn.setStyleSheet(f"""QPushButton {{ background: transparent; color: {TEXT_DIM};
                    border: 1px solid {BORDER}; border-radius: 6px; text-align: left; padding: 0 12px; }}
                    QPushButton:hover {{ background: {BG_CARD}; }}""")
        btn.toggled.connect(_upd)
        _upd(btn.isChecked())

    def _action_btn(self, text, color):
        btn = QPushButton(text)
        btn.setFont(QFont("Consolas", 11))
        btn.setFixedHeight(34)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{ background: {color}22; color: {color}; border: 1px solid {color}55;
                           border-radius: 6px; text-align: left; padding: 0 12px; }}
            QPushButton:hover {{ background: {color}44; border: 1px solid {color}; }}
        """)
        return btn

    # ── Global Style ──────────────────────────────────────────────────────────
    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {BG_DARK}; color: {TEXT_MAIN}; }}
            #sidebar {{ background: {BG_PANEL}; border-right: 1px solid {BORDER}; }}
            #rightPanel {{ background: {BG_PANEL}; border-left: 1px solid {BORDER}; }}
            #bottomBar {{ background: {BG_PANEL}; border-bottom: 1px solid {BORDER}; }}
            #logPanel {{ background: {BG_DARK}; border-top: 1px solid {BORDER}; }}
            #logHeader {{ background: {BG_PANEL}; border-bottom: 1px solid {BORDER}; }}
            #centerWrap {{ background: {BG_DARK}; }}
            QGroupBox#infoGroup {{
                background: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 8px; margin-top: 8px; padding: 8px;
                color: {TEXT_LABEL}; font-size: 11px; font-family: Consolas;
            }}
            QGroupBox#infoGroup::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 6px; color: {TEXT_DIM};
            }}
            QLabel {{ color: {TEXT_MAIN}; }}
        """)

    # ── Mode switching ────────────────────────────────────────────────────────
    _mode_btns: list

    def _set_mode(self, mode):
        btns = {
            "select":   self._btn_select,
            "add_node": self._btn_add_node,
            "add_edge": self._btn_add_edge,
            "delete":   self._btn_delete,
        }
        for m, btn in btns.items():
            btn.setChecked(m == mode)
        self._scene.set_mode(mode)
        hints = {
            "select":   "Click and drag nodes to move them. Double-click to rename.",
            "add_node": "Click anywhere on canvas to place a node.",
            "add_edge": "Click source node, then destination node.",
            "delete":   "Click on a node or edge to delete it.",
            "reverse":  "Select an edge and click to reverse its direction.",
            "edit":     "Select an edge and click to edit weight/capacity.",
        }
        self._status_lbl.setText(hints.get(mode, ""))

    def _reverse_selected_edge(self):
        """Reverse direction of selected edge."""
        # Find selected edge in scene
        selected_edge = None
        for e in self._scene._edges:
            if e.isSelected():
                selected_edge = e
                break
        
        if selected_edge:
            selected_edge.reverse()
            self._scene.graph_changed.emit()
            self._log("Edge direction reversed", "result")
        else:
            self._log("No edge selected. Select an edge first.", "warn")

    def _edit_selected_edge(self):
        """Edit weight and capacity of selected edge."""
        selected_edge = None
        for e in self._scene._edges:
            if e.isSelected():
                selected_edge = e
                break
        
        if selected_edge:
            parent_widget = self.views()[0].window() if self.views() else None
            dlg = WeightDialog(
                parent=parent_widget,
                default_weight=selected_edge.weight,
                default_capacity=selected_edge.capacity,
                is_directed=self._scene._directed_graph,
                weighted=self._scene._weighted_graph,
                capacity_enabled=self._scene._capacity_graph,
            )
            if dlg.exec():
                selected_edge.weight = dlg.get_weight()
                selected_edge.capacity = dlg.get_capacity()
                selected_edge.update_path()
                self._scene.graph_changed.emit()
                self._log(f"Edge updated: weight={selected_edge.weight}, capacity={selected_edge.capacity}", "result")
        else:
            self._log("No edge selected. Select an edge first.", "warn")

    # ── Graph type changes ────────────────────────────────────────────────────
    def _on_directed_changed(self, checked):
        self._scene.set_directed(checked)

    def _on_weighted_changed(self, checked):
        self._scene.set_weighted(checked)

        # 🔥 RESET DES POIDS
        for e in self._scene._edges:
            if checked:
                e.weight = 0
            e.update_path()

        self._scene.graph_changed.emit()

    def _on_capacity_changed(self, checked):
        self._scene.set_capacity(checked)

        # 🔥 RESET DES CAPACITÉS
        for e in self._scene._edges:
            if checked:
                e.capacity = 0
            e.update_path()

        self._scene.graph_changed.emit()

    # ── Graph changed callback ────────────────────────────────────────────────
    def _on_graph_changed(self):
        data = self._scene.get_graph_data()
        n = len(data["graph"]["nodes"])
        m = len(data["graph"]["edges"])
        self._nodes_lbl.setText(f"Nodes: {n}")
        self._edges_lbl.setText(f"Edges: {m}")

        # Update matrix
        labels, mat = self._scene.get_adjacency_matrix()
        self._update_matrix(labels, mat)

        # Update properties
        props = self._scene.get_properties()
        self._update_properties(props)

        # Update algo buttons
        self._update_algo_buttons(props, data["graph"])

    def _update_matrix(self, labels, mat):
        n = len(labels)
        self._matrix_table.setRowCount(n)
        self._matrix_table.setColumnCount(n)
        self._matrix_table.setHorizontalHeaderLabels(labels)
        self._matrix_table.setVerticalHeaderLabels(labels)
        for i in range(n):
            for j in range(n):
                val = mat[i][j]
                if val is None:
                    txt = "—"
                    color = QColor(TEXT_DIM)
                else:
                    txt = str(int(val)) if val == int(val) else str(val)
                    color = QColor(ACCENT_CYAN) if i != j else QColor(ACCENT_AMBER)
                item = QTableWidgetItem(txt)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QBrush(color))
                self._matrix_table.setItem(i, j, item)

    def _update_properties(self, props):
        if not props:
            for lbl in self._info_labels.values():
                lbl.setText("—")
                lbl.setStyleSheet(f"color: {TEXT_DIM};")
            self._euler_circuit_lbl.setText("—")
            self._euler_path_lbl.setText("—")
            return

        bool_map = {True: ("Yes", ACCENT_CYAN), False: ("No", "#f76f8e")}

        def set_bool(key, val):
            txt, col = bool_map.get(val, ("—", TEXT_DIM))
            self._info_labels[key].setText(txt)
            self._info_labels[key].setStyleSheet(f"color: {col}; font-weight: bold;")

        self._info_labels["nodes"].setText(str(props.get("nodes", "—")))
        self._info_labels["nodes"].setStyleSheet(f"color: {TEXT_MAIN};")
        self._info_labels["edges"].setText(str(props.get("edges", "—")))
        self._info_labels["edges"].setStyleSheet(f"color: {TEXT_MAIN};")
        self._info_labels["components"].setText(str(props.get("components", "—")))
        self._info_labels["components"].setStyleSheet(f"color: {TEXT_MAIN};")
        self._info_labels["density"].setText(str(props.get("density", "—")))
        self._info_labels["density"].setStyleSheet(f"color: {TEXT_MAIN};")

        set_bool("connected",  props.get("connected", False))
        set_bool("complete",   props.get("complete", False))
        set_bool("bipartite",  props.get("bipartite", False))
        set_bool("is_tree",    props.get("is_tree", False))

        if props.get("regular"):
            self._info_labels["regular"].setText(f"Yes ({props['reg_degree']}-reg)")
            self._info_labels["regular"].setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold;")
        else:
            self._info_labels["regular"].setText("No")
            self._info_labels["regular"].setStyleSheet(f"color: #f76f8e; font-weight: bold;")

        ec = props.get("eulerian_circuit", False)
        ep = props.get("eulerian_path", False)
        ec_txt, ec_col = bool_map.get(ec, ("—", TEXT_DIM))
        ep_txt, ep_col = bool_map.get(ep, ("—", TEXT_DIM))
        self._euler_circuit_lbl.setText(ec_txt)
        self._euler_circuit_lbl.setStyleSheet(f"color: {ec_col}; font-weight: bold;")
        self._euler_path_lbl.setText(ep_txt)
        self._euler_path_lbl.setStyleSheet(f"color: {ep_col}; font-weight: bold;")

    def _update_algo_buttons(self, props, graph_data):
        n = props.get("nodes", 0)
        m = props.get("edges", 0)
        directed  = graph_data.get("directed", True)
        weighted  = graph_data.get("metadata", {}).get("weighted", True)
        eulerian  = props.get("eulerian_circuit", False) or props.get("eulerian_path", False)

        availability = {
            "Bellman-Ford":          n > 0 and m > 0,
            "Dijkstra":              n > 0 and m > 0 and weighted,
            "Bellman":               n > 0 and m > 0,
            "Kruskal":               n > 0 and m > 0 and not directed,
            "Prim":                  n > 0 and m > 0 and not directed,
            "Composantes Connexes":  n > 0,
            "Chemin Eulérien":       n > 0 and eulerian,
            "Welsh-Powell":          n > 0,
        }
        for name, avail in availability.items():
            if name in self._algo_btns:
                self._algo_btns[name].set_available(avail)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _clear_graph(self):
        reply = QMessageBox.question(self, "Clear Graph",
            "Are you sure you want to clear the entire graph?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._scene.clear()
            self._scene._nodes.clear()
            self._scene._edges.clear()
            self._scene._node_counter = 0
            self._on_graph_changed()

    def _export_json(self):
        algo_name, algo_cat = self._get_selected_algo_info()
        params = {}
        if self._param_source.text().strip():
            params["source"] = self._param_source.text().strip()
        if self._param_sink.text().strip():
            params["sink"] = self._param_sink.text().strip()

        data = self._scene.get_graph_data(
            algo_name=algo_name,
            algo_category=algo_cat,
            algo_params=params,
        )
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export Graph JSON",
                                               "graph.json", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Exported", f"Graph exported to:\n{path}")

    def _get_selected_algo_info(self):
        name = self._algo_selector.currentText()
        cat_map = {n: c for n, c, _ in ALGO_DEFS}
        return name, cat_map.get(name, "shortest_path")

    def _run_algo(self, name):
        import requests

        algo_name, algo_cat = self._get_selected_algo_info()

        params = {}
        if self._param_source.text().strip():
            params["source"] = self._param_source.text().strip()
        if self._param_sink.text().strip():
            params["sink"] = self._param_sink.text().strip()

        # Build JSON from graph
        data = self._scene.get_graph_data(
            algo_name=algo_name,
            algo_category=algo_cat,
            algo_params=params,
        )

        self._log(f"Sending graph to backend...", "info")

        try:
            response = requests.post(
                "http://127.0.0.1:5000/run-algorithm",
                json=data,
                timeout=10
            )

            result = response.json()

            self._log("Received result from backend", "info")

            self._handle_backend_result(result)

        except Exception as e:
            self._log(f"Backend error: {e}", "error")
    # ── Per-algorithm log writers ─────────────────────────────────────────────

    def _node_map(self, edges):
        """Build adjacency: {label: [(neighbor, weight, capacity)]}"""
        adj = {}
        for e in edges:
            f, t, w, c = e["from"], e["to"], e.get("weight", 1), e.get("capacity", 1)
            adj.setdefault(f, []).append((t, w, c))
            if not self._scene._directed_graph:
                adj.setdefault(t, []).append((f, w, c))
        return adj
    def _handle_backend_result(self, result):
        res = result.get("result", {})
        # Clear old styles first
        self._reset_graph_style()

        # Shortest path
        if res.get("path"):
            self._highlight_path(res["path"])

        # MST
        if res.get("mst_edges"):
            self._highlight_edges(res["mst_edges"])

        # Coloring
        if res.get("coloring"):
            self._apply_coloring(res["coloring"]["node_colors"])

        self._log("Graph updated with backend result", "result")
    def _reset_graph_style(self):
        for e in self._scene._edges:
            e.setPen(QPen(QColor("#6272a4"), 2.5))

        for n in self._scene._nodes.values():
            n._update_appearance()
    def _highlight_path(self, path):
        pairs = list(zip(path, path[1:]))

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in pairs:
                e.setPen(QPen(QColor("#ff5555"), 4))
    def _highlight_edges(self, edges):
        edge_set = {(e["from"], e["to"]) for e in edges}

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in edge_set:
                e.setPen(QPen(QColor("#50fa7b"), 4))
    def _apply_coloring(self, colors):
        for node in self._scene._nodes.values():
            if node.label in colors:
                node.setBrush(QBrush(QColor(colors[node.label])))
# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GraphAlgo Pro")
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window,      QColor(BG_DARK))
    palette.setColor(QPalette.WindowText,  QColor(TEXT_MAIN))
    palette.setColor(QPalette.Base,        QColor(BG_CARD))
    palette.setColor(QPalette.AlternateBase, QColor(BG_CARD2))
    palette.setColor(QPalette.Text,        QColor(TEXT_MAIN))
    palette.setColor(QPalette.Button,      QColor(BG_PANEL))
    palette.setColor(QPalette.ButtonText,  QColor(TEXT_MAIN))
    palette.setColor(QPalette.Highlight,   QColor(ACCENT_BLUE))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()