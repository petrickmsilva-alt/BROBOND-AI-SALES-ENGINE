"""Application settings loaded from the environment."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "BROBOND AI Sales Engine"
    app_env: Literal["local", "development", "staging", "production"] = "local"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    database_url: PostgresDsn = Field(
        default=PostgresDsn("postgresql+asyncpg://brobond:brobond@postgres:5432/brobond"),
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    redis_url: RedisDsn = Field(default=RedisDsn("redis://redis:6379/0"))
    redis_cache_ttl_seconds: int = 300

    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 60.0

    n8n_base_url: str = "http://n8n:5678"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 7

    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def sync_database_url(self) -> str:
        """Return the psycopg-free synchronous URL used by Alembic tooling."""
        return str(self.database_url)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
