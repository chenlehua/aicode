"""Configuration management for DB Query backend."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")

    # Database Configuration
    db_path: Path = Path.home() / ".db_query" / "db_query.db"

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure database directory exists
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
