"""Main window assembling all Melodious components."""




import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QSplitter, QMenu, QFileDialog, QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QRect, QPoint, QEvent
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent, QMouseEvent, QIcon

from melodious.ui.title_bar import TitleBar
from melodious.ui.panels.center_panel import CenterPanel
from melodious.ui.panels.right_panel import RightPanel
from melodious.ui.visualizer import WaveformVisualizer
from melodious.ui.playbar import Playbar
from melodious.ui.settings_dialog import SettingsDialog
from melodious.ui.themes import get_theme, build_stylesheet, get_theme_names
from melodious.core.player import create_player, PlaybackState
from melodious.core.metadata import (
    TrackMetadata, extract_metadata_files, AUDIO_FILTER,
)
from melodious.utils.state import save_state, load_state



class _ResizeHandle(QWidget):
    """Invisible grab area on a window edge/corner used to resize a frameless window."""

    _CURSORS = {
        frozenset({"N"}): Qt.CursorShape.SizeVerCursor,
        frozenset({"S"}): Qt.CursorShape.SizeVerCursor,
        frozenset({"E"}): Qt.CursorShape.SizeHorCursor,
        frozenset({"W"}): Qt.CursorShape.SizeHorCursor,
        frozenset({"N", "E"}): Qt.CursorShape.SizeBDiagCursor,
        frozenset({"S", "W"}): Qt.CursorShape.SizeBDiagCursor,
        frozenset({"N", "W"}): Qt.CursorShape.SizeFDiagCursor,
        frozenset({"S", "E"}): Qt.CursorShape.SizeFDiagCursor,
    }

    def __init__(self, parent: QWidget, edges: str):
        super().__init__(parent)
        self.edges = frozenset(edges)
        self._start_geom: QRect | None = None
        self._start_pos: QPoint | None = None
        self.setCursor(self._CURSORS.get(self.edges, Qt.CursorShape.ArrowCursor))
        self.setToolTip("Resize")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.window().isMaximized():
                self._start_geom = QRect(self.window().geometry())
                self._start_pos = event.globalPosition().toPoint()
                event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._start_geom is None or self._start_pos is None:
            return
        if self.window().isMaximized():
            return

        g = QRect(self._start_geom)
        pos = event.globalPosition().toPoint()
        dx = pos.x() - self._start_pos.x()
        dy = pos.y() - self._start_pos.y()
        mw = self.window().minimumWidth()
        mh = self.window().minimumHeight()

        if "E" in self.edges:
            g.setWidth(max(mw, g.width() + dx))
        if "S" in self.edges:
            g.setHeight(max(mh, g.height() + dy))
        if "W" in self.edges:
            new_w = max(mw, g.width() - dx)
            g.setLeft(g.right() - new_w)
        if "N" in self.edges:
            new_h = max(mh, g.height() - dy)
            g.setTop(g.bottom() - new_h)

        self.window().setGeometry(g)
        event.accept()

        
        layout.addWidget(QLabel("Default Volume"))

        vol_row = QHBoxLayout()
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(current_volume)
        self.vol_value = QLabel(f"{current_volume}%")
        self.vol_value.setObjectName("InfoLabel")
        self.vol_slider.valueChanged.connect(
            lambda v: self.vol_value.setText(f"{v}%"))
        vol_row.addWidget(self.vol_slider, 1)
        vol_row.addWidget(self.vol_value)
        layout.addLayout(vol_row)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Apply")
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)
