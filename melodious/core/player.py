"""Audio playback engines for Melodious."""
import time
import random
import os
from enum import Enum
from pathlib import Path
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from melodious.core.metadata import TrackMetadata


class PlaybackState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


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

    # ---- Public API (implemented by subclasses) ----
    def play_track(self, index: int) -> None:  # pragma: no cover
        raise NotImplementedError

    def play_pause(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def stop(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def seek(self, position_ms: float) -> None:  # pragma: no cover
        raise NotImplementedError

    def get_position_ms(self) -> float:  # pragma: no cover
        return 0.0

    def get_duration_ms(self) -> float:  # pragma: no cover
        return 0.0

    def set_volume(self, vol: int) -> None:  # pragma: no cover
        self._volume = max(0, min(100, vol))

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def current_track(self) -> TrackMetadata | None:
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

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

        self.current_index = index
        track = self.playlist[index]

        media = self._instance.media_new(track.filepath)
        self.player.set_media(media)
        self.player.play()
        self._wait_for_play()
        self.player.audio_set_volume(self._volume)
        self.state = PlaybackState.PLAYING
        self._auto_advance = True
        self._timer.start()
        self.track_changed.emit(track)
        self.playback_state_changed.emit(self.state)

    def _wait_for_play(self, timeout: float = 2.0) -> None:
        if self.player is None:
            return
        start = time.time()
        while time.time() - start < timeout:
            state = self.player.get_state()
            if state in (self._vlc.State.Playing, self._vlc.State.Paused):
                return
            time.sleep(0.03)

    def play_pause(self) -> None:
        if self.player is None:
            return
        if self.state == PlaybackState.STOPPED:
            if self.playlist:
                self.play_track(max(0, self.current_index))
            return

        if self.state == PlaybackState.PLAYING:
            self.player.pause()
            self.state = PlaybackState.PAUSED
            self._timer.stop()
        elif self.state == PlaybackState.PAUSED:
            self.player.play()
            self.state = PlaybackState.PLAYING
            self._timer.start()

        self.playback_state_changed.emit(self.state)

    def stop(self) -> None:
        if self.player is None:
            return
        self._auto_advance = False
        self.player.stop()
        self.state = PlaybackState.STOPPED
        self._timer.stop()
        self.playback_state_changed.emit(self.state)

    def next_track(self) -> None:
        idx = self._select_next_index()
        if idx is not None:
            self.play_track(idx)

    def prev_track(self) -> None:
        if self.player is None or not self.playlist:
            return
        if self.player.get_time() > 3000:
            self.seek(0)
            return
        self.play_track(self._select_prev_index() or 0)

    def seek(self, position_ms: float) -> None:
        if self.player is None:
            return
        self.player.set_position(position_ms / 1000.0)

    def get_position_ms(self) -> float:
        if self.player is None:
            return 0.0
        return self.player.get_position() * 1000.0

    def get_duration_ms(self) -> float:
        if self.player is None:
            return 0.0
        length = self.player.get_length()
        return length if length > 0 else 0.0

    def set_volume(self, vol: int) -> None:
        self._volume = max(0, min(100, vol))
        if self.player is not None:
            self.player.audio_set_volume(self._volume)

    def _emit_position(self) -> None:
        super()._emit_position()
        if self.player is None:
            return
        state = self.player.get_state()
        if state == self._vlc.State.Ended:
            self._on_media_end()


class QtMultimediaPlayer(BaseAudioPlayer):
    """Fallback playback engine using PyQt6's QtMultimedia."""

    def __init__(self):
        super().__init__()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(self._volume / 100.0)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

        self.player.positionChanged.connect(self.playerPositionChanged)
        self.player.mediaStatusChanged.connect(self.playerMediaStatusChanged)
        self.player.playbackStateChanged.connect(self.playerPlaybackStateChanged)
        self.player.errorOccurred.connect(self.playerErrorOccurred)

        self._loading_next = False
        self._is_playing = False
        self._duration = 0.0
        self._position = 0.0

    def playerPositionChanged(self, pos: int) -> None:
        self._position = float(pos)
        dur = self.player.duration()
        if dur > 0:
            self._duration = float(dur)
        self.position_changed.emit(self._position, self._duration)

    def playerMediaStatusChanged(self, status) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._auto_advance:
                self._auto_advance = False
                self.state = PlaybackState.STOPPED
                self._timer.stop()
                self._advance_on_end()

    def playerPlaybackStateChanged(self, state) -> None:
        from PyQt6.QtMultimedia import QMediaPlayer
        new_state = PlaybackState.STOPPED
        if state == QMediaPlayer.PlaybackState.PlayingState:
            new_state = PlaybackState.PLAYING
        elif state == QMediaPlayer.PlaybackState.PausedState:
            new_state = PlaybackState.PAUSED
        if new_state != self.state:
            self.state = new_state
            self.playback_state_changed.emit(self.state)

    def playerErrorOccurred(self, error, error_string) -> None:
        print(f"[Melodious] Playback error: {error_string}")

    def play_track(self, index: int) -> None:
        if index < 0 or index >= len(self.playlist):
            return

        self.current_index = index
        track = self.playlist[index]

        url = QUrl.fromLocalFile(track.filepath)
        self.player.stop()
        self.player.setSource(url)
        self.player.play()
        self._duration = 0.0
        self._auto_advance = True
        self._timer.start()
        self.track_changed.emit(track)
        self.playback_state_changed.emit(PlaybackState.PLAYING)

    def play_pause(self) -> None:
        if self.state == PlaybackState.STOPPED:
            if self.playlist:
                self.play_track(max(0, self.current_index))
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self._timer.stop()
            self.state = PlaybackState.PAUSED
        else:
            self.player.play()
            self._timer.start()
            self.state = PlaybackState.PLAYING
        self.playback_state_changed.emit(self.state)

    def stop(self) -> None:
        self._auto_advance = False
        self.player.stop()
        self.state = PlaybackState.STOPPED
        self._timer.stop()
        self.playback_state_changed.emit(self.state)

    def next_track(self) -> None:
        idx = self._select_next_index()
        if idx is not None:
            self.play_track(idx)

    def prev_track(self) -> None:
        if not self.playlist:
            return
        if self._position > 3000:
            self.seek(0)
            return
        self.play_track(self._select_prev_index() or 0)

    def seek(self, position_ms: float) -> None:
        self.player.setPosition(int(position_ms))

    def get_position_ms(self) -> float:
        return float(self.player.position())

    def get_duration_ms(self) -> float:
        return float(self.player.duration()) if self._duration > 0 else float(self.player.duration())

    def set_volume(self, vol: int) -> None:
        self._volume = max(0, min(100, vol))
        self.audio_output.setVolume(self._volume / 100.0)


def create_player() -> BaseAudioPlayer:
    """Factory: try VLC, fall back to QtMultimedia if VLC is unavailable."""
    vlc_player = VLCPlayer()
    if vlc_player.init():
        return vlc_player
    print("[Melodious] VLC unavailable, using QtMultimedia backend.")
    return QtMultimediaPlayer()