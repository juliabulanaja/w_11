from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:654321@localhost:5432/contacts_db"
SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    """Initialize new session.

    :yield: New session
    """    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
