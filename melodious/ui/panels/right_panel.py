"""Right panel for cover art display."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
 QColor, QFont


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