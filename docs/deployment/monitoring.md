# Eng2SQL — Monitoring & Observability

> **Last Updated**: 2026-05-01
> **Maintained by**: DevOps Agent

---

## Overview

Eng2SQL uses Python's standard `logging` module with structured output. All services
write to `stdout`/`stderr` so container orchestrators (Docker, ECS, ACA) can collect
logs without additional agents.

---

## Logging Strategy

### Log Level

Controlled by the `LOG_LEVEL` environment variable (default: `INFO`).

| Level      | Used for                                                           |
| ---------- | ------------------------------------------------------------------ |
| `DEBUG`    | Verbose internal state (DB connection string prefix, step timings) |
| `INFO`     | Normal application events (app start, schema loaded)               |
| `WARNING`  | Degraded state that doesn't stop execution                         |
| `ERROR`    | Recoverable errors (OpenAI API failure, DB connection refused)     |
| `CRITICAL` | Unrecoverable errors (config missing, cert not found)              |

### What Is (and Is Not) Logged

| Logged ✅                                 | Never logged ❌                      |
| ---------------------------------------- | ----------------------------------- |
| SQL generation success/failure           | `OPENAI_API_KEY` value              |
| Schema load events (table count)         | DB passwords                        |
| DB connection attempt (host + port only) | DB usernames (at INFO level)        |
| Exception tracebacks (at ERROR level)    | Full SQL result data (PII risk)     |
| App startup with Python version          | User's plain-English question (PII) |

> **Why `logger.debug` for DB user?** CR-001 downgraded `logger.info("Connecting as {user}")`
> to `logger.debug` to avoid leaking usernames to INFO-level log aggregators.

### Logger Setup

Logger is initialised in `src/utils/logger.py`:

```python
import logging, os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
        ))
        logger.addHandler(handler)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    return logger
```

For production, set `LOG_LEVEL=WARNING` to reduce noise, or `LOG_LEVEL=DEBUG` when
investigating issues.

---

## Health Check

| Endpoint                               | Method | Expected | Notes              |
| -------------------------------------- | ------ | -------- | ------------------ |
| `http://localhost:8501/_stcore/health` | GET    | `200 OK` | Streamlit built-in |
| `http://localhost:8501/`               | GET    | `200 OK` | Main UI page       |

Docker healthcheck (configured in `Dockerfile`):
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

The `app` service in `docker-compose.yml` has `restart: unless-stopped`, so Docker will
automatically restart the container if the health check fails three consecutive times.

---

## Key Metrics to Track

These are not yet instrumented (Sprint 3 / Sprint 4), but define the observability
targets:

| Metric                     | Type      | Target / Alert Threshold            |
| -------------------------- | --------- | ----------------------------------- |
| SQL generation latency     | Histogram | P95 < 5 s; P50 < 2 s                |
| OpenAI API error rate      | Counter   | Alert if > 5% over 5-minute window  |
| DB connection success rate | Gauge     | Alert if < 99% over 1-minute window |
| Schema detection latency   | Histogram | P95 < 500 ms                        |
| Streamlit active sessions  | Gauge     | Alert if > 50 (capacity planning)   |
| Container restart count    | Counter   | Alert if > 0 within 1 hour          |

### Future Instrumentation Options

- **Prometheus + Grafana**: Add `prometheus-fastapi-instrumentator` or a custom
  `prometheus_client` middleware. Expose `/metrics` on a secondary port.
- **OpenTelemetry**: Instrument `SQLGenerator.generate_sql()` and
  `DBConnector.execute_query()` with OTEL spans for distributed tracing.
- **Streamlit-native**: Use `st.experimental_memo` cache hit/miss events as a proxy
  for repeated identical queries.

---

## Structured Logging (Production Enhancement)

For log aggregators (Datadog, Splunk, AWS CloudWatch), switch to JSON format:

```python
import json, logging

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)
```

Enable by setting `LOG_FORMAT=json` (not yet wired — Sprint 4 DevOps task).

---

## Alerting (Future — Sprint 4)

| Alert                   | Channel              | Condition                                   |
| ----------------------- | -------------------- | ------------------------------------------- |
| High OpenAI error rate  | Slack `#eng2sql-ops` | Error rate > 5% over 5 minutes              |
| Container unhealthy     | PagerDuty (P2)       | Docker healthcheck fails 3× consecutively   |
| DB connection refused   | Slack `#eng2sql-ops` | `DatabaseConnectionError` in last 5 minutes |
| Deployment failure (CI) | Slack `#eng2sql-ci`  | GitHub Actions workflow `publish` fails     |

Alerting integration will be implemented in Sprint 4 DevOps. See
[EPIC-005](../epics/EPIC-005-deployment-devops.md) for scope.

---

## Dependency Security Audit

`pip-audit` runs in the CI pipeline on every push (`.github/workflows/ci-cd.yml`, `audit` job):

```bash
pip-audit -r requirements.txt --ignore-vuln PYSEC-2022-42969
```

### Manual Audit

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Dependabot (Future)

Add `.github/dependabot.yml` in Sprint 4 to schedule weekly pip dependency updates:

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
```

---

## Log Retention

| Environment  | Retention          | Tool                      |
| ------------ | ------------------ | ------------------------- |
| Local Docker | Container lifetime | `docker compose logs`     |
| AWS ECS      | 30 days            | CloudWatch Logs log group |
| Azure ACA    | 30 days            | Log Analytics workspace   |

Configure log rotation in production to avoid unbounded disk usage.
