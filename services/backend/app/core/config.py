from typing import List, Union
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Basic
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database - map capital env vars
    db_name: str = Field(..., env="DB_NAME")
    db_host: str = Field(..., env="DB_HOST")
    db_username: str = Field(..., env="DB_USERNAME")
    db_password: str = Field(..., env="DB_PASSWORD")
    PORT: int = Field(..., env="DB_PORT")

    # SSO
    GOOGLE_CLIENT_ID: str
    SSO_REDIRECT_BACKEND_PATH: AnyHttpUrl
    JWKS_URL: AnyHttpUrl
    JWKS_TTL: int
    SSO_DEFAULT_PASSWORD: str

    # DB schema
    schema_name: str

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Handle CORS origins passed as string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return [str(i).strip() for i in v]
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Global settings instance
settings = Settings()

# Quick test
print("DB Username loaded from .env:", settings.db_username)
