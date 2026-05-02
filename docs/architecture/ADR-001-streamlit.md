# ADR-001: Streamlit as UI Framework

**Status**: Accepted
**Date**: 2026-05-01
**Deciders**: Architect

---

## Context

Eng2SQL needs a web UI that lets non-technical users type English questions and receive
SQL output. The team is Python-only; there is no frontend engineer. The UI must support
text input, progress indicators, code-highlighted output, and a sidebar form — all with
minimal code.

Options considered:

| Option          | Pros                                                                                              | Cons                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **Streamlit**   | Python-native, zero HTML/JS, rapid iteration, `st.code` syntax highlight, `st.dataframe` built-in | Not suited for SPAs or heavy client-side logic; limited layout control |
| Flask + Jinja2  | Full control over HTML                                                                            | Requires HTML/CSS/JS knowledge; much more boilerplate                  |
| FastAPI + React | Production-grade SPA                                                                              | Requires two codebases (Python + JS); excessive for this scope         |
| Gradio          | Even simpler than Streamlit                                                                       | Less flexible layout; smaller ecosystem                                |

## Decision

Use **Streamlit 1.35+** as the sole UI framework. All UI components are implemented as
Python classes under `src/components/`. Business logic stays in `src/services/`; components
only handle rendering and `st.session_state` manipulation.

## Consequences

### Positive
- Zero frontend code — entire codebase is Python
- Built-in widgets (`st.text_area`, `st.status`, `st.code`, `st.dataframe`) match all
  requirements exactly
- Hot-reload during development (`streamlit run src/app.py`)
- Easy Docker packaging — single `streamlit` process, port 8501

### Negative
- Streamlit re-runs the entire script on every user interaction (top-to-bottom execution
  model) — requires careful `st.session_state` management
- UI end-to-end testing requires `streamlit.testing.v1.AppTest` (deferred to BUG-001 /
  Sprint 3 follow-up)
- Not suitable if the app needs complex client-side routing or WebSockets in the future

### Neutral
- Streamlit Cloud is not used; the app is self-hosted via Docker

## References
- [Streamlit docs](https://docs.streamlit.io)
- EPIC-002: Streamlit UI — Basic Query Interface
- EPIC-003: Dynamic Schema Detection (sidebar form, schema viewer)
