"""
Database configuration for Krishi Mitra
Uses SQLite for development, easily swappable to PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use SQLite for dev; set DATABASE_URL env var for PostgreSQL in prod
# PostgreSQL example: postgresql://user:password@localhost/krishi_mitra
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./krishi_mitra.db")

# Handle SQLite thread check for development
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
