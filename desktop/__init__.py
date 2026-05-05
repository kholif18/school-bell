# desktop/__init__.py
from desktop.main_window import MainWindow

# desktop/widgets/__init__.py
from desktop.widgets.superbar import SuperBar
from desktop.widgets.audio_picker import AudioPicker

# desktop/tabs/__init__.py
from desktop.tabs.history_tab import HistoryTab, HistoryLoader
from desktop.tabs.settings_tab import SettingsTab

# desktop/dialogs/__init__.py
from desktop.dialogs.schedule_dialog import ScheduleDialog

# desktop/models/__init__.py
from desktop.models.schedule_table_model import ScheduleTableModel

# desktop/bridge/__init__.py
from desktop.bridge.ui_bridge import UiBridge

# desktop/controllers/__init__.py
from desktop.controllers.main_controller import MainController