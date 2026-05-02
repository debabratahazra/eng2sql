# Eng2SQL — Secrets Setup

> **Last Updated**: 2026-05-01
> **Maintained by**: DevOps Agent

---

## Overview

Eng2SQL uses environment variables for all secrets. Secrets are **never** stored in
source code or committed to version control. This document describes how to configure
secrets for each deployment context.

---

## GitHub Actions Secrets

Configure these in **Settings → Secrets and variables → Actions** on the repository.

| Secret Name           | Description                                         | Required for CI |
| --------------------- | --------------------------------------------------- | --------------- |
| `OPENAI_API_KEY`      | Bearer token for the corporate GPT-5.2 endpoint     | ✅ (test job)    |
| `DB_PASSWORD`         | MySQL password used in integration tests            | ❌ (SQLite used) |
| `MYSQL_ROOT_PASSWORD` | MySQL root password for docker-compose `db` service | ❌ (SQLite used) |

> **Note**: The CI test job uses `OPENAI_API_KEY=sk-test-placeholder` by default.
> The actual key is only required for end-to-end smoke tests (not currently in CI).
> The `GITHUB_TOKEN` secret is automatically provided by GitHub Actions — no manual
> configuration needed for GHCR push.

### How to Set a Secret

```bash
# Via GitHub CLI
gh secret set OPENAI_API_KEY --body "your-token-here"
gh secret set OPENAI_API_KEY < /path/to/key-file   # from file
```

Or navigate to:
`https://github.com/<org>/eng2sql/settings/secrets/actions` → **New repository secret**

---

## Local Development (`.env`)

```bash
cp .env.example .env
# Edit .env and fill in real values
```

**Required**:
```bash
OPENAI_API_KEY=<your-bearer-token>
```

**Optional** (all have working defaults):
```bash
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://gpt4ifx.icp.infineon.com
OPENAI_CERT_PATH=cert/ca-bundle.crt
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.1
STATIC_SCHEMA_PATH=config/database_config.yaml
LOG_LEVEL=INFO
```

**Live Database mode** (only needed when connecting to MySQL):
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=eng2sql_readonly
DB_PASSWORD=<db-password>
DB_NAME=your_database
```

> ⚠️ **Never commit `.env`**. It is listed in `.gitignore`. The `detect-private-key`
> pre-commit hook provides an extra guard.

---

## Docker Deployment

Pass secrets via the `.env` file:

```bash
cp .env.example .env
# fill in OPENAI_API_KEY and any DB credentials
docker compose up -d
```

`docker-compose.yml` reads all variables from `.env` automatically via the `env_file`
mechanism (or per-variable `${VAR:-default}` substitution).

---

## CA Bundle Certificate

The file `cert/ca-bundle.crt` is the corporate CA certificate used for TLS verification
against `https://gpt4ifx.icp.infineon.com`. It is:

- **Tracked in git** — it is a CA certificate (public), not a private key
- **Mounted read-only** into the container: `./cert:/app/cert:ro`
- **Never** replaced with a private key or PKCS12 bundle (those are `.gitignore`d)

To update the CA bundle:
1. Obtain the new `ca-bundle.crt` from your network team
2. Replace `cert/ca-bundle.crt`
3. Rebuild the Docker image

---

## Secret Rotation Procedure

### Rotate `OPENAI_API_KEY`

1. Generate a new token from your organisation's API key management portal.
2. Update the GitHub Actions secret:
   ```bash
   gh secret set OPENAI_API_KEY --body "new-token"
   ```
3. Update `.env` on all deployment hosts.
4. Restart the application container:
   ```bash
   docker compose up -d app
   ```
5. Verify the app is healthy:
   ```bash
   curl http://localhost:8501/_stcore/health
   ```
6. Revoke the old token in the API key management portal.

### Rotate DB credentials

1. Update the MySQL user password on the database server.
2. Update `.env` (`DB_PASSWORD`) on all deployment hosts.
3. Update the GitHub Actions secret `DB_PASSWORD` if used in CI.
4. Restart the application:
   ```bash
   docker compose up -d app
   ```

---

## Security Hardening Checklist

- [x] `.gitignore` includes `.env`, `*.key`, `*.pem`, `*.p12`, `__pycache__/`
- [x] Docker image runs as non-root user (`appuser`, UID 1001)
- [x] No privileged ports — app binds to port 8501
- [x] `detect-private-key` pre-commit hook enabled
- [x] `pip-audit` runs in CI on every push
- [ ] DB user has `SELECT`-only permissions in production (configure at DB level)
- [ ] HTTPS / TLS termination at load balancer in cloud deployment
- [ ] `OPENAI_API_KEY` stored in a secrets manager (Vault / AWS Secrets Manager / Azure Key Vault) for production
