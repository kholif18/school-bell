# bootstrap/service_runner.py
import time
import signal
import sys
from core.app_core import get_app
from bootstrap.process_lock import ProcessLock

class ServiceRunner:
    def __init__(self):
        self.app = None
        self.running = True
        self.lock = ProcessLock()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n🛑 Shutdown signal received...")
        self.running = False
        if self.app:
            try:
                self.app.shutdown_all()
            except:
                pass
        self.lock.release()
        sys.exit(0)

    def run(self):
        # Try to acquire lock (only one master)
        if not self.lock.acquire():
            print("⚠ Master already running elsewhere. Use --tray or default mode for client.")
            sys.exit(1)
        
        print("=" * 50)
        print("🔧 Starting MASTER service...")
        print("=" * 50)
        
        self.app = get_app()
        self.app.initialize(is_master=True)
        self.app.start()  # Start scheduler
        self.app.start_web(port=5000)

        print("=" * 50)
        print("✅ MASTER service active")
        print("🌐 Web UI: http://localhost:5000")
        print("=" * 50)
        print("Press Ctrl+C to stop")

        while self.running:
            time.sleep(1)

def run_service():
    ServiceRunner().run()