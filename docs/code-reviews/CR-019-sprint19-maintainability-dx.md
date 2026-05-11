# CR-019 — Code Review: Sprint 19 — Maintainability & Developer Experience

**Sprint**: 19  
**Date**: 2026-05-09  
**Reviewer**: Code Reviewer Agent  
**Status**: ✅ Approved

---

## Scope

Sprint 19 stories reviewed:

| Story  | Title                                             | Verdict    |
| ------ | ------------------------------------------------- | ---------- |
| US-082 | Add coverage badge to README.md                   | ✅ Approved |
| US-083 | CI pragma-audit check                             | ✅ Approved |
| US-084 | Widget-component pure-helper extraction guideline | ✅ Approved |

---

## US-082: Coverage Badge

### Files Changed

- `README.md` — Codecov placeholder badge replaced with static shields.io badge

### Findings

**✅ PASS** — Badge URL `https://img.shields.io/badge/coverage-100%25-brightgreen`
correctly URL-encodes the `%` and displays "100%" with a green background.

**✅ PASS** — The badge link points to the CI workflow URL, which is a valid navigation
target for contributors.

**✅ PASS** — The existing CI badge is retained; the Codecov placeholder that pointed at
`your-org` (an unregistered organisation) is removed and replaced with a deterministic
static badge — no broken link.

**✅ PASS** — The Python badge and MIT licence badge are unchanged.

### No Issues

---

## US-083: CI Pragma-Audit Check

### Files Changed

- `scripts/pragma_audit.py` — new Python script (100 lines)
- `src/components/sidebar.py` — justification comment added before certifi pragma
- `.github/workflows/ci-cd.yml` — `pragma audit` step added to `lint` job
- `tests/unit/test_pragma_audit.py` — 18 unit tests

### Findings

**✅ PASS** — `pragma_audit.py` correctly implements the ±5-line window heuristic.
`_has_justification` is simple and readable; `audit_file` handles OSError gracefully.
`main()` accepts an optional `argv` parameter for testability (no `sys.argv` dependency
in tests). Exit codes 0/1 are correct.

**✅ PASS** — The certifi pragma in `sidebar.py` now has an adjacent justification
comment: `# Excluded: certifi is an optional runtime dep; unreachable in CI/tests...`
This satisfies both the audit script and the existing code-review policy.

**✅ PASS** — The CI step (`python scripts/pragma_audit.py`) runs inside the `lint` job
after mypy, ensuring all pragmas are justified before any code reaches the test step.

**✅ PASS** — 18 unit tests cover all three public functions (`_has_justification`,
`audit_file`, `main`), including a regression guard that runs the script against the
real `src/` directory. All 18 pass in 0.20 s.

**✅ PASS** — `pragma_audit.py` uses `from __future__ import annotations`, type hints
throughout, Google-style docstrings on every public function. PEP 8 compliant.

**✅ PASS** — Coverage gate: still 100.00% (941 stmts, 0 miss). `pragma_audit.py` is in
`scripts/` which is outside `src/`, so it does not affect coverage measurement.

### Minor Observations (Non-Blocking)

- `pragma_audit.py` does not yet have a `pyproject.toml` entry or `ruff` configuration.
  This is acceptable for Sprint 19; if the script grows it could be moved to a `tools/`
  package in a future sprint.

---

## US-084: Widget-Component Extraction Guideline

### Files Changed

- `docs/guides/developer-guide.md` — "Widget-Component Extraction Guideline" section appended
- `docs/architecture/ADR-007-widget-extraction-pattern.md` — new ADR

### Findings

**✅ PASS** — The developer-guide section includes:
1. The two-layer split table (pure helper vs rendering method)
2. A before/after worked example for `ProgressTracker`
3. A unit-test example that requires no Streamlit
4. A per-file status table
5. A pre-commit checklist linking to `pragma_audit.py`

**✅ PASS** — The worked example Python is syntactically and semantically correct.
`_append_step` is a well-designed pure function with a docstring.

**✅ PASS** — ADR-007 follows the project's ADR format (Context, Decision, Consequences,
Alternatives Considered, Affected Files, References). All cross-references (user stories,
developer-guide, `scripts/pragma_audit.py`) use correct relative paths.

**✅ PASS** — Both documents reference Sprint 16's `_validate_*`/`_build_*` pattern,
providing continuity for contributors reading the guide cold.

### No Issues

---

## Summary

All three Sprint 19 stories are approved. No blocking issues found.

| Metric       | Value                       |
| ------------ | --------------------------- |
| Unit tests   | 378 passed, 4 deselected    |
| Coverage     | 100.00% (941 stmts, 0 miss) |
| Pragma audit | 0 violations (21 files)     |
| Regressions  | None                        |
