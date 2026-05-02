from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from front.theme.colors import TEXT_DIM
def section_label(text):
    lbl = QLabel(text.upper())
    lbl.setFont(QFont("Consolas", 9, QFont.Bold))
    lbl.setStyleSheet(f"color: {TEXT_DIM}; letter-spacing: 1px; padding: 4px 0;")
    return lbl