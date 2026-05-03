# ─── Tool Button ──────────────────────────────────────────────────────────────
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from front.theme.colors import *
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
