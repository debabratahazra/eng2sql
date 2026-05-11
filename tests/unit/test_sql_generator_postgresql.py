"""Unit tests for SQLGenerator dialect-specific prompt tips (US-047)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from models.config import AppConfig, SchemaColumn, TableSchema


@pytest.fixture
def fake_app_config() -> AppConfig:
    return AppConfig(
        openai_api_key="sk-test",
        openai_base_url="https://example.invalid",
        openai_cert_path="cert/ca-bundle.crt",
        model_name="gpt-test",
        max_tokens=100,
        temperature=0.0,
    )


@pytest.fixture
def schema() -> TableSchema:
    return {"users": [SchemaColumn(name="id", type="INT", nullable=False, primary_key=True)]}


def _capture_prompt(generator, schema, dialect: str) -> str:
    fake_msg = MagicMock()
    fake_msg.message.content = "SELECT 1"
    fake_response = MagicMock()
    fake_response.choices = [fake_msg]

    with patch.object(generator._client.chat.completions, "create", return_value=fake_response) as mock_create:
        generator.generate_sql("how many users", schema, dialect=dialect)
    system_prompt = mock_create.call_args.kwargs["messages"][0]["content"]
    return system_prompt


def test_postgresql_prompt_contains_dialect_tips(fake_app_config, schema):
    from services.sql_generator import SQLGenerator
    with patch("services.sql_generator.OpenAI"), patch("services.sql_generator.ssl.create_default_context"):
        gen = SQLGenerator(fake_app_config)
    prompt = _capture_prompt(gen, schema, dialect="PostgreSQL")
    assert "PostgreSQL" in prompt
    assert "ILIKE" in prompt
    assert "::" in prompt


def test_mysql_prompt_omits_postgres_tips(fake_app_config, schema):
    from services.sql_generator import SQLGenerator
    with patch("services.sql_generator.OpenAI"), patch("services.sql_generator.ssl.create_default_context"):
        gen = SQLGenerator(fake_app_config)
    prompt = _capture_prompt(gen, schema, dialect="MySQL")
    assert "MySQL" in prompt
    assert "ILIKE" not in prompt
    assert "PostgreSQL-specific" not in prompt
