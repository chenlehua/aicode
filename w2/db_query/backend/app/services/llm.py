"""LLM service for natural language to SQL generation."""

from openai import OpenAI

from app.config import settings
from app.models.database import DatabaseMetadata
from app.services.query import QueryService


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
        prompt_parts = [
            (
                "You are a SQL expert. Generate PostgreSQL SELECT queries "
                "based on natural language descriptions."
            ),
            "",
            "Database Schema:",
            f"Database: {metadata.database_name}",
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
            "Generate only valid PostgreSQL SELECT queries. "
            "Do not include any explanations or markdown formatting, just the SQL query."
        )

        return "\n".join(prompt_parts)

    def generate_sql(self, prompt: str, metadata: DatabaseMetadata) -> tuple[str, str | None]:
        """Generate SQL from natural language prompt."""
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY not configured")

        # Format the full prompt with metadata context
        system_prompt = self.format_metadata_prompt(metadata)
        user_prompt = f"User request: {prompt}\n\nGenerate SQL query:"

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

            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("LLM returned empty response")
            generated_sql = content.strip()

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

            # Validate the generated SQL
            is_valid, error_msg = QueryService.validate_sql(generated_sql)
            if not is_valid:
                raise ValueError(f"Generated SQL is invalid: {error_msg or 'Unknown error'}")

            # Generate explanation
            explanation = f"Generated SQL query for: {prompt}"

            return generated_sql, explanation
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}") from e
