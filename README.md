# Eng2SQL — English to SQL Generator

[![CI/CD](https://github.com/your-org/eng2sql/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/your-org/eng2sql/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/your-org/eng2sql/actions/workflows/ci-cd.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Type a question in plain English. Get valid MySQL SQL, PostgreSQL SQL, or MongoDB MQL instantly.

---

## What It Does

**Eng2SQL** is a Streamlit application that translates plain-English questions into
MySQL `SELECT` statements, PostgreSQL `SELECT` statements, or MongoDB MQL queries
using OpenAI GPT-5.2. Choose MySQL, PostgreSQL, or
MongoDB via the sidebar radio, connect to your server, pick a database from the
auto-discovered list, and ask your question — no SQL or MQL knowledge required.

| Capability             | Details                                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------------------------- |
| **DB type selector**   | Sidebar radio to switch between MySQL, PostgreSQL, and MongoDB                                        |
| **Two-step connect**   | Step 1: connect to server → Step 2: pick database from dropdown                                       |
| **MongoDB URI mode**   | Paste a full `mongodb://` or `mongodb+srv://` URI; enter credentials separately                       |
| **PostgreSQL sslmode** | Sidebar selector for `disable`/`allow`/`prefer`/`require`/`verify-ca`/`verify-full` (psycopg3 driver) |
| **Auto-detection**     | MySQL/PostgreSQL: SQLAlchemy `inspect()`; MongoDB: collection sampling with type inference            |
| **SQL generation**     | OpenAI GPT-5.2 translates English questions into MySQL/PostgreSQL `SELECT` or MongoDB MQL             |
| **SQL execution**      | Run the generated SQL against your MySQL or PostgreSQL database and view results in-app               |

### Example

> *"Show me the top 10 customers by total order value"*

```sql
SELECT
    c.id,
    c.first_name,
    c.last_name,
    SUM(o.total_amount) AS total_order_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.first_name, c.last_name
ORDER BY total_order_value DESC
LIMIT 10;
```

---

## Quick Start

### Option A — Docker (Recommended)

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
docker-compose up
```

Open **http://localhost:8501**

### Option B — Local Python

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Recommended (installs all runtime + DB drivers + dev/test tools):
pip install -e ".[dev,db]"

# Or use the flat pin file (identical deps, for Docker / CI compatibility):
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

streamlit run src/app.py
```

---

## Project Structure

```
eng2sql/
├── src/
│   ├── app.py                  ← Streamlit entry point
│   ├── components/             ← UI components
│   ├── services/               ← Business logic
│   │   ├── sql_generator.py    ← OpenAI SQL / MQL generation
│   │   ├── schema_detector.py  ← Static YAML + live MySQL schema
│   │   ├── db_connector.py     ← SQLAlchemy connection & execution
│   │   ├── mongo_connector.py  ← pymongo connect + database listing
│   │   └── mongo_schema_detector.py ← MongoDB collection schema inference
│   ├── models/config.py        ← Dataclasses
│   └── utils/                  ← Exceptions, logging
├── tests/
│   ├── unit/                   ← Unit tests (mocked dependencies)
│   └── integration/            ← Integration tests (SQLite)
├── config/
│   └── database_config.yaml    ← Sample static schema
├── .github/
│   ├── copilot-instructions.md ← Multi-agent system instructions
│   ├── prompts/                ← Agent prompt files (00–10)
│   └── workflows/ci-cd.yml    ← GitHub Actions pipeline
├── Dockerfile
├── docker-compose.yml
└── PROJECT_PROGRESS.md         ← Live project board
```

---

## Multi-Agent Development System

This project uses a **GitHub Copilot multi-agent SDLC system**. Every role in the
development lifecycle has a dedicated prompt file:

| To do this…          | Use this prompt                                                   |
| -------------------- | ----------------------------------------------------------------- |
| Check project status | `@workspace #file:.github/prompts/00-orchestrator.prompt.md`      |
| Plan a sprint        | `@workspace #file:.github/prompts/01-scrum-master.prompt.md`      |
| Write epics          | `@workspace #file:.github/prompts/02-epic-writer.prompt.md`       |
| Write user stories   | `@workspace #file:.github/prompts/03-user-story-writer.prompt.md` |
| Design architecture  | `@workspace #file:.github/prompts/04-architect.prompt.md`         |
| Implement features   | `@workspace #file:.github/prompts/05-developer.prompt.md`         |
| Review code          | `@workspace #file:.github/prompts/06-code-reviewer.prompt.md`     |
| Write test cases     | `@workspace #file:.github/prompts/07-test-case-writer.prompt.md`  |
| Run & report tests   | `@workspace #file:.github/prompts/08-tester.prompt.md`            |
| Deploy               | `@workspace #file:.github/prompts/09-deployment-agent.prompt.md`  |
| DevOps / infra       | `@workspace #file:.github/prompts/10-devops.prompt.md`            |

Always start with the **Orchestrator** to find out what should happen next:

```
@workspace #file:.github/prompts/00-orchestrator.prompt.md
```

---

## 📚 Documentation

| Document                                                        | Description                                              |
| --------------------------------------------------------------- | -------------------------------------------------------- |
| [Multi-Agent SDLC Guide](docs/guides/multi-agent-sdlc-guide.md) | Step-by-step guide to using the Copilot agent system     |
| [User Guide](docs/guides/user-guide.md)                         | End-user guide — getting started, modes, troubleshooting |
| [Developer Guide](docs/guides/developer-guide.md)               | Architecture, API reference, contribution workflow       |
| [System Design](docs/architecture/system-design.md)             | Component diagrams, ADRs, API contracts                  |
| [Roadmap](docs/roadmap.md)                                      | Sprint plan and milestones                               |

---

## Running Tests

```bash
# All tests with coverage
pytest --cov=src --cov-report=term-missing

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v -m integration
```

---

## Environment Variables

| Variable             | Required | Default                            | Description                           |
| -------------------- | -------- | ---------------------------------- | ------------------------------------- |
| `OPENAI_API_KEY`     | ✅        | —                                  | Bearer token / API key                |
| `OPENAI_MODEL`       | ❌        | `gpt-5.2`                          | Model to use                          |
| `OPENAI_BASE_URL`    | ❌        | `https://gpt4ifx.icp.infineon.com` | OpenAI-compatible endpoint            |
| `OPENAI_CERT_PATH`   | ❌        | `cert/ca-bundle.crt`               | Path to CA bundle for TLS verify      |
| `OPENAI_MAX_TOKENS`  | ❌        | `500`                              | Max tokens in SQL response            |
| `OPENAI_TEMPERATURE` | ❌        | `0.1`                              | LLM temperature (low = deterministic) |
| `DB_HOST`            | ❌        | `localhost`                        | MySQL host (Live mode)                |
| `DB_PORT`            | ❌        | `3306`                             | MySQL port                            |
| `DB_USER`            | ❌        | —                                  | MySQL user                            |
| `DB_PASSWORD`        | ❌        | —                                  | MySQL password                        |
| `DB_NAME`            | ❌        | —                                  | Target database name                  |
| `STATIC_SCHEMA_PATH` | ❌        | `config/database_config.yaml`      | Static schema file                    |
| `LOG_LEVEL`          | ❌        | `INFO`                             | Logging level                         |

> **MongoDB**: Connection parameters (host, port, credentials, auth mechanism) are
> entered in the sidebar UI. No `.env` variables are required for MongoDB mode.
> Install `pymongo>=4.7` (included in `requirements.txt`).

---

## License

MIT — see [LICENSE](LICENSE).
