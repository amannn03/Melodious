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

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._start_geom = None
        self._start_pos = None
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumSize(620, 420)
        self.setWindowTitle("Melodious")

        self._state = load_state()
        self._current_theme = self._state.get("theme", "dracula")
        self._theme_actions: dict[str, QAction] = {}

        self._playlists: list[tuple[str, str | None]] = []
        self._current_playlist_folder: str | None = None
        self._last_menu_close = 0.0
        self._loaded_folders: list[str] = []

        self.player = create_player()
        self._setup_ui()
        self._setup_connections()
        self._build_menus()
        self._apply_theme(self._current_theme)
        self._restore_state()

    # ------------------------------------------------------------------ UI
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(0)

        self._create_resize_handles(central)

        self.title_bar = TitleBar()
        main_layout.addWidget(self.title_bar)

        # --- horizontal splitter: tracklist | cover image (mouse adjustable)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.setObjectName("HSplitter")
        self.h_splitter.setHandleWidth(3)
        self.h_splitter.setChildrenCollapsible(False)

        self.center_panel = CenterPanel()
        self.right_panel = RightPanel()

        self.h_splitter.addWidget(self.center_panel)
        self.h_splitter.addWidget(self.right_panel)
        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 0)
        self.h_splitter.setSizes([760, 400])

        # --- vertical splitter: content | visualizer | playbar (mouse adjustable)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.setObjectName("VSplitter")
        self.v_splitter.setHandleWidth(3)
        self.v_splitter.setChildrenCollapsible(False)

        self.visualizer = WaveformVisualizer()
        self.playbar = Playbar()

        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.visualizer)
        self.v_splitter.addWidget(self.playbar)
        self.v_splitter.setStretchFactor(0, 1)
        self.v_splitter.setStretchFactor(1, 1)
        self.v_splitter.setStretchFactor(2, 0)
        self.v_splitter.setSizes([400, 100, 90])

        main_layout.addWidget(self.v_splitter, 1)

    def _create_resize_handles(self, parent: QWidget) -> None:
        self._handles: dict[str, _ResizeHandle] = {}
        specs = {
            "top": "N", "bottom": "S", "left": "W", "right": "E",
            "tl": "NW", "tr": "NE", "bl": "SW", "br": "SE",
        }
        for name, edges in specs.items():
            self._handles[name] = _ResizeHandle(parent, edges)
        self._position_resize_handles()

    def _position_resize_handles(self) -> None:
        if not hasattr(self, "_handles"):
            return
        central = self.centralWidget()
        if central is None:
            return
        w = central.width()
        h = central.height()
        t = 5
        c = 16
        geoms = {
            "top": QRect(0, 0, w, t),
            "bottom": QRect(0, h - t, w, t),
            "left": QRect(0, 0, t, h),
            "right": QRect(w - t, 0, t, h),
            "tl": QRect(0, 0, c, c),
            "tr": QRect(w - c, 0, c, c),
            "bl": QRect(0, h - c, c, c),
            "br": QRect(w - c, h - c, c, c),
        }
        visible = not self.isMaximized()
        for name, geom in geoms.items():
            handle = self._handles[name]
            handle.setGeometry(geom)
            handle.setVisible(visible)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_resize_handles()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.set_restored(self.isMaximized())
            self._position_resize_handles()

    # ------------------------------------------------------------------ menus
    def _build_menus(self) -> None:
        self._app_menu = QMenu(self)
        self._app_menu.addAction("Add Folder\u2026", self._on_add_folder)
        self._app_menu.addAction("Add File(s)\u2026", self._on_add_files)
        self._app_menu.addSeparator()

        self._playlists_menu = self._app_menu.addMenu("Playlists")
        self._app_menu.addAction("New Playlist\u2026", self._on_new_playlist)
        self._app_menu.addAction("Remove Current Playlist",
                                 self._on_remove_playlist)
        self._app_menu.addSeparator()
        self._app_menu.addAction("Clear Library", self._on_clear)

        self._app_menu.addSeparator()
        self._theme_menu = self._app_menu.addMenu("Theme")
        self._theme_group = QActionGroup(self)
        self._theme_group.setExclusive(True)
        for name in get_theme_names():
            action = QAction(get_theme(name)["name"], self)
            action.setCheckable(True)
            action.setChecked(name == self._current_theme)
            action.triggered.connect(
                lambda checked, n=name: self._apply_theme(n))
            self._theme_group.addAction(action)
            self._theme_menu.addAction(action)
            self._theme_actions[name] = action

        self._app_menu.addSeparator()
        self._app_menu.addAction("Preferences\u2026", self._show_preferences)
        self._app_menu.addAction("About Melodious", self._show_about)

        self._refresh_playlists_menu()

    def _on_menu_clicked(self) -> None:
        now = time.monotonic()
        if self._app_menu.isVisible():
            self._app_menu.close()
            self._last_menu_close = now
            return
        if now - self._last_menu_close < 0.25:
            return
        self._refresh_playlists_menu()
        btn = self.title_bar.menu_btn
        self._popup_menu_at(self._app_menu,
                            btn.mapToGlobal(QPoint(0, btn.height())))

    def _popup_menu_at(self, menu, anchor: QPoint) -> None:
        screen = self.screen()
        if screen is None:
            menu.popup(anchor)
            return
        geo = screen.availableGeometry()
        hint = menu.sizeHint()

        x = min(anchor.x(), geo.right() - hint.width() + 1)
        x = max(geo.left(), x)

        if anchor.y() + hint.height() <= geo.bottom():
            y = anchor.y()
        else:
            y = max(geo.top(), anchor.y() - hint.height() - self.title_bar.height())
        menu.popup(QPoint(x, y))

    def _refresh_playlists_menu(self) -> None:
        self._playlists_menu.clear()
        act = QAction("All Tracks", self)
        act.setCheckable(True)
        act.setChecked(self._current_playlist_folder is None)
        act.triggered.connect(lambda: self._select_playlist(None))
        self._playlists_menu.addAction(act)
        self._playlists_menu.addSeparator()
        for name, folder in self._playlists:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setChecked(self._current_playlist_folder == folder)
            act.triggered.connect(
                lambda checked, f=folder: self._select_playlist(f))
            self._playlists_menu.addAction(act)

    def _select_playlist(self, folder: str | None) -> None:
        self._current_playlist_folder = folder
        if folder is None:
            self.player.play_order = []
            self._refresh_center_panel()
            return
        prefix = str(Path(folder))
        indices = [i for i, t in enumerate(self.player.playlist)
                   if t.filepath.startswith(prefix)]
        tracks = [self.player.playlist[i] for i in indices]
        self.player.play_order = indices
        self.center_panel.set_tracks(tracks, indices)

    def _add_playlist_entry(self, name: str, folder: str | None = None) -> None:
        if any(n == name for n, _ in self._playlists):
            return
        self._playlists.append((name, folder))
        self._refresh_playlists_menu()

    def _setup_connections(self) -> None:
        self.title_bar.menu_clicked.connect(self._on_menu_clicked)

        self.center_panel.track_double_clicked.connect(self._on_track_play)
        self.center_panel.track_selected.connect(self._on_track_selected)

        self.playbar.play_pause_clicked.connect(self._on_play_pause)
        self.playbar.next_clicked.connect(self.player.next_track)
        self.playbar.prev_clicked.connect(self.player.prev_track)
        self.playbar.seek_requested.connect(self._on_seek)
        self.playbar.volume_changed.connect(self._on_volume)
        self.playbar.loop_toggled.connect(self._on_loop)
        self.playbar.shuffle_toggled.connect(self._on_shuffle)

        self.player.track_changed.connect(self._on_track_changed)
        self.player.position_changed.connect(self._on_position)
        self.player.playback_state_changed.connect(self._on_state)
        self.player.playback_ended.connect(self._on_playback_ended)

    # ------------------------------------------------------------------ theme
    def _apply_theme(self, name: str) -> None:
        self._current_theme = name
        theme = get_theme(name)
        self.setStyleSheet(build_stylesheet(theme))

        action = self._theme_actions.get(name)
        if action:
            action.setChecked(True)

        accent = theme["accent"].lstrip("#")
        self.visualizer.set_accent_color(
            int(accent[0:2], 16), int(accent[2:4], 16), int(accent[4:6], 16))
        self.playbar.set_icon_colors(theme["text"], theme["bg_titlebar"])
        self.title_bar.set_icon_colors(theme["text"])

    # ------------------------------------------------------------------ library / add
    def _on_add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Music Folder")
        if folder:
            self._on_folder_loaded(folder)

    def _on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Music Files", "", AUDIO_FILTER)
        if not files:
            return
        tracks = extract_metadata_files(files)
        added = self.player.add_tracks(tracks)
        if added:
            self._refresh_center_panel()

    def _on_folder_loaded(self, folder: str) -> None:
        new_tracks = self.player.add_folder(folder)
        if new_tracks:
            if folder not in self._loaded_folders:
                self._loaded_folders.append(folder)
            self._refresh_center_panel()
            name = folder.rstrip("/").rsplit("/", 1)[-1]
            self._add_playlist_entry(name, folder)
            self._select_playlist(folder)

    def _refresh_center_panel(self) -> None:
        indices = list(range(len(self.player.playlist)))
        self.player.play_order = []
        self.center_panel.set_tracks(self.player.playlist, indices)

    # ------------------------------------------------------------------ playlist
    def _on_new_playlist(self) -> None:
        name, ok = QInputDialog.getText(
            self, "New Playlist", "Playlist name:")
        if ok and name.strip():
            self._add_playlist_entry(name.strip())

    def _on_remove_playlist(self) -> None:
        removed = False
        if self._current_playlist_folder is not None:
            before = len(self._playlists)
            self._playlists = [
                (n, f) for n, f in self._playlists
                if f != self._current_playlist_folder
            ]
            removed = len(self._playlists) < before
        elif self._playlists:
            self._playlists.pop()
            removed = True
        if removed:
            self._current_playlist_folder = None
            self._refresh_playlists_menu()
            self._refresh_center_panel()

    # ------------------------------------------------------------------ playback
    def _on_track_play(self, index: int) -> None:
        self.player.play_track(index)

    def _on_track_selected(self, index: int) -> None:
        if 0 <= index < len(self.player.playlist):
            track = self.player.playlist[index]
            if track.cover_pixmap is None:
                track.load_cover()
            self.center_panel.update_track_info(track)
            self.right_panel.set_cover(track.cover_pixmap)
            self.right_panel.set_track_info(track.title, track.artist)
            r, g, b = track.cover_dominant_color
            self.visualizer.set_accent_color(r, g, b)

    def _on_play_pause(self) -> None:
        self.player.play_pause()

    def _on_seek(self, slider_val: int) -> None:
        dur = self.player.get_duration_ms()
        if dur > 0:
            ms = (slider_val / 1000.0) * dur
            self.player.seek(ms)

    def _on_volume(self, val: int) -> None:
        self.player.set_volume(val)

    def _on_loop(self, enabled: bool) -> None:
        self.player.loop_mode = enabled

    def _on_shuffle(self, enabled: bool) -> None:
        self.player.shuffle_mode = enabled

    def _on_track_changed(self, track: TrackMetadata | None) -> None:
        if track is None:
            return
        self.center_panel.highlight_track(self.player.current_index)
        self._on_track_selected(self.player.current_index)

    def _on_position(self, pos: float, dur: float) -> None:
        self.playbar.update_position(pos, dur)

    def _on_state(self, state: PlaybackState) -> None:
        playing = state == PlaybackState.PLAYING
        self.playbar.set_playing(playing)
        if playing:
            self.visualizer.start()
        else:
            self.visualizer.stop()

    def _on_playback_ended(self) -> None:
        self.playbar.set_playing(False)
        self.visualizer.stop()

    def _on_clear(self) -> None:
        self.player.clear()
        self._loaded_folders.clear()
        self._playlists.clear()
        self._current_playlist_folder = None
        self._refresh_playlists_menu()
        self.center_panel.set_tracks([])
        self.right_panel.set_cover(None)
        self.right_panel.set_track_info("No Track")
        self.center_panel.update_track_info(
            TrackMetadata(filepath="", title="No Track Selected",
                          artist="", album="", duration=0))
        self.visualizer.stop()
        self.playbar.set_playing(False)

    # ------------------------------------------------------------------ user menu
    def _show_preferences(self) -> None:
        dlg = SettingsDialog(
            self._current_theme,
            self.playbar.vol_slider.value(),
            self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._apply_theme(dlg.theme_name())
            vol = dlg.volume()
            self.playbar.vol_slider.setValue(vol)
            self.player.set_volume(vol)

    def _show_about(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle("About Melodious")
        box.setIcon(QMessageBox.Icon.Information)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setText(
            "<b>Melodious</b> <span style=\"color:#4DA3FF;\">&#10003;</span>"
            " <span style=\"color:#A6ADC8;\">v1.0.0</span><br><br>"
            "A modern, fully offline desktop music player.<br>"
            "Built with PyQt6, python-vlc, Mutagen and Pillow.<br><br>"
            "Made with <span style=\"color:#E5484D;\">&#10084;</span> by Amannn"
        )
        ok_btn = box.addButton(QMessageBox.StandardButton.Ok)
        ok_btn.setIcon(QIcon())
        ok_btn.setText("OK")
        box.exec()

    # ------------------------------------------------------------------ state
    def _restore_state(self) -> None:
        vol = self._state.get("volume", 80)
        self.playbar.vol_slider.setValue(vol)
        self.player.set_volume(vol)

        hsizes = self._state.get("splitter_h")
        if hsizes and isinstance(hsizes, list) and len(hsizes) == 2:
            self.h_splitter.setSizes(hsizes)
        vsizes = self._state.get("splitter_v")
        if vsizes and isinstance(vsizes, list) and len(vsizes) == 3:
            self.v_splitter.setSizes(vsizes)

        geom = self._state.get("window_geometry")
        if geom and isinstance(geom, list) and len(geom) == 4:
            self.setGeometry(*geom)
        else:
            self.resize(1200, 780)

        self._restore_music_folders()

    def _restore_music_folders(self) -> None:
        folders = self._state.get("music_folders") or []
        for folder in folders:
            if not isinstance(folder, str) or not Path(folder).is_dir():
                continue
            if folder in self._loaded_folders:
                continue
            new_tracks = self.player.add_folder(folder)
            if new_tracks:
                self._loaded_folders.append(folder)
                name = folder.rstrip("/").rsplit("/", 1)[-1]
                self._add_playlist_entry(name, folder)

        if self.player.playlist:
            self._refresh_center_panel()
            saved_pl = self._state.get("current_playlist_folder")
            if saved_pl and any(f == saved_pl for f in self._loaded_folders):
                self._select_playlist(saved_pl)

    def closeEvent(self, event: QCloseEvent) -> None:
        geo = self.geometry()
        self._state.update({
            "volume": self.player.volume,
            "theme": self._current_theme,
            "window_geometry": [geo.x(), geo.y(), geo.width(), geo.height()],
            "splitter_h": list(self.h_splitter.sizes()),
            "splitter_v": list(self.v_splitter.sizes()),
            "music_folders": list(self._loaded_folders),
            "current_playlist_folder": self._current_playlist_folder,
        })
        save_state(self._state)
        self.player.stop()
        event.accept()