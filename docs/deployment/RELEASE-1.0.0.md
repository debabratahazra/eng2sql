# Release v1.0.0 — Sprint 1: Foundation

**Date**: 2026-05-01
**Type**: Major (initial release)
**Sprint**: Sprint 1 — Foundation

---

## What's New

### Core SQL Generation (EPIC-001)

- **US-001 — Static Schema Configuration**: Bundled e-commerce schema loaded from
  `config/database_config.yaml` (customers, products, categories, orders, order_items,
  reviews). No database connection required in Static mode.

- **US-002 — OpenAI SQL Generation Service**: `SQLGenerator` service translates plain-
  English questions into MySQL `SELECT` statements using OpenAI GPT-5.2 via a custom
  corporate endpoint (`https://gpt4ifx.icp.infineon.com`) with TLS verification against
  a CA bundle (`cert/ca-bundle.crt`) and Bearer token authentication.

- **US-003 — Prompt Engineering**: System prompt injects full schema context (table names,
  column names, types, constraints) to maximise SQL accuracy.

### Streamlit UI Shell (EPIC-002)

- **US-004 — App Shell**: Streamlit single-page application at `src/app.py` with sidebar
  mode selector and session state management.

- **US-005 — Query Input Component**: English-language text area with "⚡ Generate SQL"
  button and input validation.

- **US-006 — Step-by-Step Progress Display**: Four-step progress indicator showing
  real-time generation status (Load schema → Build prompt → Generate SQL → Done).

- **US-007 — SQL Output Panel**: Syntax-highlighted SQL output block with copy-to-clipboard
  affordance and "🗑️ Clear" reset button.

---

## Bug Fixes

- **BUG-002** (Fixed): `ResourceWarning: unclosed database connection` in SQLite test
  fixtures — all `Engine` objects now properly disposed in test teardown.

---

## Known Issues / Open Bugs

- **BUG-001** (Open — Sprint 3): Overall test coverage is 45% due to Streamlit UI
  components (`src/app.py`, `src/components/`) having 0% coverage. Service-layer coverage
  is ~92%. UI coverage will be addressed in Sprint 3 using `streamlit.testing.v1.AppTest`.
  The coverage omit list in `pyproject.toml` excludes UI files until then.

---

## Breaking Changes

None — initial release.

---

## Deployment Instructions

### Docker (Recommended)

```bash
# 1. Pull the image
docker pull ghcr.io/your-org/eng2sql:1.0.0

# 2. Configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY at minimum

# 3. Start the stack
docker-compose up -d

# 4. Open the app
open http://localhost:8501
```

### Local Python

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
cp .env.example .env            # fill in OPENAI_API_KEY

streamlit run src/app.py
```

---

## Environment Variables

| Variable             | Required | Default                            | Description                             |
| -------------------- | -------- | ---------------------------------- | --------------------------------------- |
| `OPENAI_API_KEY`     | ✅        | —                                  | Bearer token for the OpenAI endpoint    |
| `OPENAI_MODEL`       | ❌        | `gpt-5.2`                          | Model name                              |
| `OPENAI_BASE_URL`    | ❌        | `https://gpt4ifx.icp.infineon.com` | Custom OpenAI-compatible base URL       |
| `OPENAI_CERT_PATH`   | ❌        | `cert/ca-bundle.crt`               | CA bundle path for TLS verification     |
| `OPENAI_MAX_TOKENS`  | ❌        | `500`                              | Maximum tokens in the SQL response      |
| `OPENAI_TEMPERATURE` | ❌        | `0.1`                              | LLM temperature (lower = deterministic) |
| `STATIC_SCHEMA_PATH` | ❌        | `config/database_config.yaml`      | Path to static schema YAML              |
| `LOG_LEVEL`          | ❌        | `INFO`                             | Application log level                   |

---

## Docker Image

| Tag            | Digest        | Notes              |
| -------------- | ------------- | ------------------ |
| `1.0.0`        | (built by CI) | Sprint 1 release   |
| `latest`       | → `1.0.0`     | Tracks `main`      |
| `sha-<commit>` | (built by CI) | Per-commit SHA tag |

Image: `ghcr.io/your-org/eng2sql`

---

## Changelog

```
2026-05-01  v1.0.0  Initial release — Sprint 1 Foundation
                    - SQLGenerator with GPT-5.2 and corporate endpoint
                    - Static schema from YAML
                    - Streamlit UI shell (query input, progress, SQL output)
                    - Docker + docker-compose stack
                    - GitHub Actions CI/CD pipeline (lint, test, build, publish)
                    - Fix BUG-002 (ResourceWarning in test fixtures)
```
