# apps/desktop/tabs/settings_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


class SettingsTab(QWidget):
    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self._build_ui()
        self._load()

    # ================= UI =================
    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._audio(layout)
        self._scheduler(layout)
        self._system(layout)

        layout.addStretch()

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

    def _audio(self, layout):
        group = QGroupBox("Audio")

        form = QFormLayout(group)

        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.valueChanged.connect(self._on_volume)

        self.vol_label = QLabel()

        box = QHBoxLayout()
        box.addWidget(self.volume)
        box.addWidget(self.vol_label)

        form.addRow("Volume", box)

        self.test = QPushButton("Test")
        self.test.clicked.connect(self._test_audio)
        form.addRow(self.test)

        layout.addWidget(group)

    def _scheduler(self, layout):
        group = QGroupBox("Scheduler")

        form = QFormLayout(group)

        self.auto_start = QCheckBox("Auto start")
        form.addRow(self.auto_start)

        layout.addWidget(group)

    def _system(self, layout):
        group = QGroupBox("System")

        form = QFormLayout(group)

        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])

        form.addRow("Log Level", self.log_level)

        layout.addWidget(group)

    # ================= LOGIC =================
    def _load(self):
        v = self.app.config.get("audio.volume", 80)
        self.volume.setValue(v)
        self.vol_label.setText(f"{v}%")

        self.auto_start.setChecked(
            self.app.config.get("auto_start", False)
        )

    def _on_volume(self, v):
        self.vol_label.setText(f"{v}%")
        self.app.audio_manager.set_volume(v)

    def _test_audio(self):
        try:
            self.app.audio_manager.play(None)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save(self):
        self.app.config.set("audio.volume", self.volume.value())
        self.app.config.set("auto_start", self.auto_start.isChecked())
        self.app.config.set("logging.level", self.log_level.currentText())

        QMessageBox.information(self, "Saved", "Settings saved")