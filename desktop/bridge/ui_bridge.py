# desktop/bridge/ui_bridge.py
from PyQt6.QtCore import QObject, pyqtSignal

class UiBridge(QObject):
    """Bridge untuk marshalling events dari backend threads ke GUI thread"""
    systemStarted = pyqtSignal()
    systemStopped = pyqtSignal()
    schedulesReloaded = pyqtSignal()
    profilesUpdated = pyqtSignal()
    profileActivated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()