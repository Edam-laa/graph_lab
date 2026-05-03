from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt
from front.theme.colors import *
class GraphView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setStyleSheet(f"background: {BG_DARK}; border: none;")
        self._draw_grid = True

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(BG_DARK))
        if not self._draw_grid:
            return
        painter.setPen(QPen(QColor(GRID_COLOR), 0.5))
        step = 40
        l, r = int(rect.left())//step*step, int(rect.right())//step*step+step
        t, b = int(rect.top())//step*step, int(rect.bottom())//step*step+step
        for x in range(l, r, step):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(t, b, step):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = event
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

