from PySide6.QtGui import QPalette, QColor
from front.theme.colors import *
def apply_dark_theme(app):
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