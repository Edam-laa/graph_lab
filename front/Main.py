from PySide6.QtWidgets import QApplication
import sys
from front.MainWindow import MainWindow
from front.theme.theme import apply_dark_theme
def main():
    app = QApplication(sys.argv)

    app.setApplicationName("GraphAlgo Pro")
    app.setStyle("Fusion")

    apply_dark_theme(app)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

main()