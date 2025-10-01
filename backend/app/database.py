# db.py
import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlmodel import Session

load_dotenv()

def get_engine(**db_config):
    """
    Get SQLAlchemy engine for PostgreSQL (Aiven SSL required)
    """
    print('b_config["username"]',db_config["username"], db_config["password"], db_config["host"])
    
    connection_url = sqlalchemy.engine.URL.create(
        "postgresql+psycopg2",
        username=db_config["username"],
        password=db_config["password"],
        host=db_config["host"],
        port=db_config.get("port"),
        database=db_config["database"],
        # query={
        #     "sslmode": "require"  # SSL is mandatory for Aiven
        #     # If you have CA cert: "sslrootcert": db_config.get("sslrootcert")
        # },
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

# Load environment variables
DB_CONFIG = {
    "username": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", 20217),
    "database": os.getenv("DB_NAME"),
    # "sslrootcert": os.getenv("DB_CA_CERT")  # optional if using verify-full
}

# Create engine
engine = get_engine(**DB_CONFIG)


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
