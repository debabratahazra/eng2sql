# TC-119–TC-124: Sprint 18 — Final Coverage Perfection

**Sprint**: 18  
**Author**: Test Case Writer Agent  
**Related Stories**: US-079, US-081  

---

## TC-119: pragma: no cover on progress_tracker Methods

**Story**: US-079  
**Type**: Unit / Configuration  
**Priority**: High

### Scenario
```
Given src/components/progress_tracker.py has # pragma: no cover on def reset() and def update()
When pytest --cov=src is run
Then progress_tracker.py shows 0 missing statements
And the pragma annotations include justification comments
```

**Verification**: UTR-023 — 100% coverage, 0 miss

---

## TC-120: pragma: no cover on query_input Button-Click Block

**Story**: US-079  
**Type**: Unit / Configuration  
**Priority**: High

### Scenario
```
Given src/components/query_input.py has # pragma: no cover on if clicked:
When pytest --cov=src is run
Then query_input.py shows 0 missing statements
```

**Verification**: UTR-023 — 100% coverage, 0 miss

---

## TC-121: pragma: no cover on schema_viewer Empty-Schema Branch

**Story**: US-079  
**Type**: Unit / Configuration  
**Priority**: High

### Scenario
```
Given src/components/schema_viewer.py has # pragma: no cover on if not schema: and if st.button(...)
When pytest --cov=src is run
Then schema_viewer.py shows 0 missing statements
```

**Verification**: UTR-023 — 100% coverage, 0 miss

---

## TC-122: pragma: no cover on sidebar.py certifi Branch

**Story**: US-079  
**Type**: Unit / Configuration  
**Priority**: High

### Scenario
```
Given src/components/sidebar.py has # pragma: no cover on return certifi.where()
When pytest --cov=src is run
Then sidebar.py shows 0 missing statements
```

**Verification**: UTR-023 — sidebar.py 100%, 0 miss

---

## TC-123: Overall Coverage 100% After Pragmas

**Story**: US-079  
**Type**: Unit / Gate  
**Priority**: High

### Scenario
```
Given all pragma annotations are applied across 5 component files
When pytest tests/unit/ --cov=src is run
Then TOTAL coverage is 100%
And total missed statements is 0
And the coverage gate (fail_under = 80) passes
```

**Verification**: UTR-023 — TOTAL: 941 stmts, 0 miss, 100.00%

---

## TC-124: Developer Guide Contains xdist and Pragma Sections

**Story**: US-081  
**Type**: Documentation  
**Priority**: Medium

### Scenario
```
Given docs/guides/developer-guide.md has been updated
When the file is read
Then it contains "AppTest + pytest-xdist Compatibility" section
And it contains "Optional-Import # pragma: no cover Pattern" section
And the pragma section includes a table of current annotations
And the pragma section includes the annotation format with justification examples
```

**Verification**: US-081 DoD checkboxes all ticked; developer-guide.md verified
