# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_path: str = "db/school_bell.db"):
        self.db_path = db_path
        self._engine = None
        self._session_factory = None
        self._initialize()

    def _initialize(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            connect_args={"check_same_thread": False}  # Allow multi-thread access
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            expire_on_commit=False  # CRITICAL: Prevents DetachedInstanceError
        )

    def create_tables(self):
        Base.metadata.create_all(self._engine)

    def get_session(self) -> Session:
        return self._session_factory()

    def close(self):
        if self._engine:
            self._engine.dispose()

# Singleton instance
_db_manager_instance = None

def get_db_manager() -> DatabaseManager:
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
        _db_manager_instance.create_tables()
    return _db_manager_instance