"""Melodious entry point."""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from melodious.ui.main_window import MainWindow

_ASSETS = Path(__file__).resolve().parent / "melodious" / "assets" / "icons"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Melodious")
    app.setOrganizationName("Melodious")

    icon = QIcon()
    for size in (16, 32, 48, 64, 128, 256, 512):
        pm = _ASSETS / f"melodious-{size}.png"
        if pm.exists():
            icon.addFile(str(pm))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
