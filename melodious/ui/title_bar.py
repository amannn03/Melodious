"""Custom frameless title bar."""


from pathlib import Path

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPixmap




class TitleBar(QWidget):
    menu_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(44)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._drag_pos: QPoint | None = None
        self._fg = "#CDD6F4"
        self._saved_geometry = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(0)

        self.menu_btn = QPushButton()
        self.menu_btn.setObjectName("MenuBtn")
        self.menu_btn.setFixedSize(36, 36)
        self.menu_btn.setIconSize(QSize(MENU_ICON, MENU_ICON))
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.menu_clicked.emit)
        self.menu_btn.setToolTip("Menu")

        self.logo_label = QLabel()
        self.logo_label.setObjectName("TitleLogo")
        self.logo_label.setFixedSize(_LOGO_SIZE + 6, _LOGO_SIZE + 6)
        self._set_logo_icon()

        self.title = QLabel("Melodious")
        self.title.setObjectName("TitleLabel")

        self.min_btn = self._make_btn("Minimize")
        self.max_btn = self._make_btn("Maximize")
        self.close_btn = self._make_btn("Close")

        self.min_btn.clicked.connect(self._minimize)
        self.max_btn.clicked.connect(self._maximize)
        self.close_btn.clicked.connect(self._close)
