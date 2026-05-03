# ─── Node ─────────────────────────────────────────────────────────────────────

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtGui import QBrush, QPen, QColor, QRadialGradient, QFont
from front.theme.colors import *
class NodeItem(QGraphicsEllipseItem):
    RADIUS = 22

    def __init__(self, node_id, label, x, y, scene_ref):
        r = self.RADIUS
        super().__init__(-r, -r, 2*r, 2*r)
        self.node_id = node_id
        self.label   = label
        self._scene  = scene_ref
        self.setPos(x, y)
        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setZValue(10)
        self._update_appearance()

        self._label_item = QGraphicsTextItem(label, self)
        self._label_item.setDefaultTextColor(QColor(TEXT_MAIN))
        self._label_item.setFont(QFont("Consolas", 11, QFont.Bold))
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)
        self._label_item.setZValue(11)

    def _update_appearance(self):
        grad = QRadialGradient(0, -5, self.RADIUS*1.2)
        if self.isSelected():
            grad.setColorAt(0, QColor("#7aa8ff"))
            grad.setColorAt(1, QColor(NODE_SEL))
            pen_c = QColor(ACCENT_BLUE)
        else:
            grad.setColorAt(0, QColor("#4a5a8a"))
            grad.setColorAt(1, QColor(NODE_DEFAULT))
            pen_c = QColor(BORDER)
        self.setBrush(QBrush(grad))
        self.setPen(QPen(pen_c, 2))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._scene.node_moved(self)
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self._update_appearance()
        return super().itemChange(change, value)

    def hoverEnterEvent(self, event):
        grad = QRadialGradient(0, -5, self.RADIUS*1.2)
        grad.setColorAt(0, QColor("#8090d0"))
        grad.setColorAt(1, QColor(NODE_HOVER))
        self.setBrush(QBrush(grad))
        self.setPen(QPen(QColor(ACCENT_CYAN), 2))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._update_appearance()
        super().hoverLeaveEvent(event)

    def setAcceptHoverEvents(self, b):
        super().setAcceptHoverEvents(b)

    def set_label(self, lbl):
        self.label = lbl
        self._label_item.setPlainText(lbl)
        rect = self._label_item.boundingRect()
        self._label_item.setPos(-rect.width()/2, -rect.height()/2)


# ─── Edge ─────────────────────────────────────────────────────────────────────
