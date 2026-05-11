# US-083 — CI Pragma-Audit Check

**ID**: US-083  
**Epic**: EPIC-016  
**Sprint**: 19  
**Points**: 3  
**Status**: ✅ Done  
**Priority**: Medium

---

## User Story

As a **developer**, I want a CI or pre-commit check that flags any `# pragma: no cover`
annotation added without an adjacent justification comment, so that future contributors
cannot silently exclude code from coverage measurement.

---

## Background

Sprint 18 established the policy: every `# pragma: no cover` annotation must include
an inline or adjacent comment explaining why the line is architecturally unreachable.
This policy is currently enforced only by code review. An automated check would prevent
regressions if code review is skipped or the reviewer overlooks a new pragma.

---

## Acceptance Criteria

- [x] A `ruff` rule, `grep`-based pre-commit hook, or custom CI step checks that
  every line containing `# pragma: no cover` is preceded or followed by a comment
  containing the word "Excluded", "excluded", or "unreachable".
- [x] The check runs in CI (`.github/workflows/ci-cd.yml` lint or separate step).
- [x] The check passes on the current codebase (all existing pragmas have comments).
- [x] A test or smoke test verifies the check script exists and is runnable.

---

## Definition of Done

- [x] Code implemented (CI check added)
- [x] Unit/smoke tests written and passing
- [x] Code review approved
- [x] Developer guide updated
- [x] User story status set to ✅ Done
