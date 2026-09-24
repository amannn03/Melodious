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


def icon_volume(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        w = 2.0 * s
        _pen(p, c, w)
        path = QPainterPath()
        path.moveTo(5 * s, 8.5 * s)
        path.lineTo(8.5 * s, 8.5 * s)
        path.lineTo(12.5 * s, 4.5 * s)
        path.lineTo(12.5 * s, 19.5 * s)
        path.lineTo(8.5 * s, 15.5 * s)
        path.lineTo(5 * s, 15.5 * s)
        path.closeSubpath()
        p.drawPath(path)
        p.drawArc(QRectF(11.5 * s, 9.5 * s, 5.5 * s, 5 * s), -50 * 16, 100 * 16)
        p.drawArc(QRectF(15.5 * s, 7 * s, 7.5 * s, 10 * s), -60 * 16, 120 * 16)
    return _render(size, color, draw)


def icon_volume_mute(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        w = 2.0 * s
        _pen(p, c, w)
        path = QPainterPath()
        path.moveTo(5 * s, 8.5 * s)
        path.lineTo(8.5 * s, 8.5 * s)
        path.lineTo(12.5 * s, 4.5 * s)
        path.lineTo(12.5 * s, 19.5 * s)
        path.lineTo(8.5 * s, 15.5 * s)
        path.lineTo(5 * s, 15.5 * s)
        path.closeSubpath()
        p.drawPath(path)
        p.drawLine(QPointF(15.5 * s, 9 * s), QPointF(21.5 * s, 15 * s))
        p.drawLine(QPointF(21.5 * s, 9 * s), QPointF(15.5 * s, 15 * s))
    return _render(size, color, draw)


def icon_menu(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        _pen(p, c, 2.1 * s)
        p.drawLine(QPointF(5 * s, 7 * s), QPointF(19 * s, 7 * s))
        p.drawLine(QPointF(5 * s, 12 * s), QPointF(19 * s, 12 * s))
        p.drawLine(QPointF(5 * s, 17 * s), QPointF(19 * s, 17 * s))
    return _render(size, color, draw)


def icon_minimize(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        _pen(p, c, 2.2 * s)
        p.drawLine(QPointF(7 * s, 12 * s), QPointF(17 * s, 12 * s))
    return _render(size, color, draw)


def icon_maximize(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        _pen(p, c, 2.0 * s)
        p.drawRect(QRectF(7 * s, 7 * s, 11 * s, 11 * s))
    return _render(size, color, draw)


def icon_restore(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        _pen(p, c, 1.8 * s)
        p.drawRect(QRectF(6 * s, 6 * s, 9.5 * s, 9.5 * s))
        p.drawRect(QRectF(9.5 * s, 9.5 * s, 9.5 * s, 9.5 * s))
    return _render(size, color, draw)


def icon_close(size: int = 24, color: str = "#CDD6F4") -> QIcon:
    def draw(p, c, s):
        _pen(p, c, 2.2 * s)
        p.drawLine(QPointF(7 * s, 7 * s), QPointF(17 * s, 17 * s))
        p.drawLine(QPointF(17 * s, 7 * s), QPointF(7 * s, 17 * s))
    return _render(size, color, draw)


def _sparkle_path(cx: float, cy: float, r: float) -> QPainterPath:
    path = QPainterPath()
    path.moveTo(cx, cy - r)
    path.lineTo(cx + r * 0.25, cy - r * 0.25)
    path.lineTo(cx + r, cy)
    path.lineTo(cx + r * 0.25, cy + r * 0.25)
    path.lineTo(cx, cy + r)
    path.lineTo(cx - r * 0.25, cy + r * 0.25)
    path.lineTo(cx - r, cy)
    path.lineTo(cx - r * 0.25, cy - r * 0.25)
    path.closeSubpath()
    return path


def icon_melodious(size: int = 256, accent: str = "#BD93F9") -> QIcon:
    """The Melodious app logo: glowing eighth-note on a dark rounded badge."""
    from PyQt6.QtGui import QLinearGradient, QRadialGradient

    s = size / 512.0
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    accent_c = QColor(accent)
    bg = QLinearGradient(0, 0, 0, size)
    bg.setColorAt(0, QColor(50, 52, 82))
    bg.setColorAt(0.5, QColor(33, 34, 54))
    bg.setColorAt(1, QColor(24, 25, 40))
    p.setPen(QPen(accent_c, 16 * s, Qt.PenStyle.SolidLine,
                  Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    p.setBrush(bg)
    p.drawRoundedRect(QRectF(10 * s, 10 * s, 492 * s, 492 * s), 118 * s, 118 * s)

    glow = QRadialGradient(QPointF(250 * s, 295 * s), 175 * s)
    glow.setColorAt(0, QColor(178, 142, 249, 110))
    glow.setColorAt(0.55, QColor(178, 142, 249, 55))
    glow.setColorAt(1, QColor(0, 0, 0, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(glow)
    p.drawEllipse(QPointF(250 * s, 295 * s), 175 * s, 175 * s)

    g2 = QRadialGradient(QPointF(430 * s, 90 * s), 150 * s)
    g2.setColorAt(0, QColor(139, 233, 253, 60))
    g2.setColorAt(1, QColor(0, 0, 0, 0))
    p.setBrush(g2)
    p.drawEllipse(QPointF(430 * s, 90 * s), 150 * s, 150 * s)

    note_grad = QLinearGradient(195 * s, 90 * s, 320 * s, 400 * s)
    note_grad.setColorAt(0, QColor(255, 255, 255))
    note_grad.setColorAt(1, QColor(190, 175, 255))
    shadow = QColor(0, 0, 0, 80)

    p.save()
    p.translate(257 * s + 8 * s, 388 * s + 10 * s)
    p.rotate(-20)
    p.setBrush(shadow)
    p.drawEllipse(QRectF(-60 * s, -40 * s, 120 * s, 80 * s))
    p.restore()

    p.save()
    p.translate(255 * s + 2 * s, 388 * s + 2 * s)
    p.rotate(-20)
    p.setBrush(note_grad)
    p.drawEllipse(QRectF(-60 * s, -40 * s, 120 * s, 80 * s))
    p.restore()

    p.setBrush(shadow)
    p.drawRoundedRect(QRectF(266 * s + 6 * s, 92 * s + 6 * s, 22 * s, 306 * s), 11 * s, 11 * s)
    p.setBrush(note_grad)
    p.drawRoundedRect(QRectF(266 * s, 92 * s, 22 * s, 306 * s), 11 * s, 11 * s)

    flag = QPainterPath()
    flag.moveTo(295 * s, 88 * s)
    flag.cubicTo(392 * s, 120 * s, 412 * s, 228 * s, 350 * s, 330 * s)
    flag.cubicTo(330 * s, 268 * s, 320 * s, 210 * s, 295 * s, 212 * s)
    flag.closeSubpath()
    p.setBrush(shadow)
    p.drawPath(QPainterPath(flag).translated(6 * s, 8 * s))
    p.setBrush(note_grad)
    p.drawPath(flag)

    p.setBrush(QColor(255, 255, 255, 200))
    p.drawPath(_sparkle_path(390 * s, 60 * s, 18 * s))
    p.setBrush(QColor(255, 255, 255, 130))
    p.drawPath(_sparkle_path(120 * s, 430 * s, 11 * s))

    p.end()
    return QIcon(pm)