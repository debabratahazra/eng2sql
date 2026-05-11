# US-044: Add `psycopg[binary]` Dependency and Dialect-Aware `DBConfig`

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 2
**Priority**: Must Have
**Source**: PostgreSQL evaluation §3 (US-A) — promoted by Retro Analyzer

## User Story

> As a **developer**, I want `DBConfig` to support a `dialect` field and pick the
> correct SQLAlchemy URL scheme, so that the same connection model can serve both
> MySQL (`mysql+pymysql`) and PostgreSQL (`postgresql+psycopg`) without duplicating
> code.

## Acceptance Criteria

```gherkin
Feature: Dialect-aware DBConfig

  Scenario: MySQL DBConfig still produces a mysql+pymysql URL (backward compatibility)
    Given a DBConfig with dialect="mysql" (default)
    When connection_url is read
    Then it starts with "mysql+pymysql://"
    And it contains "?ssl=false"

  Scenario: PostgreSQL DBConfig produces a postgresql+psycopg URL
    Given a DBConfig with dialect="postgresql", sslmode="prefer"
    When connection_url is read
    Then it starts with "postgresql+psycopg://"
    And it contains "?sslmode=prefer"

  Scenario: PostgreSQL sslmode override is honoured
    Given a DBConfig with dialect="postgresql", sslmode="disable"
    When connection_url is read
    Then it contains "?sslmode=disable"

  Scenario: Invalid dialect rejected
    Given a DBConfig instantiated with dialect="oracle"
    Then a ValueError or TypeError is raised
```

## Technical Notes

- Add to `src/models/config.py`:
  - `dialect: Literal["mysql", "postgresql"] = "mysql"` (Pydantic / dataclass field).
  - `sslmode: Literal["disable","allow","prefer","require","verify-ca","verify-full"] | None = None`
    — only used when `dialect == "postgresql"`.
- URL builder dispatch:
  - `mysql` → `f"mysql+pymysql://{user}:{quote(pw)}@{host}:{port}/{db}?ssl=false"` (existing)
  - `postgresql` → `f"postgresql+psycopg://{user}:{quote(pw)}@{host}:{port}/{db}?sslmode={sslmode or 'prefer'}"`
- Add `psycopg[binary]>=3.2,<4` to `requirements.txt`.
- Drop `psycopg2-binary` if previously listed (it is not).

## Definition of Done

- [x] `DBConfig.dialect` and `sslmode` fields added with proper typing
- [x] URL builder dispatches on dialect
- [x] `psycopg[binary]>=3.2,<4` added to `requirements.txt`
- [x] 4+ unit tests in `tests/unit/test_config.py` covering the 4 scenarios above
- [x] Existing `DBConfig` MySQL tests still pass (zero regressions)
- [x] Code review CR-010 approved
- [x] Coverage on `models/config.py` ≥ 95 %

## Status

✅ Done
