"""Shared pytest fixtures for all Eng2SQL tests."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Generator
from unittest.mock import MagicMock, patch

from models.config import AppConfig, DBConfig, SchemaColumn, TableSchema


# ── Schema fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def sample_schema() -> TableSchema:
    """A minimal e-commerce schema for unit tests."""
    return {
        "customers": [
            SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
            SchemaColumn(name="name", type="VARCHAR(100)", nullable=False),
            SchemaColumn(name="email", type="VARCHAR(200)", nullable=True),
        ],
        "orders": [
            SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
            SchemaColumn(name="customer_id", type="INT", nullable=False),
            SchemaColumn(name="total", type="DECIMAL(10,2)", nullable=False),
            SchemaColumn(name="status", type="VARCHAR(20)", nullable=False),
            SchemaColumn(name="created_at", type="DATETIME", nullable=False),
        ],
    }


@pytest.fixture
def sample_db_config() -> DBConfig:
    """Sample database configuration for unit tests (never connects to real DB)."""
    return DBConfig(
        host="localhost",
        port=3306,
        user="test_user",
        password="test_pass",
        database="test_db",
    )


# ── App config fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def app_config() -> AppConfig:
    """App configuration with a dummy API key for unit tests."""
    return AppConfig(
        openai_api_key="sk-test-0000000000000000000000000000000000000000",
        openai_base_url="https://gpt4ifx.icp.infineon.com",
        openai_cert_path="cert/ca-bundle.crt",
        model_name="gpt-5.2",
        max_tokens=500,
        temperature=0.1,
    )


# ── OpenAI mock fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def mock_openai_success():
    """Mock OpenAI client that returns a valid SELECT statement."""
    with patch("services.sql_generator.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "SELECT * FROM customers;"
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[mock_choice]
        )
        yield mock_client


@pytest.fixture
def mock_openai_error():
    """Mock OpenAI client that raises an OpenAIError."""
    from openai import OpenAIError

    with patch("services.sql_generator.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = OpenAIError("API unavailable")
        yield mock_client


# ── SQLite in-memory engine fixtures ─────────────────────────────────────────

@pytest.fixture(scope="session")
def sqlite_engine() -> Generator[Engine, None, None]:
    """An in-memory SQLite engine with sample tables for integration tests."""
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                total REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            INSERT INTO customers VALUES (1, 'Alice Smith', 'alice@example.com'),
                                         (2, 'Bob Jones', 'bob@example.com')
        """))
        conn.execute(text("""
            INSERT INTO orders VALUES (1, 1, 99.99, 'delivered', '2026-01-01 10:00:00'),
                                       (2, 2, 149.50, 'pending', '2026-01-02 12:00:00')
        """))
        conn.commit()
    yield engine
    engine.dispose()
