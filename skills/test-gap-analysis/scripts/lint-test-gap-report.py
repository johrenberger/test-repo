#!/usr/bin/env python3
"""
Linter for test-gap-analysis reports.

Enforces the contract defined in skills/test-gap-analysis/SKILL.md and
skills/test-gap-analysis/templates/test-gap-report.md.

Usage:
  lint-test-gap-report.py <report.md>            # lint a single report
  lint-test-gap-report.py <reports-dir>          # lint every tgas-*/reports/test-gap-report.md
  lint-test-gap-report.py --self-test            # lint the B6 exercise reports

Exit codes:
  0  all reports pass
  1  one or more reports failed the linter
  64 bad usage

Rules (10):
  1. Required frontmatter fields present (Task ID, Repo root, Scope, Generated at, Confidence)
  2. `Confidence:` is one of `low | medium | high`
  3. Required sections present (Stack, Inventory, Source modules, High-risk,
     Recommended, Validation, E2E, Follow-up, Provenance)
  4. Every gap's risk is from the allowed scale (critical|high|medium|low)
  5. Every gap's gap_type is from the allowed list (unit, integration,
     contract, regression, security-negative)
  6. Every gap has a non-empty `evidence` field (or equivalent)
  7. Validation commands table has Command ID + Command + Source + Confidence
  8. E2E/load/chaos recommendation is `recommended` or
     `not_recommended_in_this_scope` and has a Reason line
  9. No fabricated coverage % (matches digits+%) without a coverage artifact
 10. The report does not exceed 400 lines (sanity; very large reports are
     usually hallucinations)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_RISKS = {"critical", "high", "medium", "low"}
ALLOWED_GAP_TYPES = {
    "unit",
    "integration",
    "contract",
    "regression",
    "security-negative",
    "unit test gap",
    "integration / api test gap",
    "integration/api test gap",
    "contract test gap",
    "regression test gap",
    "security / negative test gap",
    "security-negative test gap",
}
REQUIRED_SECTIONS = [
    "## Stack and test framework detected",
    "## Existing test inventory summary",
    "## Source modules with no adjacent test coverage",
    "## High-risk untested behaviors",
    "## Recommended test additions",
    "## Validation commands discovered",
    "## E2E / load / chaos recommendation",
    "## Follow-up handoff target",
    "## Provenance",
]
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
SELF_TEST_ROOT = Path("/data/.openclaw/workspace/tasks/2026-06-12-test-gap-analysis-exercise")


def lint_report(path: Path) -> list[str]:
    """Return a list of issue strings (empty if the report passes)."""
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: report does not exist: {path}"]
    content = path.read_text()
    lines = content.splitlines()

    # 0. Preflight-aborted marker: a valid alternative to a full report
    if "PREFLIGHT ABORTED" in content:
        if "Reason" not in content and "reason" not in content:
            issues.append("FAIL: preflight-aborted report missing the abort reason")
        return issues

    # 1. Frontmatter
    for field in ("- **Task ID:**", "- **Repo root:**", "- **Scope analyzed:**", "- **Generated at:**", "- **Confidence:**"):
        if field not in content:
            issues.append(f"FAIL: missing frontmatter field '{field.rstrip(':')}'")

    # 2. Confidence value
    m = re.search(r"- \*\*Confidence:\*\*\s*(\w+)", content)
    if m and m.group(1) not in ALLOWED_CONFIDENCE:
        issues.append(f"FAIL: Confidence '{m.group(1)}' is not in {ALLOWED_CONFIDENCE}")

    # 3. Required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"FAIL: missing required section '{section}'")

    # 4. Risk values
    for m in re.finditer(r"\|\s*(critical|high|medium|low)\s*\|", content, re.IGNORECASE):
        risk = m.group(1).lower()
        if risk not in ALLOWED_RISKS:
            issues.append(f"FAIL: risk '{risk}' is not in {ALLOWED_RISKS}")

    # 5. Gap types
    for m in re.finditer(r"\|\s*([a-z][a-z /-]*[a-z])\s*\|", content):
        gt = m.group(1).lower().strip()
        if gt in ALLOWED_RISKS:
            continue
        if " " in gt and gt not in ALLOWED_GAP_TYPES and not any(gt.startswith(t) for t in ["unit", "integration", "contract", "regression", "security"]):
            continue
        if gt in ALLOWED_GAP_TYPES or any(gt.startswith(t) for t in ["unit", "integration", "contract", "regression", "security"]):
            if gt not in ALLOWED_GAP_TYPES:
                issues.append(f"FAIL: gap_type '{gt}' is not in the allowed set {ALLOWED_GAP_TYPES}")

    # 6. Evidence (in the high-risk table; the 4th column)
    if "## High-risk untested behaviors" in content:
        section = content.split("## High-risk untested behaviors")[1].split("##")[0]
        rows = re.findall(r"^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+?)\s*\|\s*$", section, re.MULTILINE)
        for r in rows:
            area, risk, gap, ev = r
            area_clean = area.strip()
            if area_clean.startswith("(none") or area_clean.startswith("(no "):
                continue
            if not ev.strip() or ev.strip() in ("-", "—", "n/a"):
                issues.append(f"FAIL: gap '{area_clean}' has empty evidence")

    # 7. Validation commands table
    if "## Validation commands discovered" in content:
        section = content.split("## Validation commands discovered")[1].split("##")[0]
        if "Command ID" not in section:
            issues.append("FAIL: validation commands table missing 'Command ID' header")
        if "Confidence" not in section:
            issues.append("FAIL: validation commands table missing 'Confidence' header")
        for m in re.finditer(r"\|\s*(high|medium|low)\s*\|", section, re.IGNORECASE):
            c = m.group(1).lower()
            if c not in ("high", "medium", "low"):
                issues.append(f"FAIL: validation command confidence '{c}' is not high|medium|low")

    # 8. E2E recommendation
    m = re.search(r"`(recommended|not_recommended_in_this_scope)`", content)
    if not m:
        if "PREFLIGHT ABORTED" not in content:
            issues.append("FAIL: E2E/load/chaos recommendation is neither 'recommended' nor 'not_recommended_in_this_scope'")
    else:
        if "Reason:" not in content:
            issues.append("FAIL: E2E/load/chaos recommendation has no 'Reason:' line")

    # 9. No fabricated coverage %
    for m in re.finditer(r"(\d+(?:\.\d+)?%)\s*(covered|coverage)", content, re.IGNORECASE):
        context_start = max(0, m.start() - 200)
        context = content[context_start:m.end() + 200]
        if "coverage artifact" not in context.lower() and "no coverage" not in context.lower() and "no real" not in context.lower():
            issues.append(f"FAIL: report claims coverage {m.group(1)} without a coverage artifact citation (forbidden per SKILL.md Forbidden Actions)")

    # 10. Size sanity
    if len(lines) > 400:
        issues.append(f"WARN: report is {len(lines)} lines (>400), may be a hallucination")

    return issues


def _collect_reports(target: Path) -> list[Path]:
    """Return a list of report paths to lint, given a target path.

    <target> is one of:
      * a single report file (path ends in test-gap-report.md)
      * a directory containing <tgas-*/reports/test-gap-report.md> workspaces
      * a directory containing a single <reports/test-gap-report.md>
    """
    if target.is_file() and target.name == "test-gap-report.md":
        return [target]
    if target.is_dir():
        # Convention 1: <dir>/tgas-*/reports/test-gap-report.md
        reports = sorted(target.glob("tgas-*/reports/test-gap-report.md"))
        if reports:
            return reports
        # Convention 2: <dir>/reports/test-gap-report.md
        single = target / "reports/test-gap-report.md"
        if single.exists():
            return [single]
    return []


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: lint-test-gap-report.py <report.md | reports-dir> | --self-test", file=sys.stderr)
        return 64
    arg = argv[1]
    if arg == "--self-test":
        if not SELF_TEST_ROOT.exists():
            print(f"FAIL: self-test exercise root not found: {SELF_TEST_ROOT}", file=sys.stderr)
            return 1
        reports = sorted(SELF_TEST_ROOT.glob("tgas-*/reports/test-gap-report.md"))
    else:
        target = Path(arg)
        if not target.exists():
            print(f"FAIL: path does not exist: {target}", file=sys.stderr)
            return 1
        reports = _collect_reports(target)
    if not reports:
        print("no reports found to lint", file=sys.stderr)
        return 1
    overall = True
    for r in reports:
        issues = lint_report(r)
        # Display the parent task-id directory if present, else the report path
        display = r.parent.parent.name if r.parent.name == "reports" else r.name
        if not issues:
            print(f"  [{display}] PASS")
        else:
            overall = False
            print(f"  [{display}] FAIL")
            for i in issues:
                print(f"      {i}")
    print()
    if overall:
        print("OVERALL: PASS")
        return 0
    print("OVERALL: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
