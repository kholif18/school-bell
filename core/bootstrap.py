# core/bootstrap.py
import logging

from core.paths import get_paths
from core.config import get_config
from core.database import DatabaseManager
from core.repositories import get_repository
from core.runtime.events import get_event_bus
from core.runtime.state import get_state_manager
from core.services.audio import get_audio_service
from core.services.scheduler import get_scheduler_service
from core.ipc import get_ipc

logger = logging.getLogger(__name__)


class AppBootstrap:
    """
    Single entry point initializer

    Rules:
    - deterministic order
    - no business logic
    - only wiring dependencies
    """

    def __init__(self):
        self.paths = None
        self.config = None
        self.db = None
        self.repo = None
        self.events = None
        self.state = None
        self.audio = None
        self.scheduler = None
        self.ipc = None

    # =========================
    # BOOT PROCESS
    # =========================

    def init(self):
        self._init_paths()
        self._init_config()
        self._init_database()
        self._init_runtime()
        self._init_services()
        self._init_ipc()
        self._wire_system()

        logger.info("🚀 Application bootstrap completed")

        return self

    # =========================
    # STEP 1 - PATHS
    # =========================

    def _init_paths(self):
        self.paths = get_paths()
        self.paths.ensure_dirs()

        logger.info("Paths initialized")

    # =========================
    # STEP 2 - CONFIG
    # =========================

    def _init_config(self):
        self.config = get_config()
        logger.info("Config loaded")

    # =========================
    # STEP 3 - DATABASE
    # =========================

    def _init_database(self):
        self.db = DatabaseManager()
        self.db.init()
        self.db.create_tables()

        logger.info("Database ready")

    # =========================
    # STEP 4 - RUNTIME
    # =========================

    def _init_runtime(self):
        self.repo = get_repository()
        self.events = get_event_bus()
        self.state = get_state_manager()

        logger.info("Runtime layer ready")

    # =========================
    # STEP 5 - SERVICES
    # =========================

    def _init_services(self):
        self.audio = get_audio_service()
        self.scheduler = get_scheduler_service()

        logger.info("Services ready")

    # =========================
    # STEP 6 - IPC (OPTIONAL)
    # =========================

    def _init_ipc(self):
        try:
            self.ipc = get_ipc()
            logger.info("IPC ready")
        except Exception:
            self.ipc = None
            logger.warning("IPC disabled")

    # =========================
    # STEP 7 - WIRING (EVENTS)
    # =========================

    def _wire_system(self):
        """
        Connect runtime systems safely
        (this replaces hidden dependencies)
        """

        # Scheduler → State
        self.events.on("JOBS_UPDATED", self._on_jobs_updated)
        self.events.on("SYSTEM_STARTED", self._on_started)
        self.events.on("SYSTEM_STOPPED", self._on_stopped)

        logger.info("Event wiring completed")

    # =========================
    # EVENT HANDLERS
    # =========================

    def _on_jobs_updated(self, count):
        self.state.set_jobs(count)

    def _on_started(self, _):
        self.state.set_running(True)

    def _on_stopped(self, _):
        self.state.set_running(False)


# =========================
# SINGLETON BOOTSTRAP
# =========================

_bootstrap = None


def get_bootstrap():
    global _bootstrap
    if _bootstrap is None:
        _bootstrap = AppBootstrap().init()
    return _bootstrap