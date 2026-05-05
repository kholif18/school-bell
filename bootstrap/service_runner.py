# bootstrap/service_runner.py
import time
import signal
import sys
from bootstrap.app_runtime import boot_runtime

class ServiceRunner:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("\n🛑 Shutdown signal received...")
        self.running = False
        
        # Try to release lock
        from bootstrap.process_lock import _lock
        _lock.release()
        
        sys.exit(0)

    def run(self):
        boot_runtime()

        print("=" * 50)
        print("✅ Background service active")
        print("🌐 Web UI: http://localhost:5000")
        print("=" * 50)
        print("Press Ctrl+C to stop")

        while self.running:
            time.sleep(1)

def run_service():
    ServiceRunner().run()