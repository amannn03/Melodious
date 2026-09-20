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
