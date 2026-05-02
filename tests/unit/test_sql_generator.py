"""Unit tests for the SQLGenerator service — TC-001 through TC-004."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from openai import OpenAIError

from models.config import AppConfig, SchemaColumn
from services.sql_generator import SQLGenerator, _build_schema_context, _clean_sql_response
from utils.exceptions import ConfigurationError, SQLGenerationError


# ── Helper / pure-function tests ─────────────────────────────────────────────

class TestBuildSchemaContext:
    """Tests for the schema context builder."""

    def test_includes_table_name(self, sample_schema):
        result = _build_schema_context(sample_schema)
        assert "customers" in result
        assert "orders" in result

    def test_includes_column_names(self, sample_schema):
        result = _build_schema_context(sample_schema)
        assert "email" in result
        assert "total" in result

    def test_marks_primary_keys(self, sample_schema):
        result = _build_schema_context(sample_schema)
        assert "PK" in result

    def test_empty_schema_returns_empty_string(self):
        result = _build_schema_context({})
        assert result == ""


class TestCleanSqlResponse:
    """Tests for the SQL response cleaner."""

    def test_strips_sql_code_fence(self):
        raw = "```sql\nSELECT * FROM customers;\n```"
        assert _clean_sql_response(raw) == "SELECT * FROM customers;"

    def test_strips_plain_code_fence(self):
        raw = "```\nSELECT 1;\n```"
        assert _clean_sql_response(raw) == "SELECT 1;"

    def test_passthrough_clean_sql(self):
        sql = "SELECT id, name FROM customers WHERE id = 1;"
        assert _clean_sql_response(sql) == sql

    def test_strips_whitespace(self):
        assert _clean_sql_response("  SELECT 1;  ") == "SELECT 1;"


# ── SQLGenerator class tests ──────────────────────────────────────────────────

class TestSQLGenerator:
    """Tests for SQLGenerator.generate_sql — TC-001 through TC-004."""

    def test_raises_configuration_error_if_no_api_key(self):
        """ConfigurationError raised when API key is empty."""
        config = AppConfig(openai_api_key="")
        with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
            SQLGenerator(config)

    def test_generates_select_for_simple_question(
        self, app_config, sample_schema, mock_openai_success
    ):
        """TC-001: Simple English → SELECT SQL returned."""
        generator = SQLGenerator(app_config)
        sql = generator.generate_sql("Show all customers", sample_schema)
        assert sql.upper().startswith("SELECT")

    def test_schema_context_sent_to_openai(
        self, app_config, sample_schema, mock_openai_success
    ):
        """TC-002: Schema context is present in the messages sent to OpenAI."""
        generator = SQLGenerator(app_config)
        generator.generate_sql("Show all customers", sample_schema)

        call_kwargs = mock_openai_success.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        system_content = next(m["content"] for m in messages if m["role"] == "system")
        assert "customers" in system_content
        assert "orders" in system_content

    def test_raises_sql_generation_error_on_api_failure(
        self, app_config, sample_schema, mock_openai_error
    ):
        """TC-003: OpenAI API failure → SQLGenerationError raised."""
        generator = SQLGenerator(app_config)
        with pytest.raises(SQLGenerationError, match="OpenAI API error"):
            generator.generate_sql("Show all customers", sample_schema)

    def test_raises_value_error_on_empty_question(self, app_config, sample_schema):
        """TC-004: Empty question → ValueError raised."""
        with patch("services.sql_generator.OpenAI"):
            generator = SQLGenerator(app_config)
        with pytest.raises(ValueError, match="empty"):
            generator.generate_sql("", sample_schema)

    def test_raises_value_error_on_whitespace_question(self, app_config, sample_schema):
        """TC-004 variant: whitespace-only question → ValueError raised."""
        with patch("services.sql_generator.OpenAI"):
            generator = SQLGenerator(app_config)
        with pytest.raises(ValueError, match="empty"):
            generator.generate_sql("   ", sample_schema)

    def test_raises_value_error_on_empty_schema(self, app_config):
        """ValueError raised when schema is empty."""
        with patch("services.sql_generator.OpenAI"):
            generator = SQLGenerator(app_config)
        with pytest.raises(ValueError, match="Schema cannot be empty"):
            generator.generate_sql("Show me data", {})

    def test_strips_markdown_fences_from_response(self, app_config, sample_schema):
        """SQL returned without markdown code fences."""
        with patch("services.sql_generator.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_choice = MagicMock()
            mock_choice.message.content = "```sql\nSELECT * FROM customers;\n```"
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[mock_choice]
            )
            generator = SQLGenerator(app_config)
            sql = generator.generate_sql("All customers", sample_schema)

        assert "```" not in sql
        assert sql == "SELECT * FROM customers;"

    def test_raises_on_empty_openai_response(self, app_config, sample_schema):
        """SQLGenerationError raised if OpenAI returns empty content."""
        with patch("services.sql_generator.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_choice = MagicMock()
            mock_choice.message.content = ""
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[mock_choice]
            )
            generator = SQLGenerator(app_config)
            with pytest.raises(SQLGenerationError, match="empty response"):
                generator.generate_sql("Show customers", sample_schema)

    @pytest.mark.parametrize(
        "question,expected_keyword",
        [
            ("Show all customers", "customers"),
            ("List all orders", "orders"),
            ("Get customer emails", "email"),
        ],
    )
    def test_generated_sql_references_schema_entities(
        self, app_config, sample_schema, question, expected_keyword
    ):
        """Parametrised: generated SQL contains expected schema keywords."""
        with patch("services.sql_generator.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_choice = MagicMock()
            mock_choice.message.content = f"SELECT * FROM {expected_keyword};"
            mock_client.chat.completions.create.return_value = MagicMock(
                choices=[mock_choice]
            )
            generator = SQLGenerator(app_config)
            sql = generator.generate_sql(question, sample_schema)

        assert expected_keyword in sql

    # ── BUG-003 regression tests ──────────────────────────────────────────────

    def test_uses_max_completion_tokens_not_max_tokens(
        self, app_config, sample_schema, mock_openai_success
    ):
        """BUG-003: API call must use max_completion_tokens, not max_tokens."""
        generator = SQLGenerator(app_config)
        generator.generate_sql("Show all customers", sample_schema)

        call_kwargs = mock_openai_success.chat.completions.create.call_args.kwargs
        assert "max_completion_tokens" in call_kwargs, (
            "max_completion_tokens must be passed to the OpenAI API"
        )
        assert "max_tokens" not in call_kwargs, (
            "max_tokens is deprecated and must not be passed to the OpenAI API"
        )
        assert call_kwargs["max_completion_tokens"] == app_config.max_tokens

    def test_unsupported_parameter_400_wrapped_as_sql_generation_error(
        self, app_config, sample_schema
    ):
        """BUG-003: HTTP 400 unsupported_parameter error is wrapped as SQLGenerationError."""
        from openai import BadRequestError
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": (
                    "Unsupported parameter: 'max_tokens' is not supported with "
                    "this model. Use 'max_completion_tokens' instead."
                ),
                "type": "invalid_request_error",
                "param": "max_tokens",
                "code": "unsupported_parameter",
            }
        }
        mock_response.request = MagicMock()
        mock_response.headers = {}

        with patch("services.sql_generator.OpenAI") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_client.chat.completions.create.side_effect = BadRequestError(
                message="Unsupported parameter: 'max_tokens'",
                response=mock_response,
                body={"error": {"code": "unsupported_parameter"}},
            )
            generator = SQLGenerator(app_config)
            with pytest.raises(SQLGenerationError, match="OpenAI API error"):
                generator.generate_sql("Show all customers", sample_schema)
