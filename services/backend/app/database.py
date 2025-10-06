import sqlalchemy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlmodel import Session
from app.core.config import settings  # import our fixed Settings

def get_engine():
    """Get SQLAlchemy engine"""
    print("user name", settings.db_username)  # sanity check

    connection_url = sqlalchemy.engine.URL.create(
        "postgresql+psycopg2",
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.PORT,
        database=settings.db_name,
    )

    engine = sqlalchemy.create_engine(
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
    """Session generator for FastAPI dependency injection"""
    with Session(engine) as session:
        yield session
