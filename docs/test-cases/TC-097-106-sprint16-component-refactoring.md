# TC-097–104 — Test Cases: Sprint 16 Component Refactoring & Test Infrastructure

**Sprint**: 16  
**Epic**: EPIC-013 — Component Refactoring & Full-Stack Coverage  
**Author**: Test Case Writer Agent  
**Date**: 2025-07-14  

---

## TC-097 — Validate relational inputs: all fields present

**User Story**: US-071  
**Type**: Unit  
**Priority**: High  

**Given** valid host, user, password, and `admin_db=None`  
**When** `_validate_relational_inputs("localhost", "user", "pass", None)` is called  
**Then** the return value is `None` (no validation error)

---

## TC-098 — Validate relational inputs: missing required field

**User Story**: US-071  
**Type**: Unit  
**Priority**: High  

**Given** an empty host string  
**When** `_validate_relational_inputs("", "user", "pass", None)` is called  
**Then** the return value is a `("warning", …)` tuple with a message about filling in required fields

---

## TC-099 — Validate relational inputs: blank admin_db

**User Story**: US-071  
**Type**: Unit  
**Priority**: Medium  

**Given** valid host/user/password and `admin_db="   "` (whitespace only)  
**When** `_validate_relational_inputs("host", "u", "p", "   ")` is called  
**Then** the return value is a `("warning", …)` tuple mentioning admin DB

---

## TC-100 — Build relational config: field mapping

**User Story**: US-071  
**Type**: Unit  
**Priority**: High  

**Given** individual connection parameters  
**When** `_build_relational_config("host", 3306, "user", "pass", "db", "mysql", None)` is called  
**Then** the result is a `DBConfig` instance with all fields correctly assigned

---

## TC-101 — Format connect success: singular vs plural

**User Story**: US-071  
**Type**: Unit  
**Priority**: Medium  

**Given** `n=1` database found  
**When** `_format_connect_success("myhost", 1)` is called  
**Then** the result contains `"1 database found"` (not `"databases"`)

**Given** `n=3` databases found  
**When** `_format_connect_success("myhost", 3)` is called  
**Then** the result contains `"3 databases found"`

---

## TC-102 — Select default index: found and fallback

**User Story**: US-071  
**Type**: Unit  
**Priority**: Medium  

**Given** `available = ["alpha", "beta", "gamma"]` and `current = "beta"`  
**When** `_select_default_index(available, current)` is called  
**Then** the return value is `1`

**Given** `current` is not in `available`  
**When** `_select_default_index(available, "delta")` is called  
**Then** the return value is `0`

---

## TC-103 — Validate MongoDB fields: no_auth bypass

**User Story**: US-071  
**Type**: Unit  
**Priority**: High  

**Given** a valid host but empty username and password with `no_auth=True`  
**When** `_validate_mongo_fields_inputs("localhost", "", "", True)` is called  
**Then** the return value is `None` (credentials not required when no_auth is True)

---

## TC-104 — Sidebar smoke regression after refactor

**User Story**: US-071  
**Type**: Smoke  
**Priority**: High  

**Given** the Streamlit app loaded with `AppTest`  
**When** all existing sidebar smoke tests (TC-073–083, Sprint 15 set) are executed  
**Then** all 355 unit + smoke tests pass with zero failures

---

## TC-105 — test_sidebar_logic.py: all 34 tests pass

**User Story**: US-072  
**Type**: Unit  
**Priority**: High  

**Given** `tests/unit/test_sidebar_logic.py` containing 34 tests for 6 pure functions  
**When** executed via `pytest tests/unit/test_sidebar_logic.py -v`  
**Then** all 34 tests pass without importing Streamlit or requiring a Streamlit session

---

## TC-106 — pytest-xdist parallel run: all tests pass

**User Story**: US-074  
**Type**: Infrastructure  
**Priority**: Medium  

**Given** `pytest-xdist` installed and `-n auto` in `pyproject.toml` `addopts`  
**When** `pytest tests/unit` is executed (default configuration)  
**Then** 12 workers are spawned, 335 tests pass, wall-clock time < 60 s  
**And** no test order-dependency failures occur
