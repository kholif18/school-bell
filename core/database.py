# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base, scoped_session
from core.path_helper import DB_PATH
import os
import threading

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._engine = None
        self._session_factory = None
        self._initialize()

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
                _db_manager_instance.create_tables()
    return _db_manager_instance