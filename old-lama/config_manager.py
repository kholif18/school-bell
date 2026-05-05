# core/config_manager.py
import json
import os
import threading

from typing import Any, Optional
from core.paths import CONFIG_PATH

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or CONFIG_PATH
        self.config = self._load_defaults()
        self._load()
    
    def _load_defaults(self) -> dict:
        """Default configuration"""
        return {
            "app_name": "School Bell Automation",
            "version": "1.0.0",
            "audio": {
                "volume": 80,
                "default_bell": "assets/audio/default_bell.wav"
            },
            "scheduler": {
                "timezone": "Asia/Jakarta",
                "check_interval": 60
            },
            "web": {
                "enabled": True,
                "port": 5000,
                "host": "0.0.0.0"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/school_bell.log"
            }
        }
    
    def _load(self):
        """Load config from file"""
        if os.path.exists(self.config_path) and os.path.isfile(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    saved_config = json.load(f)
                    self._merge_config(saved_config)
                print(f"✓ Config loaded from {self.config_path}")
            except Exception as e:
                print(f"⚠ Failed to load config: {e}")
        else:
            self.save()
            print(f"✓ Default config created at {self.config_path}")
    
    def _merge_config(self, new_config: dict):
        """Deep merge configuration"""
        def merge(base, updates):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge(base[key], value)
                else:
                    base[key] = value
        merge(self.config, new_config)
    
    def save(self):
        """Save config to file"""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠ Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot notation (e.g., 'audio.volume')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set config value by dot notation"""
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        return self.save()

# Singleton
_config_manager = None
_config_lock = threading.Lock()

def get_config() -> ConfigManager:
    global _config_manager
    with _config_lock:
        if _config_manager is None:
            _config_manager = ConfigManager()
    return _config_manager