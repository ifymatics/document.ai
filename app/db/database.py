from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Create base class for models
Base = declarative_base()

def get_engine(database_url: str = None, echo: bool = False):
    """Create database engine with optional overrides for migrations"""
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        from app.core.config import settings
        url = settings.DATABASE_URL
    return create_engine(
        url,
        pool_pre_ping=True,
        echo=echo
    )

# Default engine (used by application)
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()