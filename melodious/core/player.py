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