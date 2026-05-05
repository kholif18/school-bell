# desktop/widgets/superbar.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from datetime import datetime

class SuperBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("superbar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        # ===== LEFT: Profile & Status =====
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(2)
        
        self.profile_label = QLabel("📋 Profile: --")
        self.profile_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        left_layout.addWidget(self.profile_label)
        
        self.status_indicator = QLabel("🟢 RUNNING")
        self.status_indicator.setObjectName("running_indicator")
        left_layout.addWidget(self.status_indicator)
        
        layout.addWidget(left_widget, 1)
        
        # ===== CENTER: Clock =====
        clock_widget = QWidget()
        clock_layout = QVBoxLayout(clock_widget)
        clock_layout.setSpacing(2)
        clock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.clock_label = QLabel("--:--:--")
        self.clock_label.setObjectName("clock_display")
        clock_layout.addWidget(self.clock_label)
        
        self.date_label = QLabel("--, -- -- ----")
        self.date_label.setObjectName("date_display")
        clock_layout.addWidget(self.date_label)
        
        layout.addWidget(clock_widget, 2)
        
        # ===== RIGHT: Next Bell =====
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_layout.setSpacing(2)
        
        next_title = QLabel("🔔 NEXT BELL")
        next_title.setStyleSheet("font-size: 10px; color: #8B949E;")
        right_layout.addWidget(next_title)
        
        self.next_time_label = QLabel("--:--:--")
        self.next_time_label.setObjectName("next_bell_time")
        right_layout.addWidget(self.next_time_label)
        
        self.next_name_label = QLabel("No schedule")
        self.next_name_label.setObjectName("next_bell_name")
        right_layout.addWidget(self.next_name_label)
        
        layout.addWidget(right_widget, 1)
    
    def update_time(self):
        now = datetime.now()
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%a, %d %b %Y"))
    
    def update_next_bell(self, next_time, next_name):
        if next_time:
            if hasattr(next_time, 'strftime'):
                # Hitung countdown
                now = datetime.now()
                if hasattr(next_time, 'tzinfo') and next_time.tzinfo:
                    next_time = next_time.replace(tzinfo=None)
                
                if next_time > now:
                    diff = next_time - now
                    total_seconds = int(diff.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    
                    if hours > 0:
                        countdown_text = f"{hours}h {minutes}m"
                    elif minutes > 0:
                        countdown_text = f"{minutes}m {seconds}s"
                    else:
                        countdown_text = f"{seconds}s"
                        self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #39FF14;")
                else:
                    countdown_text = "🔔 NOW!"
                    self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFA500;")
            else:
                countdown_text = str(next_time)
            
            self.next_time_label.setText(countdown_text)
            self.next_name_label.setText(next_name[:30] if next_name else "Bell")
        else:
            self.next_time_label.setText("--:--:--")
            self.next_time_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFA500;")
            self.next_name_label.setText("No upcoming bell")
    
    def update_profile(self, profile_name):
        self.profile_label.setText(f"📋 Profile: {profile_name}")
    
    def set_running(self, is_running):
        if is_running:
            self.status_indicator.setText("🟢 RUNNING")
            self.status_indicator.setObjectName("running_indicator")
        else:
            self.status_indicator.setText("🔴 STOPPED")
            self.status_indicator.setObjectName("stopped_indicator")
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)