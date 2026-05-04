# core/app_core.py (FIXED)
import logging
import sys
import threading
from typing import Optional

from core.database import get_db_manager
from core.schedule_manager import get_schedule_manager
from core.audio_manager import get_audio_manager
from core.scheduler_engine import SchedulerEngine
from core.config_manager import get_config
from core.event_manager import get_event_manager
from core.path_helper import DB_PATH, LOG_PATH, CONFIG_PATH

# Setup logging (only once)
_logging_setup = False

def setup_logging():
    global _logging_setup
    if _logging_setup:
        return
    
    config = get_config()
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file', LOG_PATH)
    
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
    _logging_setup = True

class SchoolBellApp:
    """Main application class - orchestrates all components"""
    
    def __init__(self):
        self.config = get_config()
        self.db_manager = get_db_manager()
        self.schedule_manager = get_schedule_manager()
        self.audio_manager = get_audio_manager()  # SINGLETON
        self.scheduler = SchedulerEngine()
        self.event_manager = get_event_manager()
        self._initialized = False
        self.web_thread = None
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            setup_logging()
            logger = logging.getLogger(__name__)
            logger.info(f"Initializing {self.config.get('app_name')} v{self.config.get('version')}")
            
            # Set volume from config
            volume = self.config.get('audio.volume', 80)
            self.audio_manager.set_volume(volume)
            
            self._initialized = True
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize: {e}")
            return False
    
    def start(self):
        """Start the application"""
        if not self._initialized:
            if not self.initialize():
                return False
        
        logger = logging.getLogger(__name__)
        logger.info("Starting School Bell Application...")
        
        # Start scheduler
        self.scheduler.start()
        
        # Emit event AFTER successful start (FIX: no dead code)
        self.event_manager.emit('system_started')
        
        logger.info("Application running successfully")
        return True
    
    def stop(self):
        """Stop the application"""
        logger = logging.getLogger(__name__)
        logger.info("Stopping School Bell Application...")
        
        # Stop scheduler
        self.scheduler.stop()
        
        # Emit event
        self.event_manager.emit('system_stopped')
        
        # Close database
        self.db_manager.close()
        
        logger.info("Application stopped")

    def shutdown_all(self):
        """Complete shutdown of all resources"""
        logger = logging.getLogger(__name__)
        logger.info("Shutting down all resources...")
        
        # Stop scheduler
        try:
            self.scheduler.stop()
        except Exception as e:
            logger.warning(f"Scheduler stop error: {e}")
        
        # Stop audio
        try:
            self.audio_manager.stop()
            import pygame
            pygame.mixer.quit()
        except Exception as e:
            logger.warning(f"Audio shutdown error: {e}")
        
        # Close database
        try:
            self.db_manager.close()
        except Exception as e:
            logger.warning(f"Database close error: {e}")
        
        logger.info("Shutdown complete")
    
    def get_status(self) -> dict:
        """Get overall application status"""
        scheduler_status = self.scheduler.get_status()
        
        return {
            'initialized': self._initialized,
            'scheduler': scheduler_status,
            'config': {
                'app_name': self.config.get('app_name'),
                'version': self.config.get('version'),
                'volume': self.config.get('audio.volume')
            }
        }
    
    def reload_schedules(self):
        """Reload schedules (after database changes)"""
        self.scheduler.reload()
    
    def start_web(self, port=5000):
        """Start web server in separate thread"""
        from web.server import start_web_server
        self.web_thread = threading.Thread(target=start_web_server, args=(self, port), daemon=True)
        self.web_thread.start()
        logger = logging.getLogger(__name__)
        logger.info(f"Web server started on http://localhost:{port}")

# Singleton
_app_instance = None
_app_lock = threading.Lock()

def get_app() -> SchoolBellApp:
    """Get singleton app instance"""
    global _app_instance
    with _app_lock:
        if _app_instance is None:
            _app_instance = SchoolBellApp()
    return _app_instance