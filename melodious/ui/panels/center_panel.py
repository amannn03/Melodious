"""Center panel with track info header and tracklist table."""
from PyQt6.QtWidgets import QWidget, 
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont



class CenterPanel(QWidget):
    track_double_clicked = pyqtSignal(int)
    track_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CenterPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 8, 8)
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