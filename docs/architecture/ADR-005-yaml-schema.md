# ADR-005: YAML for Static Schema Configuration

**Status**: Accepted
**Date**: 2026-05-01
**Deciders**: Architect

---

## Context

EPIC-001 requires that the SQL generator can run without a live database connection,
using a pre-defined schema as context. Developers and power users need to be able to
define tables and columns in a human-readable, version-controllable format.

Options considered:

| Option | Human-readable | Version-controllable | Python parsing | Notes |
|--------|---------------|---------------------|----------------|-------|
| **YAML** | ✅ Excellent | ✅ Git-friendly | `PyYAML` / `yaml.safe_load` | Standard config format; widely understood |
| JSON | ✅ Good | ✅ | `json.load` | Verbose for nested structures; no comments |
| TOML | ✅ Good | ✅ | `tomllib` (stdlib 3.11+) | Less natural for nested list/dict schemas |
| Python dict (hardcoded) | ❌ Code change required | ❌ Mixes config with code | n/a | Anti-pattern |
| Database migration file | ✅ | ✅ | Complex parsing | Overkill for a static config |

## Decision

Use **YAML** at `config/database_config.yaml` loaded with `yaml.safe_load()`. The
schema format is:

```yaml
tables:
  customers:
    - name: id
      type: INT
      nullable: false
      primary_key: true
    - name: email
      type: VARCHAR(200)
      nullable: true
  orders:
    - name: id
      type: INT
      nullable: false
      primary_key: true
    - name: customer_id
      type: INT
      nullable: false
```

`SchemaDetector.load_static_schema()` parses this into a `TableSchema` dict of
`SchemaColumn` dataclass instances. The same `TableSchema` type is produced by
`detect_live_schema()`, ensuring the SQL generator's interface is identical in both modes.

`yaml.safe_load()` is used (not `yaml.load()`) to prevent arbitrary code execution from
maliciously crafted YAML files.

## Consequences

### Positive
- Human-readable; comments supported (`# this is a comment`)
- Git diff-friendly — changes are visible line-by-line in PRs
- `PyYAML` is a transitive dependency of many tools; minimal overhead
- Unified `TableSchema` type means static and dynamic modes are interchangeable

### Negative
- Manual updates required when the real schema changes (acceptable for v1 demo/prototyping)
- YAML indentation errors cause silent misparse — mitigated by `SchemaDetectionError`
  validation in `load_static_schema()`
- No schema validation schema (e.g. JSON Schema) enforced on the YAML file (future work)

### Neutral
- In Live Database mode, this file is ignored entirely; `detect_live_schema()` is used instead

## References
- `config/database_config.yaml`
- `src/services/schema_detector.py` — `load_static_schema()`
- `src/models/config.py` — `SchemaColumn`, `TableSchema`
- EPIC-001: Core SQL Generation Engine
- EPIC-003: Dynamic Schema Detection
