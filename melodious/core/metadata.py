"""Metadata extraction using Mutagen and Pillow."""



from pathlib import Path
from dataclasses import dataclass, field

from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4
from mutagen.id3 import ID3FileType


@dataclass
class TrackMetadata:
    filepath: str
    title: str
    artist: str
    album: str
    duration: float
    cover_pixmap: QPixmap | None = None
    cover_dominant_color: tuple[int, int, int] = field(default_factory=lambda: DEFAULT_COLOR)

    @property
    def duration_str(self) -> str:
        mins = int(self.duration) // 60
        secs = int(self.duration) % 60
        return f"{mins:02d}:{secs:02d}"

    def load_cover(self) -> None:
        """Lazily load the embedded cover art for an unloaded track."""
        if self.cover_pixmap is None:
            pix, color = _extract_cover(self.filepath)
            self.cover_pixmap = pix
            self.cover_dominant_color = color


AUDIO_EXTENSIONS = {
    ".mp3", ".flac", ".wav", ".ogg", ".aac",
    ".m4a", ".wma", ".opus", ".aiff", ".alac",
}

AUDIO_FILTER = "Audio Files (*.mp3 *.flac *.wav *.ogg *.aac *.m4a *.wma *.opus *.aiff *.alac)"


def extract_metadata(filepath: str) -> TrackMetadata | None:
    path = Path(filepath)
    if not path.exists() or path.suffix.lower() not in AUDIO_EXTENSIONS:
        return None

    try:
        audio = MutagenFile(filepath, easy=True)
        if audio is None:
            return None

        duration = audio.info.length if audio.info else 0.0
        title = (audio.get("title", [path.stem]))[0]
        artist = (audio.get("artist", ["Unknown Artist"]))[0]
        album = (audio.get("album", ["Unknown Album"]))[0]

        pix, color = _extract_cover(filepath)

        return TrackMetadata(
            filepath=filepath,
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            cover_pixmap=pix,
            cover_dominant_color=color,
        )
    except Exception:
        return TrackMetadata(
            filepath=filepath,
            title=path.stem,
            artist="Unknown Artist",
            album="Unknown Album",
            duration=0.0,
        )
