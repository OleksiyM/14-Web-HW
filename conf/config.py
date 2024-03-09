"""
App configuration
"""
from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    SECRET_KEY_JWT: str = "secret_key_jwt"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "contactapp@example.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "ContactsApp"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None
    CLD_NAME: str = "contactapp"
    CLD_API_KEY: int = 123
    CLD_API_SECRET: str = "secret"
    LIMIT_TIMES: int = 5
    LIMIT_SECONDS: int = 10
    CACHE_TTL_SEC: int = 600

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, val: Any):
        if val not in ["HS256", "HS384", "HS512"]:
            raise ValueError("Algorithm must be HS256, HS384 or HS512")
        return val

    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
