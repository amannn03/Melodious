"""Center panel with track info header and tracklist table."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt

from melodious.core.metadata import TrackMetadata


class CenterPanel(QWidget):
    track_double_clicked = pyqtSignal(int)
    track_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CenterPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 8, 8)
        layout.setSpacing(8)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)

        self.title_label = QLabel("No Track Selected")
        self.title_label.setObjectName("TrackInfoTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setMinimumSize(0, 0)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        info_col.addWidget(self.title_label)
        info_layout.addLayout(info_col)
        info_layout.addStretch()

        layout.addLayout(info_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Title", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        self._tracks: list[TrackMetadata] = []
        self._global_indices: list[int] = []

    def set_tracks(self, tracks: list[TrackMetadata],
                   global_indices: list[int] | None = None) -> None:
        self._tracks = tracks
        self._global_indices = (global_indices
                                if global_indices is not None
                                else list(range(len(tracks))))
        self.table.setRowCount(len(tracks))
        self.table.clearSelection()

        for i, track in enumerate(tracks):
            title_item = QTableWidgetItem(track.title)
            dur_item = QTableWidgetItem(track.duration_str)
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(i, 0, title_item)
            self.table.setItem(i, 1, dur_item)

    def highlight_track(self, index: int) -> None:
        if index in self._global_indices:
            row = self._global_indices.index(index)
            self.table.selectRow(row)

    def update_track_info(self, track: TrackMetadata) -> None:
        self.title_label.setText(track.title)

    def _on_double_click(self, index) -> None:
        row = index.row()
        if 0 <= row < len(self._global_indices):
            self.track_double_clicked.emit(self._global_indices[row])

    def _on_selection_changed(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            if 0 <= row < len(self._global_indices):
                self.track_selected.emit(self._global_indices[row])