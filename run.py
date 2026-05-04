# run.py
import sys
from PyQt6.QtWidgets import QApplication
from core.app_core import get_app
from desktop.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    core_app = get_app()
    core_app.initialize()
    core_app.start()
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()