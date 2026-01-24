"""Configuration management for pg-mcp."""

import logging
import os
import re
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class LLMSettings(BaseSettings):
    """LLM API configuration settings."""

    model_config = SettingsConfigDict(env_prefix="LLM_")

    api_key: SecretStr = Field(description="LLM API key")
    base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="LLM API base URL",
    )
    model: str = Field(default="qwen-plus", description="LLM model name")
    temperature: float = Field(default=0.1, ge=0, le=2, description="Generation temperature")
    timeout: float = Field(default=30.0, gt=0, description="API request timeout in seconds")
    max_tokens: int = Field(default=2048, gt=0, description="Maximum tokens to generate")


class QuerySettings(BaseSettings):
    """Query execution configuration settings."""

    model_config = SettingsConfigDict(env_prefix="QUERY_")

    default_limit: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Default row limit for queries",
    )
    statement_timeout: int = Field(
        default=30000,
        ge=1000,
        description="SQL statement timeout in milliseconds",
    )
    enable_validation: bool = Field(
        default=True,
        description="Whether to enable LLM result validation",
    )


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(env_prefix="PG_MCP_")

    config_path: str | None = Field(
        default=None,
        description="Path to database configuration YAML file",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    llm: LLMSettings = Field(default_factory=LLMSettings)
    query: QuerySettings = Field(default_factory=QuerySettings)


class DatabaseConfig(BaseModel):
    """Database connection configuration."""

    name: str = Field(description="Database alias/identifier")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535, description="Database port")
    database: str = Field(description="Database name")
    user: str = Field(description="Database user")
    password: SecretStr = Field(description="Database password")
    min_pool_size: int = Field(default=2, ge=1, description="Minimum connection pool size")
    max_pool_size: int = Field(default=10, ge=1, description="Maximum connection pool size")
    ssl: bool = Field(default=False, description="Whether to use SSL connection")

    @computed_field
    @property
    def dsn(self) -> str:
        """Generate PostgreSQL DSN connection string."""
        password = self.password.get_secret_value()
        ssl_suffix = "?sslmode=require" if self.ssl else ""
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.database}{ssl_suffix}"


class ConfigLoader:
    """Loader for database configuration from YAML file."""

    # Pattern to match ${ENV_VAR} or ${ENV_VAR:default}
    ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?::([^}]*))?\}")

    @classmethod
    def load_databases(cls, path: str | Path) -> list[DatabaseConfig]:
        """Load database configurations from a YAML file.

        Args:
            path: Path to the YAML configuration file.

        Returns:
            List of DatabaseConfig instances.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            ValueError: If the configuration is invalid.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError("Configuration file is empty")

        databases_config = config.get("databases", [])
        if not databases_config:
            raise ValueError("No databases configured in configuration file")

        databases: list[DatabaseConfig] = []
        for db_config in databases_config:
            expanded = cls._expand_env_vars(db_config)
            databases.append(DatabaseConfig(**expanded))

        logger.info(f"Loaded {len(databases)} database configuration(s)")
        return databases

    @classmethod
    def _expand_env_vars(cls, config: dict) -> dict:
        """Expand environment variable references in configuration values.

        Supports ${VAR_NAME} and ${VAR_NAME:default} syntax.

        Args:
            config: Configuration dictionary.

        Returns:
            Configuration with environment variables expanded.
        """
        result: dict = {}
        for key, value in config.items():
            if isinstance(value, str):
                result[key] = cls._expand_string(value)
            elif isinstance(value, dict):
                result[key] = cls._expand_env_vars(value)
            elif isinstance(value, list):
                result[key] = [
                    cls._expand_string(v) if isinstance(v, str) else v for v in value
                ]
            else:
                result[key] = value
        return result

    @classmethod
    def _expand_string(cls, value: str) -> str:
        """Expand environment variables in a string value.

        Args:
            value: String value that may contain ${VAR} references.

        Returns:
            String with environment variables expanded.
        """

        def replace_match(match: re.Match) -> str:
            var_name = match.group(1)
            default_value = match.group(2)
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            if default_value is not None:
                return default_value
            raise ValueError(f"Environment variable {var_name} not set and no default provided")

        return cls.ENV_VAR_PATTERN.sub(replace_match, value)
