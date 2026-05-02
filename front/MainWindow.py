import sys
import json
import math
from PySide6.QtWidgets import ( QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QGroupBox,
    QLineEdit, QComboBox, QAbstractItemView, QPlainTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPen, QBrush, QColor, QFont
)

from front.GraphScene import GraphScene
from front.WeightDialog import WeightDialog
from front.GraphView import GraphView
from front.ResultWindow import ResultWindow
from front.Algobtn import AlgoBtn
from front.Toolbtn import ToolBtn
from front.theme.colors import *
from front.widgets.ui_helpers import section_label

ALGO_DEFS = [
    ("Bellman-Ford",       "shortest_path",  ACCENT_BLUE),
    ("Dijkstra",           "shortest_path",  ACCENT_BLUE),
    ("Bellman",            "shortest_path",  ACCENT_BLUE),
    ("Kruskal",            "spanning_tree",  ACCENT_CYAN),
    ("Prim",               "spanning_tree",  ACCENT_CYAN),
    ("Composantes Connexes","connectivity",  ACCENT_AMBER),
    ("Chemin Eulérien",    "euler",          ACCENT_PINK),
    ("Welsh-Powell",       "coloring",       ACCENT_PURPLE),
]

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