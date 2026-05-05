# apps/desktop/bridge/ui_bridge.py
from core.client import AppClient


class UiBridge:
    """
    Bridge antara UI (PyQt) dan core event system
    Clean event wrapper (no direct access)
    """

    def __init__(self):
        self.client = AppClient()

    def on(self, event: str, callback):
        """Subscribe event"""
        self.client.events.on(event, callback)

    def emit(self, event: str, data=None):
        """Emit event"""
        self.client.events.emit(event, data)