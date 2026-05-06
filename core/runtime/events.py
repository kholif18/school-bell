# core/runtime/events.py

import threading
import logging
from collections import defaultdict
from typing import Callable, Any, Dict, List


class EventBus:
    """
    Lightweight in-memory event system

    Rules:
    - NO IO
    - NO DB
    - NO external broker
    - thread-safe
    - simple pub/sub only
    """

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()

    # =========================
    # SUBSCRIBE
    # =========================

    def on(self, event: str, callback: Callable[[Any], None]):
        with self._lock:
            if callback not in self._listeners[event]:
                self._listeners[event].append(callback)

    def once(self, event: str, callback: Callable[[Any], None]):
        """
        Auto remove after first trigger
        """
        def wrapper(data):
            self.off(event, wrapper)
            callback(data)

        self.on(event, wrapper)

    # =========================
    # EMIT
    # =========================

    def emit(self, event: str, data: Any = None):
        with self._lock:
            listeners = list(self._listeners[event])

        for cb in listeners:
            try:
                cb(data)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Event '{event}' error: {e}")

    # =========================
    # UNSUBSCRIBE
    # =========================

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