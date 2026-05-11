#!/usr/bin/env python3
"""Eng2SQL Multi-Agent SDLC Pipeline Orchestrator.

Drives the full SDLC pipeline using the OpenAI API. Each agent phase is executed
in sequence; completed phases are automatically skipped based on output file presence.

Usage:
    # Run full pipeline from the beginning
    python scripts/run_pipeline.py

    # Check which phases still need running (no writes)
    python scripts/run_pipeline.py --check-only

    # Run a specific phase only
    python scripts/run_pipeline.py --phase 6

    # Dry-run (print prompts, call API, but do not write files)
    python scripts/run_pipeline.py --dry-run

Environment variables:
    OPENAI_API_KEY      Required. Bearer token for the OpenAI-compatible endpoint.
    OPENAI_BASE_URL     Optional. Defaults to https://gpt4ifx.icp.infineon.com
    PIPELINE_START_PHASE Optional. Start from this phase number (default: 1).
    DRY_RUN             Optional. Set to "true" to skip file writes.
"""
from __future__ import annotations

import argparse
import os
import re
import ssl
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx
from openai import OpenAI

# ── Constants ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
PROMPTS_DIR = ROOT / ".github" / "prompts"
DOCS_DIR = ROOT / "docs"
SRC_DIR = ROOT / "src"
TESTS_DIR = ROOT / "tests"

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.2")
MAX_TOKENS = int(os.environ.get("PIPELINE_MAX_TOKENS", "8000"))
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# ── File-output parser ────────────────────────────────────────────────────────
_FILE_RE = re.compile(r'<FILE path="([^"]+)">(.*?)</FILE>', re.DOTALL)
_FENCE_RE = re.compile(r"^```[a-z]*\n(.*?)```$", re.DOTALL | re.MULTILINE)


def parse_file_blocks(response: str) -> dict[str, str]:
    """Extract <FILE path="...">content</FILE> blocks from an LLM response."""
    files: dict[str, str] = {}
    for m in _FILE_RE.finditer(response):
        path, content = m.group(1).strip(), m.group(2).strip()
        # Strip outer markdown code fences if present
        fence = _FENCE_RE.match(content)
        files[path] = fence.group(1).strip() if fence else content
    return files


def write_files(files: dict[str, str]) -> list[str]:
    """Write parsed files to disk; return list of written paths."""
    written: list[str] = []
    if DRY_RUN:
        for path in files:
            print(f"  [DRY-RUN] Would write: {path}")
        return list(files.keys())
    for rel_path, content in files.items():
        target = ROOT / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  ✅ Written: {rel_path}")
        written.append(rel_path)
    return written


# ── OpenAI client factory ─────────────────────────────────────────────────────
def build_client() -> OpenAI:
    """Create an OpenAI client configured for the corporate proxy."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://gpt4ifx.icp.infineon.com")
    cert_path = ROOT / "cert" / "ca-bundle.crt"
    if cert_path.exists():
        ssl_ctx = ssl.create_default_context(cafile=str(cert_path))
        http_client: httpx.Client = httpx.Client(verify=ssl_ctx)
    else:
        http_client = httpx.Client()
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={"Authorization": f"Bearer {api_key}"},
        http_client=http_client,
    )


def call_api(client: OpenAI, system: str, user: str) -> str:
    """Call the OpenAI chat completions API and return the response text."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS,
    )
    return resp.choices[0].message.content or ""


# ── Context helpers ───────────────────────────────────────────────────────────
def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_dir(directory: Path, glob: str = "*.md") -> dict[str, str]:
    """Read all matching files from a directory; return {filename: content}."""
    result: dict[str, str] = {}
    if directory.exists():
        for f in sorted(directory.glob(glob)):
            result[f.name] = f.read_text(encoding="utf-8")
    return result


def prompt_file(name: str) -> str:
    return read(PROMPTS_DIR / name)


def progress() -> str:
    return read(ROOT / "PROJECT_PROGRESS.md")


def file_output_instructions() -> str:
    return (
        "\n\n## OUTPUT FORMAT\n"
        "Wrap EVERY file you create or modify in exactly this XML block:\n"
        '<FILE path="relative/path/from/repo/root/filename.ext">\n'
        "file content here\n"
        "</FILE>\n"
        "Use the repo-root-relative path (e.g. docs/epics/EPIC-001.md). "
        "Do not use code fences around the XML tags themselves. "
        "Produce ALL required files — do not truncate or summarise."
    )


