"""Shared pytest fixtures for all Eng2SQL tests."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Generator
from unittest.mock import MagicMock, patch

from models.config import AppConfig, DBConfig, MongoConfig, SchemaColumn, TableSchema


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


# ── MongoDB fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def mongo_config() -> MongoConfig:
    """Sample MongoDB configuration for unit tests (never connects to real server)."""
    return MongoConfig(
        host="localhost",
        port=27017,
        username="test_user",
        password="test_pass",
        auth_source="admin",
        auth_mechanism="SCRAM-SHA-256",
    )


@pytest.fixture
def mongo_config_no_auth() -> MongoConfig:
    """MongoDB configuration with no-auth mode for unit tests."""
    return MongoConfig(
        host="localhost",
        port=27017,
        auth_mechanism="None / No Auth",
    )


# ── Docker-based MySQL integration fixture (US-042) ──────────────────────────

@pytest.fixture(scope="session")
def mysql_container() -> Generator[DBConfig, None, None]:
    """Spin up a real MySQL 8.0 container for integration tests.

    Skips the test (rather than failing) when:
    - The optional ``testcontainers`` package is not installed.
    - The Docker daemon is not running / not reachable.

    Yields:
        A :class:`DBConfig` pointing at the dynamically-mapped container port,
        ready to feed into :meth:`DBConnector.create_engine`.

    Notes:
        - Container is started **once per pytest session** (scope="session")
          to keep the integration suite under ~30 s of cold-start overhead.
        - The container is torn down automatically when the session ends.
        - All tests using this fixture should also be marked
          ``@pytest.mark.docker`` so they can be excluded from the default
          unit-test run with ``-m "not docker"``.
    """
    try:
        from testcontainers.mysql import MySqlContainer  # type: ignore[import-not-found]
    except ImportError:
        pytest.skip("testcontainers not installed — skipping Docker MySQL fixture")

    try:
        container = MySqlContainer(
            "mysql:8.0",
            username="testroot",
            password="testroot",
            dbname="testdb",
        )
        container.start()
    except Exception as exc:  # noqa: BLE001
        # DockerException, ConnectionError, etc. — collapse into a single skip
        pytest.skip(f"Docker not available — skipping Docker MySQL fixture: {exc}")

    try:
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(3306))
        yield DBConfig(
            host=host,
            port=port,
            user="testroot",
            password="testroot",
            database="testdb",
        )
    finally:
        try:
            container.stop()
        except Exception:  # noqa: BLE001
            pass


# -- Docker-based PostgreSQL integration fixture (EPIC-009 / US-048) ---------

@pytest.fixture(scope="session")
def postgres_container() -> Generator[DBConfig, None, None]:
    """Spin up a real PostgreSQL 16 container for integration tests.

    Skip semantics mirror :func:`mysql_container`: skips when ``testcontainers``
    is not installed or the Docker daemon is unreachable.

    Yields:
        A :class:`DBConfig` pointing at the dynamically-mapped container port,
        with ``dialect="postgresql"`` so :meth:`DBConnector.create_engine`
        builds a ``postgresql+psycopg://`` URL.
    """
    try:
        from testcontainers.postgres import PostgresContainer  # type: ignore[import-not-found]
    except ImportError:
        pytest.skip("testcontainers[postgres] not installed - skipping Docker Postgres fixture")

    try:
        container = PostgresContainer(
            "postgres:16-alpine",
            username="testroot",
            password="testroot",
            dbname="testdb",
        )
        container.start()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Docker not available - skipping Docker Postgres fixture: {exc}")

    try:
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(5432))
        yield DBConfig(
            host=host,
            port=port,
            user="testroot",
            password="testroot",
            database="testdb",
            dialect="postgresql",
            sslmode="disable",
        )
    finally:
        try:
            container.stop()
        except Exception:  # noqa: BLE001
            pass


# ── AppTest fixture investigation (US-077) ────────────────────────────────────
#
# FINDING: Module/session-scoped AppTest fixtures are UNSAFE for tests that
# mutate widget state or session_state.  Interactive tests (button clicks,
# radio changes, text input) leave dirty state in the AppTest instance, causing
# subsequent tests to see stale values and become order-dependent — a violation
# of the test-isolation requirement.
#
# SAFE USE: A module-scoped fixture is acceptable ONLY for tests that call
# `at.run()` exactly once and make NO widget mutations.  These read-only checks
# save the ~1–2 s AppTest cold-start overhead when multiple checks operate on
# the same initial render.
#
# See docs/guides/developer-guide.md §"AppTest Fixture Scoping" for full
# analysis and timing benchmark.

@pytest.fixture(scope="module")
def initial_app_state():
    """Module-scoped AppTest snapshot of the app's initial render.

    **READ-ONLY — do not call click(), set_value(), or mutate session_state.**

    Safe for tests that only inspect the initial widget tree or session-state
    defaults.  Using this fixture for interactive tests will cause flaky,
    order-dependent failures.

    Returns:
        A fully-rendered :class:`~streamlit.testing.v1.AppTest` instance.
    """
    import pathlib
    from streamlit.testing.v1 import AppTest

    app_path = str(pathlib.Path(__file__).parent.parent / "src" / "app.py")
    at = AppTest.from_file(app_path, default_timeout=30)
    at.run()
    return at
