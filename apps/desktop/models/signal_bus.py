# apps/desktop/models/signal_bus.py
from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    jobs_updated = pyqtSignal(int)
    system_started = pyqtSignal()
    system_stopped = pyqtSignal()
    bell_triggered = pyqtSignal(dict)