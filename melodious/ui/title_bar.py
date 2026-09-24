"""Custom frameless title bar."""
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPixmap

from melodious.ui import icons

WIN_ICON = 16
MENU_ICON = 18
_LOGO_SIZE = 28
_ASSETS = Path(__file__).resolve().parent.parent / "assets" / "icons"


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

        self.close_btn.setObjectName("CloseBtn")

        layout.addWidget(self.menu_btn)
        layout.addSpacing(8)
        layout.addWidget(self.logo_label)
        layout.addSpacing(6)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addSpacing(4)
        layout.addWidget(self.max_btn)
        layout.addSpacing(4)
        layout.addWidget(self.close_btn)

        self._build_icons()

    def _make_btn(self, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("WinControlBtn")
        btn.setFixedSize(28, 28)
        btn.setIconSize(QSize(WIN_ICON, WIN_ICON))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        return btn

    def _build_icons(self) -> None:
        self.menu_btn.setIcon(icons.icon_menu(MENU_ICON, self._fg))
        self.min_btn.setIcon(icons.icon_minimize(WIN_ICON, self._fg))
        self._apply_maximize_icon()
        self.close_btn.setIcon(icons.icon_close(WIN_ICON, self._fg))

    def _set_logo_icon(self) -> None:
        for name in ("melodious-32.png", "melodious-48.png", "melodious-64.png"):
            path = _ASSETS / name
            if path.exists():
                pm = QPixmap(str(path))
                if not pm.isNull():
                    self.logo_label.setPixmap(
                        pm.scaled(_LOGO_SIZE, _LOGO_SIZE,
                                  Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation))
                    return

    def _apply_maximize_icon(self) -> None:
        if self.window() is not None and self.window().isMaximized():
            self.max_btn.setIcon(icons.icon_restore(WIN_ICON, self._fg))
        else:
            self.max_btn.setIcon(icons.icon_maximize(WIN_ICON, self._fg))

    def set_icon_colors(self, fg: str) -> None:
        self._fg = fg
        self._build_icons()

    def _minimize(self) -> None:
        w = self.window()
        if w is None:
            return
        if w.isMaximized():
            w.showNormal()
        g = w.geometry()
        if self._saved_geometry is None:
            self._saved_geometry = g
            w.setGeometry(g.x() + g.width() // 4,
                          g.y() + g.height() // 4,
                          g.width() // 2,
                          g.height() // 2)
        else:
            w.setGeometry(self._saved_geometry)
            self._saved_geometry = None

    def _maximize(self) -> None:
        w = self.window()
        if w:
            if w.isMaximized():
                w.showNormal()
            else:
                w.showMaximized()

    def _close(self) -> None:
        if self.window():
            self.window().close()

    def set_restored(self, maximized: bool) -> None:
        self.max_btn.setToolTip("Restore" if maximized else "Maximize")
        self._apply_maximize_icon()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self._maximize()