# ── Phase readiness checks ────────────────────────────────────────────────────
def phase_complete(phase: int) -> bool:
    """Return True if the phase's required outputs already exist."""

    # Phase 0 — Retro Analysis: complete when every SPRINT-*-retro.md is recorded
    # as processed in PROJECT_PROGRESS.md.
    if phase == 0:
        retro_files = sorted((DOCS_DIR / "sprints").glob("SPRINT-*-retro.md"))
        if not retro_files:
            return True  # no retros exist yet → nothing to process
        progress_text = read(ROOT / "PROJECT_PROGRESS.md")
        for retro in retro_files:
            sprint_tag = retro.stem  # e.g. SPRINT-7-retro
            if f"Processed {sprint_tag}.md" not in progress_text:
                return False
        return True

    checks: dict[int, list[Path]] = {
        1: [DOCS_DIR / "epics" / f"EPIC-00{i}-{s}.md"
            for i, s in [(1, "core-sql-generation"), (2, "streamlit-ui"),
                         (3, "dynamic-schema"), (4, "quality-assurance"),
                         (5, "deployment-devops")]],
        2: list((DOCS_DIR / "user-stories" / "sprint-1").glob("US-*.md"))
           + list((DOCS_DIR / "user-stories" / "sprint-2").glob("US-*.md")),
        3: [DOCS_DIR / "architecture" / f
            for f in ["system-design.md", "ADR-001-streamlit.md",
                      "api-contracts.md", "security.md"]],
        4: [DOCS_DIR / "sprints" / "SPRINT-1.md",
            DOCS_DIR / "sprints" / "SPRINT-2.md"],
        5: [SRC_DIR / "services" / "sql_generator.py",
            SRC_DIR / "services" / "schema_detector.py",
            SRC_DIR / "services" / "db_connector.py",
            SRC_DIR / "app.py",
            TESTS_DIR / "unit" / "test_sql_generator.py"],
        6: list((DOCS_DIR / "code-reviews").glob("CR-*.md"))
           if (DOCS_DIR / "code-reviews").exists() else [],
        7: list((DOCS_DIR / "test-cases").glob("TC-*.md"))
           if (DOCS_DIR / "test-cases").exists() else [],
        8: list((DOCS_DIR / "test-results").glob("TR-*.md"))
           if (DOCS_DIR / "test-results").exists() else [],
        9: [ROOT / "Dockerfile",
            ROOT / "docker-compose.yml",
            DOCS_DIR / "deployment" / "runbook.md"],
        10: [ROOT / ".pre-commit-config.yaml",
             DOCS_DIR / "deployment" / "secrets-setup.md"],
    }
    required = checks.get(phase, [])
    if not required:
        return False
    return all(p.exists() and p.stat().st_size > 100 for p in required)


