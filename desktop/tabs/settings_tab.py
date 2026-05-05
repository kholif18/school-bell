# desktop/tabs/settings_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Audio settings
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout(audio_group)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        self.volume_label = QLabel("80%")
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        audio_layout.addRow("Master Volume:", volume_layout)
        
        self.test_audio_btn = QPushButton("🔊 Test Audio")
        self.test_audio_btn.clicked.connect(self.test_audio)
        audio_layout.addRow("", self.test_audio_btn)
        
        layout.addWidget(audio_group)
        
        # Scheduler settings
        sched_group = QGroupBox("Scheduler Settings")
        sched_layout = QFormLayout(sched_group)
        
        self.auto_start_cb = QCheckBox("Auto-start scheduler on app launch")
        sched_layout.addRow("", self.auto_start_cb)
        
        layout.addWidget(sched_group)
        
        # System settings
        system_group = QGroupBox("System")
        system_layout = QFormLayout(system_group)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        system_layout.addRow("Log Level:", self.log_level)
        
        layout.addWidget(system_group)
        layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)
    
    def load_settings(self):
        volume = self.app.config.get('audio.volume', 80)
        self.volume_slider.setValue(volume)
        self.volume_label.setText(f"{volume}%")
        
        auto_start = self.app.config.get('auto_start', False)
        self.auto_start_cb.setChecked(auto_start)
    
    def on_volume_change(self, val):
        self.volume_label.setText(f"{val}%")
        self.app.audio_manager.set_volume(val)
    
    def test_audio(self):
        try:
            self.app.audio_manager.play(None)
        except Exception as e:
            QMessageBox.critical(self, "Audio Error", f"Failed to play audio:\n{str(e)}")
    
    def save_settings(self):
        self.app.config.set('audio.volume', self.volume_slider.value())
        self.app.config.set('auto_start', self.auto_start_cb.isChecked())
        level = self.log_level.currentText()
        self.app.config.set('logging.level', level)
        
        QMessageBox.information(self, "Settings", "Settings saved successfully")