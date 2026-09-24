
## Overview

**Melodious** (codenamed *AuraPlayer*) is a modern, fully **offline** desktop music player
built with **Python** and **PyQt6**. It combines a sleek, frameless interface with a rich
feature set — auto-playing smart queue, a live 64-bar waveform visualizer, album-art
discovery, five hand-crafted dark themes, keyboard shortcuts, and complete state
persistence.

It is designed to be **beginner-friendly**: install the dependencies, add a folder, and
double-click a song to start. No accounts, no streaming, no network — your music stays on
your machine.

---

## Features

### Playback Engine
- **Dual audio backends with automatic fallback** — Melodious tries the **VLC** engine
  first; if VLC is unavailable it silently switches to **QtMultimedia (FFmpeg)**, so the
  app always plays.
- **Auto-advance** — when a song finishes, the next one starts automatically.
- **Smart queue wrapping** — when the playlist ends, playback wraps around and starts from
  the top.
- **Repeat one 🔂** — loop the current track over and over.
- **Shuffle 🔀** — play tracks in random order (never repeats until the queue is exhausted).
- **Skip back / forward ⏮ ⏭** — jump between tracks instantly.
- **Smart "Previous"** — if playback is more than 3 seconds in, *Previous* restarts the
  current track; otherwise it goes to the previous one.
- **Play / pause toggle** — the transport button swaps between play ▶ and pause ⏸ icons.

### Live Waveform Visualizer
- A smooth, animated spectrum of **64 bars**, rendered in real time at ~33 FPS with
  `QPainter` and `numpy`.
- Each bar is drawn with a vertical gradient and pill-shaped caps; alpha and height react
  to the animation value.
- **Smart colorization** — the visualizer automatically re-colors to match the active
  theme's accent color, or the **dominant color of the current album art** when a track is
  selected.
- **Smooth fade-out** — when playback stops or ends, the bars decay exponentially instead
  of freezing.

### Cover Art & Metadata
- Embedded album artwork is extracted from your audio files via **Mutagen** and **Pillow**
  (ID3 `APIC`, MP4 `covr`, FLAC pictures, Vorbis/OGG `METADATA_BLOCK_PICTURE`, etc.).
- A large, square right-side **cover-art panel** shows the current song's artwork (with a
  stylish ♫ placeholder when no art is embedded).
- Artwork is normalized to a clean **400×400** preview.
- Track metadata — title, artist, album and duration — is read from **ID3 / Vorbis / MP4 /
  WAV** tags, with sensible fallbacks (`Unknown Artist`, `Unknown Album`, filename as title).
