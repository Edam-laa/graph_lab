import math
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QBrush, QPolygonF, QFont
from PySide6.QtCore import QPointF, Qt
from front.NodeItem import NodeItem
from front.theme.colors import *

class EdgeItem(QGraphicsPathItem):
    def __init__(self, src: NodeItem, dst: NodeItem, weight=1.0, capacity=1, directed=True):
        super().__init__()
        self.src      = src
        self.dst      = dst
        self.weight   = weight
        self.capacity = capacity
        self.directed = directed
        self.setZValue(1)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._pen = QPen(QColor(EDGE_COLOR), 2.5, Qt.SolidLine, Qt.RoundCap)
        self._arrow_tip  = None
        self._arrow_nx   = 0.0
        self._arrow_ny   = 0.0

        self._weight_item = QGraphicsTextItem(self)
        self._weight_item.setDefaultTextColor(QColor(ACCENT_AMBER))
        self._weight_item.setFont(QFont("Consolas", 9, QFont.Bold))
        self._weight_item.setZValue(5)

        self.setPen(self._pen)
        # update_path() is called by the scene AFTER addItem()

    def update_path(self):
        # All coordinates in scene space; EdgeItem sits at scene origin (pos = 0,0)
        p1 = self.src.scenePos()
        p2 = self.dst.scenePos()

        # Safety: if nodes not in scene yet, skip
        if p1 == p2 and self.src is not self.dst:
            return

        dx   = p2.x() - p1.x()
        dy   = p2.y() - p1.y()
        dist = math.hypot(dx, dy) or 1.0
        nx, ny = dx / dist, dy / dist

        r  = NodeItem.RADIUS
        sp = QPointF(p1.x() + nx * r, p1.y() + ny * r)
        ep = QPointF(p2.x() - nx * r, p2.y() - ny * r)

        # Determine curve offset for parallel edges
        curve_offset = self._get_curve_offset()

        self.prepareGeometryChange()
        path = QPainterPath(sp)
        if self.src is self.dst:
            path.cubicTo(
                QPointF(sp.x() + 50, sp.y() - 70),
                QPointF(ep.x() - 50, ep.y() - 70),
                ep,
            )
        else:
            mid  = QPointF((sp.x() + ep.x()) / 2, (sp.y() + ep.y()) / 2)
            ctrl = QPointF(mid.x() - ny * curve_offset, mid.y() + nx * curve_offset)
            path.quadTo(ctrl, ep)

        self.setPath(path)

        # Arrow data stored for paint()
        self._arrow_tip = ep
        self._arrow_nx  = nx
        self._arrow_ny  = ny

        # Weight / capacity label
        mid_pt = path.pointAtPercent(0.5)
        w = self.weight if self.weight is not None else 1
        c = self.capacity

        def fmt_number(value):
            if value is None:
                return ""
            return str(int(value)) if value == int(value) else str(value)

        w_txt = fmt_number(w)
        c_txt = fmt_number(c)
        
        # Show based on scene settings
        scene = self.scene()
        show_w = getattr(scene, '_weighted_graph', True) if scene else True
        show_c = (getattr(scene, '_capacity_graph', True) if scene else True) and c is not None
        
        if show_w and show_c:
            label_txt = f"{w_txt}/{c_txt}" if c != 1 else w_txt
        elif show_w:
            label_txt = w_txt
        elif show_c:
            label_txt = c_txt
        else:
            label_txt = ""
        
        self._weight_item.setPlainText(label_txt)
        wr = self._weight_item.boundingRect()
        self._weight_item.setPos(
            mid_pt.x() - wr.width() / 2 - ny * (curve_offset * 0.6 + 8),
            mid_pt.y() - wr.height() / 2 + nx * (curve_offset * 0.6 + 8),
        )
        self.update()

    def _get_curve_offset(self):
        """Return a curve offset so parallel edges between same nodes fan out."""
        scene = self.scene()
        if scene is None:
            return 18
        # Count all parallel edges between this src/dst pair (both directions count as parallel)
        parallel = [
            e for e in scene._edges
            if (e.src is self.src and e.dst is self.dst)
            or (e.src is self.dst and e.dst is self.src)
        ]
        if len(parallel) <= 1:
            return 18  # default slight curve
        # Assign index to self among parallel edges
        try:
            idx = parallel.index(self)
        except ValueError:
            idx = 0
        total = len(parallel)
        # Spread: evenly spaced offsets centered around 0
        # e.g. 2 edges: -40, +40 ; 3 edges: -50, 0, +50
        spacing = 45
        start = -(total - 1) * spacing / 2
        return start + idx * spacing

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        self.setPen(self._pen)
        super().paint(painter, option, widget)
        if self.directed and self._arrow_tip is not None:
            self._paint_arrow(painter)

    def _paint_arrow(self, painter):
        tip = self._arrow_tip
        nx, ny = self._arrow_nx, self._arrow_ny
        sz = 12
        left  = QPointF(tip.x() - nx*sz + ny*sz*0.5,
                        tip.y() - ny*sz - nx*sz*0.5)
        right = QPointF(tip.x() - nx*sz - ny*sz*0.5,
                        tip.y() - ny*sz + nx*sz*0.5)
        painter.setBrush(QBrush(QColor(EDGE_COLOR)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(QPolygonF([tip, left, right]))

    def reverse(self):
        """Reverse the direction of the edge (swap src and dst)."""
        self.src, self.dst = self.dst, self.src
        self.update_path()
