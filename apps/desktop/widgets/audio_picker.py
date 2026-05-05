# desktop/widgets/audio_picker.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal
from pathlib import Path

from core.audio_manager import get_audio_manager


class AudioPicker(QWidget):
    fileChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("🔔 Default bell")
        self.label.setStyleSheet("color: #8B949E;")

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._preview)
        self.play_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear)
        self.clear_btn.setEnabled(False)

        layout.addWidget(self.label, 2)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.clear_btn)

    # =========================
    # FILE ACTIONS
    # =========================
    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio",
            "",
            "Audio (*.mp3 *.wav *.ogg)"
        )
        if path:
            self.set_file(path)

    def set_file(self, path: str):
        self.current_file = path

        name = Path(path).name
        self.label.setText(f"🎵 {name}")
        self.label.setStyleSheet("color: #39FF14;")

        self.play_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        self.fileChanged.emit(path)

    def _preview(self):
        if self.current_file:
            get_audio_manager().play(self.current_file)

    def _clear(self):
        self.current_file = None

        self.label.setText("🔔 Default bell")
        self.label.setStyleSheet("color: #8B949E;")

        self.play_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)

        self.fileChanged.emit("")

    def get_path(self):
        return self.current_file