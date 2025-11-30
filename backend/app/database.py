"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# MySQL connection arguments
mysql_connect_args = {
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "autocommit": False,
}

# Create database engine
# Use get_database_url() method to construct the URL
database_url = settings.get_database_url()

engine = create_engine(
    database_url,
    connect_args=mysql_connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

