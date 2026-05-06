# apps/desktop/bridge/ui_bridge.py
from core.client import AppClient


class UiBridge:
    """
    Bridge antara UI (PyQt) dan core event system
    Clean event wrapper (no direct access)
    """

    def __init__(self, core_app):
        self.core = core_app

    def events(self):
        return self.core.events