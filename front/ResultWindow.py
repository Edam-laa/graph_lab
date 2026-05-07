"""
GraphAlgo Pro — PySide6 Graph Editor
Full frontend: drag-and-drop nodes, weighted/directed edges,
adjacency matrix, graph properties, algorithm buttons, JSON export.
"""

import sys
import json
import math
import colorsys
from collections import defaultdict
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

        # JSON Display Panel
        json_panel = self._build_json_panel()
        layout.addWidget(json_panel)

        self._apply_style()

    def set_result_data(self, data):
        """Load a frontend-style result payload into the window."""
        data = self._coerce_result_payload(data)
        self._current_data = data
        self.draw_graph(data)
        self.apply_result(data)
        self._populate_info(data)
        self._check_and_log_errors(data)

    def _coerce_result_payload(self, data):
        """Accept either the frontend payload or the Flask response envelope."""
        if not isinstance(data, dict):
            return {}

        inner = data.get("result")
        if isinstance(inner, dict) and {"graph", "algorithm", "execution", "result"} <= set(inner.keys()):
            return inner

        return data

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
            ("objective",   "Objective"),
            ("status",      "Status"),
            ("complexity",  "Complexity"),
            ("exec_time",   "Exec. Time"),
            ("path",        "Primary Result"),
            ("total_cost",  "Cost / Value"),
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

        # Algorithm-specific details
        details_grp = QGroupBox("Result Details")
        details_grp.setObjectName("infoGroup")
        details_layout = QVBoxLayout(details_grp)
        details_layout.setSpacing(0)

        self._details_log = QPlainTextEdit()
        self._details_log.setReadOnly(True)
        self._details_log.setFont(QFont("Consolas", 9))
        self._details_log.setFixedHeight(130)
        self._details_log.setStyleSheet(f"""
            QPlainTextEdit {{ background: {BG_DARK}; color: {TEXT_MAIN};
                              border: none; padding: 6px; }}
        """)
        details_layout.addWidget(self._details_log)
        layout.addWidget(details_grp)

        # Metrics table
        self._dist_group = QGroupBox("Metrics")
        self._dist_group.setObjectName("infoGroup")
        dist_layout = QVBoxLayout(self._dist_group)
        dist_layout.setSpacing(2)

        self._dist_table = QTableWidget(0, 2)
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
        layout.addWidget(self._dist_group)

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

    def _build_json_panel(self):
        """Build a panel to display raw backend JSON response."""
        panel = QWidget()
        panel.setFixedHeight(180)
        panel.setStyleSheet(f"background: {BG_PANEL}; border-top: 1px solid {BORDER};")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(28)
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(12, 4, 12, 4)
        hlay.setSpacing(8)
        
        title = QLabel("📋  Backend Response JSON")
        title.setFont(QFont("Consolas", 10, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT_DIM};")
        hlay.addWidget(title)
        
        btn_copy = QPushButton("📋 Copy")
        btn_copy.setFont(QFont("Consolas", 9))
        btn_copy.setFixedHeight(24)
        btn_copy.setFixedWidth(70)
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.setStyleSheet(f"""
            QPushButton {{ background: {ACCENT_CYAN}22; color: {ACCENT_CYAN};
                           border: 1px solid {ACCENT_CYAN}55; border-radius: 4px; }}
            QPushButton:hover {{ background: {ACCENT_CYAN}44; border-color: {ACCENT_CYAN}; }}
        """)
        btn_copy.clicked.connect(self._copy_json)
        hlay.addWidget(btn_copy)
        
        hlay.addStretch()
        
        layout.addWidget(header)
        
        # JSON Display
        self._json_display = QPlainTextEdit()
        self._json_display.setReadOnly(True)
        self._json_display.setFont(QFont("Consolas", 8))
        self._json_display.setStyleSheet(f"""
            QPlainTextEdit {{ background: {BG_DARK}; color: {TEXT_MAIN};
                              border: none; padding: 6px; }}
        """)
        layout.addWidget(self._json_display, 1)
        
        return panel

    def _copy_json(self):
        """Copy JSON to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self._json_display.toPlainText())
        QMessageBox.information(self, "Info", "JSON copied to clipboard!")

    def _apply_style(self):
        """Apply stylesheet to the dialog."""
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

        self.set_result_data(data)

    def draw_graph(self, data):
        self.scene.clear()
        self.scene._nodes.clear()
        self.scene._edges.clear()

        graph = data.get("graph", {})
        result = data.get("result", {})
        positions = graph.get("node_positions", {})
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        directed = graph.get("directed", True)
        fallback_positions = self._fallback_positions(nodes)

        category = data.get("algorithm", {}).get("category", "")
        result_type = result.get("type", "")
        path = result.get("path", [])

        # For shortest_path results, only render nodes/edges on the path
        if (category == "shortest_path" or result_type == "shortest_path") and len(path) >= 2:
            visible_nodes = set(path)
            path_pairs    = set(zip(path, path[1:]))

            nodes_to_draw = [lbl for lbl in nodes if lbl in visible_nodes]
            edges_to_draw = [
                e for e in edges
                if (e["from"], e["to"]) in path_pairs
                or (not directed and (e["to"], e["from"]) in path_pairs)
            ]
        elif result_type == "mst" and result.get("mst_edges"):
            mst_edges = [self._normalize_edge(edge) for edge in result.get("mst_edges", [])]
            visible_nodes = {
                label
                for edge in mst_edges
                for label in (edge.get("from"), edge.get("to"))
                if label is not None
            }
            nodes_to_draw = [lbl for lbl in nodes if lbl in visible_nodes]
            edges_to_draw = mst_edges
        else:
            nodes_to_draw = nodes
            edges_to_draw = edges

        # Create nodes — scale positions for better visibility
        for i, label in enumerate(nodes_to_draw):
            pos = positions.get(label, fallback_positions.get(label, {"x": 0, "y": 0}))
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
                directed
            )
            self.scene.addItem(edge)
            edge.update_path()
            self.scene._edges.append(edge)

        bounds = self.scene.itemsBoundingRect()
        if not bounds.isEmpty():
            self.view.fitInView(bounds.adjusted(-40, -40, 40, 40), Qt.KeepAspectRatio)

    def apply_result(self, data):
        result = data.get("result", {})
        graph = data.get("graph", {})
        directed = graph.get("directed", True)
        result_type = result.get("type", "")
        path = result.get("path", [])

        self._legend_label.setText("")
        for e in self.scene._edges:
            if hasattr(e, "set_label_override"):
                e.set_label_override(None)
            e.setPen(QPen(QColor("#6272a4"), 2.5))
        for n in self.scene._nodes.values():
            n._update_appearance()

        # 1. Shortest path
        if path and len(path) >= 2:
            self._highlight_node_path(path, "#ff5555", directed)
            self._legend_label.setText("Source: green | Via: amber | Target: red | Path: red")

        # 2. MST edges
        mst = [self._normalize_edge(edge) for edge in result.get("mst_edges", [])]
        if mst:
            self._highlight_edge_set(mst, QColor("#50fa7b"), 4, directed=False)
            self._legend_label.setText("MST edges highlighted in green")

        # 3. Traversal tree edges
        traversal = result.get("traversal", {})
        tree_edges = [self._normalize_edge(edge) for edge in traversal.get("tree_edges", [])]
        if tree_edges and not path:
            self._highlight_edge_set(tree_edges, QColor("#8be9fd"), 3, directed=directed)
            for label in traversal.get("order", []):
                node = self._node_by_label(label)
                if node:
                    node.setPen(QPen(QColor("#8be9fd"), 2))
            self._legend_label.setText("Traversal tree edges highlighted in cyan")

        # 4. Node coloring
        coloring = result.get("coloring", {})
        node_colors = coloring.get("node_colors", {})
        if node_colors:
            for node in self.scene._nodes.values():
                if node.label in node_colors:
                    node.setBrush(QBrush(QColor(self._color_value(node_colors[node.label]))))
            self._legend_label.setText("Node coloring applied")

        # 5. Flow edges
        flow = self._flow_data(result)
        edge_flows = flow.get("edge_flows", {})
        has_flow_result = result_type == "max_flow" or flow.get("value") is not None or bool(edge_flows)
        if has_flow_result:
            edge_assignments = self._edge_flow_assignments(edge_flows)
            has_positive_flow = False
            for e in self.scene._edges:
                flow_amount = edge_assignments.get(
                    e,
                    self._net_edge_flow(edge_flows, e.src.label, e.dst.label),
                )
                is_positive = self._is_positive_amount(flow_amount)
                has_positive_flow = has_positive_flow or is_positive
                label_color = "#bd93f9" if is_positive else ACCENT_AMBER
                if hasattr(e, "set_label_override"):
                    e.set_label_override(
                        f"{self._format_value(flow_amount)}/{self._format_value(e.capacity)}",
                        label_color,
                    )
                if is_positive:
                    e.setPen(QPen(QColor("#bd93f9"), 4))

            source = data.get("algorithm", {}).get("params", {}).get("source")
            sink = data.get("algorithm", {}).get("params", {}).get("sink")
            for label, color in [(source, "#50fa7b"), (sink, "#ff5555")]:
                node = self._node_by_label(label)
                if node:
                    node.setBrush(QBrush(QColor(color)))
                    node.setPen(QPen(QColor(color), 2))
            if has_positive_flow:
                self._legend_label.setText("Positive flow edges highlighted in purple")
            else:
                self._legend_label.setText("No positive flow | Source: green | Sink: red")

        # 6. Connected components
        components = result.get("components", [])
        if components:
            for comp_idx, component_nodes in enumerate(components):
                color = self._color_from_index(comp_idx)
                for node in self.scene._nodes.values():
                    if node.label in component_nodes:
                        node.setBrush(QBrush(QColor(color)))
                        node.setPen(QPen(QColor(color), 2))
            if len(components) > 1 or result_type in {"connectivity_check", "strong_connectivity_check"}:
                self._legend_label.setText(f"{len(components)} connected component(s)")

        # 7. Eulerian path/circuit
        eulerian_path = result.get("eulerian_path", [])
        eulerian_circuit = result.get("eulerian_circuit", [])
        if eulerian_path and len(eulerian_path) >= 2:
            self._highlight_node_path(eulerian_path, "#ffb86c", directed)
            self._legend_label.setText("Eulerian path highlighted in amber")
        elif eulerian_circuit and len(eulerian_circuit) >= 2:
            self._highlight_node_path(eulerian_circuit, "#f1fa8c", directed)
            self._legend_label.setText("Eulerian circuit highlighted in yellow")

    def _fallback_positions(self, nodes):
        if not nodes:
            return {}

        radius = max(80, 28 * len(nodes))
        result = {}
        for index, label in enumerate(nodes):
            angle = (2 * math.pi * index) / len(nodes)
            result[label] = {
                "x": round(math.cos(angle) * radius, 2),
                "y": round(math.sin(angle) * radius, 2),
            }
        return result

    def _node_by_label(self, label):
        if not label:
            return None
        for node in self.scene._nodes.values():
            if node.label == label:
                return node
        return None

    def _normalize_edge(self, edge):
        if isinstance(edge, dict):
            return {
                "from": edge.get("from"),
                "to": edge.get("to"),
                "weight": edge.get("weight"),
                "capacity": edge.get("capacity"),
            }

        if isinstance(edge, (list, tuple)):
            if len(edge) >= 4:
                return {"from": edge[0], "to": edge[1], "weight": edge[2], "capacity": edge[3]}
            if len(edge) == 3:
                return {"from": edge[0], "to": edge[1], "weight": edge[2], "capacity": None}
            if len(edge) == 2:
                return {"from": edge[0], "to": edge[1], "weight": None, "capacity": None}

        return {"from": None, "to": None, "weight": None, "capacity": None}

    def _flow_data(self, result):
        flow = dict(result.get("flow", {}) or {})
        if "value" not in flow and "max_flow" in result:
            flow["value"] = result.get("max_flow")

        edge_flows = flow.get("edge_flows") or result.get("edge_flows") or {}
        edge_flows = dict(edge_flows) if isinstance(edge_flows, dict) else {}

        augmenting_paths = flow.get("augmenting_paths") or result.get("augmenting_paths") or []
        if not edge_flows and augmenting_paths:
            edge_flows = self._edge_flows_from_augmenting_paths(augmenting_paths)

        flow["edge_flows"] = edge_flows
        flow["augmenting_paths"] = augmenting_paths
        return flow

    def _edge_flows_from_augmenting_paths(self, augmenting_paths):
        edge_flows = {}
        for path_result in augmenting_paths:
            if not isinstance(path_result, dict):
                continue
            amount = path_result.get("flow", 0)
            edges = path_result.get("edges") or self._path_to_edge_items(path_result.get("path", []))
            for edge in edges:
                normalized = self._normalize_edge(edge)
                src = normalized.get("from")
                dst = normalized.get("to")
                if src is None or dst is None:
                    continue
                key = f"{src}->{dst}"
                edge_flows[key] = edge_flows.get(key, 0) + amount
        return edge_flows

    def _path_to_edge_items(self, path):
        if not path:
            return []
        if all(isinstance(item, (list, tuple)) and len(item) >= 2 for item in path):
            return path
        return list(zip(path, path[1:]))

    def _net_edge_flow(self, edge_flows, src, dst):
        forward = self._amount_value(edge_flows.get(f"{src}->{dst}", 0))
        reverse = self._amount_value(edge_flows.get(f"{dst}->{src}", 0))
        return self._clean_number(max(forward - reverse, 0))

    def _display_edge_flows(self, edge_flows):
        scene = getattr(self, "scene", None)
        if scene is None or not scene._edges:
            return edge_flows

        edge_assignments = self._edge_flow_assignments(edge_flows)
        if not edge_assignments:
            return edge_flows

        counts = defaultdict(int)
        display = {}
        for edge in scene._edges:
            base = f"{edge.src.label}->{edge.dst.label}"
            counts[base] += 1
            suffix = f"#{counts[base]}" if counts[base] > 1 else ""
            display[f"{base}{suffix}"] = edge_assignments.get(edge, 0)

        return display

    def _edge_flow_assignments(self, edge_flows):
        if not edge_flows:
            return {}

        scene = getattr(self, "scene", None)
        if scene is None or not scene._edges:
            return {}

        groups = defaultdict(list)
        for edge in scene._edges:
            groups[(edge.src.label, edge.dst.label)].append(edge)

        assignments = {}
        for (src, dst), edges in groups.items():
            remaining = self._amount_value(self._net_edge_flow(edge_flows, src, dst))
            for edge in edges:
                if remaining <= 0:
                    assignments[edge] = 0
                    continue

                cap = edge.capacity
                if cap is None:
                    flow = remaining
                else:
                    flow = min(remaining, self._amount_value(cap))

                assignments[edge] = self._clean_number(flow)
                remaining -= self._amount_value(flow)

        return assignments

    def _amount_value(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0

    def _clean_number(self, value):
        return int(value) if isinstance(value, float) and value.is_integer() else value

    def _is_positive_amount(self, value):
        try:
            return float(value) > 0
        except (TypeError, ValueError):
            return False

    def _edge_matches(self, scene_edge, result_edge, directed=True):
        src = result_edge.get("from")
        dst = result_edge.get("to")
        if scene_edge.src.label == src and scene_edge.dst.label == dst:
            return True
        return not directed and scene_edge.src.label == dst and scene_edge.dst.label == src

    def _highlight_edge_set(self, edges, color, width, directed=True):
        for scene_edge in self.scene._edges:
            if any(self._edge_matches(scene_edge, result_edge, directed) for result_edge in edges):
                scene_edge.setPen(QPen(color, width))

    def _highlight_node_path(self, path, edge_color, directed=True):
        path_edges = [
            {"from": src, "to": dst}
            for src, dst in zip(path, path[1:])
        ]
        self._highlight_edge_set(path_edges, QColor(edge_color), 4, directed=directed)

        path_nodes = set(path)
        for node in self.scene._nodes.values():
            if node.label == path[0]:
                node.setBrush(QBrush(QColor("#50fa7b")))
                node.setPen(QPen(QColor("#50fa7b"), 2))
            elif node.label == path[-1]:
                node.setBrush(QBrush(QColor("#ff5555")))
                node.setPen(QPen(QColor("#ff5555"), 2))
            elif node.label in path_nodes:
                node.setBrush(QBrush(QColor("#ffb86c")))
                node.setPen(QPen(QColor("#ffb86c"), 2))

    def _color_value(self, color):
        if isinstance(color, str) and color.startswith("#"):
            return color
        return self._color_from_index(color)

    def _color_from_index(self, index):
        palette = [
            "#ff5555", "#50fa7b", "#8be9fd", "#ffb86c",
            "#bd93f9", "#f1fa8c", "#ff79c6", "#6272a4",
            "#00f5d4", "#ff006e", "#8338ec", "#3a86ff",
            "#ffbe0b", "#fb5607", "#06d6a0", "#118ab2",
            "#ef476f", "#ffd166", "#06d6a0", "#073b4c",
            "#90dbf4", "#cdb4db", "#ffc8dd", "#bde0fe",
            "#a0c4ff", "#d0f4de", "#fef9c3", "#fde2e4"
        ]
        try:
            idx = int(float(index))
        except (TypeError, ValueError):
            return "#cccccc"

        if idx < 0:
            idx = abs(idx)

        if idx < len(palette):
            return palette[idx]

        hue = (idx * 0.61803398875) % 1.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.65)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def _populate_info(self, data):
        result = data.get("result", {})
        algo   = data.get("algorithm", {})
        exec_  = data.get("execution", {})

        algo_name = algo.get("name", "")
        if algo_name:
            self._algo_badge.setText(f"  {algo_name}  ")
            self._algo_badge.show()
        else:
            self._algo_badge.hide()

        self._result_labels["algo"].setText(algo_name or "--")
        self._result_labels["objective"].setText(
            result.get("objective") or self._build_objective_text(algo, result) or "--"
        )
        self._result_labels["status"].setText(exec_.get("status", "--"))
        self._result_labels["complexity"].setText(exec_.get("complexity", "--"))

        t = exec_.get("execution_time")
        self._result_labels["exec_time"].setText(f"{t:.4f}s" if t is not None else "--")

        primary_text, value_text = self._primary_summary(algo, result)
        self._result_labels["path"].setText(primary_text or "--")
        self._result_labels["total_cost"].setText(value_text or "--")

        self._details_log.clear()
        details = self._detail_lines(algo, result)
        if details:
            for line in details:
                self._details_log.appendPlainText(line)
        else:
            self._details_log.appendPlainText("No algorithm-specific details.")

        self._populate_metric_table(algo, result)

        # Steps log
        self._steps_log.clear()
        steps = result.get("steps", [])
        if steps:
            for step in steps:
                self._steps_log.appendPlainText(f"  > {self._format_step(step)}")
        else:
            self._steps_log.appendPlainText("  - No steps recorded.")

        # Display full JSON response
        self._display_json_response(data)

    def _primary_summary(self, algo, result):
        result_type = result.get("type", "")
        distances = result.get("distances", {})
        path = result.get("path", [])

        if result_type == "shortest_path":
            if path:
                value = distances.get(path[-1], "--")
                return self._format_path(path), self._format_value(value)
            source = algo.get("params", {}).get("source")
            return f"Distances from {source}" if source else "Distances computed", "--"

        if result_type == "mst":
            edges = result.get("mst_edges", [])
            weight = result.get("total_weight")
            return f"{len(edges)} MST edge(s)", self._format_value(weight)

        if result_type == "max_flow":
            flow = self._flow_data(result)
            return "Maximum flow", self._format_value(flow.get("value"))

        if result_type == "traversal":
            order = result.get("traversal", {}).get("order", [])
            return self._format_path(order), f"{len(order)} visited"

        if result_type == "graph_coloring":
            colors = result.get("coloring", {}).get("node_colors", {})
            color_count = len(set(colors.values())) if colors else 0
            return f"{color_count} color(s)", f"{len(colors)} node(s)"

        if result_type == "connectivity_check":
            props = result.get("graph_properties", {})
            return self._bool_text(props.get("is_connected")), f"{len(result.get('components', []))} component(s)"

        if result_type == "strong_connectivity_check":
            props = result.get("graph_properties", {})
            return self._bool_text(props.get("is_strongly_connected")), "--"

        if result_type == "eulerian_analysis":
            tour = result.get("eulerian_circuit") or result.get("eulerian_path") or []
            label = "Eulerian circuit" if result.get("eulerian_circuit") else "Eulerian path"
            if tour:
                return self._format_path(tour), f"{max(len(tour) - 1, 0)} edge(s)"
            return f"No {label.lower()} found", "--"

        return "--", "--"

    def _detail_lines(self, algo, result):
        result_type = result.get("type", "")
        lines = []

        if result_type == "shortest_path":
            path = result.get("path", [])
            distances = result.get("distances", {})
            predecessors = result.get("predecessors", {})
            params = algo.get("params", {})
            if path:
                lines.append(f"Path: {self._format_path(path)}")
                lines.append(f"Total distance: {self._format_value(distances.get(path[-1]))}")
            elif params.get("target") or params.get("sink"):
                target = params.get("target") or params.get("sink")
                lines.append(f"No reachable path to {target}.")
            lines.append(f"Reachable nodes: {sum(1 for d in distances.values() if not self._is_inf(d))}/{len(distances)}")
            if predecessors:
                lines.append("Predecessors:")
                for node, prev in sorted(predecessors.items()):
                    lines.append(f"  {node}: {prev or '-'}")

        elif result_type == "mst":
            lines.append(f"Total weight: {self._format_value(result.get('total_weight'))}")
            for edge in result.get("mst_edges", []):
                e = self._normalize_edge(edge)
                lines.append(f"{e['from']} - {e['to']} (w={self._format_value(e.get('weight'))})")

        elif result_type == "max_flow":
            flow = self._flow_data(result)
            lines.append(f"Max flow value: {self._format_value(flow.get('value'))}")
            augmenting_paths = flow.get("augmenting_paths", [])
            if augmenting_paths:
                lines.append("Augmenting paths:")
                for index, path_result in enumerate(augmenting_paths, start=1):
                    path = path_result.get("path", [])
                    lines.append(f"  {index}. {self._format_path(path)} | flow={self._format_value(path_result.get('flow'))}")
            edge_flows = flow.get("edge_flows", {})
            if edge_flows:
                lines.append("Net edge flows:")
                for edge_key, amount in sorted(self._display_edge_flows(edge_flows).items()):
                    lines.append(f"  {edge_key}: {self._format_value(amount)}")

        elif result_type == "traversal":
            traversal = result.get("traversal", {})
            lines.append(f"Order: {self._format_path(traversal.get('order', []))}")
            for edge in traversal.get("tree_edges", []):
                e = self._normalize_edge(edge)
                lines.append(f"Tree edge: {e['from']} -> {e['to']}")

        elif result_type == "graph_coloring":
            colors = result.get("coloring", {}).get("node_colors", {})
            lines.append(f"Colors used: {len(set(colors.values())) if colors else 0}")
            for node, color in sorted(colors.items()):
                lines.append(f"{node}: {color}")

        elif result_type in {"connectivity_check", "strong_connectivity_check"}:
            props = result.get("graph_properties", {})
            if "is_connected" in props:
                lines.append(f"Connected: {self._bool_text(props.get('is_connected'))}")
            if "is_strongly_connected" in props:
                lines.append(f"Strongly connected: {self._bool_text(props.get('is_strongly_connected'))}")
            components = result.get("components", [])
            if components:
                lines.append(f"Components: {len(components)}")
                for index, component in enumerate(components, start=1):
                    lines.append(f"  C{index}: {', '.join(str(node) for node in component)}")

        elif result_type == "eulerian_analysis":
            props = result.get("graph_properties", {})
            lines.append(f"Eulerian: {self._bool_text(props.get('is_eulerian'))}")
            path = result.get("eulerian_path", [])
            circuit = result.get("eulerian_circuit", [])
            if circuit:
                lines.append(f"Circuit: {self._format_path(circuit)}")
            elif path:
                lines.append(f"Path: {self._format_path(path)}")
            else:
                lines.append("No Eulerian path or circuit exists.")

        return lines

    def _populate_metric_table(self, algo, result):
        result_type = result.get("type", "")

        if result_type == "shortest_path":
            distances = result.get("distances", {})
            path_nodes = set(result.get("path", []))
            rows = [
                [node, self._format_value(distance)]
                for node, distance in sorted(distances.items(), key=lambda item: self._distance_sort_key(item[1]))
            ]
            self._set_table("Distances From Source", ["Node", "Distance"], rows, path_nodes)
            return

        if result_type == "traversal":
            traversal = result.get("traversal", {})
            if traversal.get("levels"):
                rows = [[node, self._format_value(level)] for node, level in sorted(traversal["levels"].items())]
                self._set_table("Traversal Levels", ["Node", "Level"], rows, set(traversal.get("order", [])))
                return
            if traversal.get("times"):
                rows = [
                    [node, self._format_value(times.get("discover")), self._format_value(times.get("finish"))]
                    for node, times in sorted(traversal["times"].items())
                ]
                self._set_table("DFS Times", ["Node", "Discover", "Finish"], rows, set(traversal.get("order", [])))
                return

        if result_type == "graph_coloring":
            colors = result.get("coloring", {}).get("node_colors", {})
            rows = [[node, str(color)] for node, color in sorted(colors.items())]
            self._set_table("Node Colors", ["Node", "Color"], rows, set(colors.keys()))
            return

        if result_type == "max_flow":
            edge_flows = self._flow_data(result).get("edge_flows", {})
            display_flows = self._display_edge_flows(edge_flows)
            rows = [[edge, self._format_value(amount)] for edge, amount in sorted(display_flows.items())]
            self._set_table("Edge Flows", ["Edge", "Flow"], rows)
            return

        if result_type == "mst":
            rows = []
            for edge in result.get("mst_edges", []):
                e = self._normalize_edge(edge)
                rows.append([f"{e['from']}-{e['to']}", self._format_value(e.get("weight"))])
            self._set_table("MST Edges", ["Edge", "Weight"], rows)
            return

        components = result.get("components", [])
        if components:
            rows = [
                [f"C{index}", ", ".join(str(node) for node in component)]
                for index, component in enumerate(components, start=1)
            ]
            self._set_table("Components", ["Component", "Nodes"], rows)
            return

        self._set_table("Metrics", ["Metric", "Value"], [])

    def _set_table(self, title, columns, rows, highlighted_nodes=None):
        highlighted_nodes = highlighted_nodes or set()
        self._dist_group.setTitle(title)
        self._dist_table.clear()
        self._dist_table.setColumnCount(len(columns))
        self._dist_table.setHorizontalHeaderLabels(columns)
        self._dist_table.setRowCount(0)

        for row_values in rows:
            row = self._dist_table.rowCount()
            self._dist_table.insertRow(row)
            for col, value in enumerate(row_values):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                if row_values and row_values[0] in highlighted_nodes:
                    item.setForeground(QBrush(QColor(ACCENT_AMBER)))
                    item.setFont(QFont("Consolas", 9, QFont.Bold))
                self._dist_table.setItem(row, col, item)

    def _format_step(self, step):
        if isinstance(step, dict):
            code = step.get("indexCode") or step.get("code")
            message = step.get("message") or step.get("detail") or step
            return f"[{code}] {message}" if code else str(message)
        if isinstance(step, (list, tuple)):
            return " -> ".join(str(item) for item in step)
        return str(step)

    def _format_path(self, path):
        return " -> ".join(str(node) for node in path) if path else "--"

    def _format_value(self, value):
        if value is None:
            return "--"
        if self._is_inf(value):
            return "INF"
        return str(value)

    def _is_inf(self, value):
        return isinstance(value, float) and math.isinf(value)

    def _distance_sort_key(self, value):
        if self._is_inf(value):
            return float("inf")
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("inf")

    def _bool_text(self, value):
        if value is True:
            return "Yes"
        if value is False:
            return "No"
        return "--"

    def _build_objective_text(self, algo, result):
        name = (algo.get("name") or "").lower()
        params = algo.get("params", {})
        source = params.get("source")
        target = params.get("target") or params.get("sink")
        sink = params.get("sink")

        if name in {"dijkstra", "bellman_ford", "bellman"}:
            if source and target:
                return f"Shortest path from {source} to {target}"
            if source:
                return f"Shortest paths from source {source}"
            return "Shortest path"

        if name == "ford_fulkerson":
            if source and sink:
                return f"Maximum flow from {source} to {sink}"
            return "Maximum flow"

        if name in {"kruskal", "prim"}:
            return "Minimum spanning tree"

        if name in {"bfs", "dfs"}:
            if source:
                return f"Traversal from source {source}"
            return "Graph traversal"

        if name in {"connectivity", "connected_components"}:
            return "Connectivity check"

        if name in {"strong_connectivity", "strongly_connected"}:
            return "Strong connectivity check"

        if name == "eulerian":
            if result.get("eulerian_circuit"):
                return "Find an Eulerian circuit"
            if result.get("eulerian_path"):
                return "Find an Eulerian path"
            return "Eulerian analysis"

        if name == "welsh_powell":
            return "Graph coloring"

        return "Algorithm result"

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

    def _display_json_response(self, data):
        """Display the full backend response as formatted JSON."""
        # Create a response object containing only result and execution info
        response = {
            "algorithm": data.get("algorithm", {}),
            "result": data.get("result", {}),
            "execution": data.get("execution", {})
        }
        
        # Format as indented JSON
        json_str = json.dumps(response, indent=2, default=str)
        self._json_display.setPlainText(json_str)

    def _on_status_clicked(self):
        """Handle status label click to log any errors."""
        if self._current_data:
            self._check_and_log_errors(self._current_data)

