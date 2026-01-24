"""Tests for database service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from pg_mcp.config import DatabaseConfig, QuerySettings
from pg_mcp.database import ConnectionPool, DatabaseService, SchemaCache
from pg_mcp.models import (
    DatabaseSchema,
    QueryResultData,
    SQLExecutionError,
    SQLTimeoutError,
    TableInfo,
    ColumnInfo,
)


class TestConnectionPool:
    """Tests for ConnectionPool."""

    @pytest.fixture
    def db_config(self) -> DatabaseConfig:
        """Create database configuration for testing."""
        return DatabaseConfig(
            name="test_db",
            host="localhost",
            port=5432,
            database="testdb",
            user="testuser",
            password="testpass",
        )

    def test_pool_init(self, db_config: DatabaseConfig) -> None:
        """Test ConnectionPool initialization."""
        pool = ConnectionPool(db_config)
        assert pool.config == db_config
        assert pool._pool is None
        assert pool.is_initialized is False

    @pytest.mark.asyncio
    async def test_pool_initialize(self, db_config: DatabaseConfig) -> None:
        """Test ConnectionPool.initialize()."""
        with patch("pg_mcp.database.connection.asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_pool = MagicMock()
            mock_create.return_value = mock_pool

            pool = ConnectionPool(db_config)
            await pool.initialize()

            assert pool.is_initialized is True
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_pool_double_initialize(self, db_config: DatabaseConfig) -> None:
        """Test that double initialization is idempotent."""
        with patch("pg_mcp.database.connection.asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_pool = MagicMock()
            mock_create.return_value = mock_pool

            pool = ConnectionPool(db_config)
            await pool.initialize()
            await pool.initialize()

            # Should only create pool once
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_pool_acquire(self, db_config: DatabaseConfig) -> None:
        """Test ConnectionPool.acquire()."""
        with patch("pg_mcp.database.connection.asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_conn = MagicMock()
            mock_pool = MagicMock()
            mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_create.return_value = mock_pool

            pool = ConnectionPool(db_config)
            await pool.initialize()

            async with pool.acquire() as conn:
                assert conn == mock_conn

    @pytest.mark.asyncio
    async def test_pool_close(self, db_config: DatabaseConfig) -> None:
        """Test ConnectionPool.close()."""
        with patch("pg_mcp.database.connection.asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
            mock_pool = MagicMock()
            mock_pool.close = AsyncMock()
            mock_create.return_value = mock_pool

            pool = ConnectionPool(db_config)
            await pool.initialize()
            await pool.close()

            mock_pool.close.assert_called_once()
            assert pool.is_initialized is False

    @pytest.mark.asyncio
    async def test_pool_close_not_initialized(self, db_config: DatabaseConfig) -> None:
        """Test closing an uninitialized pool does nothing."""
        pool = ConnectionPool(db_config)
        await pool.close()  # Should not raise
        assert pool.is_initialized is False


class TestSchemaCache:
    """Tests for SchemaCache."""

    @pytest.fixture
    def schema_cache(self) -> SchemaCache:
        """Create SchemaCache for testing."""
        return SchemaCache("testdb")

    def test_schema_cache_init(self, schema_cache: SchemaCache) -> None:
        """Test SchemaCache initialization."""
        assert schema_cache.database_name == "testdb"
        assert schema_cache._schema is None

    def test_schema_property_before_refresh(self, schema_cache: SchemaCache) -> None:
        """Test accessing schema before refresh returns None."""
        assert schema_cache.schema is None

    def test_get_table_names_empty(self, schema_cache: SchemaCache) -> None:
        """Test get_table_names when schema is not loaded."""
        assert schema_cache.get_table_names() == set()

    @pytest.mark.asyncio
    async def test_refresh_schema(self, schema_cache: SchemaCache) -> None:
        """Test schema refresh from database."""
        mock_conn = AsyncMock()

        # Mock queries in the order they're called in refresh()
        # Order: TABLES_QUERY, COLUMNS_QUERY, PRIMARY_KEYS_QUERY, FOREIGN_KEYS_QUERY,
        #        INDEXES_QUERY, VIEWS_QUERY, ENUM_TYPES_QUERY
        mock_conn.fetch.side_effect = [
            # Tables query
            [
                {
                    "table_schema": "public",
                    "table_name": "users",
                    "table_comment": "User table",
                    "estimated_row_count": 100,
                },
            ],
            # Columns query
            [
                {
                    "table_schema": "public",
                    "table_name": "users",
                    "column_name": "id",
                    "data_type": "integer",
                    "is_nullable": False,
                    "column_default": None,
                    "column_comment": None,
                },
                {
                    "table_schema": "public",
                    "table_name": "users",
                    "column_name": "name",
                    "data_type": "varchar",
                    "is_nullable": True,
                    "column_default": None,
                    "column_comment": None,
                },
            ],
            # Primary keys query
            [
                {"table_schema": "public", "table_name": "users", "column_name": "id"},
            ],
            # Foreign keys query
            [],
            # Indexes query
            [],
            # Views query
            [],
            # Enum types query
            [],
        ]

        result = await schema_cache.refresh(mock_conn)

        assert result is not None
        assert result.database_name == "testdb"
        assert len(result.tables) == 1
        assert result.tables[0].name == "users"

    def test_get_table_names_with_schema(self) -> None:
        """Test get_table_names with loaded schema."""
        cache = SchemaCache("testdb")
        cache._schema = DatabaseSchema(
            database_name="testdb",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[
                        ColumnInfo(name="id", data_type="integer"),
                    ],
                ),
                TableInfo(
                    schema_name="public",
                    name="orders",
                    columns=[
                        ColumnInfo(name="id", data_type="integer"),
                    ],
                ),
            ],
        )

        names = cache.get_table_names()

        assert "users" in names
        assert "orders" in names
        assert "public.users" in names
        assert "public.orders" in names


class TestDatabaseService:
    """Tests for DatabaseService."""

    @pytest.fixture
    def db_config(self) -> DatabaseConfig:
        """Create database configuration."""
        return DatabaseConfig(
            name="test_db",
            host="localhost",
            port=5432,
            database="testdb",
            user="testuser",
            password="testpass",
        )

    @pytest.fixture
    def query_settings(self) -> QuerySettings:
        """Create query settings."""
        return QuerySettings(
            default_limit=100,
            statement_timeout=30000,
            enable_validation=True,
        )

    @pytest.fixture
    def sample_schema(self) -> DatabaseSchema:
        """Create sample schema."""
        return DatabaseSchema(
            database_name="testdb",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(name="name", data_type="varchar"),
                    ],
                ),
            ],
        )

    def test_service_init(
        self, db_config: DatabaseConfig, query_settings: QuerySettings
    ) -> None:
        """Test DatabaseService initialization."""
        service = DatabaseService(db_config, query_settings)
        assert service.config == db_config
        assert service.query_settings == query_settings

    def test_schema_property_before_init(
        self, db_config: DatabaseConfig, query_settings: QuerySettings
    ) -> None:
        """Test accessing schema before initialization raises error."""
        service = DatabaseService(db_config, query_settings)

        with pytest.raises(RuntimeError) as exc:
            _ = service.schema
        assert "initialize" in str(exc.value).lower()

    @pytest.mark.asyncio
    async def test_service_initialize(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test DatabaseService.initialize()."""
        service = DatabaseService(db_config, query_settings)

        with patch.object(service._pool, "initialize", new_callable=AsyncMock) as mock_pool_init:
            with patch.object(service, "refresh_schema", new_callable=AsyncMock) as mock_refresh:
                mock_refresh.return_value = sample_schema

                await service.initialize()

                mock_pool_init.assert_called_once()
                mock_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_close(
        self, db_config: DatabaseConfig, query_settings: QuerySettings
    ) -> None:
        """Test DatabaseService.close()."""
        service = DatabaseService(db_config, query_settings)

        with patch.object(service._pool, "close", new_callable=AsyncMock) as mock_close:
            await service.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_success(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test successful query execution."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
        mock_conn.execute = AsyncMock()

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()  # Mark as initialized

            result = await service.execute_query("SELECT * FROM users")

            assert result.row_count == 2
            assert result.columns == ["id", "name"]
            assert result.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_execute_query_auto_limit(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test that LIMIT is automatically added."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.execute = AsyncMock()

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            await service.execute_query("SELECT * FROM users")

            # Check that LIMIT was added
            called_sql = mock_conn.fetch.call_args[0][0]
            assert "LIMIT" in called_sql

    @pytest.mark.asyncio
    async def test_execute_query_preserves_existing_limit(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test that existing LIMIT is preserved."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.execute = AsyncMock()

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            await service.execute_query("SELECT * FROM users LIMIT 10")

            # Check that original LIMIT is preserved
            called_sql = mock_conn.fetch.call_args[0][0]
            assert "LIMIT 10" in called_sql
            assert called_sql.count("LIMIT") == 1

    @pytest.mark.asyncio
    async def test_execute_query_empty_result(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test query with empty result."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.execute = AsyncMock()

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            result = await service.execute_query("SELECT * FROM users WHERE id = 999")

            assert result.row_count == 0
            assert result.columns == []
            assert result.rows == []

    @pytest.mark.asyncio
    async def test_execute_query_timeout(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test query timeout."""
        import asyncpg

        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetch.side_effect = asyncpg.QueryCanceledError("timeout")

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            with pytest.raises(SQLTimeoutError):
                await service.execute_query("SELECT pg_sleep(100)")

    @pytest.mark.asyncio
    async def test_execute_query_postgres_error(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test PostgreSQL error handling."""
        import asyncpg

        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetch.side_effect = asyncpg.PostgresError("relation does not exist")

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            with pytest.raises(SQLExecutionError):
                await service.execute_query("SELECT * FROM nonexistent")

    @pytest.mark.asyncio
    async def test_execute_query_unexpected_error(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test unexpected error handling."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetch.side_effect = RuntimeError("Unexpected error")

        with patch.object(service._pool, "acquire") as mock_acquire:
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_acquire.return_value.__aexit__.return_value = None
            service._pool._pool = MagicMock()

            with pytest.raises(SQLExecutionError) as exc:
                await service.execute_query("SELECT * FROM users")
            assert "Unexpected" in str(exc.value)

    def test_get_table_names(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test get_table_names returns cached table names."""
        service = DatabaseService(db_config, query_settings)
        service._schema_cache._schema = sample_schema

        names = service.get_table_names()

        assert "users" in names
        assert "public.users" in names

    @pytest.mark.asyncio
    async def test_refresh_schema(
        self, db_config: DatabaseConfig, query_settings: QuerySettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test schema refresh."""
        service = DatabaseService(db_config, query_settings)

        mock_conn = AsyncMock()

        with patch.object(service._pool, "acquire") as mock_acquire:
            with patch.object(service._schema_cache, "refresh", new_callable=AsyncMock) as mock_refresh:
                mock_acquire.return_value.__aenter__.return_value = mock_conn
                mock_acquire.return_value.__aexit__.return_value = None
                service._pool._pool = MagicMock()
                mock_refresh.return_value = sample_schema

                result = await service.refresh_schema()

                assert result == sample_schema
                mock_refresh.assert_called_once_with(mock_conn)
