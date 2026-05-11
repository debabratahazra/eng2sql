# US-056 — Sidebar sslmode `verify-*` pre-validation against CA bundle

**Sprint**: Sprint 11
**Source**: SPRINT-10-retro.md "What Could Be Improved" §6
**Points**: 2
**Owner**: Developer

## User Story

As a **user selecting `verify-ca` or `verify-full` sslmode** for PostgreSQL, I want the
sidebar to validate that a CA bundle is reachable **before** clicking Connect, so I see
a clear actionable warning instead of a cryptic libpq error after a long timeout.

## Acceptance Criteria

1. When PG Step 1 sslmode is `verify-ca` or `verify-full`, the sidebar checks for the
   presence of a CA bundle in this order:
   - `PGSSLROOTCERT` env var → file must exist
   - `~/.postgresql/root.crt` → file must exist
   - `certifi.where()` (if installed) → fallback
2. If none found, render a yellow warning with the exact text:
   "verify-ca/verify-full requires a CA bundle. Set the PGSSLROOTCERT env var or place
   one at ~/.postgresql/root.crt."
3. Connect button remains enabled (user can override) but the warning persists.
4. New AppTest test verifies the warning shows when sslmode=`verify-ca` and no CA file
   exists, and is absent when sslmode=`prefer` or `disable`.

## Definition of Done

- [x] CA-bundle resolution logic implemented in sidebar
- [x] Warning rendered correctly for verify-ca / verify-full
- [x] No warning for disable / allow / prefer / require
- [x] 2+ AppTest tests added
- [x] User guide updated with CA bundle setup instructions
- [x] CR-011 approved

## Status

✅ Done
