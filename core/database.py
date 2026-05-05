# core/database.py
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session, declarative_base, scoped_session
from core.path_helper import DB_PATH
import os
import threading
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._engine = None
        self._session_factory = None
        self._initialize()
        self._auto_migrate()  # <-- TAMBAHKAN INI

    def _initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            },
            pool_pre_ping=True
        )
        self._session_factory = scoped_session(sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        ))

    def _auto_migrate(self):
        """Auto-create scheduler_state table and default data"""
        try:
            # Import models here to avoid circular import
            from core.models import SchedulerState
            
            # Create all tables (including new ones)
            Base.metadata.create_all(self._engine)
            
            # Insert default scheduler state if not exists
            session = self.get_session()
            try:
                from core.models import SchedulerState
                state = session.query(SchedulerState).filter(SchedulerState.id == 1).first()
                if not state:
                    state = SchedulerState(id=1, is_running=False)
                    session.add(state)
                    session.commit()
                    logger.info("✓ Scheduler state table initialized")
            finally:
                session.close()
                
        except Exception as e:
            logger.warning(f"Auto-migration warning: {e}")

    def create_tables(self):
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        return self._session_factory()

    def remove_session(self):
        self._session_factory.remove()

    def close(self):
        if self._session_factory:
            self._session_factory.remove()
        if self._engine:
            self._engine.dispose()

_db_manager_instance = None
_db_lock = threading.Lock()

def get_db_manager() -> DatabaseManager:
    global _db_manager_instance
    if _db_manager_instance is None:
        with _db_lock:
            if _db_manager_instance is None:
                _db_manager_instance = DatabaseManager()
                # create_tables sudah dipanggil di _auto_migrate
    return _db_manager_instance