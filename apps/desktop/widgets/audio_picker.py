# desktop/widgets/audio_picker.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os


class AudioPicker(QWidget):

    def __init__(self, app_core, parent=None):
        super().__init__(parent)

        self.app = app_core
        self.current_file = None

        self._build()

    def _build(self):
        layout = QHBoxLayout(self)

        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)

        self.pick_btn = QPushButton("Browse")
        self.test_btn = QPushButton("Test")

        layout.addWidget(self.path_input)
        layout.addWidget(self.pick_btn)
        layout.addWidget(self.test_btn)

        self.pick_btn.clicked.connect(self.pick_file)
        self.test_btn.clicked.connect(self.test_audio)

    def pick_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio",
            "",
            "Audio Files (*.mp3 *.wav)"
        )

        if file:
            self.current_file = file
            self.path_input.setText(file)

    def test_audio(self):
        self.app.test_audio(self.current_file)

    def get_value(self):
        return self.current_file

    def set_value(self, path):
        self.current_file = path
        self.path_input.setText(path or "")