"""Full-width audio waveform visualizer using QPainter."""



import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QLinearGradient

import numpy as np


class WaveformVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)

        self._bars = 64
        self._values = np.zeros(self._bars)
        self._target_values = np.zeros(self._bars)
        self._accent_color = QColor(203, 166, 247)
        self._is_playing = False

        self._timer = QTimer()
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._animate)

    def start(self) -> None:
        self._is_playing = True
        self._timer.start()

    def stop(self) -> None:
        self._is_playing = False

    def set_accent_color(self, r: int, g: int, b: int) -> None:
        self._accent_color = QColor(r, g, b)

    def _animate(self) -> None:
        if self._is_playing:
            for i in range(self._bars):
                self._target_values[i] = random.uniform(0.1, 1.0)
        else:
            for i in range(self._bars):
                self._target_values[i] *= 0.92

        for i in range(self._bars):
            diff = self._target_values[i] - self._values[i]
            self._values[i] += diff * 0.3

        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_width = max(2, (w - self._bars * 2) / self._bars)
        gap = 2
        total_width = self._bars * (bar_width + gap) - gap
        start_x = (w - total_width) / 2

        base_color = self._accent_color

        for i in range(self._bars):
            val = self._values[i]
            bar_h = max(3, val * (h - 10))
            x = start_x + i * (bar_width + gap)
            y = h - bar_h

            alpha = int(120 + val * 135)
            color = QColor(base_color)
            color.setAlpha(alpha)

            gradient = QLinearGradient(x, y, x, h)
            gradient.setColorAt(0.0, QColor(base_color))
            gradient.setColorAt(0.5, QColor(
                min(255, base_color.red() + 30),
                min(255, base_color.green() + 30),
                min(255, base_color.blue() + 30),
                alpha))
            gradient.setColorAt(1.0, QColor(base_color.red() // 2,
                                             base_color.green() // 2,
                                             base_color.blue() // 2, alpha // 2))

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRect(int(x), int(y), int(bar_width), int(bar_h)),
                int(bar_width / 2), int(bar_width / 2))

        painter.end()
