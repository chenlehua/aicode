"""LLM service for natural language to SQL generation."""

import logging
import time

from openai import OpenAI

from app.adapters import DatabaseRegistry
from app.config import settings
from app.models.database import DatabaseMetadata, DatabaseType

# Configure logger
logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating SQL from natural language using Qwen via DashScope."""

    def __init__(self) -> None:
        """Initialize OpenAI client configured for DashScope."""
        self.client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-turbo"  # Qwen model via DashScope

    def format_metadata_prompt(self, metadata: DatabaseMetadata) -> str:
        """Format database metadata into a prompt context for LLM."""
        db_type = metadata.database_type
        db_type_name = "MySQL" if db_type == DatabaseType.MYSQL else "PostgreSQL"

        prompt_parts = [
            (
                f"You are a SQL expert. Generate {db_type_name} SELECT queries "
                "based on natural language descriptions."
            ),
            "",
            "Database Schema:",
            f"Database: {metadata.database_name}",
            f"Database Type: {db_type_name}",
            "",
        ]

        # Add tables
        if metadata.tables:
            prompt_parts.append("Tables:")
            for table in metadata.tables:
                prompt_parts.append(f"  - {table.table_name} (table)")
                for col in table.columns:
                    pk_marker = " [PK]" if col.is_primary_key else ""
                    fk_marker = f" [FK -> {col.references}]" if col.is_foreign_key else ""
                    nullable_marker = "" if col.is_nullable else " [NOT NULL]"
                    prompt_parts.append(
                        f"    - {col.name}: {col.data_type}{pk_marker}{fk_marker}{nullable_marker}"
                    )
            prompt_parts.append("")

        # Add views
        if metadata.views:
            prompt_parts.append("Views:")
            for view in metadata.views:
                prompt_parts.append(f"  - {view.table_name} (view)")
                for col in view.columns:
                    prompt_parts.append(f"    - {col.name}: {col.data_type}")
            prompt_parts.append("")

        prompt_parts.append(
            f"Generate only valid {db_type_name} SELECT queries. "
            "Do not include any explanations or markdown formatting, just the SQL query."
        )

        return "\n".join(prompt_parts)

    def generate_sql(self, prompt: str, metadata: DatabaseMetadata) -> tuple[str, str | None]:
        """Generate SQL from natural language prompt."""
        if not settings.dashscope_api_key:
            logger.error("DASHSCOPE_API_KEY not configured")
            raise ValueError("DASHSCOPE_API_KEY not configured")

        # Format the full prompt with metadata context
        system_prompt = self.format_metadata_prompt(metadata)
        user_prompt = f"User request: {prompt}\n\nGenerate SQL query:"

        logger.info("=" * 60)
        logger.info("[LLM Request] Calling Alibaba DashScope API")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Database: {metadata.database_name}")
        logger.info(f"  Tables: {len(metadata.tables)}, Views: {len(metadata.views)}")
        logger.info(f"  User prompt: {prompt}")
        logger.debug(f"  System prompt:\n{system_prompt}")

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # Lower temperature for more deterministic SQL
                max_tokens=500,
            )

            elapsed_time = time.time() - start_time

            content = response.choices[0].message.content
            if not content:
                logger.error("[LLM Response] Empty response from LLM")
                raise RuntimeError("LLM returned empty response")

            generated_sql = content.strip()

            logger.info(f"[LLM Response] Received in {elapsed_time:.2f}s")
            logger.info(f"  Raw response:\n{generated_sql}")

            # Log token usage if available
            if hasattr(response, "usage") and response.usage:
                logger.info(
                    f"  Token usage - Prompt: {response.usage.prompt_tokens}, "
                    f"Completion: {response.usage.completion_tokens}, "
                    f"Total: {response.usage.total_tokens}"
                )

            # Clean up the SQL (remove markdown code blocks if present)
            if generated_sql.startswith("```"):
                # Remove markdown code block markers
                lines = generated_sql.split("\n")
                # Remove first line (```sql or ```)
                lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                generated_sql = "\n".join(lines).strip()
                logger.debug(f"  Cleaned SQL:\n{generated_sql}")

            # Validate the generated SQL based on database type
            db_type = metadata.database_type
            # Use the string value for compatibility between model and core DatabaseType
            adapter = DatabaseRegistry.get_adapter(db_type.value)
            is_valid, error_msg = adapter.validate_sql(generated_sql)
            if not is_valid:
                logger.warning(f"[LLM Validation] Generated SQL is invalid: {error_msg}")
                raise ValueError(f"Generated SQL is invalid: {error_msg or 'Unknown error'}")

            logger.info(f"[LLM Success] Generated valid SQL in {elapsed_time:.2f}s")
            logger.info("=" * 60)

            # Generate explanation
            explanation = f"Generated SQL query for: {prompt}"

            return generated_sql, explanation
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"[LLM Error] Failed after {elapsed_time:.2f}s: {str(e)}")
            logger.info("=" * 60)
            raise RuntimeError(f"LLM generation failed: {str(e)}") from e
