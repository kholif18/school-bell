# apps/desktop/tabs/settings_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


class SettingsTab(QWidget):

    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Volume"))

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.app.config.get("volume", 80))

        self.test_btn = QPushButton("🔊 Test Audio")

        layout.addWidget(self.volume_slider)
        layout.addWidget(self.test_btn)
        layout.addStretch()

        self.volume_slider.valueChanged.connect(self.save_volume)
        self.test_btn.clicked.connect(self.test_audio)

    def save_volume(self, v):
        self.app.config.set("volume", v)
        self.app.audio.set_volume(v)

    def test_audio(self):
        self.app.test_audio()