# main.py
from PyQt6.QtWidgets import QApplication
import sys

from core.bootstrap import get_app
from apps.desktop.main_window import MainWindow


def main():
    qt_app = QApplication(sys.argv)

    app_core = get_app()
    app_core.initialize()

    window = MainWindow(app_core)   # <-- INI WAJIB DIKIRIM
    window.show()

    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()