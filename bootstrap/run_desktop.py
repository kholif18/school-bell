import sys
from PyQt6.QtWidgets import QApplication

from core.app import CoreApp
from apps.desktop.main_window import MainWindow


def main():
    qt = QApplication(sys.argv)

    core = CoreApp()
    core.initialize()

    window = MainWindow(core)
    window.show()

    sys.exit(qt.exec())


if __name__ == "__main__":
    main()