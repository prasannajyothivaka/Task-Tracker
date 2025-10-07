"""
    configs defined in core
"""
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Base settings class"""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Task_Tracker")

    # Default CORS origins; can be overridden by env vars
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://task-tracker-htesg7gfdhcfaxba.canadacentral-01.azurewebsites.net",
    ]

    # Database and Azure environment values
    db_username: str = os.getenv("DB_USERNAME", "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "")
    db_name: str = os.getenv("DB_NAME", "")
    PORT: int = int(os.getenv("DB_PORT", 5432))
    schema_name: str = os.getenv("SCHEMA_NAME", "task_tracker")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Convert comma-separated CORS string to list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        """Config Class"""
        case_sensitive = True
        env_file = ".env"  # optional for local use
        extra = "allow"


settings = Settings()
