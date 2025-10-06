"""
Application configuration loaded from .env or GitHub secrets
"""

from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Basic
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    db_name: str
    db_host: str
    db_username: str
    db_password: str
    PORT: int

    # SSO
    GOOGLE_CLIENT_ID: str
    SSO_REDIRECT_BACKEND_PATH: AnyHttpUrl
    JWKS_URL: AnyHttpUrl
    JWKS_TTL: int
    SSO_DEFAULT_PASSWORD: str

    # db schema
    schema_name: str

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) ->  List[str]:
        """Handle CORS origins passed as string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return [str(i).strip() for i in v]
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",          # Load from .env
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Instantiate global settings
settings = Settings()
