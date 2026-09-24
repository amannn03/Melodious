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
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setToolTip("Shuffle (random order)")
        self.shuffle_btn.setFixedSize(44, 44)
        self.shuffle_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.shuffle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shuffle_btn.toggled.connect(self.shuffle_toggled.emit)

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

        controls_row.addStretch()
        controls_row.addWidget(self.shuffle_btn)
        controls_row.addSpacing(8)
        controls_row.addWidget(self.prev_btn)
        controls_row.addSpacing(4)
        controls_row.addWidget(self.play_btn)
        controls_row.addSpacing(4)
        controls_row.addWidget(self.next_btn)
        controls_row.addSpacing(8)
        controls_row.addWidget(self.loop_btn)
        controls_row.addStretch()

        vol_row = QHBoxLayout()
        vol_row.setSpacing(4)

        self.vol_icon = QPushButton()
        self.vol_icon.setObjectName("VolumeBtn")
        self.vol_icon.setFixedSize(34, 34)
        self.vol_icon.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self.vol_icon.setCursor(Qt.CursorShape.PointingHandCursor)

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setObjectName("VolumeSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.valueChanged.connect(self.volume_changed.emit)

        vol_row.addWidget(self.vol_icon)
        vol_row.addWidget(self.vol_slider)

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addStretch()
        right_layout.addLayout(vol_row)

        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addLayout(controls_row, 3)
        outer.addLayout(right_layout, 1)

        main_layout.addLayout(outer)

        self._setup_shortcuts()
        self._fg = "#CDD6F4"
        self._on_accent = "#11111B"
        self._build_icons()

    def _build_icons(self) -> None:
        fg = self._fg
        self.shuffle_btn.setIcon(icons.icon_shuffle(ICON_SIZE, fg))
        self.prev_btn.setIcon(icons.icon_prev(ICON_SIZE, fg))
        self.next_btn.setIcon(icons.icon_next(ICON_SIZE, fg))
        self.loop_btn.setIcon(icons.icon_repeat_one(ICON_SIZE, fg))
        self.vol_icon.setIcon(icons.icon_volume(ICON_SIZE, fg))
        self._apply_play_icon()

    def _apply_play_icon(self) -> None:
        if self._is_playing:
            self.play_btn.setIcon(icons.icon_pause(ICON_SIZE, self._on_accent))
        else:
            self.play_btn.setIcon(icons.icon_play(ICON_SIZE, self._on_accent))

    def set_icon_colors(self, fg: str, on_accent: str) -> None:
        self._fg = fg
        self._on_accent = on_accent
        self._build_icons()

    def _setup_shortcuts(self) -> None:
        space = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space.activated.connect(self.play_pause_clicked.emit)

        left = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        left.activated.connect(self.prev_clicked.emit)

        right = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        right.activated.connect(self.next_clicked.emit)

        up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up.activated.connect(lambda: self.vol_slider.setValue(
            min(100, self.vol_slider.value() + 5)))

        down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down.activated.connect(lambda: self.vol_slider.setValue(
            max(0, self.vol_slider.value() - 5)))

    def _on_seek_press(self) -> None:
        self._seeking = True

    def _on_seek_release(self) -> None:
        self._seeking = False
        self.seek_requested.emit(self.seek_slider.value())

    def _on_seek_move(self, value: int) -> None:
        pass

    def set_playing(self, playing: bool) -> None:
        self._is_playing = playing
        self._apply_play_icon()

    def update_position(self, ms: float, duration_ms: float) -> None:
        if not self._seeking:
            if duration_ms > 0:
                self.seek_slider.setValue(int((ms / duration_ms) * 1000))
            self.time_label.setText(self._fmt(ms))
        self.duration_label.setText(self._fmt(duration_ms))

    @staticmethod
    def _fmt(ms: float) -> str:
        total_secs = int(ms / 1000)
        mins = total_secs // 60
        secs = total_secs % 60
        return f"{mins:02d}:{secs:02d}"
