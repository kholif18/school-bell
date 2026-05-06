# core/runtime/events.py

import threading
import logging
from collections import defaultdict
from typing import Callable, Any, Dict, List
from PyQt6.QtCore import QObject, pyqtSignal, Qt


class EventBus(QObject):
    """Thread-safe event bus dengan auto-switch ke main thread"""
    
    _signal = pyqtSignal(str, object)
    
    def __init__(self):
        super().__init__()
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()
        self._signal.connect(self._dispatch, Qt.ConnectionType.QueuedConnection)

    def on(self, event: str, callback: Callable[[Any], None]):
        with self._lock:
            if callback not in self._listeners[event]:
                self._listeners[event].append(callback)

    def once(self, event: str, callback: Callable[[Any], None]):
        def wrapper(data):
            self.off(event, wrapper)
            callback(data)
        self.on(event, wrapper)

    def emit(self, event: str, data: Any = None):
        """AMAN dipanggil dari thread manapun"""
        self._signal.emit(event, data)

    def _dispatch(self, event: str, data: Any):
        """Dipanggil di MAIN THREAD"""
        with self._lock:
            listeners = list(self._listeners[event])
        
        for cb in listeners:
            try:
                cb(data)
            except Exception as e:
                logging.getLogger(__name__).error(f"Event '{event}' error: {e}")

    def off(self, event: str, callback: Callable = None):
        with self._lock:
            if callback:
                if callback in self._listeners[event]:
                    self._listeners[event].remove(callback)
            else:
                self._listeners[event].clear()


# =========================
# SINGLETON
# =========================

_event_bus = None
_lock = threading.Lock()


def get_event_bus():
    global _event_bus
    with _lock:
        if _event_bus is None:
            _event_bus = EventBus()
        return _event_bus