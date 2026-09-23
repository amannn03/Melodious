"""Vector-drawn transport icons (font-independent, theme-colored)."""
import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor, QFont, QIcon, QPainter, QPainterPath, QPen,
    QPixmap, QPolygonF,
)

GRID = 24.0


def _render(size: int, color: str, draw) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    draw(p, QColor(color), size / GRID)
    p.end()
    return QIcon(pm)


def _pen(p: QPainter, c: QColor, w: float) -> None:
    p.setPen(QPen(c, w, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))


def _arrowhead(p: QPainter, tip: QPointF, deg: float, length: float, width: float) -> None:
    rad = math.radians(deg)
    dx, dy = math.cos(rad), math.sin(rad)
    tail = QPointF(tip.x() - dx * length, tip.y() - dy * length)
    p.drawLine(tail, tip)
    b1 = QPointF(tip.x() - dx * length * 0.65 - dy * width,
                 tip.y() - dy * length * 0.65 + dx * width)
    b2 = QPointF(tip.x() - dx * length * 0.65 + dy * width,
                 tip.y() - dy * length * 0.65 - dx * width)
    p.drawLine(tip, b1)
    p.drawLine(tip, b2)


def icon_play(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawPolygon(QPolygonF(
            [QPointF(8 * s, 5 * s), QPointF(20 * s, 12 * s), QPointF(8 * s, 19 * s)]))
    return _render(size, color, draw)


def icon_pause(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(7 * s, 5 * s, 4 * s, 14 * s), 1.2 * s, 1.2 * s)
        p.drawRoundedRect(QRectF(13 * s, 5 * s, 4 * s, 14 * s), 1.2 * s, 1.2 * s)
    return _render(size, color, draw)


def icon_prev(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    # skip-previous: triangle pointing left, bar beside it toward center-right
    def draw(p, c, s):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(16.5 * s, 4.5 * s, 3 * s, 15 * s), 1.2 * s, 1.2 * s)
        p.drawPolygon(QPolygonF(
            [QPointF(15.5 * s, 4.5 * s), QPointF(4.5 * s, 12 * s), QPointF(15.5 * s, 19.5 * s)]))
    return _render(size, color, draw)


def icon_next(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    # skip-next: triangle pointing right, bar beside it toward center-left
    def draw(p, c, s):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(4.5 * s, 4.5 * s, 3 * s, 15 * s), 1.2 * s, 1.2 * s)
        p.drawPolygon(QPolygonF(
            [QPointF(8.5 * s, 4.5 * s), QPointF(19.5 * s, 12 * s), QPointF(8.5 * s, 19.5 * s)]))
    return _render(size, color, draw)


def icon_shuffle(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        w = 2.1 * s
        _pen(p, c, w)
        p.drawLine(QPointF(3 * s, 6 * s), QPointF(13 * s, 6 * s))
        _arrowhead(p, QPointF(16 * s, 6 * s), 0, 7 * s, 3.2 * s)
        p.drawLine(QPointF(21 * s, 18 * s), QPointF(11 * s, 18 * s))
        _arrowhead(p, QPointF(8 * s, 18 * s), 180, 7 * s, 3.2 * s)
        p.drawLine(QPointF(13 * s, 6 * s), QPointF(16 * s, 9 * s))
        p.drawLine(QPointF(11 * s, 18 * s), QPointF(8 * s, 15 * s))
    return _render(size, color, draw)


def icon_repeat_one(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        w = 2.2 * s
        _pen(p, c, w)
        rect = QRectF(3.5 * s, 3.5 * s, 17 * s, 17 * s)
        path = QPainterPath()
        path.arcMoveTo(rect, 80)
        path.arcTo(rect, 80, 280)
        p.drawPath(path)
        cx, cy, r = 12 * s, 12 * s, 8.5 * s
        end = math.radians(80 + 280)
        tip = QPointF(cx + r * math.cos(end), cy + r * math.sin(end))
        tangent = math.degrees(math.atan2(math.cos(end), -math.sin(end)))
        _arrowhead(p, tip, tangent, 5.5 * s, 2.6 * s)
        p.setPen(Qt.PenStyle.NoPen)
        f = QFont()
        f.setPixelSize(int(11 * s))
        f.setBold(True)
        p.setFont(f)
        p.setPen(c)
        p.drawText(QRectF(4 * s, 8 * s, 16 * s, 9 * s),
                   Qt.AlignmentFlag.AlignCenter, "1")
    return _render(size, color, draw)
