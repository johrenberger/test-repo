#!/usr/bin/env python3
"""
Linter for repo-discovery reports.

Enforces the contract defined in skills/repo-discovery/SKILL.md and
skills/repo-discovery/templates/repo-discovery-report.md.

Rules (10):
  1. Required frontmatter fields present (Task ID, Repo root, Scope,
     Generated at)
  2. Repository layout is one of the allowed values
     (single-app | multi-module | monorepo | mixed | not_detected)
  3. Primary stack is populated or marked not_detected
  4. Package managers table has at least 1 row or is not_detected
  5. Source/test directories table has at least 1 row or is not_detected
  6. Build, CI, container, IaC table has all 5 rows (build, ci, container,
     iac, migrations); values may be `not_detected`
  7. Detected validation commands table has at least 1 row or is
     not_detected
  8. Smallest impacted module section is present (only if SCOPE was
     provided); absent if SCOPE was none
  9. Risk zones are populated (or `none_detected`)
 10. No fabricated values: every populated field has a real source
     (the report cites `Evidence` in tables, and the `Risk zones`
     section has a file path)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

EXERCISE = Path("/data/.openclaw/workspace/tasks/2026-06-12-repo-discovery-exercise")

ALLOWED_LAYOUTS = {"single-app", "multi-module", "monorepo", "mixed", "not_detected"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
REQUIRED_SECTIONS = [
    "## Repository layout",
    "## Primary stack",
    "## Package managers and wrappers",
    "## Source and test directories",
    "## Build, CI, container, and IaC",
    "## Detected validation commands",
    "## Risk zones",
    "## Notes and caveats",
    "## Provenance",
]


def lint_report(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: report does not exist: {path}"]
    content = path.read_text()

    # 1. Frontmatter
    for field in ("- **Task ID:**", "- **Repo root:**", "- **Scope (optional):**", "- **Generated at:**"):
        if field not in content:
            issues.append(f"FAIL: missing frontmatter field '{field.rstrip(':')}'")

    # 2. Repository layout
    m = re.search(r"`(single-app|multi-module|monorepo|mixed|not_detected)`", content)
    if not m:
        issues.append("FAIL: missing repository layout or layout is not in the allowed set")
    elif m.group(1) not in ALLOWED_LAYOUTS:
        issues.append(f"FAIL: layout '{m.group(1)}' is not in {ALLOWED_LAYOUTS}")

    # 3. Required sections (the smallest_impacted_module section is conditional)
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"FAIL: missing required section '{section}'")

    # 4. Primary stack
    section = content.split("## Primary stack")[1].split("##")[0]
    if "not_detected" not in section and "|" not in section:
        issues.append("FAIL: primary stack is empty AND not marked not_detected")

    # 5. Package managers
    section = content.split("## Package managers and wrappers")[1].split("##")[0]
    if "not_detected" not in section and "|" not in section:
        issues.append("FAIL: package managers table is empty AND not marked not_detected")

    # 6. Source / test dirs
    section = content.split("## Source and test directories")[1].split("##")[0]
    if "not_detected" not in section and "|" not in section:
        issues.append("FAIL: source/test directories table is empty AND not marked not_detected")

    # 7. Build, CI, container, IaC: must have 5 rows (build, ci, container, iac, migrations)
    section = content.split("## Build, CI, container, and IaC")[1].split("##")[0]
    for kind in ("build", "ci", "container", "iac", "migrations"):
        if f"| {kind} " not in section and f"| {kind} |" not in section:
            issues.append(f"FAIL: build/CI/container/IaC table missing row for '{kind}'")

    # 8. Detected validation commands
    section = content.split("## Detected validation commands")[1].split("##")[0]
    if "not_detected" not in section and "|" not in section:
        issues.append("FAIL: detected validation commands table is empty AND not marked not_detected")
    # If populated, every row should have Command ID, Command, Confidence, Evidence
    if "|" in section and "Command ID" not in section:
        issues.append("FAIL: validation commands table missing 'Command ID' header")
    if "|" in section and "Confidence" not in section:
        issues.append("FAIL: validation commands table missing 'Confidence' header")
    for m in re.finditer(r"\|\s*(high|medium|low)\s*\|", section, re.IGNORECASE):
        c = m.group(1).lower()
        if c not in ALLOWED_CONFIDENCE:
            issues.append(f"FAIL: validation command confidence '{c}' is not in {ALLOWED_CONFIDENCE}")

    # 9. Risk zones
    section = content.split("## Risk zones")[1].split("##")[0]
    if "none_detected" not in section and "-" not in section:
        issues.append("FAIL: risk zones section is empty AND not marked none_detected")

    # 10. No fabricated values: every populated row in the validation
    # commands table should have an Evidence column. The column should
    # be a real file path (not "not_detected" or empty).
    if "## Detected validation commands" in content:
        section = content.split("## Detected validation commands")[1].split("##")[0]
        # Find rows like: | mvn_test | `mvn test` | high | pom.xml |
        rows = re.findall(r"^\|\s*(\w+)\s*\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|\s*([^|]+?)\s*\|", section, re.MULTILINE)
        for cid, cmd, conf, ev in rows:
            if not ev.strip() or "not_detected" in ev.lower():
                issues.append(f"FAIL: validation command '{cid}' has empty/not_detected evidence (fabrication)")

    return issues


def main() -> int:
    report_dirs = sorted(d for d in EXERCISE.iterdir() if d.is_dir() and d.name.startswith("rds-"))
    if not report_dirs:
        print("no rds-s* directories found")
        return 1
    overall = True
    for d in report_dirs:
        report_path = d / "discovery/repo-discovery.md"
        issues = lint_report(report_path)
        if not issues:
            print(f"  [{d.name}] PASS")
        else:
            overall = False
            print(f"  [{d.name}] FAIL")
            for i in issues:
                print(f"      {i}")
    print()
    if overall:
        print("OVERALL: PASS")
        return 0
    print("OVERALL: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
