# Eng2SQL — Deployment Runbook

> **Last Updated**: 2026-05-01
> **Version**: 1.0.0
> **Maintained by**: Deployment Agent / DevOps Agent

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Cloud Deployment Outline](#cloud-deployment-outline)
7. [Scaling Considerations](#scaling-considerations)
8. [Rollback Procedure](#rollback-procedure)
9. [Health Checks](#health-checks)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool           | Minimum Version | Notes                               |
| -------------- | --------------- | ----------------------------------- |
| Python         | 3.11+           | For local development               |
| Docker         | 24.0+           | For containerised deployment        |
| Docker Compose | 2.20+           | `docker compose` v2 syntax          |
| Git            | 2.40+           | For source checkout                 |
| OpenAI API key | —               | Bearer token for GPT-5.2 endpoint   |
| CA bundle      | —               | `cert/ca-bundle.crt` for TLS verify |

---

## Environment Variables

Copy `.env.example` to `.env` and populate before running.

| Variable              | Required | Default                            | Description                                |
| --------------------- | -------- | ---------------------------------- | ------------------------------------------ |
| `OPENAI_API_KEY`      | ✅        | —                                  | Bearer token for corporate OpenAI endpoint |
| `OPENAI_MODEL`        | ❌        | `gpt-5.2`                          | Model name                                 |
| `OPENAI_BASE_URL`     | ❌        | `https://gpt4ifx.icp.infineon.com` | Custom OpenAI-compatible base URL          |
| `OPENAI_CERT_PATH`    | ❌        | `cert/ca-bundle.crt`               | CA bundle path for TLS verification        |
| `OPENAI_MAX_TOKENS`   | ❌        | `500`                              | Maximum tokens in the SQL response         |
| `OPENAI_TEMPERATURE`  | ❌        | `0.1`                              | LLM temperature (lower = deterministic)    |
| `STATIC_SCHEMA_PATH`  | ❌        | `config/database_config.yaml`      | Path to static schema YAML file            |
| `LOG_LEVEL`           | ❌        | `INFO`                             | Application log level (`DEBUG`/`INFO`/…)   |
| `DB_HOST`             | ❌        | `localhost`                        | MySQL host (Live Database mode only)       |
| `DB_PORT`             | ❌        | `3306`                             | MySQL port                                 |
| `DB_USER`             | ❌        | —                                  | MySQL username                             |
| `DB_PASSWORD`         | ❌        | —                                  | MySQL password                             |
| `DB_NAME`             | ❌        | —                                  | Target database name                       |
| `MYSQL_ROOT_PASSWORD` | ❌        | —                                  | MySQL root password (docker-compose `db`)  |

> **Security**: Never commit `.env` to source control. Rotate `OPENAI_API_KEY` via your
> secrets manager if it is ever exposed.

---

## Local Development

### 1. Clone and set up the virtual environment

```bash
git clone https://github.com/your-org/eng2sql.git
cd eng2sql

python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
pre-commit install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set OPENAI_API_KEY at minimum
```

### 3. Run the application

```bash
streamlit run src/app.py
# Open http://localhost:8501
```

### 4. Run the test suite

```bash
# Unit + integration tests (coverage report)
python -m pytest tests/ --cov=src --cov-report=term-missing

# Lint and type check
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
```

---

## Docker Deployment

### Quick Start

```bash
cp .env.example .env            # fill in OPENAI_API_KEY
docker compose up               # foreground, Ctrl+C to stop
docker compose up -d            # detached (background)
```

Open **http://localhost:8501**.

### Build Locally

```bash
docker build -t eng2sql:local .
docker run -p 8501:8501 \
  --env-file .env \
  -v "$(pwd)/cert:/app/cert:ro" \
  -v "$(pwd)/config:/app/config:ro" \
  eng2sql:local
```

### Pull from GHCR

```bash
docker pull ghcr.io/your-org/eng2sql:1.0.0
docker pull ghcr.io/your-org/eng2sql:latest
```

### Full Stack (App + MySQL)

```bash
# Start both services
docker compose up -d

# Follow logs
docker compose logs -f app

# Stop and remove containers (data volumes preserved)
docker compose down

# Stop and REMOVE volumes (destroys MySQL data)
docker compose down -v
```

### Verify Container Health

```bash
docker compose ps              # STATUS should show (healthy)
curl http://localhost:8501/_stcore/health
```

---

## CI/CD Pipeline

The GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) runs on every push to
`main` / `develop` and on every pull request targeting `main`.

### Pipeline Stages

| Stage    | Job name  | Trigger              | Description                         |
| -------- | --------- | -------------------- | ----------------------------------- |
| 1. Lint  | `lint`    | every push / PR      | `ruff check`, `ruff format`, `mypy` |
| 2. Test  | `test`    | after lint           | pytest + coverage ≥ 80%             |
| 3. Audit | `audit`   | every push / PR      | `pip-audit` dependency scan         |
| 4. Docs  | `docs`    | every push / PR      | Validate guide files exist          |
| 5. Build | `build`   | after lint+test+docs | Docker build (no push)              |
| 6. Push  | `publish` | `main` push only     | Push image to GHCR                  |

### Coverage Gate

- **Measured scope**: `src/services/`, `src/models/`, `src/utils/` (service layer)
- **Excluded (Sprint 1–2)**: `src/app.py`, `src/components/*` — see BUG-001
- **Gate**: ≥ 80% (enforced by `[tool.coverage.report] fail_under = 80` in `pyproject.toml`)
- Sprint 3 will add Streamlit `AppTest` harness to cover UI layer

### Secrets Required

| Secret           | Where         | Notes                                                   |
| ---------------- | ------------- | ------------------------------------------------------- |
| `GITHUB_TOKEN`   | Auto-provided | Used to push to GHCR                                    |
| `OPENAI_API_KEY` | Repo secret   | Placeholder (`sk-test-placeholder`) used in CI test run |

---

## Cloud Deployment Outline

### AWS ECS (Fargate)

```
1. Push image to ECR (replace GHCR with ECR in publish job)
2. Create ECS cluster (Fargate)
3. Create Task Definition:
   - Image: <account>.dkr.ecr.<region>.amazonaws.com/eng2sql:1.0.0
   - CPU: 512 (0.5 vCPU), Memory: 1024 MB
   - Port mapping: 8501
   - Environment variables from AWS Secrets Manager / Parameter Store
   - Volume mount for cert/: use EFS mount or bake cert into image
4. Create ECS Service (desired count: 1–2)
5. Attach to Application Load Balancer on port 80/443
6. Configure Target Group health check: GET /_stcore/health → 200
```

### Azure Container Apps

```
1. Push image to Azure Container Registry (ACR)
2. Create Container App:
   az containerapp create \
     --name eng2sql \
     --resource-group <rg> \
     --image <acr>.azurecr.io/eng2sql:1.0.0 \
     --target-port 8501 \
     --ingress external \
     --env-vars OPENAI_API_KEY=secretref:openai-key \
                OPENAI_BASE_URL=https://gpt4ifx.icp.infineon.com
3. Set secrets via:
   az containerapp secret set --name eng2sql --secrets openai-key=<value>
4. Mount CA bundle via Azure Files volume (if not baked in image)
```

---

## Scaling Considerations

- **Streamlit sessions** are stateful (WebSocket per browser tab). Horizontal scaling
  requires sticky sessions (load-balancer affinity).
- **Stateless services** (`SQLGenerator`, `SchemaDetector`, `DBConnector`) scale without
  any shared state.
- **Cert bundle** should be mounted via a read-only volume or baked into the image at
  build time if deploying to a managed service without volume support.
- **MySQL Live mode**: Ensure the database user has `SELECT`-only privileges. Do not
  expose the `db` service container publicly.
- **Rate limiting**: OpenAI API calls are not rate-limited in the application; add a
  per-session throttle in Sprint 3 if needed.

---

## Rollback Procedure

### Docker Compose

```bash
# Re-tag the previous stable image as latest
docker tag ghcr.io/your-org/eng2sql:<previous-sha> ghcr.io/your-org/eng2sql:latest

# Redeploy
docker compose pull app
docker compose up -d app
```

### GitHub Actions

1. Identify the last passing run on `main` in **Actions → CI/CD Pipeline**.
2. Copy the `sha-<commit>` tag from that run.
3. Update `docker-compose.yml` `image:` to pin to that tag.
4. `git revert <bad-commit>` and push — CI will re-build and re-publish.

---

## Health Checks

| Endpoint                                   | Expected Response | Notes                          |
| ------------------------------------------ | ----------------- | ------------------------------ |
| `GET http://localhost:8501/_stcore/health` | `200 OK`          | Streamlit built-in healthcheck |
| `GET http://localhost:8501/`               | `200 OK` (HTML)   | Main app page                  |

Docker healthcheck is configured in the `Dockerfile`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

---

## Troubleshooting

### App container exits immediately

```bash
docker compose logs app
```
- Check `OPENAI_API_KEY` is set — app validates it on startup.
- Check cert file exists at the path specified in `OPENAI_CERT_PATH`.

### TLS verification failure (`SSLCertVerificationError`)

- Confirm `cert/ca-bundle.crt` is present and the volume mount is active:
  ```bash
  docker compose exec app ls -la /app/cert/
  ```
- Check `OPENAI_CERT_PATH` matches the file path inside the container.

### Coverage gate failing in CI

- Services-layer coverage should be ≥ 80% (BUG-001 excludes UI layer).
- Run locally: `python -m pytest tests/ --cov=src --cov-report=term-missing`
- If new service code is under-tested, add unit tests before pushing.

### MySQL container unhealthy

```bash
docker compose logs db
```
- Ensure `DB_PASSWORD` and `MYSQL_ROOT_PASSWORD` are set in `.env`.
- The `db` service has a 30-second start period; wait before checking health.
