# main.py (entry point baru)
import sys
import threading
from PyQt6.QtWidgets import QApplication
from core.app_core import get_app
from desktop.main_window import MainWindow

def main():
    # Start core app
    app = get_app()
    app.initialize()
    app.start()
    
    # Start web server
    app.start_web(port=5000)
    
    # Start desktop GUI
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(qt_app.exec())

if __name__ == "__main__":
    main()