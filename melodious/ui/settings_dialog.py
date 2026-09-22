"""Preferences dialog for Melodious (theme + volume)."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSlider, QPushButton
)
from PyQt6.QtCore import Qt

from melodious.ui.themes import THEMES


class SettingsDialog(QDialog):
    def __init__(self, current_theme: str, current_volume: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setFixedWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dracula", "dracula")
        self.theme_combo.addItem("Gruvbox Dark", "gruvbox")
        self.theme_combo.addItem("Ayu Dark", "ayu_dark")
        self.theme_combo.addItem("Tokyo Night", "tokyo_night")
        self.theme_combo.addItem("Nord", "nord")
        idx = self.theme_combo.findData(current_theme)
        self.theme_combo.setCurrentIndex(max(0, idx))
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Default Volume"))

        vol_row = QHBoxLayout()
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(current_volume)
        self.vol_value = QLabel(f"{current_volume}%")
        self.vol_value.setObjectName("InfoLabel")
        self.vol_slider.valueChanged.connect(
            lambda v: self.vol_value.setText(f"{v}%"))
        vol_row.addWidget(self.vol_slider, 1)
        vol_row.addWidget(self.vol_value)
        layout.addLayout(vol_row)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Apply")
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)

    def theme_name(self) -> str:
        return self.theme_combo.currentData()

    def volume(self) -> int:
        return self.vol_slider.value()