# bootstrap/process_lock.py
import os
import fcntl
from pathlib import Path

LOCK_FILE = Path("/tmp/schoolbell_engine.lock")

class ProcessLock:
    """Singleton lock to prevent multiple engine instances"""
    
    def __init__(self):
        self.fp = None

    def acquire(self):
        """Acquire lock - returns True if acquired, False if already locked"""
        try:
            LOCK_FILE.touch(exist_ok=True)
            self.fp = open(LOCK_FILE, "r+")
            
            fcntl.flock(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.fp.seek(0)
            self.fp.write(str(os.getpid()))
            self.fp.truncate()
            self.fp.flush()
            return True
        except (BlockingIOError, OSError):
            # Read the PID of the existing process
            try:
                with open(LOCK_FILE, 'r') as f:
                    pid = f.read().strip()
                print(f"Engine already running with PID: {pid}")
            except:
                pass
            return False

    def release(self):
        """Release lock"""
        if self.fp:
            try:
                fcntl.flock(self.fp, fcntl.LOCK_UN)
                self.fp.close()
                if LOCK_FILE.exists():
                    LOCK_FILE.unlink()
            except:
                pass
            self.fp = None

# Export instance for external use
_lock = ProcessLock()  # <-- ADD THIS

def get_lock():
    return _lock