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
        self.resize(900, 680)
        self.parent_window = parent
        self._current_data = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet(f"background: {BG_PANEL}; border-bottom: 1px solid {BORDER};")
        tlay = QHBoxLayout(toolbar)
        tlay.setContentsMargins(12, 6, 12, 6)
        tlay.setSpacing(10)

        btn_load = QPushButton("📂  Load JSON")
        btn_load.setFont(QFont("Consolas", 11))
        btn_load.setFixedHeight(34)
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setStyleSheet(f"""
            QPushButton {{ background: {ACCENT_BLUE}22; color: {ACCENT_BLUE};
                           border: 1px solid {ACCENT_BLUE}55; border-radius: 6px; padding: 0 14px; }}
            QPushButton:hover {{ background: {ACCENT_BLUE}44; border-color: {ACCENT_BLUE}; }}
        """)
        btn_load.clicked.connect(self.load_json)
        tlay.addWidget(btn_load)

        tlay.addSpacing(8)
        self._legend_label = QLabel("")
        self._legend_label.setFont(QFont("Consolas", 10))
        self._legend_label.setStyleSheet(f"color: {TEXT_DIM};")
        tlay.addWidget(self._legend_label)

        tlay.addStretch()

        self._algo_badge = QLabel("")
        self._algo_badge.setFont(QFont("Consolas", 10, QFont.Bold))
        self._algo_badge.setStyleSheet(
            f"color: {ACCENT_CYAN}; background: {ACCENT_CYAN}22; "
            f"border: 1px solid {ACCENT_CYAN}55; border-radius: 4px; padding: 2px 10px;"
        )
        self._algo_badge.hide()
        tlay.addWidget(self._algo_badge)

        layout.addWidget(toolbar)

        # Body: canvas + info panel
        body = QSplitter(Qt.Horizontal)
        body.setStyleSheet(f"QSplitter::handle {{ background: {BORDER}; width: 4px; }}")

        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        body.addWidget(self.view)

        info_panel = self._build_info_panel()
        body.addWidget(info_panel)

        body.setStretchFactor(0, 3)
        body.setStretchFactor(1, 1)
        body.setSizes([640, 260])

        layout.addWidget(body, 1)
        self._apply_style()

    def _build_info_panel(self):
        panel = QWidget()
        panel.setFixedWidth(260)
        panel.setStyleSheet(f"background: {BG_PANEL}; border-left: 1px solid {BORDER};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(10)

        # Result Summary
        res_grp = QGroupBox("Result Summary")
        res_grp.setObjectName("infoGroup")
        res_layout = QVBoxLayout(res_grp)
        res_layout.setSpacing(4)

        self._result_labels = {}
        for key, display in [
            ("algo",        "Algorithm"),
            ("status",      "Status"),
            ("complexity",  "Complexity"),
            ("exec_time",   "Exec. Time"),
            ("path",        "Path"),
            ("total_cost",  "Total Cost"),
        ]:
            row = QHBoxLayout()
            k = QLabel(display + ":")
            k.setFont(QFont("Consolas", 9))
            k.setStyleSheet(f"color: {TEXT_DIM};")
            v = QLabel("--")
            v.setFont(QFont("Consolas", 9, QFont.Bold))
            v.setStyleSheet(f"color: {TEXT_MAIN};")
            v.setAlignment(Qt.AlignRight)
            v.setWordWrap(True)
            
            # Make status label clickable to log errors
            if key == "status":
                v.setCursor(Qt.PointingHandCursor)
                v.mousePressEvent = lambda event, s=v: self._on_status_clicked()
                self._status_label = v
            
            row.addWidget(k, 1)
            row.addWidget(v, 2)
            res_layout.addLayout(row)
            self._result_labels[key] = v

        layout.addWidget(res_grp)

        # Distances
        dist_grp = QGroupBox("Distances from Source")
        dist_grp.setObjectName("infoGroup")
        dist_layout = QVBoxLayout(dist_grp)
        dist_layout.setSpacing(2)

        self._dist_table = QTableWidget(0, 2)
        self._dist_table.setHorizontalHeaderLabels(["Node", "Distance"])
        self._dist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._dist_table.setSelectionMode(QAbstractItemView.NoSelection)
        self._dist_table.setFixedHeight(160)
        self._dist_table.setStyleSheet(f"""
            QTableWidget {{ background: {BG_DARK}; color: {TEXT_MAIN};
                            border: none; gridline-color: {BORDER}; font-size: 10px; }}
            QHeaderView::section {{ background: {BG_CARD2}; color: {TEXT_DIM};
                                    border: 1px solid {BORDER}; padding: 2px; font-size: 10px; }}
            QTableWidget::item {{ padding: 2px; }}
        """)
        self._dist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._dist_table.verticalHeader().hide()
        dist_layout.addWidget(self._dist_table)
        layout.addWidget(dist_grp)

        # Steps log
        steps_grp = QGroupBox("Execution Steps")
        steps_grp.setObjectName("infoGroup")
        steps_layout = QVBoxLayout(steps_grp)
        steps_layout.setSpacing(0)

        self._steps_log = QPlainTextEdit()
        self._steps_log.setReadOnly(True)
        self._steps_log.setFont(QFont("Consolas", 9))
        self._steps_log.setFixedHeight(150)
        self._steps_log.setStyleSheet(f"""
            QPlainTextEdit {{ background: {BG_DARK}; color: {TEXT_MAIN};
                              border: none; padding: 6px; }}
        """)
        steps_layout.addWidget(self._steps_log)
        layout.addWidget(steps_grp)

        layout.addStretch()
        scroll.setWidget(inner)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        return panel

    def _apply_style(self):
        self.setStyleSheet(f"""
            QDialog, QWidget {{ background: {BG_DARK}; color: {TEXT_MAIN}; }}
            QGroupBox#infoGroup {{
                background: {BG_CARD}; border: 1px solid {BORDER};
                border-radius: 8px; margin-top: 8px; padding: 8px;
                color: {TEXT_LABEL}; font-size: 11px; font-family: Consolas;
            }}
            QGroupBox#infoGroup::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 6px; color: {TEXT_DIM};
            }}
        """)

    # ── JSON Loading ──────────────────────────────────────────────────────────

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON (*.json)")
        if not path:
            return

        with open(path, "r") as f:
            data = json.load(f)

        self._current_data = data
        self.draw_graph(data)
        self.apply_result(data)
        self._populate_info(data)
        self._check_and_log_errors(data)

    def draw_graph(self, data):
        self.scene.clear()
        self.scene._nodes.clear()
        self.scene._edges.clear()

        positions = data["graph"]["node_positions"]
        category  = data.get("algorithm", {}).get("category", "")
        path      = data.get("result", {}).get("path", [])

        # For shortest_path results, only render nodes/edges on the path
        if category == "shortest_path" and len(path) >= 2:
            visible_nodes = set(path)
            path_pairs    = set(zip(path, path[1:]))

            nodes_to_draw = [lbl for lbl in data["graph"]["nodes"] if lbl in visible_nodes]
            edges_to_draw = [
                e for e in data["graph"]["edges"]
                if (e["from"], e["to"]) in path_pairs
            ]
        else:
            nodes_to_draw = data["graph"]["nodes"]
            edges_to_draw = data["graph"]["edges"]

        # Create nodes — scale positions for better visibility
        for i, label in enumerate(nodes_to_draw):
            pos = positions[label]
            node = NodeItem(i, label, pos["x"] * 2, pos["y"] * 2, self.scene)
            self.scene.addItem(node)
            self.scene._nodes[i] = node

        label_to_node = {n.label: n for n in self.scene._nodes.values()}

        # Create edges
        for e in edges_to_draw:
            src = label_to_node.get(e["from"])
            dst = label_to_node.get(e["to"])
            if src is None or dst is None:
                continue
            edge = EdgeItem(
                src,
                dst,
                e.get("weight", 1),
                e.get("capacity", 1),
                data["graph"]["directed"]
            )
            self.scene.addItem(edge)
            edge.update_path()
            self.scene._edges.append(edge)

        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def apply_result(self, data):
        result   = data.get("result", {})
        category = data.get("algorithm", {}).get("category", "")

        path = result.get("path", [])

        # In shortest_path mode the canvas only contains path nodes/edges —
        # no need to reset the whole graph first.
        if category != "shortest_path":
            for e in self.scene._edges:
                e.setPen(QPen(QColor("#6272a4"), 2.5))
            for n in self.scene._nodes.values():
                n._update_appearance()

        # ── 1. Shortest Path ─────────────────────────────────────────────────
        if path and len(path) >= 2:
            path_pairs = set(zip(path, path[1:]))
            path_nodes = set(path)

            for e in self.scene._edges:
                if (e.src.label, e.dst.label) in path_pairs:
                    e.setPen(QPen(QColor("#ff5555"), 4))

            for node in self.scene._nodes.values():
                if node.label == path[0]:
                    # Source: green
                    node.setBrush(QBrush(QColor("#50fa7b")))
                    node.setPen(QPen(QColor("#50fa7b"), 2))
                elif node.label == path[-1]:
                    # Target: red
                    node.setBrush(QBrush(QColor("#ff5555")))
                    node.setPen(QPen(QColor("#ff5555"), 2))
                elif node.label in path_nodes:
                    # Intermediate: orange
                    node.setBrush(QBrush(QColor("#ffb86c")))
                    node.setPen(QPen(QColor("#ffb86c"), 2))

            self._legend_label.setText(
                "  \U0001f7e2 Source   \U0001f7e0 Via   \U0001f534 Target   \u2501\u2501 Path"
            )

        # ── 2. MST edges ─────────────────────────────────────────────────────
        mst = result.get("mst_edges", [])
        if mst:
            mst_set = {(e["from"], e["to"]) for e in mst}
            for e in self.scene._edges:
                if (e.src.label, e.dst.label) in mst_set or \
                   (e.dst.label, e.src.label) in mst_set:
                    e.setPen(QPen(QColor("#50fa7b"), 4))
            self._legend_label.setText("  \U0001f7e2 MST Edges")

        # ── 3. Traversal tree edges (only if no path result) ─────────────────
        traversal = result.get("traversal", {})
        tree_edges = traversal.get("tree_edges", [])
        if tree_edges and not path:
            tree_set = {(e["from"], e["to"]) for e in tree_edges}
            for e in self.scene._edges:
                if (e.src.label, e.dst.label) in tree_set:
                    e.setPen(QPen(QColor("#8be9fd"), 3))
            self._legend_label.setText("  \U0001f535 Traversal Tree Edges")

        # ── 4. Node coloring ─────────────────────────────────────────────────
        coloring = result.get("coloring", {})
        node_colors = coloring.get("node_colors", {})
        if node_colors:
            for node in self.scene._nodes.values():
                if node.label in node_colors:
                    node.setBrush(QBrush(QColor(node_colors[node.label])))
            self._legend_label.setText("  \U0001f3a8 Node Coloring Applied")

        # ── 5. Flow edges ─────────────────────────────────────────────────────
        flow = result.get("flow", {})
        edge_flows = flow.get("edge_flows", {})
        if edge_flows:
            for e in self.scene._edges:
                key = f"{e.src.label}->{e.dst.label}"
                if key in edge_flows and edge_flows[key] > 0:
                    e.setPen(QPen(QColor("#bd93f9"), 4))
            self._legend_label.setText("  \U0001f7e3 Flow Edges")

    def _populate_info(self, data):
        result = data.get("result", {})
        algo   = data.get("algorithm", {})
        exec_  = data.get("execution", {})

        algo_name = algo.get("name", "")
        if algo_name:
            self._algo_badge.setText(f"  {algo_name}  ")
            self._algo_badge.show()

        self._result_labels["algo"].setText(algo_name or "--")
        self._result_labels["status"].setText(exec_.get("status", "--"))
        self._result_labels["complexity"].setText(exec_.get("complexity", "--"))

        t = exec_.get("execution_time")
        self._result_labels["exec_time"].setText(f"{t:.4f}s" if t is not None else "--")

        path = result.get("path", [])
        self._result_labels["path"].setText(" -> ".join(path) if path else "--")

        distances = result.get("distances", {})
        if path and distances and path[-1] in distances:
            self._result_labels["total_cost"].setText(str(distances[path[-1]]))
        else:
            self._result_labels["total_cost"].setText("--")

        # Distances table
        self._dist_table.setRowCount(0)
        if distances:
            path_nodes = set(path)
            sorted_dists = sorted(distances.items(), key=lambda x: (x[1] if x[1] != float('inf') else 99999))
            for node_label, dist in sorted_dists:
                row = self._dist_table.rowCount()
                self._dist_table.insertRow(row)

                n_item = QTableWidgetItem(node_label)
                n_item.setTextAlignment(Qt.AlignCenter)
                if node_label in path_nodes:
                    if node_label == path[0]:
                        n_item.setForeground(QBrush(QColor("#50fa7b")))
                    elif node_label == path[-1]:
                        n_item.setForeground(QBrush(QColor("#ff5555")))
                    else:
                        n_item.setForeground(QBrush(QColor("#ffb86c")))

                d_item = QTableWidgetItem(str(dist) if dist != float('inf') else "INF")
                d_item.setTextAlignment(Qt.AlignCenter)
                if node_label in path_nodes:
                    d_item.setForeground(QBrush(QColor(ACCENT_AMBER)))
                    d_item.setFont(QFont("Consolas", 9, QFont.Bold))

                self._dist_table.setItem(row, 0, n_item)
                self._dist_table.setItem(row, 1, d_item)

        # Steps log
        self._steps_log.clear()
        steps = result.get("steps", [])
        if steps:
            for step in steps:
                self._steps_log.appendPlainText(f"  > {step}")
        else:
            self._steps_log.appendPlainText("  · No steps recorded.")

    def _check_and_log_errors(self, data):
        """Check if execution status indicates an error and log it to MainWindow."""
        exec_ = data.get("execution", {})
        status = exec_.get("status", "").lower()
        message = exec_.get("message", "")
        
        # Check if status indicates an error
        error_keywords = ["error", "failed", "exception", "invalid", "timeout"]
        is_error = any(keyword in status for keyword in error_keywords)
        
        if is_error and self.parent_window and hasattr(self.parent_window, '_log'):
            # Log the error to the main window's execution log
            self.parent_window._log(f"ERROR in Result Panel: Status = {status}", kind="error")
            if message:
                self.parent_window._log(f"Message: {message}", kind="error")

    def _on_status_clicked(self):
        """Handle status label click to log any errors."""
        if self._current_data:
            self._check_and_log_errors(self._current_data)

