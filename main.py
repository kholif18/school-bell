# main.py
import sys
import logging
from threading import Thread
from PyQt6.QtWidgets import QApplication

from core.app import CoreApp
from apps.desktop.main_window import MainWindow
from apps.desktop.tray_icon import TrayIcon
from apps.web.app import create_web_app


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)

def run_web(core):
    app = create_web_app(core)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def main():
    backend = CoreApp()
    backend.initialize()

    # ================= WEB THREAD =================
    web_thread = Thread(target=run_web, args=(backend,), daemon=True)
    web_thread.start()

    # ================= DESKTOP =================
    qt = QApplication(sys.argv)

    window = MainWindow(backend)

    tray = TrayIcon(qt, window, backend)
    tray.show()

    window.show()

    sys.exit(qt.exec())


if __name__ == "__main__":
    main()