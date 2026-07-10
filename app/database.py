"""
Database configuration and setup.

This module handles the connection to SQLite (locally) or PostgreSQL (in production).
SQLAlchemy is an ORM (Object-Relational Mapping) that lets us define tables as Python classes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./project_dashboard.db")

# Create database engine
# - echo=True prints SQL queries (useful for debugging)
# - connect_args for SQLite thread safety
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# SessionLocal creates database sessions for queries
# Each request gets its own session (like a conversation with the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models - we inherit from this to define tables
Base = declarative_base()


def get_db():
    """
    Dependency function that provides a database session to endpoints.
    
    FastAPI automatically calls this and injects 'db' into endpoints that need it.
    Example: def login(db: Session = Depends(get_db))
    
    yields: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
