# ADR-007 — Widget-Component Pure-Helper Extraction Pattern

**Status**: Accepted  
**Date**: 2026-05-09  
**Sprint**: 19  
**Deciders**: Developer, Code Reviewer

---

## Context

Streamlit widget calls (`st.button`, `st.text_input`, `st.write`, etc.) can only execute
inside a live Streamlit render loop. The standard `pytest` environment has no Streamlit
runtime; running widget code in a test raises `StreamlitAPIException` or silently
no-ops, making direct testing impossible.

Starting in Sprint 15 the project reached **100% measured coverage** by annotating the
smallest possible blocks of genuinely-unreachable widget-call code with
`# pragma: no cover`. Sprint 16 extracted pure-logic helpers from `sidebar.py`
(`_validate_relational_inputs`, `_build_relational_config`, etc.) so that business logic
stayed testable even as rendering calls were excluded.

Sprint 19 (US-084) formalises this pattern as a project-wide ADR so that future
contributors know the expectation before adding logic to widget-heavy component files.

---

## Decision

> **Every piece of business logic inside a widget-heavy component must be extracted
> into a pure helper function before being implemented.**

A *pure helper* is defined as a module-level or class-level function that:

1. Accepts only plain Python types as arguments (strings, ints, lists, dataclasses).
2. Makes **no** calls to `st.*`, `st.session_state`, or any external I/O.
3. Returns a plain Python value.
4. Is independently unit-testable with `pytest` and `unittest.mock`.

The *rendering method* that calls the helper may remain under `# pragma: no cover`
because it contains only `st.*` delegation calls and no testable logic.

---

## Consequences

### Positive

* All business logic (validation, transformation, limiting) is unit-tested and
  measured by coverage — the `# pragma: no cover` scope stays minimal.
* Future contributors can add functionality without needing to run the full
  Streamlit app to exercise a logic branch.
* The pragma-audit CI check (`scripts/pragma_audit.py`) enforces that no
  `# pragma: no cover` annotation is added silently without a justification comment.

### Negative / Trade-offs

* Slightly more functions per component file; each helper must be documented.
* Module-level helpers in component files are technically part of the public API
  (importable). Use underscore-prefix naming (`_append_step`) to signal internal use.

---

## Alternatives Considered

### Alternative 1 — Use `AppTest` for full rendering coverage

`streamlit.testing.v1.AppTest` can exercise widget calls. However:

- AppTest tests must run sequentially (incompatible with `-n auto`, see
  [developer-guide.md AppTest + pytest-xdist Compatibility](../guides/developer-guide.md));
- They are slow (~2–5 s per test) and fragile when widget-tree indices shift;
- They do not provide line-level coverage for `st.*` internals.

*Verdict*: AppTest is used for smoke and rendering tests, not as a substitute for
pure-unit coverage of business logic.

### Alternative 2 — Mock `streamlit` at import time

Replacing `st` with `MagicMock()` before import allows widget-call code to execute
without a live Streamlit process. However:

- Mock patching is fragile and must be coordinated across every test that imports
  the component;
- Behaviour of mocked `st.status()` context managers differs from the real
  implementation, leading to false-passing tests;
- Coverage for mocked paths does not reflect real-world execution.

*Verdict*: Not recommended for ongoing use. The extraction pattern is more robust.

---

## Affected Files

| File                                 | Extraction status                         |
| ------------------------------------ | ----------------------------------------- |
| `src/components/sidebar.py`          | ✅ Fully extracted (Sprint 16 — US-071)    |
| `src/components/progress_tracker.py` | Widget-only today; extract if logic added |
| `src/components/query_input.py`      | Widget-only today; extract if logic added |
| `src/components/schema_viewer.py`    | Widget-only today; extract if logic added |
| `src/components/sql_output.py`       | Widget-only today; extract if logic added |

---

## References

- [US-071 — Sidebar refactor: extract pure-logic functions](../user-stories/sprint-16/US-071-sidebar-logic-extraction.md)
- [US-072 — Unit tests for extracted sidebar logic](../user-stories/sprint-16/US-072-sidebar-logic-tests.md)
- [US-084 — Widget-component pure-helper extraction guideline](../user-stories/sprint-19/US-084-widget-extraction-guideline.md)
- [developer-guide.md — Widget-Component Extraction Guideline section](../guides/developer-guide.md)
- [scripts/pragma_audit.py](../../scripts/pragma_audit.py)
