# core/app_core.py
import logging
import sys
from typing import Optional

from core.database import get_db_manager
from core.schedule_manager import get_schedule_manager
from core.audio_manager import AudioManager
from core.scheduler_engine import SchedulerEngine
from core.config_manager import get_config

# Setup logging
def setup_logging():
    config = get_config()
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', 'logs/school_bell.log')
    
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

class SchoolBellApp:
    """Main application class - orchestrates all components"""
    
    def __init__(self):
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = AudioManager()
        self.scheduler = SchedulerEngine()
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            setup_logging()
            logger = logging.getLogger(__name__)
            logger.info(f"Initializing {self.config.get('app_name')} v{self.config.get('version')}")
            
            # Set volume from config
            volume = self.config.get('audio.volume', 80)
            self.audio_manager.set_volume(volume)
            
            # Ensure default bell exists
            default_bell = self.config.get('audio.default_bell')
            if default_bell and not self._check_audio_file(default_bell):
                logger.warning(f"Default bell not found: {default_bell}")
            
            self._initialized = True
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize: {e}")
            return False
    
    def _check_audio_file(self, path: str) -> bool:
        """Check if audio file exists"""
        import os
        return os.path.exists(path)
    
    def start(self):
        """Start the application"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        logger = logging.getLogger(__name__)
        logger.info("Starting School Bell Application...")
        
        # Start scheduler
        self.scheduler.start()
        
        logger.info("Application running successfully")
        return True
    
    def stop(self):
        """Stop the application"""
        logger = logging.getLogger(__name__)
        logger.info("Stopping School Bell Application...")
        
        # Stop scheduler
        self.scheduler.stop()
        
        # Close database
        self.db_manager.close()
        
        logger.info("Application stopped")
    
    def get_status(self) -> dict:
        """Get overall application status"""
        return {
            'initialized': self._initialized,
            'scheduler': self.scheduler.get_status(),
            'config': {
                'app_name': self.config.get('app_name'),
                'version': self.config.get('version'),
                'volume': self.config.get('audio.volume')
            }
        }
    
    def reload_schedules(self):
        """Reload schedules (after database changes)"""
        self.scheduler.reload()
    
    def add_schedule(self, name: str, hour: int, minute: int, days: list, audio_file: str = None):
        """Add new schedule (convenience method)"""
        from datetime import time
        bell_time = time(hour, minute)
        return self.schedule_manager.add_schedule(name, bell_time, days, audio_file)

# Singleton
_app_instance = None

def get_app() -> SchoolBellApp:
    """Get singleton app instance"""
    global _app_instance
    if _app_instance is None:
        _app_instance = SchoolBellApp()
    return _app_instance