# Security Architecture — Eng2SQL

> **Last reviewed**: 2026-05-01
> **Reviewer**: Architect
> **Standard**: OWASP Top 10 (2021)

---

## Security Controls

### Secrets Management

- [x] `OPENAI_API_KEY` stored in `.env` only; loaded via `python-dotenv`; never committed
- [x] `.env` listed in `.gitignore`; `.env.example` committed with placeholder values
- [x] DB credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, etc.) stored in `.env`
- [x] No credentials appear in log output (logger uses `DEBUG` level for connection info; password never logged)
- [x] GitHub Actions uses repository secrets (`OPENAI_API_KEY`); secrets masked in logs
- [x] `cert/ca-bundle.crt` is a **public** CA certificate — safe to commit; no private keys tracked
- [x] `.gitignore` includes `*.key`, `*.pem`, `*.p12`, `*.pfx` — private key patterns blocked
- [x] `.pre-commit-config.yaml` includes `detect-private-key` hook — blocks accidental commits

### SQL Injection Prevention

- [x] Generated SQL is **read-only** — only SELECT statements are permitted
- [x] `DBConnector.execute_query()` enforces `sql.strip().upper().startswith("SELECT")`; raises `ValueError` for any other statement type
- [x] SQL passed to `sqlalchemy.text()` — not string-formatted with user data
- [x] User's English question never interpolated into SQL — the LLM generates SQL; user input is only the natural language question
- [x] DB user should be granted `SELECT` privilege only on the target database (documented in runbook)

> **Note on OWASP A03 (Injection)**: The primary injection vector is the LLM-generated SQL
> itself. Since only SELECT is permitted and results are displayed read-only, the blast
> radius of a prompt-injection attack is limited to data exfiltration, not modification.

### Transport Security

- [x] OpenAI API calls use HTTPS via corporate proxy (`https://gpt4ifx.icp.infineon.com`)
- [x] TLS verified using corporate CA bundle (`cert/ca-bundle.crt`) via `ssl.create_default_context(cafile=...)`
- [x] `httpx.Client(verify=ssl.SSLContext)` — SSL context object passed (not string path) for httpx ≥ 0.28 compatibility
- [x] MySQL connections use TCP; TLS can be enabled via `connect_args={"ssl": {...}}` in `DBConfig` (future hardening)

### Authentication & Authorisation

- [x] OpenAI API: Bearer token authentication (`Authorization: Bearer <token>`)
- [x] DB access: username/password via SQLAlchemy connection URL (URL-encoded via `urllib.parse.quote_plus`)
- [x] No user authentication in the app itself — single-user local tool (v1 scope)
- [ ] **Future**: Add Streamlit authentication for multi-user shared deployments

### Container Security

- [x] Docker image runs as non-root user (`appuser`) — `USER appuser` in Dockerfile
- [x] No privileged ports — app binds to port 8501
- [x] Base image: `python:3.11-slim` — minimal attack surface; no unnecessary system packages
- [x] `.env` file **not** copied into Docker image (excluded via `.dockerignore`)
- [x] Secrets passed at runtime via environment variables (`--env-file .env`)

### Dependency Security

- [x] `pip-audit -r requirements.txt` runs in CI; build fails on critical CVEs
- [x] `requirements.txt` pins exact versions for all dependencies
- [x] Dependency updates reviewed before merging (no automated Dependabot in v1)

---

## OWASP Top 10 (2021) Review

| #   | Category                                 | Risk                            | Mitigation                                                         |
| --- | ---------------------------------------- | ------------------------------- | ------------------------------------------------------------------ |
| A01 | Broken Access Control                    | Low — single-user tool; no auth | No multi-user roles in v1; document before sharing                 |
| A02 | Cryptographic Failures                   | Low                             | TLS enforced for all external calls; CA bundle verified            |
| A03 | Injection                                | Medium                          | SELECT-only enforcement; user input never interpolated into SQL    |
| A04 | Insecure Design                          | Low                             | Read-only DB access by design; schema detection is non-destructive |
| A05 | Security Misconfiguration                | Low                             | Non-root Docker user; minimal base image; secrets via env          |
| A06 | Vulnerable & Outdated Components         | Low                             | `pip-audit` in CI; exact version pins                              |
| A07 | Identification & Authentication Failures | N/A                             | No user login in v1                                                |
| A08 | Software & Data Integrity Failures       | Low                             | `pip-audit`; no `--no-verify` in git hooks                         |
| A09 | Security Logging & Monitoring Failures   | Medium                          | Logging present; no SIEM integration in v1 (Sprint 4 monitoring)   |
| A10 | Server-Side Request Forgery (SSRF)       | Low                             | No user-supplied URLs; DB host from form (restricted env)          |

---

## Known Risks & Accepted Limitations (v1)

| Risk                                    | Severity | Accepted?                               | Mitigation / Future Work                            |
| --------------------------------------- | -------- | --------------------------------------- | --------------------------------------------------- |
| No app-level user authentication        | Medium   | ✅ Yes (single-user local tool)          | Add Streamlit auth before multi-user deployment     |
| LLM prompt injection via question field | Medium   | ✅ Yes (SELECT-only limits blast radius) | Add input sanitisation / output validation in v2    |
| MySQL traffic unencrypted by default    | Low      | ✅ Yes (internal network assumed)        | Enable `ssl_ca` in `connect_args` for production    |
| No rate limiting on SQL generation      | Low      | ✅ Yes (single user)                     | Add per-session throttling before public deployment |

---

## Security Checklist (Pre-Release)

- [x] `OPENAI_API_KEY` not in any committed file
- [x] `.env` in `.gitignore`
- [x] `detect-private-key` pre-commit hook active
- [x] `pip-audit` clean (zero critical CVEs)
- [x] Docker non-root user confirmed (`whoami` → `appuser`)
- [x] SQL execution restricted to SELECT statements
- [x] No passwords in log output
- [x] OWASP Top 10 reviewed and documented above
