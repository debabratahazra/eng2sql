# US-017: Dockerfile & Docker Compose

**Epic**: EPIC-005
**Sprint**: Sprint 4
**Points**: 5
**Priority**: Must Have

## User Story

> As a **DevOps engineer**, I want a production-grade `Dockerfile` and `docker-compose.yml`
> so that the application and its MySQL dependency can be started with a single command
> (`docker-compose up`) in any environment.

## Acceptance Criteria

```gherkin
Feature: Dockerfile & Docker Compose

  Scenario: Docker image builds successfully
    Given the repository root contains a Dockerfile
    When "docker build -t eng2sql ." is run
    Then the image builds without errors
    And the image is based on python:3.11-slim
    And the app runs as a non-root user

  Scenario: Application starts via docker-compose
    Given docker-compose.yml defines "app" and "db" services
    When "docker-compose up -d" is run
    Then the Streamlit app is accessible at http://localhost:8501
    And the app container passes its health check within 30 seconds

  Scenario: Secrets passed via environment variables only
    Given .env.example lists all required variables
    When the container starts with those variables set
    Then no secrets appear in the image layers or environment dumps
    And OPENAI_API_KEY and DB credentials are consumed from env only

  Scenario: .env.example documents all required variables
    Given the project root contains .env.example
    When a developer copies it to .env and fills in values
    Then the application starts without configuration errors

  Scenario: Non-root user enforced
    Given the running container
    When "docker exec eng2sql whoami" is run
    Then the output is "appuser" (not "root")
```

## Technical Notes
- Base image: `python:3.11-slim`; multi-stage build not required for v1
- Non-root user: `RUN useradd -m appuser && chown -R appuser /app`
- Health check: `HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health`
- `docker-compose.yml` services: `app` (Streamlit), `db` (mysql:8.0)
- `cert/ca-bundle.crt` copied into image; never copy `.env` into image
- `EXPOSE 8501` declared; `CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]`

## Definition of Done
- [x] `Dockerfile` created with non-root user, health check, and correct CMD
- [x] `docker-compose.yml` created with `app` + `db` services and env_file reference
- [x] `.env.example` lists all variables: `OPENAI_API_KEY`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- [x] `docker build` completes without errors
- [x] `docker-compose up` starts Streamlit at `http://localhost:8501`
- [x] No secrets in image layers (verified via `docker history`)
- [x] Code review approved

## Status
✅ DONE
