# apps/desktop/tray_icon.py
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject


class TrayIcon(QSystemTrayIcon):

    def __init__(self, qt_app, window):
        super().__init__(window)

        self.qt_app = qt_app
        self.window = window

        self.setToolTip("School Bell Automation")

        menu = QMenu()

        show_action = QAction("Show")
        quit_action = QAction("Quit")

        show_action.triggered.connect(self.window.showNormal)
        quit_action.triggered.connect(self.quit_app)

        menu.addAction(show_action)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.show()

    def quit_app(self):
        self.window.close()
        self.qt_app.quit()