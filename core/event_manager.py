# core/event_manager.py
from typing import Callable, Dict, List
import threading
import logging
logger = logging.getLogger(__name__)


class EventManager:
    """Simple event system for cross-component communication"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def on(self, event: str, callback: Callable):
        """Register callback for an event"""
        with self._lock:
            if event not in self._listeners:
                self._listeners[event] = []

            if callback not in self._listeners[event]:
                self._listeners[event].append(callback)
    
    def emit(self, event: str, data: any = None):
        """Emit an event to all registered callbacks"""
        with self._lock:
            callbacks = self._listeners.get(event, []).copy()
        
        for callback in callbacks:
            try:
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                logger.exception("Error in event callback")
    
    def off(self, event: str, callback: Callable = None):
        """Remove callback for an event"""
        with self._lock:
            if event in self._listeners:
                if callback:
                    self._listeners[event].remove(callback)
                else:
                    del self._listeners[event]

# Singleton
_event_manager = None
_event_lock = threading.Lock()

def get_event_manager() -> EventManager:
    global _event_manager
    with _event_lock:
        if _event_manager is None:
            _event_manager = EventManager()
    return _event_manager