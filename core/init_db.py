from core.database import engine
from core.models import Base

def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("DATABASE INITIALIZED SUCCESSFULLY")

if __name__ == "__main__":
    initialize_database()
