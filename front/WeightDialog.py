from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QDialogButtonBox, QFrame, QCheckBox
)
from PySide6.QtGui import QFont
from front.theme.colors import *
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
