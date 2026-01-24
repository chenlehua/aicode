"""LLM service for SQL generation and result validation."""

import json
import logging
import re

from openai import AsyncOpenAI

from pg_mcp.config import LLMSettings
from pg_mcp.llm.prompts import (
    RESULT_VALIDATION_SYSTEM_PROMPT,
    RESULT_VALIDATION_USER_TEMPLATE,
    SQL_GENERATION_SYSTEM_PROMPT,
    SQL_GENERATION_USER_TEMPLATE,
)
from pg_mcp.models import (
    DatabaseSchema,
    LLMError,
    QueryResultData,
    SQLGenerationError,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered SQL generation and validation.

    Args:
        settings: LLM configuration settings.
    """

    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self._client = AsyncOpenAI(
            api_key=settings.api_key.get_secret_value(),
            base_url=settings.base_url,
            timeout=settings.timeout,
        )

    async def generate_sql(self, query: str, schema: DatabaseSchema) -> str:
        """Generate SQL from a natural language query.

        Args:
            query: The natural language query from the user.
            schema: The database schema for context.

        Returns:
            The generated SQL statement.

        Raises:
            SQLGenerationError: If SQL generation fails.
            LLMError: If the LLM API call fails.
        """
        schema_context = schema.to_llm_context()
        user_message = SQL_GENERATION_USER_TEMPLATE.format(
            schema=schema_context,
            query=query,
        )

        logger.debug(f"Generating SQL for query: {query}")

        try:
            response = await self._client.chat.completions.create(
                model=self.settings.model,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                messages=[
                    {"role": "system", "content": SQL_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )

            content = response.choices[0].message.content
            if not content:
                raise SQLGenerationError("LLM 返回了空响应")

            sql = self._clean_sql(content)
            if not sql:
                raise SQLGenerationError("无法从 LLM 响应中提取有效的 SQL")

            logger.info(f"Generated SQL: {sql[:200]}...")
            return sql

        except SQLGenerationError:
            raise
        except Exception as e:
            logger.exception("LLM API call failed during SQL generation")
            raise LLMError(f"LLM API 调用失败: {e}")

    async def validate_result(
        self,
        query: str,
        sql: str,
        result: QueryResultData,
    ) -> ValidationResult:
        """Validate query results using LLM.

        Args:
            query: The original natural language query.
            sql: The generated SQL statement.
            result: The query execution result.

        Returns:
            Validation result with pass/fail status and message.
        """
        # Format sample rows (up to 5)
        sample_rows = self._format_sample_rows(result)

        user_message = RESULT_VALIDATION_USER_TEMPLATE.format(
            query=query,
            sql=sql,
            columns=", ".join(result.columns) if result.columns else "无",
            row_count=result.row_count,
            sample_rows=sample_rows,
        )

        logger.debug(f"Validating result for query: {query}")

        try:
            response = await self._client.chat.completions.create(
                model=self.settings.model,
                temperature=self.settings.temperature,
                max_tokens=512,
                messages=[
                    {"role": "system", "content": RESULT_VALIDATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )

            content = response.choices[0].message.content
            if not content:
                return ValidationResult(passed=True, message="验证完成（无响应）")

            validation = self._parse_validation_response(content)
            logger.info(f"Validation result: passed={validation.passed}, message={validation.message}")
            return validation

        except Exception as e:
            logger.exception("LLM API call failed during result validation")
            # Default to pass if validation fails to not block the query
            return ValidationResult(
                passed=True,
                message=f"验证过程出错，默认通过: {e}",
            )

    def _clean_sql(self, content: str) -> str:
        """Clean LLM response to extract pure SQL.

        Removes markdown code blocks and extra whitespace.

        Args:
            content: Raw LLM response content.

        Returns:
            Cleaned SQL statement.
        """
        sql = content.strip()

        # Remove markdown code blocks
        sql = re.sub(r"```sql\s*", "", sql)
        sql = re.sub(r"```\s*", "", sql)

        # Remove leading/trailing whitespace and newlines
        sql = sql.strip()

        # Remove any leading explanation text before SELECT
        if "SELECT" in sql.upper():
            # Find the first SELECT and take everything from there
            match = re.search(r"(SELECT\s+.+)", sql, re.IGNORECASE | re.DOTALL)
            if match:
                sql = match.group(1)

        return sql.strip()

    def _parse_validation_response(self, content: str) -> ValidationResult:
        """Parse LLM validation response into ValidationResult.

        Args:
            content: LLM response content.

        Returns:
            Parsed ValidationResult.
        """
        content = content.strip()

        # Try to extract JSON from the response
        # Handle case where LLM might wrap JSON in markdown
        json_match = re.search(r"\{[^{}]*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                data = json.loads(json_str)
                return ValidationResult(
                    passed=bool(data.get("passed", True)),
                    message=str(data.get("message", "验证完成")),
                )
            except json.JSONDecodeError:
                pass

        # If JSON parsing fails, try to extract meaning from text
        content_lower = content.lower()
        passed = "false" not in content_lower and "不" not in content

        return ValidationResult(
            passed=passed,
            message=content[:200] if len(content) > 200 else content,
        )

    def _format_sample_rows(self, result: QueryResultData, max_rows: int = 5) -> str:
        """Format sample rows for display.

        Args:
            result: Query result data.
            max_rows: Maximum number of rows to include.

        Returns:
            Formatted string representation of sample rows.
        """
        if not result.rows:
            return "（无数据）"

        lines: list[str] = []
        for i, row in enumerate(result.rows[:max_rows]):
            # Format each cell, handling None and long values
            formatted = []
            for val in row:
                if val is None:
                    formatted.append("NULL")
                else:
                    str_val = str(val)
                    if len(str_val) > 50:
                        str_val = str_val[:47] + "..."
                    formatted.append(str_val)
            lines.append(f"{i + 1}. {', '.join(formatted)}")

        if result.row_count > max_rows:
            lines.append(f"... (还有 {result.row_count - max_rows} 行)")

        return "\n".join(lines)
