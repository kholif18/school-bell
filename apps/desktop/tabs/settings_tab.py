#  apps/desktop/tabs/settings_tab.py
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from apps.desktop.widgets.audio_picker import AudioPicker

class SettingsTab(QWidget):

    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        form = QVBoxLayout(container)

        # =========================
        # 🔊 AUDIO
        # =========================
        audio_box = QGroupBox("🔊 Audio Settings")
        audio_layout = QVBoxLayout(audio_box)

        audio_layout.addWidget(QLabel("Volume"))

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.app.config.get("volume", 80))

        self.volume_label = QLabel(f"{self.volume_slider.value()}%")
        self.test_btn = QPushButton("🔊 Test Audio")

        audio_layout.addWidget(self.volume_slider)
        audio_layout.addWidget(self.volume_label)
        audio_layout.addWidget(self.test_btn)

        form.addWidget(audio_box)

        # =========================
        # ⚙️ SYSTEM
        # =========================
        system_box = QGroupBox("⚙️ System")
        system_layout = QVBoxLayout(system_box)

        # =========================
        # Startup Button
        # =========================
        self.autostart = QCheckBox("Jalankan saat startup")
        system_layout.addWidget(self.autostart)

        # ❗ disable signal dulu
        self.autostart.blockSignals(True)
        self.autostart.setChecked(self.app.config.get("autostart", False))
        self.autostart.blockSignals(False)

        # connect setelah init
        self.autostart.stateChanged.connect(self.on_autostart_change)

        system_layout.addWidget(QLabel("🔔 Manual Bell Audio"))

        self.manual_audio = AudioPicker(self.app)
        system_layout.addWidget(self.manual_audio)
        saved = self.app.config.get("manual_bell_audio", "")
        if saved:
            self.manual_audio.set_value(saved)

        self.manual_bell_btn = QPushButton("🔔 Play Manual Bell")
        system_layout.addWidget(self.manual_bell_btn)

        form.addWidget(system_box)

        self.save_btn = QPushButton("💾 Save Settings")
        form.addWidget(self.save_btn)
        form.addStretch()

        self.save_btn.clicked.connect(self.save_all)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # =========================
        # SIGNALS
        # =========================
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        self.test_btn.clicked.connect(self.test_audio)
        self.manual_bell_btn.clicked.connect(self.manual_bell)

    # =========================
    # ACTIONS
    # =========================

    def test_audio(self):
        self.app.test_audio()

    def manual_bell(self):
        file_path = self.manual_audio.get_value()

        if file_path:
            self.app.test_audio(file_path)
        else:
            self.app.test_audio()
            
    def on_autostart_change(self, state):
        enabled = state == Qt.CheckState.Checked.value

        # simpan config saja (UI state)
        self.app.config.set("autostart", enabled)

        # panggil OS service
        if enabled:
            self.app.autostart_service.enable()
        else:
            self.app.autostart_service.disable()
            
    def on_volume_change(self, v):
        self.volume_label.setText(f"{v}%")

        # realtime apply
        self.app.audio.set_volume(v)

        # optional: persist langsung juga boleh
        self.app.config.set("volume", v)

    def save_all(self):
        self.app.config.set("autostart", self.autostart.isChecked())
        self.app.config.set("manual_bell_audio", self.manual_audio.get_value())

        if self.autostart.isChecked():
            self.app.autostart_service.enable()
        else:
            self.app.autostart_service.disable()

        QMessageBox.information(self, "Settings", "Settings berhasil disimpan")