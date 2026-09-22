# Audio playback engines for Melodious.


from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput




class BaseAudioPlayer(QObject):
    track_changed = pyqtSignal(object)
    position_changed = pyqtSignal(float, float)
    playback_state_changed = pyqtSignal(object)
    playback_ended = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.playlist: list[TrackMetadata] = []
        self.current_index: int = -1
        self.state = PlaybackState.STOPPED
        self.loop_mode = False
        self.shuffle_mode = False
        self.play_order: list[int] = []
        self._auto_advance = False
        self._volume = 80

        self._timer = QTimer()
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._emit_position)

    # ---- Playlist management ----
    def add_tracks(self, tracks: list[TrackMetadata]) -> list[TrackMetadata]:
        added = []
        for t in tracks:
            if not any(p.filepath == t.filepath for p in self.playlist):
                self.playlist.append(t)
                added.append(t)
        return added

    def add_folder(self, folder: str) -> list[TrackMetadata]:
        from melodious.core.metadata import scan_folder
        return self.add_tracks(scan_folder(folder))

    def clear(self) -> None:
        self.stop()
        self.playlist.clear()
        self.current_index = -1
        self.play_order = []

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


                
    def _current_seq(self) -> list[int]:
        if self.play_order:
            return [i for i in self.play_order if 0 <= i < len(self.playlist)]
        return list(range(len(self.playlist)))

    def _select_next_index(self) -> int | None:
        seq = self._current_seq()
        if not seq:
            return None
        if self.shuffle_mode:
            pool = [i for i in seq if i != self.current_index] or seq
            return random.choice(pool)
        if self.current_index in seq:
            return seq[(seq.index(self.current_index) + 1) % len(seq)]
        return seq[0]

    def _select_auto_next_index(self) -> int | None:
        """Index to advance to automatically when the current track ends."""
        if self._current_seq():
            if self.loop_mode:
                return max(0, self.current_index)
            return self._select_next_index()
        return None

    def _advance_on_end(self) -> None:
        idx = self._select_auto_next_index()
        if idx is not None:
            self.play_track(idx)

    def _select_prev_index(self) -> int | None:
        seq = self._current_seq()
        if not seq:
            return None
        if self.current_index in seq:
            return seq[(seq.index(self.current_index) - 1) % len(seq)]
        return seq[0]

    def _emit_position(self) -> None:
        self.position_changed.emit(self.get_position_ms(),
                                   self.get_duration_ms())


class VLCPlayer(BaseAudioPlayer):

            """Index to advance to automatically when the current track ends."""
            if self._current_seq():
                if self.loop_mode:
                    return max(0, self.current_index)
                return self._select_next_index()
            return None
    
        def _advance_on_end(self) -> None:
            idx = self._select_auto_next_index()
            if idx is not None:
                self.play_track(idx)
    
        def _select_prev_index(self) -> int | None:
            seq = self._current_seq()
            if not seq:
                return None
            if self.current_index in seq:
                return seq[(seq.index(self.current_index) - 1) % len(seq)]
            return seq[0]
    
        def _emit_position(self) -> None:
            self.position_changed.emit(self.get_position_ms(),
                                       self.get_duration_ms())
    
    
    class VLCPlayer(BaseAudioPlayer):
        """Playback engine backed by python-vlc."""
    
        _media_end_reached = pyqtSignal()
    
        def __init__(self):
            super().__init__()
            self._locate_libvlc()
            import vlc
            self._vlc = vlc
            self._instance = None
            self.player = None
            self._end_callback = None
            self._media_end_reached.connect(self._on_media_end)
    
        def init(self) -> bool:
            try:
                self._instance = self._vlc.Instance("--no-video", "--aout=auto")
                if self._instance is None:
                    return False
                self.player = self._instance.media_player_new()
                if self.player is None:
                    return False
                self._end_callback = self._on_end_reached_event
                self.player.event_manager().event_attach(
                    self._vlc.EventType.MediaPlayerEndReached, self._end_callback)
                return True
            except Exception:
                return False
    
        def _on_end_reached_event(self, event) -> None:
            self._media_end_reached.emit()
    
        def _on_media_end(self) -> None:
            if self.player is None:
                return
            if self._auto_advance:
                self._auto_advance = False
                self.state = PlaybackState.STOPPED
                self._timer.stop()
                self._advance_on_end()
    
        @staticmethod
        def _locate_libvlc() -> None:
            """Point python-vlc at a versioned libvlc.so.* if the env var is unset."""
            if os.environ.get("PYTHON_VLC_LIB_PATH"):
                return
            import ctypes.util
            candidates = [
                ctypes.util.find_library("vlc"),
                ctypes.util.find_library("vlc.so.5"),
                "/usr/lib/libvlc.so.5",
                "/usr/lib64/libvlc.so.5",
                "/lib/libvlc.so.5",
                "/lib64/libvlc.so.5",
            ]
            for path in candidates:
                if path and os.path.exists(path):
                    os.environ["PYTHON_VLC_LIB_PATH"] = path
                    return
    
        def play_track(self, index: int) -> None:
            if not self.player or index < 0 or index >= len(self.playlist):
                return