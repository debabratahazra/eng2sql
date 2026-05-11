#!/usr/bin/env python3
"""Pragma audit: every ``# pragma: no cover`` annotation must include a
justification comment or docstring within five lines.

This script enforces the policy established in Sprint 18 (US-083):

    Every ``# pragma: no cover`` annotation must be preceded or followed
    (within 5 lines) by a comment, docstring, or text containing one of the
    words: "Excluded", "excluded", "Unreachable", or "unreachable".

Exit codes:
    0 — all annotations are justified; audit passes.
    1 — at least one annotation lacks a justification; CI should fail.

Usage::

    python scripts/pragma_audit.py          # audits src/
    python scripts/pragma_audit.py src/     # explicit path (overrides default)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Keywords that count as a valid justification.
_KEYWORDS: tuple[str, ...] = ("Excluded", "excluded", "Unreachable", "unreachable")

# How many lines above/below the pragma line to search.
_WINDOW: int = 5

# Default source root relative to this script's parent directory.
_DEFAULT_SRC = Path(__file__).parent.parent / "src"


def _has_justification(lines: list[str], pragma_idx: int) -> bool:
    """Return True if any line within *_WINDOW* of *pragma_idx* contains a keyword."""
    start = max(0, pragma_idx - _WINDOW)
    end = min(len(lines), pragma_idx + _WINDOW + 1)
    context = "\n".join(lines[start:end])
    return any(kw in context for kw in _KEYWORDS)


def audit_file(path: Path, root: Path) -> list[str]:
    """Audit a single Python file for unjustified pragma annotations.

    Args:
        path: Absolute path to the Python source file.
        root: Project root used to build relative paths in messages.

    Returns:
        List of human-readable violation messages; empty when the file passes.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"{path}: could not read file — {exc}"]

    violations: list[str] = []
    for idx, line in enumerate(lines):
        if "# pragma: no cover" not in line:
            continue
        if not _has_justification(lines, idx):
            try:
                rel = path.relative_to(root)
            except ValueError:
                rel = path
            violations.append(
                f"{rel}:{idx + 1}: '# pragma: no cover' without justification "
                f"(no keyword within {_WINDOW} lines)"
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Optional argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code: 0 for pass, 1 for failures.
    """
    args = argv if argv is not None else sys.argv[1:]
    src_root = Path(args[0]).resolve() if args else _DEFAULT_SRC.resolve()
    project_root = src_root.parent

    if not src_root.exists():
        print(f"ERROR: source path '{src_root}' does not exist.", file=sys.stderr)
        return 1

    all_violations: list[str] = []
    files_checked = 0
    for py_file in sorted(src_root.rglob("*.py")):
        files_checked += 1
        all_violations.extend(audit_file(py_file, project_root))

    if all_violations:
        print("PRAGMA AUDIT FAILURES:", file=sys.stderr)
        for violation in all_violations:
            print(f"  {violation}", file=sys.stderr)
        print(
            f"\nEvery '# pragma: no cover' must be preceded or followed (within "
            f"{_WINDOW} lines) by a comment or docstring containing one of: "
            + ", ".join(f"'{kw}'" for kw in _KEYWORDS)
            + ".",
            file=sys.stderr,
        )
        print(
            f"\n{files_checked} file(s) checked — "
            f"{len(all_violations)} violation(s) found.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Pragma audit passed — {files_checked} file(s) checked, 0 violations."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