# ── Phase runners ─────────────────────────────────────────────────────────────
def run_phase_0(client: OpenAI) -> None:
    """Retro Analysis — seed next sprint from retrospective action items."""
    print("\n── Phase 0: Retro Analysis ───────────────────────────────────")
    retro_files = sorted((DOCS_DIR / "sprints").glob("SPRINT-*-retro.md"))
    if not retro_files:
        print("  ℹ️  No retro files found — skipping.")
        return

    progress_text = read(ROOT / "PROJECT_PROGRESS.md")
    unprocessed = [
        f for f in retro_files
        if f"Processed {f.stem}.md" not in progress_text
    ]
    if not unprocessed:
        print("  ✅ All retros already processed — skipping.")
        return

    print(f"  Found {len(unprocessed)} unprocessed retro(s): "
          f"{[f.name for f in unprocessed]}")

    # Build context: all existing IDs so the LLM can determine next numbers
    existing_epics = read_dir(DOCS_DIR / "epics")
    existing_bugs = read_dir(DOCS_DIR / "bug-reports")
    existing_stories: dict[str, str] = {}
    for sprint_dir in sorted((DOCS_DIR / "user-stories").glob("sprint-*")):
        existing_stories.update(read_dir(sprint_dir))
    existing_sprints = read_dir(DOCS_DIR / "sprints")

    retro_contents = "\n\n---\n\n".join(
        f"# {f.name}\n{f.read_text(encoding='utf-8')}" for f in unprocessed
    )

    system = (
        prompt_file("11-retro-analyzer.prompt.md")
        + "\n\n"
        + read(ROOT / ".github" / "instructions" / "retro-analyzer.instructions.md")
        + file_output_instructions()
    )
    user = (
        f"PROJECT_PROGRESS.md:\n{progress_text}\n\n"
        f"docs/roadmap.md:\n{read(DOCS_DIR / 'roadmap.md')}\n\n"
        f"Unprocessed retro files:\n{retro_contents}\n\n"
        f"Existing epic files: {list(existing_epics.keys())}\n"
        f"Existing user story files: {list(existing_stories.keys())}\n"
        f"Existing bug report files: {list(existing_bugs.keys())}\n"
        f"Existing sprint files: {list(existing_sprints.keys())}\n\n"
        "Process ALL unprocessed retro files listed above. For each one, create the "
        "required Bug Reports, User Stories, and/or Epics. Update docs/roadmap.md and "
        "PROJECT_PROGRESS.md. Follow all rules in the retro-analyzer instructions. "
        "Use sequential IDs that do not conflict with existing files."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_1(client: OpenAI) -> None:
    """Epic Writing."""
    print("\n── Phase 1: Epic Writing ─────────────────────────────────────")
    existing = read_dir(DOCS_DIR / "epics")
    system = prompt_file("02-epic-writer.prompt.md") + file_output_instructions()
    user = (
        f"Current PROJECT_PROGRESS.md:\n{progress()}\n\n"
        f"Existing epic files ({len(existing)} found):\n"
        + "\n---\n".join(f"# {k}\n{v}" for k, v in existing.items())
        + "\n\nCreate ALL missing epic files (EPIC-001 through EPIC-005). "
        "Skip any that already exist with complete content."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_2(client: OpenAI) -> None:
    """User Story Writing."""
    print("\n── Phase 2: User Story Writing ───────────────────────────────")
    epics = read_dir(DOCS_DIR / "epics")
    existing: list[str] = []
    for sprint_dir in sorted((DOCS_DIR / "user-stories").glob("sprint-*")):
        existing += [f.name for f in sprint_dir.glob("US-*.md")]
    system = prompt_file("03-user-story-writer.prompt.md") + file_output_instructions()
    user = (
        f"Epic files:\n" + "\n---\n".join(f"# {k}\n{v}" for k, v in epics.items())
        + f"\n\nAlready existing story files: {existing}\n\n"
        "Create ALL missing user story files (US-001 through US-020) in the correct "
        "sprint sub-directories. Skip any that already exist."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_3(client: OpenAI) -> None:
    """Architecture."""
    print("\n── Phase 3: Architecture ─────────────────────────────────────")
    stories = {}
    for sprint_dir in sorted((DOCS_DIR / "user-stories").glob("sprint-*")):
        stories.update(read_dir(sprint_dir))
    existing_arch = read_dir(DOCS_DIR / "architecture")
    system = prompt_file("04-architect.prompt.md") + file_output_instructions()
    user = (
        "User stories (selected):\n"
        + "\n---\n".join(f"# {k}\n{v}" for k, v in list(stories.items())[:10])
        + f"\n\nExisting architecture files: {list(existing_arch.keys())}\n\n"
        "Create all missing architecture files: system-design.md, ADR-001 through "
        "ADR-005, api-contracts.md, security.md."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_4(client: OpenAI) -> None:
    """Sprint Planning."""
    print("\n── Phase 4: Sprint Planning ──────────────────────────────────")
    existing_sprints = read_dir(DOCS_DIR / "sprints")
    system = prompt_file("01-scrum-master.prompt.md") + file_output_instructions()
    user = (
        f"PROJECT_PROGRESS.md:\n{progress()}\n\n"
        f"docs/roadmap.md:\n{read(DOCS_DIR / 'roadmap.md')}\n\n"
        f"Existing sprint files: {list(existing_sprints.keys())}\n\n"
        "Create all missing sprint plan files (SPRINT-1.md through SPRINT-4.md) "
        "and retrospective files (SPRINT-1-retro.md through SPRINT-4-retro.md). "
        "Also update docs/roadmap.md story statuses."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_5(client: OpenAI) -> None:
    """Development — generate source code and tests."""
    print("\n── Phase 5: Development ──────────────────────────────────────")
    arch = read_dir(DOCS_DIR / "architecture")
    stories: dict[str, str] = {}
    for sprint_dir in sorted((DOCS_DIR / "user-stories").glob("sprint-*")):
        stories.update(read_dir(sprint_dir))

    system = (
        prompt_file("05-developer.prompt.md")
        + "\n\n"
        + read(ROOT / ".github" / "instructions" / "developer.instructions.md")
        + file_output_instructions()
    )
    user = (
        "Architecture:\n"
        + "\n---\n".join(f"# {k}\n{v}" for k, v in arch.items())
        + "\n\nUser stories (Sprint 1 + 2):\n"
        + "\n---\n".join(f"# {k}\n{v}" for k, v in list(stories.items())[:12])
        + "\n\nGenerate ALL source files: src/models/config.py, src/utils/exceptions.py, "
        "src/utils/logger.py, src/services/sql_generator.py, "
        "src/services/schema_detector.py, src/services/db_connector.py, "
        "src/app.py, src/components/sidebar.py, src/components/query_input.py, "
        "src/components/sql_output.py, src/components/schema_viewer.py, "
        "src/components/progress_tracker.py, tests/conftest.py, "
        "tests/unit/test_sql_generator.py, tests/unit/test_schema_detector.py, "
        "tests/integration/test_db_connector.py. "
        "Follow Python 3.11+ standards, full type hints, Google docstrings."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_6(client: OpenAI) -> None:
    """Code Review."""
    print("\n── Phase 6: Code Review ──────────────────────────────────────")

    def _read_src(glob: str) -> dict[str, str]:
        return {f.relative_to(ROOT).as_posix(): f.read_text(encoding="utf-8")
                for f in sorted(ROOT.glob(glob)) if f.is_file()}

    src_files = _read_src("src/**/*.py")
    test_files = _read_src("tests/**/*.py")
    existing_reviews = read_dir(DOCS_DIR / "code-reviews")

    system = prompt_file("06-code-reviewer.prompt.md") + file_output_instructions()
    user = (
        "Source files to review:\n"
        + "\n---\n".join(f"# {k}\n```python\n{v}\n```" for k, v in src_files.items())
        + "\n\nTest files:\n"
        + "\n---\n".join(f"# {k}\n```python\n{v}\n```" for k, v in test_files.items())
        + f"\n\nExisting reviews: {list(existing_reviews.keys())}\n\n"
        "Produce a complete code review document at docs/code-reviews/CR-002-sprint2.md. "
        "If any issues require code fixes, produce the corrected source file as well."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_7(client: OpenAI) -> None:
    """Test Case Writing."""
    print("\n── Phase 7: Test Case Writing ────────────────────────────────")
    stories: dict[str, str] = {}
    for sprint_dir in sorted((DOCS_DIR / "user-stories").glob("sprint-*")):
        stories.update(read_dir(sprint_dir))
    existing_tc = read_dir(DOCS_DIR / "test-cases")

    system = prompt_file("07-test-case-writer.prompt.md") + file_output_instructions()
    user = (
        "User stories:\n"
        + "\n---\n".join(f"# {k}\n{v}" for k, v in stories.items())
        + f"\n\nExisting test case files: {list(existing_tc.keys())}\n\n"
        "Create test case documents for any uncovered user stories."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_8(client: OpenAI) -> None:
    """Tester — run actual tests and generate results document."""
    print("\n── Phase 8: Testing ──────────────────────────────────────────")
    if not DRY_RUN:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q",
             "--cov=src", "--cov-report=term-missing", "--cov-report=xml"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(SRC_DIR),
                 "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "sk-test")},
        )
        test_output = result.stdout + result.stderr
        exit_code = result.returncode
        print(test_output[-3000:])  # last 3000 chars
    else:
        test_output = "[DRY-RUN: tests not executed]"
        exit_code = 0

    system = prompt_file("08-tester.prompt.md") + file_output_instructions()
    user = (
        f"Test execution output (exit code {exit_code}):\n```\n{test_output}\n```\n\n"
        "Create a test results document at docs/test-results/TR-002-sprint-2.md "
        "summarising the results. If there are failures, also create bug report files "
        "in docs/bug-reports/."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)

    if exit_code != 0 and not DRY_RUN:
        print("⚠️  Tests failed — bug reports generated. Review docs/bug-reports/.")


def run_phase_9(client: OpenAI) -> None:
    """Deployment Agent."""
    print("\n── Phase 9: Deployment ───────────────────────────────────────")
    existing_deploy = read_dir(DOCS_DIR / "deployment")
    has_dockerfile = (ROOT / "Dockerfile").exists()
    has_compose = (ROOT / "docker-compose.yml").exists()

    system = prompt_file("09-deployment-agent.prompt.md") + file_output_instructions()
    user = (
        f"Existing deployment files: {list(existing_deploy.keys())}\n"
        f"Dockerfile exists: {has_dockerfile}\n"
        f"docker-compose.yml exists: {has_compose}\n\n"
        f"requirements.txt:\n{read(ROOT / 'requirements.txt')}\n\n"
        "Produce any missing files: Dockerfile, docker-compose.yml, .env.example, "
        "docs/deployment/RELEASE-1.0.0.md, docs/deployment/runbook.md. "
        "Also ensure .github/workflows/ci-cd.yml is complete."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


def run_phase_10(client: OpenAI) -> None:
    """DevOps."""
    print("\n── Phase 10: DevOps ──────────────────────────────────────────")
    existing_deploy = read_dir(DOCS_DIR / "deployment")
    has_precommit = (ROOT / ".pre-commit-config.yaml").exists()

    system = prompt_file("10-devops.prompt.md") + file_output_instructions()
    user = (
        f"Existing deployment docs: {list(existing_deploy.keys())}\n"
        f".pre-commit-config.yaml exists: {has_precommit}\n\n"
        f"Current .gitignore (last 30 lines):\n"
        f"{chr(10).join(read(ROOT / '.gitignore').splitlines()[-30:])}\n\n"
        "Produce any missing files: .pre-commit-config.yaml, "
        "docs/deployment/secrets-setup.md, docs/deployment/monitoring.md. "
        "Also produce an updated .gitignore with private key patterns."
    )
    response = call_api(client, system, user)
    files = parse_file_blocks(response)
    write_files(files)


# ── Phase registry ────────────────────────────────────────────────────────────
PHASES: dict[int, tuple[str, Any]] = {
    0:  ("Retro Analysis",      run_phase_0),
    1:  ("Epic Writing",        run_phase_1),
    2:  ("User Story Writing",  run_phase_2),
    3:  ("Architecture",        run_phase_3),
    4:  ("Sprint Planning",     run_phase_4),
    5:  ("Development",         run_phase_5),
    6:  ("Code Review",         run_phase_6),
    7:  ("Test Case Writing",   run_phase_7),
    8:  ("Testing",             run_phase_8),
    9:  ("Deployment",          run_phase_9),
    10: ("DevOps",              run_phase_10),
}


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Eng2SQL Multi-Agent Pipeline")
    parser.add_argument("--phase", type=int, help="Run a single phase only")
    parser.add_argument("--check-only", action="store_true",
                        help="Print phase status without running anything")
    parser.add_argument("--dry-run", action="store_true",
                        help="Call API but do not write files")
    args = parser.parse_args()

    global DRY_RUN
    if args.dry_run:
        DRY_RUN = True

    start_phase = int(os.environ.get("PIPELINE_START_PHASE", "0"))

    if args.check_only:
        print("\n── Pipeline Phase Status ─────────────────────────────────")
        for n in sorted(PHASES.keys()):
            name, _ = PHASES[n]
            status = "✅ COMPLETE" if phase_complete(n) else "🔲 PENDING"
            print(f"  Phase {n:2d}: {name:<25} {status}")
        return

    client = build_client()

    if args.phase:
        name, runner = PHASES[args.phase]
        print(f"\n🚀 Running Phase {args.phase}: {name}")
        runner(client)
        print(f"\n✅ Phase {args.phase} complete.")
        return

    print("\n🚀 Eng2SQL Full Pipeline Starting")
    print(f"   Start phase : {start_phase}")
    print(f"   Model       : {MODEL}")
    print(f"   Dry run     : {DRY_RUN}")
    print("─" * 60)

    completed: list[str] = []
    skipped: list[str] = []

    for n in sorted(k for k in PHASES if k >= start_phase):
        name, runner = PHASES[n]
        if phase_complete(n):
            print(f"\n⏭  Phase {n} ({name}): already complete — skipping")
            skipped.append(name)
            continue
        runner(client)
        completed.append(name)

    print("\n" + "═" * 60)
    print("🎉 Pipeline Complete")
    print(f"   Executed : {', '.join(completed) or 'none'}")
    print(f"   Skipped  : {', '.join(skipped) or 'none'}")
    print("═" * 60)


if __name__ == "__main__":
    main()
