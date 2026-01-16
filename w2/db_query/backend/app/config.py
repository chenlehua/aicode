"""Configuration management for DB Query backend."""

import json
import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")

    # Database Configuration
    db_path: Path = Path(os.getenv("DB_PATH", str(Path.home() / ".db_query" / "db_query.db")))

    # API Configuration
    api_v1_prefix: str = os.getenv("API_V1_PREFIX", "/api/v1")
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from environment variable."""
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            try:
                parsed: list[str] = json.loads(cors_env)
                if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
                    return parsed
                return ["*"]
            except (json.JSONDecodeError, TypeError):
                return ["*"]
        return ["*"]

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure database directory exists
settings.db_path.parent.mkdir(parents=True, exist_ok=True)
