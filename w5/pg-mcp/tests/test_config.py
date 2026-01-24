"""Tests for pg-mcp configuration."""

import os
import pytest
import tempfile
from pathlib import Path

from pg_mcp.config import (
    ConfigLoader,
    DatabaseConfig,
    LLMSettings,
    QuerySettings,
    Settings,
)


class TestLLMSettings:
    """Tests for LLMSettings."""

    def test_default_values(self) -> None:
        """Test LLMSettings default values."""
        settings = LLMSettings(api_key="test-key")

        assert settings.model == "qwen-plus"
        assert settings.temperature == 0.1
        assert settings.timeout == 30.0
        assert settings.max_tokens == 2048
        assert "dashscope" in settings.base_url

    def test_api_key_secret(self) -> None:
        """Test that API key is stored as SecretStr."""
        settings = LLMSettings(api_key="my-secret-key")

        # Should not expose the secret in string representation
        assert "my-secret-key" not in str(settings)
        assert "my-secret-key" not in repr(settings)

        # But should be accessible via get_secret_value
        assert settings.api_key.get_secret_value() == "my-secret-key"


class TestQuerySettings:
    """Tests for QuerySettings."""

    def test_default_values(self) -> None:
        """Test QuerySettings default values."""
        settings = QuerySettings()

        assert settings.default_limit == 100
        assert settings.statement_timeout == 30000
        assert settings.enable_validation is True

    def test_validation_limit_bounds(self) -> None:
        """Test that default_limit has proper bounds."""
        with pytest.raises(ValueError):
            QuerySettings(default_limit=0)

        with pytest.raises(ValueError):
            QuerySettings(default_limit=20000)


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_dsn_generation(self) -> None:
        """Test DSN connection string generation."""
        config = DatabaseConfig(
            name="test",
            host="localhost",
            port=5432,
            database="mydb",
            user="myuser",
            password="mypass",
        )

        dsn = config.dsn

        assert "postgresql://" in dsn
        assert "myuser" in dsn
        assert "mypass" in dsn
        assert "localhost" in dsn
        assert "5432" in dsn
        assert "mydb" in dsn

    def test_dsn_with_ssl(self) -> None:
        """Test DSN includes SSL parameter when enabled."""
        config = DatabaseConfig(
            name="test",
            host="localhost",
            port=5432,
            database="mydb",
            user="myuser",
            password="mypass",
            ssl=True,
        )

        assert "sslmode=require" in config.dsn

    def test_password_secret(self) -> None:
        """Test that password is stored as SecretStr."""
        config = DatabaseConfig(
            name="test",
            host="localhost",
            port=5432,
            database="mydb",
            user="myuser",
            password="secret123",
        )

        # Password field itself should be masked
        assert config.password.get_secret_value() == "secret123"
        # Note: DSN computed field will contain the password for connection purposes


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_load_valid_config(self) -> None:
        """Test loading a valid configuration file."""
        config_content = """
databases:
  - name: test_db
    host: localhost
    port: 5432
    database: testdb
    user: testuser
    password: testpass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(config_content)
            f.flush()

            try:
                databases = ConfigLoader.load_databases(f.name)

                assert len(databases) == 1
                assert databases[0].name == "test_db"
                assert databases[0].host == "localhost"
                assert databases[0].database == "testdb"
            finally:
                os.unlink(f.name)

    def test_load_config_with_env_var(self) -> None:
        """Test loading configuration with environment variable substitution."""
        os.environ["TEST_PG_PASSWORD"] = "env_password"

        config_content = """
databases:
  - name: test_db
    host: localhost
    port: 5432
    database: testdb
    user: testuser
    password: "${TEST_PG_PASSWORD}"
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(config_content)
            f.flush()

            try:
                databases = ConfigLoader.load_databases(f.name)

                assert databases[0].password.get_secret_value() == "env_password"
            finally:
                os.unlink(f.name)
                del os.environ["TEST_PG_PASSWORD"]

    def test_load_config_with_default_value(self) -> None:
        """Test loading configuration with default value in env var."""
        config_content = """
databases:
  - name: test_db
    host: "${NONEXISTENT_HOST:default_host}"
    port: 5432
    database: testdb
    user: testuser
    password: testpass
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(config_content)
            f.flush()

            try:
                databases = ConfigLoader.load_databases(f.name)

                assert databases[0].host == "default_host"
            finally:
                os.unlink(f.name)

    def test_load_missing_file(self) -> None:
        """Test loading from a non-existent file."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load_databases("/nonexistent/path.yaml")

    def test_load_empty_config(self) -> None:
        """Test loading an empty configuration file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("")
            f.flush()

            try:
                with pytest.raises(ValueError, match="empty"):
                    ConfigLoader.load_databases(f.name)
            finally:
                os.unlink(f.name)

    def test_load_no_databases(self) -> None:
        """Test loading configuration without databases section."""
        config_content = """
some_other_key: value
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(config_content)
            f.flush()

            try:
                with pytest.raises(ValueError, match="No databases"):
                    ConfigLoader.load_databases(f.name)
            finally:
                os.unlink(f.name)
