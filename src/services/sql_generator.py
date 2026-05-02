"""SQL generation service using OpenAI GPT-5.2.

This service accepts a plain-English question and a database schema, then uses
the OpenAI API to produce a valid SQL SELECT statement.
"""
from __future__ import annotations

import re
import ssl

import httpx
from openai import OpenAI, OpenAIError

from models.config import AppConfig, SchemaColumn, TableSchema
from utils.exceptions import ConfigurationError, SQLGenerationError
from utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT_TEMPLATE = """\
You are an expert SQL query writer. Generate a single, valid {dialect} SELECT query
that answers the user's question based on the provided database schema.

Rules:
- Output ONLY the SQL query — no explanation, no markdown, no code fences.
- Use only the tables and columns listed in the schema below.
- Write read-only SELECT queries only; never INSERT, UPDATE, DELETE, or DROP.
- Use proper SQL aliases for readability when joining tables.
- If the question is ambiguous, make a reasonable assumption.

Database Schema:
{schema_context}
"""


def _build_schema_context(schema: TableSchema) -> str:
    """Convert a TableSchema into a human-readable string for the LLM prompt.

    Args:
        schema: Mapping of table names to their column definitions.

    Returns:
        A formatted string describing all tables and columns.
    """
    lines: list[str] = []
    for table, columns in schema.items():
        col_parts: list[str] = []
        for col in columns:
            flags: list[str] = []
            if col.primary_key:
                flags.append("PK")
            if not col.nullable:
                flags.append("NOT NULL")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            col_parts.append(f"  - {col.name} ({col.type}){flag_str}")
        lines.append(f"Table: {table}")
        lines.extend(col_parts)
        lines.append("")
    return "\n".join(lines).strip()


def _clean_sql_response(raw: str) -> str:
    """Strip markdown code fences and leading/trailing whitespace from LLM output.

    Args:
        raw: Raw string returned by the OpenAI API.

    Returns:
        Cleaned SQL string.
    """
    cleaned = re.sub(r"^```(?:sql)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


class SQLGenerator:
    """Generates SQL SELECT statements from plain-English questions using OpenAI."""

    def __init__(self, config: AppConfig) -> None:
        """Initialise the generator with application configuration.

        Args:
            config: Application configuration including OpenAI API key and model settings.

        Raises:
            ConfigurationError: If the OpenAI API key is missing.
        """
        if not config.openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )
        self._config = config
        ssl_ctx = ssl.create_default_context(cafile=config.openai_cert_path)
        self._client = OpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            default_headers={"Authorization": f"Bearer {config.openai_api_key}"},
            http_client=httpx.Client(verify=ssl_ctx),
        )

    def generate_sql(
        self,
        question: str,
        schema: TableSchema,
        dialect: str = "MySQL",
    ) -> str:
        """Generate a SQL SELECT statement from a plain-English question.

        Args:
            question: The user's question in plain English.
            schema: Database schema providing table and column context.
            dialect: SQL dialect hint for the LLM (default: "MySQL").

        Returns:
            A valid SQL SELECT statement as a string.

        Raises:
            ValueError: If ``question`` is empty or whitespace-only.
            SQLGenerationError: If the OpenAI API call fails or returns no content.
        """
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        if not schema:
            raise ValueError("Schema cannot be empty — provide at least one table.")

        schema_context = _build_schema_context(schema)
        system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            dialect=dialect,
            schema_context=schema_context,
        )

        logger.debug("Sending question to OpenAI: %s", question)

        try:
            response = self._client.chat.completions.create(
                model=self._config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                max_completion_tokens=self._config.max_tokens,
                temperature=self._config.temperature,
            )
        except OpenAIError as exc:
            logger.error("OpenAI API error: %s", exc)
            raise SQLGenerationError(
                f"Failed to generate SQL — OpenAI API error: {exc}"
            ) from exc

        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message.content:
            raise SQLGenerationError("OpenAI returned an empty response.")

        sql = _clean_sql_response(choice.message.content)
        logger.debug("Generated SQL: %s", sql)
        return sql
