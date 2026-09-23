"""Right panel for cover art display."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont


class RightPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumWidth(170)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 12, 8)
        layout.setSpacing(8)

        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setMinimumSize(0, 0)
        self.cover_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.cover_label.setStyleSheet(
            "background-color: #313244; border-radius: 12px;")
        layout.addWidget(self.cover_label, 1)

        self.track_label = QLabel("No Track")
        self.track_label.setObjectName("TrackInfoTitle")
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_label.setWordWrap(True)
        layout.addWidget(self.track_label)

        self._pixmap: QPixmap | None = None
        self._render_cover()

    def set_cover(self, pixmap: QPixmap | None) -> None:
        self._pixmap = pixmap
        self._render_cover()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render_cover()

    def _render_cover(self) -> None:
        size = self.cover_label.contentsRect().size()
        if size.width() < 10 or size.height() < 10:
            return
        if self._pixmap is None:
            self.cover_label.setPixmap(self._make_placeholder(size))
        else:
            scaled = self._pixmap.scaled(
                size, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.cover_label.setPixmap(scaled)

    def _make_placeholder(self, size) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(QColor("#313244"))
        painter = QPainter(pixmap)
        painter.setPen(QColor("#585B70"))
        font = QFont()
        font.setPixelSize(max(24, int(pixmap.height() * 0.2)))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "\u266B")
        painter.end()
        return pixmap

    def set_track_info(self, title: str, artist: str = "") -> None:
        self.track_label.setText(title)