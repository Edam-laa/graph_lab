'''import sys
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
    ("Strongly Connected",  "connectivity",  ACCENT_AMBER),
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
        window = self._ensure_result_window()
        latest = getattr(self, "_last_result_data", None)
        if latest:
            window.set_result_data(latest)
        window.show()
        window.raise_()
        window.activateWindow()

    def _ensure_result_window(self):
        if not hasattr(self, "_result_window") or self._result_window is None:
            self._result_window = ResultWindow(self)
        return self._result_window

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
        bar.setFixedHeight(52)
        bar.setObjectName("bottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(6)

        # Source input
        src_lbl = QLabel("Source:")
        src_lbl.setFont(QFont("Consolas", 10))
        src_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(src_lbl)

        self._param_source = QLineEdit()
        self._param_source.setPlaceholderText("A")
        self._param_source.setFont(QFont("Consolas", 10))
        self._param_source.setFixedWidth(52)
        self._param_source.setFixedHeight(32)
        self._param_source.setStyleSheet(self._field_style())
        layout.addWidget(self._param_source)

        layout.addSpacing(4)

        # Target input
        tgt_lbl = QLabel("Target:")
        tgt_lbl.setFont(QFont("Consolas", 10))
        tgt_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(tgt_lbl)

        self._param_sink = QLineEdit()
        self._param_sink.setPlaceholderText("Z")
        self._param_sink.setFont(QFont("Consolas", 10))
        self._param_sink.setFixedWidth(52)
        self._param_sink.setFixedHeight(32)
        self._param_sink.setStyleSheet(self._field_style())
        layout.addWidget(self._param_sink)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(sep)

        # Algo buttons
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
            "Strongly Connected":    n > 0,
            "Chemin Eulérien":       n > 0 and eulerian,
            "Welsh-Powell":          n > 0,
            "Ford-Fulkerson":        n > 0 and m > 0 and directed,
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

    def _get_selected_algo_info(self, name=None):
        if name is None:
            # Fallback: first algo
            name = ALGO_DEFS[0][0]
        cat_map = {n: c for n, c, _ in ALGO_DEFS}
        return name, cat_map.get(name, "shortest_path")

    def _on_algo_clicked(self, name):
        """Handle algorithm button click: track selection and run algorithm"""
        self._current_algo = name
        self._run_algo(name)

    def _run_algo(self, name):
        import requests

        algo_name, algo_cat = self._get_selected_algo_info(name)

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

        # Store data for result window
        self._last_graph_data = data

        self._update_execution_info({
            "status": "running",
            "complexity": "--",
            "execution_time": None,
        })
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
            self._update_execution_info({
                "status": "error",
                "complexity": "--",
                "execution_time": None,
            })
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
        if result.get("status") == "error":
            self._log(result.get("message", "Backend returned an error"), "error")
            return

        frontend_result = result.get("result", result)
        res = frontend_result.get("result", {})
        # Clear old styles first
        self._reset_graph_style()

        # Shortest path
        if res.get("path"):
            self._highlight_path(res["path"])

        # MST
        if res.get("mst_edges"):
            self._highlight_edges(res["mst_edges"], QColor("#50fa7b"))

        traversal_edges = res.get("traversal", {}).get("tree_edges", [])
        if traversal_edges:
            self._highlight_edges(traversal_edges, QColor("#8be9fd"))

        eulerian_path = res.get("eulerian_path") or res.get("eulerian_circuit") or []
        if eulerian_path:
            self._highlight_path(eulerian_path, QColor("#ffb86c"))

        components = res.get("components", [])
        if len(components) > 1:
            self._apply_component_colors(components)

        # Coloring
        node_colors = res.get("coloring", {}).get("node_colors", {})
        if node_colors:
            self._apply_coloring(node_colors)

        self._log("Graph updated with backend result", "result")
        
        # ── open ResultWindow automatically ──
        # Merge backend result with graph data
        if self._last_graph_data:
            complete_data = self._last_graph_data.copy()
            complete_data["result"] = frontend_result.get("result", {})
            complete_data["execution"] = frontend_result.get("execution", {})
            complete_data["algorithm"] = frontend_result.get("algorithm", {})
            complete_data["graph"] = frontend_result.get("graph", complete_data.get("graph", {}))

            self._last_result_data = complete_data
            self._ensure_result_window().set_result_data(complete_data)

        self._ensure_result_window().show()
        self._result_window.raise_()
        self._result_window.activateWindow()
    def _reset_graph_style(self):
        for e in self._scene._edges:
            e.setPen(QPen(QColor("#6272a4"), 2.5))

        for n in self._scene._nodes.values():
            n._update_appearance()
    def _highlight_path(self, path, color=None):
        color = color or QColor("#ff5555")
        pairs = list(zip(path, path[1:]))

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in pairs or \
               (not self._scene._directed_graph and (e.dst.label, e.src.label) in pairs):
                e.setPen(QPen(color, 4))
    def _highlight_edges(self, edges, color=None):
        color = color or QColor("#50fa7b")
        edge_set = set()
        for edge in edges:
            if isinstance(edge, dict):
                edge_set.add((edge.get("from"), edge.get("to")))
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                edge_set.add((edge[0], edge[1]))

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in edge_set or \
               (not self._scene._directed_graph and (e.dst.label, e.src.label) in edge_set):
                e.setPen(QPen(color, 4))
    def _highlight_flow_edges(self, edge_flows):
        for e in self._scene._edges:
            key = f"{e.src.label}->{e.dst.label}"
            if edge_flows.get(key, 0) > 0:
                e.setPen(QPen(QColor("#bd93f9"), 4))
    def _apply_coloring(self, colors):
        palette = [
            "#ff5555", "#50fa7b", "#8be9fd", "#ffb86c",
            "#bd93f9", "#f1fa8c", "#ff79c6", "#6272a4"
        ]
        for node in self._scene._nodes.values():
            if node.label in colors:
                color = colors[node.label]
                if not (isinstance(color, str) and color.startswith("#")):
                    try:
                        color = palette[int(color) % len(palette)]
                    except (TypeError, ValueError):
                        color = "#cccccc"
                node.setBrush(QBrush(QColor(color)))
    def _apply_component_colors(self, components):
        palette = [
            "#50fa7b", "#ff5555", "#8be9fd", "#ffb86c",
            "#bd93f9", "#f1fa8c", "#ff79c6", "#6272a4"
        ]
        for index, component in enumerate(components):
            color = QColor(palette[index % len(palette)])
            for node in self._scene._nodes.values():
                if node.label in component:
                    node.setBrush(QBrush(color))
                    node.setPen(QPen(color, 2))
'''
import sys
import json
import math
import os
import colorsys
from PySide6.QtWidgets import ( QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSplitter, QToolBar, QStatusBar,
    QGroupBox, QDialog, QListWidget, QDialogButtonBox,
    QLineEdit, QComboBox, QAbstractItemView, QPlainTextEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPen, QBrush, QColor, QFont
)

