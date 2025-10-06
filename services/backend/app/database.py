# db.py
from sqlmodel import Session
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import create_engine
from app.core.config import settings  # import the Settings object

def get_engine():
    """
    Get SQLAlchemy engine for PostgreSQL (Aiven SSL required)
    """
    print("user name", settings.db_username)  # log the username

    connection_url = f"postgresql+psycopg2://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.PORT}/{settings.db_name}"

    engine = create_engine(
        connection_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=600,
        pool_timeout=60,
    )
    return engine

# Create engine
engine = get_engine()

@as_declarative()
class Base:
    """Base class for SQLModel/SQLAlchemy models"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

def get_session():
    """
    Session generator for FastAPI dependency injection
    Usage:
        with get_session() as session:
            ...
    """
    with Session(engine) as session:
        yield session
