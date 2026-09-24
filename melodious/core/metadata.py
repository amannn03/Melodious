"""Metadata extraction using Mutagen and Pillow."""
import io
from pathlib import Path
from dataclasses import dataclass, field

from mutagen import File as MutagenFile
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4
from mutagen.id3 import ID3FileType
from mutagen.wave import WAVE
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap


DEFAULT_COLOR = (203, 166, 247)


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


def extract_metadata_files(files: list[str]) -> list[TrackMetadata]:
    return [m for m in (extract_metadata(f) for f in files) if m]


def scan_folder(folder: str) -> list[TrackMetadata]:
    tracks = []
    path = Path(folder)
    if not path.is_dir():
        return tracks

    for f in sorted(path.rglob("*")):
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
            meta = extract_metadata(str(f))
            if meta:
                tracks.append(meta)
    return tracks


def _extract_cover(filepath: str) -> tuple[QPixmap | None, tuple[int, int, int]]:
    cover_data = _read_cover_data(filepath)
    if cover_data is None:
        return None, DEFAULT_COLOR
    return _bytes_to_cover(cover_data)


def _read_cover_data(filepath: str) -> bytes | None:
    try:
        audio = MutagenFile(filepath)
    except Exception:
        return None
    if audio is None:
        return None

    try:
        if isinstance(audio, MP4):
            tags = audio.tags
            if tags and "covr" in tags and tags["covr"]:
                return bytes(tags["covr"][0])
        elif isinstance(audio, FLAC):
            if audio.pictures:
                return audio.pictures[0].data
        elif isinstance(audio, ID3FileType):
            tags = audio.tags
            if tags:
                for key in tags.getall("APIC"):
                    return key.data
        elif isinstance(audio, WAVE):
            tags = audio.tags
            if tags:
                for key in tags.getall("APIC"):
                    return key.data
        else:
            data = _read_picture_attr(audio)
            if data:
                return data
    except Exception:
        return None
    return None


def _read_picture_attr(audio) -> bytes | None:
    """Read picture data from OGG/Opus-style containers."""
    pictures = getattr(audio, "pictures", None)
    if pictures:
        try:
            return pictures[0].data
        except Exception:
            pass

    tags = getattr(audio, "tags", None)
    if tags is None:
        return None

    vorbis = tags.get("METADATA_BLOCK_PICTURE") or tags.get("metadata_block_picture")
    if vorbis:
        try:
            return Picture(vorbis[0]).data
        except Exception:
            pass

    cover = tags.get("COVERART") or tags.get("coverart")
    if cover:
        try:
            return bytes(cover[0]) if not isinstance(cover[0], bytes) else cover[0]
        except Exception:
            pass
    return None


def _bytes_to_cover(cover_data: bytes) -> tuple[QPixmap | None, tuple[int, int, int]]:
    try:
        img = Image.open(io.BytesIO(cover_data))
        img = img.convert("RGB")

        dominant = _dominant_color(img)

        img = img.resize((400, 400), Image.Resampling.LANCZOS)
        data = img.tobytes("raw", "RGB")
        qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimg), dominant
    except Exception:
        return None, DEFAULT_COLOR


def _dominant_color(img: Image.Image) -> tuple[int, int, int]:
    try:
        small = img.resize((50, 50), Image.Resampling.LANCZOS)
        q = small.quantize(colors=1, method=Image.Quantize.MEDIANCUT)
        palette = q.getpalette()
        if palette:
            return (palette[0], palette[1], palette[2])
    except Exception:
        pass
    return DEFAULT_COLOR