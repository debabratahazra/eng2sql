# EPIC-016 — Maintainability & Developer Experience

**ID**: EPIC-016  
**Created**: Sprint 18 Retro  
**Target Sprint**: 19  
**Status**: 🟡 In Progress  
**Priority**: Low

---

## Goal

Improve long-term maintainability of the project by adding a coverage badge to the
README, adding a CI pragma-audit check to prevent undocumented `# pragma: no cover`
additions, and establishing guidelines for future pure-logic extraction in
widget-heavy components.

---

## Background

Sprint 18 achieved 100% measured coverage via pragma annotations. The next maintenance
priority is:
1. Surfacing the achievement visually (README badge).
2. Preventing regression (automated pragma-justification audit).
3. Documenting the extraction pattern for future widget-heavy components.

---

## Acceptance Outcomes

- `README.md` has a live coverage badge linked to the CI coverage report.
- A CI or pre-commit check flags any `# pragma: no cover` without an adjacent
  justification comment.
- Developer guide documents the pure-helper extraction guideline for widget components.

---

## Stories

| Story  | Description                                               | Points |
| ------ | --------------------------------------------------------- | ------ |
| US-082 | Add coverage badge to README.md                           | 1      |
| US-083 | CI pragma-audit check                                     | 3      |
| US-084 | Extract-or-document guideline for widget-heavy components | 2      |

**Total**: 6 story points
