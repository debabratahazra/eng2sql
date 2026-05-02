# ADR-002: OpenAI GPT-5.2 for SQL Generation

**Status**: Accepted
**Date**: 2026-05-01
**Deciders**: Architect

---

## Context

Eng2SQL must translate arbitrary English questions into valid MySQL SELECT statements for
any schema provided at runtime. The quality, schema-awareness, and reliability of this
translation is the core product value.

Options considered:

| Option                         | Pros                                                                                    | Cons                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **OpenAI GPT-5.2**             | State-of-the-art NL→SQL; handles complex joins and subqueries; reliable JSON/SQL output | API cost per query; requires network; rate limits                                |
| OpenAI GPT-4o                  | Proven SQL generation; well-tested                                                      | Slightly less capable than GPT-5.2 for complex queries                           |
| Local LLM (llama.cpp / Ollama) | No API cost; air-gapped                                                                 | Inferior SQL accuracy; requires GPU for adequate performance; complex deployment |
| Rule-based parser              | Deterministic; no API cost                                                              | Cannot handle ambiguous natural language; brittle maintenance                    |
| Text-to-SQL fine-tuned model   | Specialised; potentially lower cost                                                     | Fine-tuning pipeline required; schema-awareness limited without RAG              |

The deployment environment uses a **corporate OpenAI-compatible proxy** at
`https://gpt4ifx.icp.infineon.com` with Bearer token authentication and a custom CA
certificate (`cert/ca-bundle.crt`). This endpoint supports the standard OpenAI Chat
Completions API.

## Decision

Use **OpenAI GPT-5.2** accessed via the corporate proxy endpoint, authenticated with
a Bearer token (`OPENAI_API_KEY` env var). The `openai` Python SDK is used with:

- `base_url = "https://gpt4ifx.icp.infineon.com"`
- Custom `httpx.Client(verify=ssl.SSLContext)` for CA bundle TLS verification
- `default_headers = {"Authorization": f"Bearer {api_key}"}`
- `temperature = 0.1` (near-deterministic SQL output)
- `max_tokens = 500` (sufficient for complex SELECT statements)

A structured system prompt (`_SYSTEM_PROMPT_TEMPLATE` in `sql_generator.py`) includes
the full schema context (tables, columns, types) so the model generates schema-aware SQL.

## Consequences

### Positive
- Best-in-class NL→SQL accuracy for complex multi-table queries
- Handles ambiguous questions gracefully (asks for clarification context in prompt)
- Markdown code fences stripped automatically; raw SQL returned
- Corporate proxy provides audit trail and rate-limit governance

### Negative
- API latency: P95 < 5 s target; varies with proxy and model load
- `OPENAI_API_KEY` must be kept secret — stored only in `.env` / GitHub Actions secrets
- httpx `verify=ssl.SSLContext` (not string path) required for httpx ≥ 0.28 compatibility

### Neutral
- Model can be swapped by changing `AppConfig.model_name`; no other code change needed

## References
- `src/services/sql_generator.py`
- `src/models/config.py` — `AppConfig`
- EPIC-001: Core SQL Generation Engine
- ADR-005: YAML for static schema config (schema context source)
