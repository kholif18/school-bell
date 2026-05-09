#  apps/desktop/tabs/settings_tab.py
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from apps.desktop.widgets.audio_picker import AudioPicker
from core import paths
from core.paths import get_paths
from core.version import APP_VERSION
import webbrowser

class SettingsTab(QWidget):

    def __init__(self, app_core):
        super().__init__()
        self.app = app_core
        self.theme = self.app.theme
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
        # 🎨 APPEARANCE + BACKUP
        # =========================

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # =====================================================
        # THEME BOX
        # =====================================================

        theme_box = QGroupBox("🎨 Theme")
        theme_layout = QVBoxLayout(theme_box)

        self.theme_label = QLabel(
            f"Current: {self.theme.current_theme}"
        )

        self.theme_toggle = QPushButton("Switch Theme")
        self.theme_toggle.setObjectName("systemButton")

        theme_layout.addWidget(self.theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_toggle)

        # =====================================================
        # BACKUP BOX
        # =====================================================

        backup_box = QGroupBox("💾 Backup & Restore")
        backup_layout = QVBoxLayout(backup_box)

        backup_info = QLabel(
            "Backup database schedules dan profiles."
        )

        backup_info.setWordWrap(True)

        btn_row = QHBoxLayout()

        self.backup_btn = QPushButton("💾 Backup")
        self.restore_btn = QPushButton("📂 Restore")

        btn_row.addWidget(self.backup_btn)
        btn_row.addWidget(self.restore_btn)

        backup_layout.addWidget(backup_info)
        backup_layout.addStretch()
        backup_layout.addLayout(btn_row)

        # =====================================================
        # UPDATE BOX
        # =====================================================

        update_box = QGroupBox("🚀 Update")
        update_layout = QVBoxLayout(update_box)

        self.version_label = QLabel(
            f"Version: {APP_VERSION}"
        )

        update_info = QLabel(
            "Check aplikasi terbaru dan update system."
        )

        update_info.setWordWrap(True)

        self.check_update_btn = QPushButton("🚀 Check Update")
        self.check_update_btn.setObjectName("systemButton")

        update_layout.addWidget(self.version_label)
        update_layout.addWidget(update_info)
        update_layout.addStretch()
        update_layout.addWidget(self.check_update_btn)

        # =====================================================
        # SIZE RATIO
        # =====================================================

        top_row.addWidget(theme_box, 1)
        top_row.addWidget(backup_box, 2)
        top_row.addWidget(update_box, 1)

        form.addLayout(top_row)

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

        # =========================
        # MANUAL BELL CONTROLS
        # =========================
        btn_row = QHBoxLayout()

        self.manual_bell_btn = QPushButton("🔔 Play Manual Bell")
        self.stop_bell_btn = QPushButton("⏹ Stop Bell")

        self.stop_bell_btn.setObjectName("dangerButton")

        btn_row.addWidget(self.manual_bell_btn)
        btn_row.addWidget(self.stop_bell_btn)

        system_layout.addLayout(btn_row)

        form.addWidget(system_box)

        # =========================
        # SAVE BUTTON
        # =========================

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
        self.stop_bell_btn.clicked.connect(self.stop_bell)
        self.theme_toggle.clicked.connect(self.toggle_theme)

        saved = self.app.config.get("theme", "dark")
        self.theme.current_theme = saved
        self.theme_label.setText(f"Current Theme: {saved}")

        self.backup_btn.clicked.connect(self.backup_database)
        self.restore_btn.clicked.connect(self.restore_database)
        self.check_update_btn.clicked.connect(self.check_update)

    # =========================
    # ACTIONS
    # =========================
    def toggle_theme(self):
        new_theme = self.app.theme.toggle()
        print("THEME:", new_theme)

        self.app.config.set("theme", new_theme)

        self.theme_label.setText(f"Current Theme: {new_theme}")
        
    def test_audio(self):
        self.app.test_audio()

    def manual_bell(self):
        file_path = self.manual_audio.get_value()

        if file_path:
            self.app.test_audio(file_path)
        else:
            self.app.test_audio()
            
    def stop_bell(self):
        self.app.audio.stop()

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

    # =========================
    # BACKUP DATABASE
    # =========================
    def backup_database(self):
        paths = get_paths()
        db_path = paths.db_path()

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Database",
            "school-bell-backup.db",
            "Database (*.db)"
        )

        if not file_name:
            return

        try:
            import shutil
            shutil.copy2(db_path, file_name)

            QMessageBox.information(
                self,
                "Backup",
                "Backup database berhasil"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Error",
                str(e)
            )

    # =========================
    # RESTORE DATABASE
    # =========================
    def restore_database(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Database",
            "",
            "Database (*.db)"
        )

        if not file_name:
            return

        confirm = QMessageBox.question(
            self,
            "Restore",
            "Restore database akan menimpa data sekarang.\nLanjutkan?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            import shutil

            paths = get_paths()
            db_path = paths.db_path()

            shutil.copy2(file_name, db_path)

            QMessageBox.information(
                self,
                "Restore",
                "Restore berhasil.\nRestart aplikasi."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Error",
                str(e)
            )

    # =========================
    # CHECK UPDATE
    # =========================
    def check_update(self):
        try:
            data = self.app.update_service.check_latest()

            latest = data["version"]
            current = APP_VERSION

            if latest != current:
                reply = QMessageBox.question(
                    self,
                    "Update Available",
                    f"Version {latest} tersedia.\nBuka halaman download?"
                )

                if reply == QMessageBox.StandardButton.Yes:
                    import webbrowser
                    webbrowser.open(data["url"])

            else:
                QMessageBox.information(
                    self,
                    "Update",
                    "Aplikasi sudah versi terbaru"
                )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Update Error",
                str(e)
            )