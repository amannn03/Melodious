"""Bottom playbar with transport controls, seek bar, and volume."""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence

from melodious.ui import icons

ICON_SIZE = 22


class _SeekSlider(QSlider):
    """QSlider that also jumps to the clicked position on the groove."""

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.width() > 0:
            ratio = event.position().x() / self.width()
            value = self.minimum() + (self.maximum() - self.minimum()) * ratio
            self.setValue(int(value))
            self.sliderPressed.emit()
        super().mousePressEvent(event)


class Playbar(QWidget):
    play_pause_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    seek_requested = pyqtSignal(int)
    volume_changed = pyqtSignal(int)
    loop_toggled = pyqtSignal(bool)
    shuffle_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BottomPlaybar")
        self.setMinimumHeight(84)
        self.setMaximumHeight(260)
        self._is_playing = False
        self._seeking = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 4, 16, 8)
        main_layout.setSpacing(4)

        seek_row = QHBoxLayout()
        seek_row.setSpacing(8)

        self.time_label = QLabel("00:00")
        self.time_label.setObjectName("InfoLabel")

        self.seek_slider = _SeekSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderPressed.connect(self._on_seek_press)
        self.seek_slider.sliderReleased.connect(self._on_seek_release)
        self.seek_slider.sliderMoved.connect(self._on_seek_move)

        self.duration_label = QLabel("00:00")
        self.duration_label.setObjectName("InfoLabel")

        seek_row.addWidget(self.time_label)
        seek_row.addWidget(self.seek_slider, 1)
        seek_row.addWidget(self.duration_label)
        main_layout.addLayout(seek_row)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(8)

        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setObjectName("ShuffleBtn")
        self.seek_slider = _SeekSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderPressed.connect(self._on_seek_press)
        self.seek_slider.sliderReleased.connect(self._on_seek_release)
        self.seek_slider.sliderMoved.connect(self._on_seek_move)


        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("TransportBtn")
        self.prev_btn.setFixedSize(46, 46)
        self.prev_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self.prev_clicked.emit)

        self.play_btn = QPushButton()
        self.play_btn.setObjectName("PlayPauseBtn")
        self.play_btn.setFixedSize(54, 54)
        self.play_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)

        self.next_btn = QPushButton()
        self.next_btn.setObjectName("TransportBtn")
        self.next_btn.setFixedSize(46, 46)
        self.next_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.next_clicked.emit)

        self.loop_btn = QPushButton()
        self.loop_btn.setObjectName("LoopBtn")
        self.loop_btn.setCheckable(True)
        self.loop_btn.setToolTip("Repeat current track")
        self.loop_btn.setFixedSize(44, 44)
        self.loop_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.loop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.loop_btn.toggled.connect(self.loop_toggled.emit)


        vol_row = QHBoxLayout()
        vol_row.setSpacing(4)

        self.vol_icon = QPushButton()
        self.vol_icon.setObjectName("VolumeBtn")
        self.vol_icon.setFixedSize(34, 34)
        self.vol_icon.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.vol_icon.setCursor(Qt.CursorShape.PointingHandCursor)
