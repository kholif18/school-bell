# core/config.py
import json
import threading
from core.paths import get_paths


class Config:
    """
    Single source of truth configuration
    - JSON based
    - thread-safe
    - no business logic
    """

    def __init__(self):
        self.paths = get_paths()
        self.file = self.paths.config_file
        self._lock = threading.RLock()

        self.data = self._default_config()
        self._load()

    # =========================
    # DEFAULT
    # =========================

    def _default_config(self):
        return {
            "app_name": "School Bell",
            "timezone": "Asia/Jakarta",
            "volume": 80,
            "scheduler": {
                "misfire_grace_time": 30,
                "max_instances": 1
            }
        }

    # =========================
    # LOAD / SAVE
    # =========================

    def _load(self):
        try:
            if self.file.exists():
                with open(self.file, "r") as f:
                    self.data.update(json.load(f))
        except Exception:
            pass

    def save(self):
        with self._lock:
            with open(self.file, "w") as f:
                json.dump(self.data, f, indent=2)

    # =========================
    # GET / SET
    # =========================

    def get(self, key: str, default=None):
        keys = key.split(".")
        value = self.data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    def set(self, key: str, value):
        with self._lock:
            keys = key.split(".")
            target = self.data

            for k in keys[:-1]:
                target = target.setdefault(k, {})

            target[keys[-1]] = value
            self.save()


# singleton
_config = None
_lock = threading.Lock()


def get_config():
    global _config

    with _lock:
        if _config is None:
            _config = Config()

    return _config