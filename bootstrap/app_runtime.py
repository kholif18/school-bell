# bootstrap/app_runtime.py
import sys
import logging
from core.app_core import get_app
from bootstrap.process_lock import ProcessLock

_runtime = None
_lock = ProcessLock()

logger = logging.getLogger(__name__)

def boot_runtime(is_master: bool = False):
    """
    Boot runtime - handles process locking and mode detection
    
    Args:
        is_master: True for headless (will start scheduler), False for clients
    """
    global _runtime

    if _runtime is not None:
        return _runtime

    app = get_app()

    if is_master:
        # MASTER MODE - acquire lock and start engine
        acquired = _lock.acquire()
        if acquired:
            print("=" * 50)
            print("🔧 Starting MASTER engine...")
            print("=" * 50)
            app.initialize(is_master=True)
            app.start()  # Start scheduler
            app.start_web(port=5000)
            print("✓ Master engine started successfully")
        else:
            print("ERROR: Another master is already running!")
            print("Use --tray or default mode for clients.")
            sys.exit(1)
    else:
        # CLIENT MODE - attach to existing engine
        print("=" * 50)
        print("🔄 Starting CLIENT (attaching to existing engine)...")
        print("=" * 50)
        app.initialize(is_master=False)
        app.start_web(port=5000)  # Web for monitoring only
        print("✓ Client attached to engine")

    _runtime = app
    return _runtime

def is_engine_running():
    """Check if engine is already running"""
    return _lock.acquire() is False