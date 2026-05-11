# Test Cases TC-125 to TC-130 — Sprint 19: Maintainability & Developer Experience

**Sprint**: 19  
**Epic**: EPIC-016  
**Stories covered**: US-082, US-083, US-084  
**Date**: 2026-05-09

---

## TC-125 — README coverage badge present

**Story**: US-082  
**Type**: Documentation / Smoke  
**Priority**: Low

### Given / When / Then

```
Given the project README.md
When the file is read
Then a shields.io coverage badge URL (img.shields.io/badge/coverage-100%25) is present
And the badge text shows "100%"
And the badge has a green background indicator (brightgreen)
```

**Acceptance**: `grep -q "coverage-100%25-brightgreen" README.md`

---

## TC-126 — Pragma audit script exists and is runnable

**Story**: US-083  
**Type**: Functional  
**Priority**: Medium

### Given / When / Then

```
Given the project root
When scripts/pragma_audit.py is invoked with no arguments
Then it exits with code 0
And it prints "Pragma audit passed — N file(s) checked, 0 violations."
```

**Acceptance**: `python scripts/pragma_audit.py` returns 0

---

## TC-127 — Pragma audit detects unjustified pragma

**Story**: US-083  
**Type**: Functional  
**Priority**: Medium

### Given / When / Then

```
Given a temporary Python file containing:
    if foo:  # pragma: no cover
        pass
(with no adjacent justification comment)
When scripts/pragma_audit.py is run on that file
Then it exits with code 1
And the error output references the file name and line number
And the error output mentions "without justification"
```

**Acceptance**: `TestMain::test_fails_on_unjustified_pragma` ✅

---

## TC-128 — Pragma audit passes on real src/ (regression guard)

**Story**: US-083  
**Type**: Regression  
**Priority**: High

### Given / When / Then

```
Given the real src/ directory with 7 existing # pragma: no cover annotations
When scripts/pragma_audit.py is run on src/
Then it exits with code 0 (all annotations are justified)
```

**Acceptance**: `TestMain::test_real_src_directory_passes` ✅

---

## TC-129 — CI pragma-audit step present in ci-cd.yml

**Story**: US-083  
**Type**: Configuration  
**Priority**: Medium

### Given / When / Then

```
Given .github/workflows/ci-cd.yml
When the lint job steps are read
Then a step "Pragma audit" is present that runs python scripts/pragma_audit.py
```

**Acceptance**: `grep -q "pragma_audit.py" .github/workflows/ci-cd.yml`

---

## TC-130 — Widget-component extraction guideline documented

**Story**: US-084  
**Type**: Documentation  
**Priority**: Low

### Given / When / Then

```
Given docs/guides/developer-guide.md
When the file is read
Then a section "Widget-Component Extraction Guideline" is present
And it contains a worked example with _append_step pure helper
And it contains a pre-commit checklist
Given docs/architecture/ADR-007-widget-extraction-pattern.md
When the file is read
Then it exists and is non-empty
And it contains "Decision" and "Consequences" sections
```

**Acceptance**: grep confirms section headings; ADR-007 file exists with > 0 bytes
