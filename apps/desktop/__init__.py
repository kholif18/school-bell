# desktop/__init__.py
from apps.desktop.main_window import MainWindow

# desktop/widgets/__init__.py
from apps.desktop.widgets.superbar import SuperBar
from apps.desktop.widgets.audio_picker import AudioPicker

# desktop/tabs/__init__.py
from apps.desktop.tabs.history_tab import HistoryTab, HistoryLoader
from apps.desktop.tabs.settings_tab import SettingsTab

# desktop/dialogs/__init__.py
from apps.desktop.dialogs.schedule_dialog import ScheduleDialog

# desktop/models/__init__.py
from apps.desktop.models.schedule_table_model import ScheduleTableModel

# desktop/bridge/__init__.py
from apps.desktop.bridge.ui_bridge import UiBridge

# desktop/controllers/__init__.py
from apps.desktop.controllers.main_controller import MainController