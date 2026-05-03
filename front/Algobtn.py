from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from front.theme.colors import *
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

