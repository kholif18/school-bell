# main.py
import sys
import threading
from PyQt6.QtWidgets import QApplication
from core.app_core import SchoolBellApp
from desktop.main_window import MainWindow
from web.server import start_web_server
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/school_bell.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    # Initialize the core application
    app_core = SchoolBellApp()
    
    # Start the scheduler
    app_core.start()
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=start_web_server, args=(app_core, 5000), daemon=True)
    web_thread.start()
    logger.info("Web server started on http://localhost:5000")
    
    # Start desktop GUI
    qt_app = QApplication(sys.argv)
    window = MainWindow(app_core)
    window.show()
    
    # Run the application
    try:
        sys.exit(qt_app.exec())
    finally:
        app_core.stop()

if __name__ == "__main__":
    main()