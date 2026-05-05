# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

from core.paths import get_paths

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        paths = get_paths()
        self.db_path = paths.db_path()

        self.engine = None
        self.SessionLocal = None

    def init(self):
        paths = get_paths()
        self.db_path = paths.db_path()

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
            pool_pre_ping=True,
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

        logger.info("Database initialized")

    def get_session(self):
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        logger.info("Tables created")

    def close(self):
        if self.engine:
            self.engine.dispose()

_db_manager = None

def get_db_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.init()
    return _db_manager