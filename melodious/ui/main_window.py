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

