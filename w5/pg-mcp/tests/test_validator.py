"""Tests for SQL validator."""

import pytest

from pg_mcp.models import SQLUnsafeError
from pg_mcp.validator import SQLValidator


class TestSQLValidator:
    """Tests for SQLValidator."""

    @pytest.fixture
    def validator(self) -> SQLValidator:
        """Create a validator instance."""
        return SQLValidator()

    @pytest.fixture
    def validator_with_tables(self) -> SQLValidator:
        """Create a validator with known tables."""
        return SQLValidator(known_tables={"users", "orders", "public.users", "public.orders"})

    # Valid SELECT queries

    def test_simple_select(self, validator: SQLValidator) -> None:
        """Test simple SELECT statement passes validation."""
        sql = "SELECT * FROM users"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_where(self, validator: SQLValidator) -> None:
        """Test SELECT with WHERE clause passes validation."""
        sql = "SELECT id, name FROM users WHERE id = 1"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_join(self, validator: SQLValidator) -> None:
        """Test SELECT with JOIN passes validation."""
        sql = """
        SELECT u.name, o.total
        FROM users u
        JOIN orders o ON u.id = o.user_id
        """
        result = validator.validate(sql)
        assert "SELECT" in result

    def test_select_with_subquery(self, validator: SQLValidator) -> None:
        """Test SELECT with subquery passes validation."""
        sql = """
        SELECT * FROM users
        WHERE id IN (SELECT user_id FROM orders WHERE total > 100)
        """
        result = validator.validate(sql)
        assert "SELECT" in result

    def test_select_with_aggregate(self, validator: SQLValidator) -> None:
        """Test SELECT with aggregate functions passes validation."""
        sql = "SELECT COUNT(*), SUM(total) FROM orders GROUP BY user_id"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_cte(self, validator: SQLValidator) -> None:
        """Test SELECT with CTE passes validation."""
        sql = """
        WITH active_users AS (
            SELECT * FROM users WHERE active = true
        )
        SELECT * FROM active_users
        """
        result = validator.validate(sql)
        assert "WITH" in result

    # Invalid statements - DML

    def test_insert_rejected(self, validator: SQLValidator) -> None:
        """Test INSERT statement is rejected."""
        sql = "INSERT INTO users (name) VALUES ('test')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "SELECT" in str(exc.value) or "INSERT" in str(exc.value).upper()

    def test_update_rejected(self, validator: SQLValidator) -> None:
        """Test UPDATE statement is rejected."""
        sql = "UPDATE users SET name = 'test' WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_delete_rejected(self, validator: SQLValidator) -> None:
        """Test DELETE statement is rejected."""
        sql = "DELETE FROM users WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Invalid statements - DDL

    def test_drop_rejected(self, validator: SQLValidator) -> None:
        """Test DROP statement is rejected."""
        sql = "DROP TABLE users"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_create_rejected(self, validator: SQLValidator) -> None:
        """Test CREATE statement is rejected."""
        sql = "CREATE TABLE test (id int)"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_alter_rejected(self, validator: SQLValidator) -> None:
        """Test ALTER statement is rejected."""
        sql = "ALTER TABLE users ADD COLUMN email varchar"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_truncate_rejected(self, validator: SQLValidator) -> None:
        """Test TRUNCATE statement is rejected."""
        sql = "TRUNCATE TABLE users"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Multiple statements

    def test_multiple_statements_rejected(self, validator: SQLValidator) -> None:
        """Test multiple statements are rejected."""
        sql = "SELECT 1; DROP TABLE users"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "多条" in str(exc.value)

    def test_select_then_insert_rejected(self, validator: SQLValidator) -> None:
        """Test SELECT followed by INSERT is rejected."""
        sql = "SELECT * FROM users; INSERT INTO users VALUES (1)"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Dangerous functions

    def test_pg_read_file_rejected(self, validator: SQLValidator) -> None:
        """Test pg_read_file function is rejected."""
        sql = "SELECT pg_read_file('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "pg_read_file" in str(exc.value)

    def test_dblink_rejected(self, validator: SQLValidator) -> None:
        """Test dblink function is rejected."""
        sql = "SELECT * FROM dblink('host=evil.com', 'SELECT 1')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "dblink" in str(exc.value)

    def test_lo_import_rejected(self, validator: SQLValidator) -> None:
        """Test lo_import function is rejected."""
        sql = "SELECT lo_import('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "lo_import" in str(exc.value)

    # Syntax errors

    def test_syntax_error_rejected(self, validator: SQLValidator) -> None:
        """Test SQL syntax errors are rejected."""
        sql = "SELEC * FORM users"
        with pytest.raises(SQLUnsafeError):
            # SQLGlot may parse this as an Alias rather than throwing a syntax error,
            # but it should still be rejected since it's not a valid SELECT statement
            validator.validate(sql)

    def test_empty_sql_rejected(self, validator: SQLValidator) -> None:
        """Test empty SQL is rejected."""
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate("")
        assert "空" in str(exc.value)

    def test_whitespace_only_rejected(self, validator: SQLValidator) -> None:
        """Test whitespace-only SQL is rejected."""
        with pytest.raises(SQLUnsafeError):
            validator.validate("   ")

    # Table validation

    def test_known_table_passes(self, validator_with_tables: SQLValidator) -> None:
        """Test query with known tables passes."""
        sql = "SELECT * FROM users"
        result = validator_with_tables.validate(sql)
        assert result == sql

    def test_unknown_table_rejected(self, validator_with_tables: SQLValidator) -> None:
        """Test query with unknown tables is rejected."""
        sql = "SELECT * FROM nonexistent_table"
        with pytest.raises(SQLUnsafeError) as exc:
            validator_with_tables.validate(sql)
        assert "未知" in str(exc.value)

    # is_select_only helper

    def test_is_select_only_true(self, validator: SQLValidator) -> None:
        """Test is_select_only returns True for valid SELECT."""
        assert validator.is_select_only("SELECT * FROM users") is True

    def test_is_select_only_false_for_insert(self, validator: SQLValidator) -> None:
        """Test is_select_only returns False for INSERT."""
        assert validator.is_select_only("INSERT INTO users VALUES (1)") is False

    def test_is_select_only_false_for_invalid(self, validator: SQLValidator) -> None:
        """Test is_select_only returns False for invalid SQL."""
        assert validator.is_select_only("NOT VALID SQL") is False
