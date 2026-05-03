
from collections import defaultdict
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

from front.WeightDialog import  WeightDialog
from front.EdgeItem import EdgeItem
from front.NodeItem import NodeItem
from front.theme.colors import *
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

    def _get_next_label(self):
        """Return the first label not currently used by any node."""
        used = {n.label for n in self._nodes.values()}
        for lbl in self._node_labels:
            if lbl not in used:
                return lbl
        # Fallback: double letters AA, AB, ...
        for a in self._node_labels:
            for b in self._node_labels:
                lbl = a + b
                if lbl not in used:
                    return lbl
        return "?"

    def _add_node(self, pos):
        nid = self._node_counter
        lbl = self._get_next_label()
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
        # Refresh all edges between the same pair so parallel ones re-space
        self._refresh_parallel_edges(src, dst)
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
            src, dst = item.src, item.dst
            self.removeItem(item)
            self._edges.remove(item)
            self._refresh_parallel_edges(src, dst)
            self.graph_changed.emit()
        elif isinstance(item, QGraphicsTextItem):
            parent = item.parentItem()
            if isinstance(parent, EdgeItem):
                # Save to history for undo
                self._history.append(("delete_edge", parent))
                src, dst = parent.src, parent.dst
                self.removeItem(parent)
                self._edges.remove(parent)
                self._refresh_parallel_edges(src, dst)
                self.graph_changed.emit()

    def _refresh_parallel_edges(self, src, dst):
        """Re-draw all edges between src<->dst so they fan out correctly."""
        for e in self._edges:
            if (e.src is src and e.dst is dst) or (e.src is dst and e.dst is src):
                e.update_path()

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
        adj_undir=defaultdict(list)
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

        # Complete check (direction-sensitive)
        if self._directed_graph:
            # For directed: need bidirectional edges between every pair of nodes
            complete = all(len(adj[i]) == n - 1 and len(adj_in[i]) == n - 1 for i in ids)
        else:
            # For undirected: every node must be connected to all others
            complete = all(len(adj_undir[i]) == n - 1 for i in ids)

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