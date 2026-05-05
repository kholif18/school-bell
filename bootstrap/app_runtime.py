# bootstrap/app_runtime.py
import sys
import logging
from core.app_core import get_app
from bootstrap.process_lock import ProcessLock

_runtime = None
_engine_started = False
_lock = ProcessLock()

logger = logging.getLogger(__name__)

def boot_runtime():
    """Boot runtime - only one instance will start the engine"""
    global _runtime, _engine_started

    if _runtime is not None:
        return _runtime

    app = get_app()

    if not _engine_started:
        acquired = _lock.acquire()

        if acquired:
            print("=" * 50)
            print("🔧 Starting core engine (first instance)...")
            print("=" * 50)
            app.initialize()
            app.start()
            app.start_web(port=5000)
            _engine_started = True
            print("✓ Core engine started successfully")
        else:
            print("=" * 50)
            print("🔄 Core engine already running (attaching to existing)...")
            print("=" * 50)
            # Attach to existing engine (no need to re-init)
            _engine_started = True
            print("✓ Attached to running engine")

    _runtime = app
    return _runtime

def is_engine_running():
    """Check if engine is already running"""
    return _engine_started or _lock.acquire() is False