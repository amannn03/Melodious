"""State persistence for Melodious."""
import json
from pathlib import Path


STATE_FILE = Path.home() / ".melodious_state.json"


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
    except Exception:
        pass
    return {
        "volume": 80,
        "theme": "dracula",
        "window_geometry": None,
        "last_track": None,
        "last_position": 0,
        "playlist": [],
    }