from front.GraphScene import GraphScene
from front.EdgeItem import EdgeItem
from front.NodeItem import NodeItem
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
    ("Strongly Connected",  "connectivity",  ACCENT_AMBER),
    ("Chemin Eulérien",    "euler",          ACCENT_PINK),
    ("Welsh-Powell",       "coloring",       ACCENT_PURPLE),
    ("Ford-Fulkerson",     "max_flow",       "#bd93f9"),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GraphAlgo Pro  —  Graph Editor")
        self.resize(1320, 820)
        self.setMinimumSize(900, 600)

        self._scene = GraphScene()
        self._scene.graph_changed.connect(self._on_graph_changed)
        self._loading_graph = False

        self._build_ui()
        self._apply_global_style()
        self._on_graph_changed()
    def _open_result_window(self):
        window = self._ensure_result_window()
        latest = getattr(self, "_last_result_data", None)
        if latest:
            window.set_result_data(latest)
        window.show()
        window.raise_()
        window.activateWindow()

    def _ensure_result_window(self):
        if not hasattr(self, "_result_window") or self._result_window is None:
            self._result_window = ResultWindow(self)
        return self._result_window

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

        self._btn_load_ready = self._action_btn("📂  Load Graph", ACCENT_BLUE)
        self._btn_load_ready.clicked.connect(self._open_ready_graphs_dialog)
        layout.addWidget(self._btn_load_ready)

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
        bar.setFixedHeight(52)
        bar.setObjectName("bottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(6)

        # Source input
        src_lbl = QLabel("Source:")
        src_lbl.setFont(QFont("Consolas", 10))
        src_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(src_lbl)

        self._param_source = QLineEdit()
        self._param_source.setPlaceholderText("A")
        self._param_source.setFont(QFont("Consolas", 10))
        self._param_source.setFixedWidth(52)
        self._param_source.setFixedHeight(32)
        self._param_source.setStyleSheet(self._field_style())
        layout.addWidget(self._param_source)

        layout.addSpacing(4)

        # Target input
        tgt_lbl = QLabel("Target:")
        tgt_lbl.setFont(QFont("Consolas", 10))
        tgt_lbl.setStyleSheet(f"color: {TEXT_DIM};")
        layout.addWidget(tgt_lbl)

        self._param_sink = QLineEdit()
        self._param_sink.setPlaceholderText("Z")
        self._param_sink.setFont(QFont("Consolas", 10))
        self._param_sink.setFixedWidth(52)
        self._param_sink.setFixedHeight(32)
        self._param_sink.setStyleSheet(self._field_style())
        layout.addWidget(self._param_sink)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {BORDER};")
        layout.addWidget(sep)

        # Algo buttons
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

        if getattr(self, "_loading_graph", False):
            self._scene.graph_changed.emit()
            return

        # 🔥 RESET DES POIDS
        for e in self._scene._edges:
            if checked:
                e.weight = 0
            e.update_path()

        self._scene.graph_changed.emit()

    def _on_capacity_changed(self, checked):
        self._scene.set_capacity(checked)

        if getattr(self, "_loading_graph", False):
            self._scene.graph_changed.emit()
            return

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
            "Kruskal":               n > 0 and m > 0 ,
            "Prim":                  n > 0 and m > 0 ,
            "Composantes Connexes":  n > 0,
            "Strongly Connected":    n > 0,
            "Chemin Eulérien":       n > 0 and eulerian,
            "Welsh-Powell":          n > 0,
            "Ford-Fulkerson":        n > 0 and m > 0 and directed,
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

    def _open_ready_graphs_dialog(self):
        folder = self._ready_graphs_dir()
        if not os.path.isdir(folder):
            QMessageBox.warning(self, "Ready Graphs", f"Folder not found:\n{folder}")
            return

        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".json")])
        if not files:
            QMessageBox.information(self, "Ready Graphs", "No JSON graphs found in ready_graphs.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Ready Graphs")
        dlg.setMinimumWidth(360)
        layout = QVBoxLayout(dlg)

        list_widget = QListWidget()
        list_widget.addItems(files)
        list_widget.setCurrentRow(0)
        layout.addWidget(list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() != QDialog.Accepted:
            return

        selected = list_widget.currentItem()
        if not selected:
            return

        self._load_graph_file(os.path.join(folder, selected.text()))

    def _ready_graphs_dir(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return os.path.join(base_dir, "data", "ready_graphs")

    def _load_graph_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.warning(self, "Load Graph", f"Failed to read JSON:\n{exc}")
            return

        graph_data = None
        case_name = None
        if isinstance(data, dict) and isinstance(data.get("graphs"), dict):
            case_name = self._select_graph_case(os.path.basename(path), data.get("graphs", {}))
            if not case_name:
                return
            graph_data = data.get("graphs", {}).get(case_name)
            if not isinstance(graph_data, dict):
                QMessageBox.warning(self, "Load Graph", "Selected graph case is invalid.")
                return
            self._apply_graph_metadata_params(graph_data, prefer_existing=False)
        else:
            graph_data = self._extract_graph_payload(data)
            if not graph_data:
                QMessageBox.warning(self, "Load Graph", "Selected JSON does not contain a graph payload.")
                return
            self._apply_algo_params(data)
            self._apply_graph_metadata_params(graph_data, prefer_existing=True)

        self._load_graph_into_scene(graph_data)
        label = os.path.basename(path)
        if case_name:
            label = f"{label} :: {case_name}"
        self._status_lbl.setText(f"Loaded graph: {label}")

    def _select_graph_case(self, filename, graphs):
        if not graphs:
            QMessageBox.information(self, "Ready Graphs", "No graph cases found in this file.")
            return None

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Choose Graph Case ({filename})")
        dlg.setMinimumWidth(380)
        layout = QVBoxLayout(dlg)

        list_widget = QListWidget()
        list_widget.addItems(sorted(graphs.keys()))
        list_widget.setCurrentRow(0)
        layout.addWidget(list_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() != QDialog.Accepted:
            return None

        selected = list_widget.currentItem()
        return selected.text() if selected else None

    def _extract_graph_payload(self, data):
        if isinstance(data, dict) and isinstance(data.get("graph"), dict):
            return data.get("graph")
        if isinstance(data, dict) and "nodes" in data and "edges" in data:
            return data
        return {}

    def _apply_algo_params(self, data):
        if not isinstance(data, dict):
            return
        params = data.get("algorithm", {}).get("params", {})
        if not isinstance(params, dict):
            return

        source = params.get("source")
        sink = params.get("sink") or params.get("target")
        if source is not None:
            self._param_source.setText(str(source))
        if sink is not None:
            self._param_sink.setText(str(sink))

    def _apply_graph_metadata_params(self, graph_data, prefer_existing=True):
        if not isinstance(graph_data, dict):
            return
        meta = graph_data.get("metadata", {})
        if not isinstance(meta, dict):
            return

        source = meta.get("source")
        sink = meta.get("sink") or meta.get("target")

        if source is not None and (not prefer_existing or not self._param_source.text().strip()):
            self._param_source.setText(str(source))
        if sink is not None and (not prefer_existing or not self._param_sink.text().strip()):
            self._param_sink.setText(str(sink))

    def _load_graph_into_scene(self, graph_data):
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            QMessageBox.warning(self, "Load Graph", "Graph payload must contain 'nodes' and 'edges' lists.")
            return

        directed = bool(graph_data.get("directed", True))
        weighted = self._infer_weighted(graph_data)
        capacity_enabled = self._infer_capacity(graph_data)

        self._loading_graph = True
        self._chk_directed.setChecked(directed)
        self._chk_weighted.setChecked(weighted)
        self._chk_capacity.setChecked(capacity_enabled)
        self._loading_graph = False

        self._scene.clear()
        self._scene._nodes.clear()
        self._scene._edges.clear()
        self._scene._node_counter = 0
        self._scene._history = []

        positions = graph_data.get("node_positions", {}) or {}
        fallback_positions = self._fallback_positions(nodes)

        for index, label in enumerate(nodes):
            pos = positions.get(label) or fallback_positions.get(label, {"x": 0, "y": 0})
            node = NodeItem(index, label, pos.get("x", 0), pos.get("y", 0), self._scene)
            node.setAcceptHoverEvents(True)
            self._scene.addItem(node)
            self._scene._nodes[index] = node

        self._scene._node_counter = len(nodes)
        label_to_node = {n.label: n for n in self._scene._nodes.values()}

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            src = label_to_node.get(edge.get("from"))
            dst = label_to_node.get(edge.get("to"))
            if src is None or dst is None:
                continue

            weight = edge.get("weight", 1)
            capacity = edge.get("capacity", None)
            edge_item = EdgeItem(src, dst, weight, capacity, self._scene._directed_graph)
            self._scene.addItem(edge_item)
            edge_item.update_path()
            self._scene._edges.append(edge_item)
            self._scene._refresh_parallel_edges(src, dst)

        self._scene.graph_changed.emit()
        self._on_graph_changed()

    def _infer_weighted(self, graph_data):
        meta = graph_data.get("metadata", {}) if isinstance(graph_data, dict) else {}
        if isinstance(meta, dict) and "weighted" in meta:
            return bool(meta.get("weighted"))
        edges = graph_data.get("edges", []) if isinstance(graph_data, dict) else []
        return any(isinstance(edge, dict) and edge.get("weight") is not None for edge in edges)

    def _infer_capacity(self, graph_data):
        edges = graph_data.get("edges", []) if isinstance(graph_data, dict) else []
        return any(isinstance(edge, dict) and edge.get("capacity") is not None for edge in edges)

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

    def _get_selected_algo_info(self, name=None):
        if name is None:
            # Fallback: first algo
            name = ALGO_DEFS[0][0]
        cat_map = {n: c for n, c, _ in ALGO_DEFS}
        return name, cat_map.get(name, "shortest_path")

    def _on_algo_clicked(self, name):
        """Handle algorithm button click: track selection and run algorithm"""
        self._current_algo = name
        self._run_algo(name)

    def _run_algo(self, name):
        import requests

        algo_name, algo_cat = self._get_selected_algo_info(name)

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

        # Store data for result window
        self._last_graph_data = data

        self._update_execution_info({
            "status": "running",
            "complexity": "--",
            "execution_time": None,
        })
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
            self._update_execution_info({
                "status": "error",
                "complexity": "--",
                "execution_time": None,
            })
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
    def _update_execution_info(self, execution=None):
        execution = execution or {}
        if not hasattr(self, "_exec_labels"):
            return

        status = execution.get("status") or "--"
        complexity = execution.get("complexity") or "--"
        exec_time = execution.get("execution_time")
        if isinstance(exec_time, (int, float)):
            exec_time_text = f"{exec_time:.4f}s"
        elif exec_time is not None:
            exec_time_text = str(exec_time)
        else:
            exec_time_text = "--"

        status_color = {
            "success": ACCENT_CYAN,
            "running": ACCENT_AMBER,
            "not_started": TEXT_DIM,
            "error": ACCENT_PINK,
            "failed": ACCENT_PINK,
        }.get(str(status).lower(), TEXT_MAIN)

        self._exec_labels["exec_status"].setText(str(status))
        self._exec_labels["exec_status"].setStyleSheet(f"color: {status_color}; font-weight: bold;")
        self._exec_labels["exec_complexity"].setText(str(complexity))
        self._exec_labels["exec_complexity"].setStyleSheet(f"color: {TEXT_MAIN}; font-weight: bold;")
        self._exec_labels["exec_time"].setText(exec_time_text)
        self._exec_labels["exec_time"].setStyleSheet(f"color: {TEXT_MAIN}; font-weight: bold;")
    def _handle_backend_result(self, result):
        # Check top-level status
        if result.get("status") == "error":
            error_message = result.get("message", "Backend returned an error")
            self._update_execution_info({
                "status": "error",
                "complexity": "--",
                "execution_time": None,
            })
            self._log(error_message, "error")
            print(f"[ERROR] {error_message}")
            return

        # Check nested execution status
        frontend_result = result.get("result", result)
        self._update_execution_info(frontend_result.get("execution", {}))
        exec_status = frontend_result.get("execution", {}).get("status", "").lower()
        error_keywords = ["error", "failed", "exception", "invalid", "timeout"]
        
        if any(keyword in exec_status for keyword in error_keywords):
            error_message = frontend_result.get("execution", {}).get("message", f"Algorithm failed with status: {exec_status}")
            self._log(error_message, "error")
            print(f"[ERROR] {error_message}")
            return

        res = frontend_result.get("result", {})
        # Clear old styles first
        self._reset_graph_style()

        # Shortest path
        if res.get("path"):
            self._highlight_path(res["path"])

        # MST
        if res.get("mst_edges"):
            self._highlight_edges(res["mst_edges"], QColor("#50fa7b"))

        traversal_edges = res.get("traversal", {}).get("tree_edges", [])
        if traversal_edges:
            self._highlight_edges(traversal_edges, QColor("#8be9fd"))

        eulerian_path = res.get("eulerian_path") or res.get("eulerian_circuit") or []
        if eulerian_path:
            self._highlight_path(eulerian_path, QColor("#ffb86c"))

        components = res.get("components", [])
        if len(components) > 1:
            self._apply_component_colors(components)

        # Coloring
        node_colors = res.get("coloring", {}).get("node_colors", {})
        if node_colors:
            self._apply_coloring(node_colors)

        self._log("Graph updated with backend result", "result")
        
        # ── open ResultWindow automatically ──
        # Merge backend result with graph data
        if self._last_graph_data:
            complete_data = self._last_graph_data.copy()
            complete_data["result"] = frontend_result.get("result", {})
            complete_data["execution"] = frontend_result.get("execution", {})
            complete_data["algorithm"] = frontend_result.get("algorithm", {})
            complete_data["graph"] = frontend_result.get("graph", complete_data.get("graph", {}))

            self._last_result_data = complete_data
            self._ensure_result_window().set_result_data(complete_data)

        self._ensure_result_window().show()
        self._result_window.raise_()
        self._result_window.activateWindow()
    def _reset_graph_style(self):
        for e in self._scene._edges:
            e.setPen(QPen(QColor("#6272a4"), 2.5))

        for n in self._scene._nodes.values():
            n._update_appearance()
    def _highlight_path(self, path, color=None):
        color = color or QColor("#ff5555")
        pairs = list(zip(path, path[1:]))

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in pairs or \
               (not self._scene._directed_graph and (e.dst.label, e.src.label) in pairs):
                e.setPen(QPen(color, 4))
    def _highlight_edges(self, edges, color=None):
        color = color or QColor("#50fa7b")
        edge_set = set()
        for edge in edges:
            if isinstance(edge, dict):
                edge_set.add((edge.get("from"), edge.get("to")))
            elif isinstance(edge, (list, tuple)) and len(edge) >= 2:
                edge_set.add((edge[0], edge[1]))

        for e in self._scene._edges:
            if (e.src.label, e.dst.label) in edge_set or \
               (not self._scene._directed_graph and (e.dst.label, e.src.label) in edge_set):
                e.setPen(QPen(color, 4))
    def _highlight_flow_edges(self, edge_flows):
        for e in self._scene._edges:
            key = f"{e.src.label}->{e.dst.label}"
            if edge_flows.get(key, 0) > 0:
                e.setPen(QPen(QColor("#bd93f9"), 4))

    def _color_from_index(self, index):
        palette = [
            "#50fa7b", "#ff5555", "#8be9fd", "#ffb86c",
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

    def _resolve_color_value(self, color):
        if isinstance(color, str) and color.startswith("#"):
            return color
        return self._color_from_index(color)

    def _apply_coloring(self, colors):
        for node in self._scene._nodes.values():
            if node.label in colors:
                color = self._resolve_color_value(colors[node.label])
                node.setBrush(QBrush(QColor(color)))
    def _apply_component_colors(self, components):
        for index, component in enumerate(components):
            color = QColor(self._color_from_index(index))
            for node in self._scene._nodes.values():
                if node.label in component:
                    node.setBrush(QBrush(color))
                    node.setPen(QPen(color, 2))

