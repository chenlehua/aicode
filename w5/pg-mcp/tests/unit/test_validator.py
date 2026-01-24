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

    # Additional SELECT statement variants

    def test_select_with_left_join(self, validator: SQLValidator) -> None:
        """Test SELECT with LEFT JOIN passes validation."""
        sql = "SELECT * FROM users u LEFT JOIN orders o ON u.id = o.user_id"
        result = validator.validate(sql)
        assert "SELECT" in result

    def test_select_with_order_by(self, validator: SQLValidator) -> None:
        """Test SELECT with ORDER BY passes validation."""
        sql = "SELECT * FROM users ORDER BY id DESC"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_limit_offset(self, validator: SQLValidator) -> None:
        """Test SELECT with LIMIT and OFFSET passes validation."""
        sql = "SELECT * FROM users LIMIT 10 OFFSET 5"
        result = validator.validate(sql)
        assert result == sql

    def test_select_distinct(self, validator: SQLValidator) -> None:
        """Test SELECT DISTINCT passes validation."""
        sql = "SELECT DISTINCT name FROM users"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_alias(self, validator: SQLValidator) -> None:
        """Test SELECT with aliases passes validation."""
        sql = "SELECT u.name AS user_name FROM users u"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_case(self, validator: SQLValidator) -> None:
        """Test SELECT with CASE expression passes validation."""
        sql = "SELECT CASE WHEN x > 0 THEN 'positive' ELSE 'negative' END FROM t"
        result = validator.validate(sql)
        assert "CASE" in result

    def test_select_with_coalesce(self, validator: SQLValidator) -> None:
        """Test SELECT with COALESCE passes validation."""
        sql = "SELECT COALESCE(name, 'N/A') FROM users"
        result = validator.validate(sql)
        assert "COALESCE" in result

    def test_select_with_cast(self, validator: SQLValidator) -> None:
        """Test SELECT with CAST passes validation."""
        sql = "SELECT CAST(id AS TEXT) FROM users"
        result = validator.validate(sql)
        assert "CAST" in result

    def test_select_union_rejected(self, validator: SQLValidator) -> None:
        """Test SELECT UNION is rejected (not a pure SELECT)."""
        # UNION is parsed as Union type, not Select, so it gets rejected
        sql = "SELECT a FROM t1 UNION SELECT b FROM t2"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "Union" in str(exc.value)

    def test_select_exists(self, validator: SQLValidator) -> None:
        """Test SELECT with EXISTS passes validation."""
        sql = "SELECT * FROM t WHERE EXISTS (SELECT 1 FROM s WHERE s.id = t.id)"
        result = validator.validate(sql)
        assert "EXISTS" in result

    def test_select_with_having(self, validator: SQLValidator) -> None:
        """Test SELECT with HAVING passes validation."""
        sql = "SELECT user_id, COUNT(*) FROM orders GROUP BY user_id HAVING COUNT(*) > 1"
        result = validator.validate(sql)
        assert "HAVING" in result

    def test_select_with_in_subquery(self, validator: SQLValidator) -> None:
        """Test SELECT with IN subquery passes validation."""
        sql = "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders)"
        result = validator.validate(sql)
        assert "SELECT" in result

    def test_safe_functions_allowed(self, validator: SQLValidator) -> None:
        """Test that safe functions are allowed."""
        sql = "SELECT COUNT(*), MAX(id), NOW(), CURRENT_TIMESTAMP FROM users"
        result = validator.validate(sql)
        assert "COUNT" in result

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

    def test_insert_with_select_rejected(self, validator: SQLValidator) -> None:
        """Test INSERT ... SELECT is rejected."""
        sql = "INSERT INTO t SELECT * FROM s"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_update_rejected(self, validator: SQLValidator) -> None:
        """Test UPDATE statement is rejected."""
        sql = "UPDATE users SET name = 'test' WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_update_with_where_rejected(self, validator: SQLValidator) -> None:
        """Test UPDATE with WHERE is still rejected."""
        sql = "UPDATE users SET x = 1 WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_delete_rejected(self, validator: SQLValidator) -> None:
        """Test DELETE statement is rejected."""
        sql = "DELETE FROM users WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_delete_without_where_rejected(self, validator: SQLValidator) -> None:
        """Test DELETE without WHERE is rejected."""
        sql = "DELETE FROM users"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_merge_rejected(self, validator: SQLValidator) -> None:
        """Test MERGE statement is rejected."""
        sql = "MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET x = 1"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Invalid statements - DDL

    def test_drop_rejected(self, validator: SQLValidator) -> None:
        """Test DROP statement is rejected."""
        sql = "DROP TABLE users"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_drop_database_rejected(self, validator: SQLValidator) -> None:
        """Test DROP DATABASE is rejected."""
        sql = "DROP DATABASE testdb"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_create_rejected(self, validator: SQLValidator) -> None:
        """Test CREATE statement is rejected."""
        sql = "CREATE TABLE test (id int)"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_create_index_rejected(self, validator: SQLValidator) -> None:
        """Test CREATE INDEX is rejected."""
        sql = "CREATE INDEX idx ON users(id)"
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

    def test_grant_rejected(self, validator: SQLValidator) -> None:
        """Test GRANT is rejected."""
        sql = "GRANT SELECT ON users TO public"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_revoke_rejected(self, validator: SQLValidator) -> None:
        """Test REVOKE is rejected."""
        sql = "REVOKE SELECT ON users FROM public"
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

    def test_multiple_selects_rejected(self, validator: SQLValidator) -> None:
        """Test multiple SELECT statements are rejected."""
        sql = "SELECT 1; SELECT 2"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "多条" in str(exc.value)

    def test_comment_bypass_attempt_rejected(self, validator: SQLValidator) -> None:
        """Test comment-based bypass attempt is rejected."""
        sql = "SELECT 1; -- comment\n DROP TABLE x"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Dangerous functions

    def test_pg_read_file_rejected(self, validator: SQLValidator) -> None:
        """Test pg_read_file function is rejected."""
        sql = "SELECT pg_read_file('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "pg_read_file" in str(exc.value)

    def test_pg_read_binary_file_rejected(self, validator: SQLValidator) -> None:
        """Test pg_read_binary_file function is rejected."""
        sql = "SELECT pg_read_binary_file('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "pg_read_binary_file" in str(exc.value)

    def test_pg_ls_dir_rejected(self, validator: SQLValidator) -> None:
        """Test pg_ls_dir function is rejected."""
        sql = "SELECT pg_ls_dir('/')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "pg_ls_dir" in str(exc.value)

    def test_pg_stat_file_rejected(self, validator: SQLValidator) -> None:
        """Test pg_stat_file function is rejected."""
        sql = "SELECT pg_stat_file('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "pg_stat_file" in str(exc.value)

    def test_dblink_rejected(self, validator: SQLValidator) -> None:
        """Test dblink function is rejected."""
        sql = "SELECT * FROM dblink('host=evil.com', 'SELECT 1')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "dblink" in str(exc.value)

    def test_dblink_exec_rejected(self, validator: SQLValidator) -> None:
        """Test dblink_exec function is rejected."""
        sql = "SELECT dblink_exec('conn', 'DROP TABLE users')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "dblink_exec" in str(exc.value)

    def test_dblink_connect_rejected(self, validator: SQLValidator) -> None:
        """Test dblink_connect function is rejected."""
        sql = "SELECT dblink_connect('host=evil.com')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "dblink_connect" in str(exc.value)

    def test_lo_import_rejected(self, validator: SQLValidator) -> None:
        """Test lo_import function is rejected."""
        sql = "SELECT lo_import('/etc/passwd')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "lo_import" in str(exc.value)

    def test_lo_export_rejected(self, validator: SQLValidator) -> None:
        """Test lo_export function is rejected."""
        sql = "SELECT lo_export(12345, '/tmp/x')"
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate(sql)
        assert "lo_export" in str(exc.value)

    def test_nested_dangerous_function_rejected(self, validator: SQLValidator) -> None:
        """Test nested dangerous function is rejected."""
        sql = "SELECT (SELECT pg_read_file('x'))"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    # Syntax errors and edge cases

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

    def test_incomplete_sql_rejected(self, validator: SQLValidator) -> None:
        """Test incomplete SQL is rejected."""
        sql = "SELECT * FROM"
        with pytest.raises(SQLUnsafeError):
            validator.validate(sql)

    def test_very_long_sql(self, validator: SQLValidator) -> None:
        """Test that very long SQL is handled properly."""
        # Create a valid but long SQL
        columns = ", ".join([f"col{i}" for i in range(100)])
        sql = f"SELECT {columns} FROM users"
        result = validator.validate(sql)
        assert "SELECT" in result

    def test_unicode_table_name(self, validator: SQLValidator) -> None:
        """Test SQL with unicode table name is handled."""
        sql = 'SELECT * FROM "用户表"'
        # Should either pass or raise SQLUnsafeError (not crash)
        try:
            result = validator.validate(sql)
            assert "SELECT" in result
        except SQLUnsafeError:
            # This is also acceptable behavior
            pass

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

    def test_schema_qualified_table_passes(self, validator_with_tables: SQLValidator) -> None:
        """Test schema-qualified table name passes."""
        sql = "SELECT * FROM public.users"
        result = validator_with_tables.validate(sql)
        assert result == sql

    def test_no_known_tables_skip_check(self, validator: SQLValidator) -> None:
        """Test that without known_tables, table check is skipped."""
        sql = "SELECT * FROM any_table"
        result = validator.validate(sql)
        assert result == sql

    def test_join_all_tables_known(self, validator_with_tables: SQLValidator) -> None:
        """Test JOIN with all known tables passes."""
        sql = "SELECT * FROM users u JOIN orders o ON u.id = o.user_id"
        result = validator_with_tables.validate(sql)
        assert "JOIN" in result

    def test_join_one_table_unknown(self, validator_with_tables: SQLValidator) -> None:
        """Test JOIN with one unknown table is rejected."""
        sql = "SELECT * FROM users u JOIN unknown_table t ON u.id = t.user_id"
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
