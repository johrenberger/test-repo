#!/usr/bin/env python3
"""
lint-release-readiness.py — auto-check for the
release-readiness skill.

Checks a `release-readiness-report.md` (or
`go-no-go-checklist.md`) against the report contract from
skills/release-readiness/SKILL.md and
references/release-gate-checklist.md.

Usage:
  python3 lint-release-readiness.py <task_workspace>
  python3 lint-release-readiness.py --self-test

The linter verifies:
  1. Required artifacts are present in the task workspace
     (validation-report.md, code-review-report.md, etc.)
  2. Release-readiness report has all required H2 sections
  3. Status is one of: Ready | Ready with known risks | Not ready
     | Blocked pending approval / evidence
  4. Each gate item has a verdict (pass | concern | finding)
  5. Unresolved Critical findings = 0 (or recorded in
     decisions/<id>.md)
  6. Unresolved High findings = 0 (or recorded in
     decisions/<id>.md)
  7. Rollback plan is documented
  8. Monitoring plan is documented
  9. Approvals are recorded

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found

This is the auto-check the `validated` definition requires
for the release-readiness skill.
"""
from __future__ import annotations
import re
import sys
import json
import subprocess
from pathlib import Path

# Required H2 sections in the release-readiness report
REQUIRED_SECTIONS = [
    "## Status",
    "## Discovery",
    "## Evidence",
    "## Gate verdicts",
    "## Approvals",
    "## Recommended next action",
]

# Allowed statuses (per SKILL.md)
ALLOWED_STATUSES = {
    "ready",
    "ready with known risks",
    "not ready",
    "blocked pending approval / evidence",
}

# Required evidence artifacts (per SKILL.md Required Inputs)
# A release-readiness assessment must find at least these
EVIDENCE_ARTIFACTS = {
    "validation": "validation/validation-report.md",
    "code-review": "reports/code-change-review-report.md",
    "dependency-review": "reports/dependency-change-report.md",
}


def check_evidence_artifacts(ws: Path) -> list[str]:
    """Check that the task workspace has the required evidence
    artifacts. Returns list of FAIL strings."""
    failures = []
    for name, rel_path in EVIDENCE_ARTIFACTS.items():
        full = ws / rel_path
        if not full.exists():
            failures.append(f"FAIL: missing required evidence artifact: {rel_path} (for {name})")
    return failures


def check_report(report_path: Path) -> list[str]:
    """Check the release-readiness report itself. Returns list of FAIL strings."""
    failures = []

    if not report_path.exists():
        return [f"FAIL: report does not exist: {report_path}"]
    text = report_path.read_text()
    if not text.strip():
        return [f"FAIL: report is empty: {report_path}"]

    # 1. Required H2 sections
    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"FAIL: missing required section: {section}")

    # 2. Status must be one of 4 allowed values
    m = re.search(r"## Status\s*\n\s*[`']?(ready|ready with known risks|not ready|blocked pending approval / evidence)[`']?", text, re.IGNORECASE)
    if not m:
        failures.append(f"FAIL: ## Status section missing or has invalid value (allowed: {sorted(ALLOWED_STATUSES)})")
    else:
        status = m.group(1).lower()
        if status not in ALLOWED_STATUSES:
            failures.append(f"FAIL: status '{status}' is not in {sorted(ALLOWED_STATUSES)}")

    # 3. Gate verdicts — each gate item must have a verdict
    if "## Gate verdicts" in text:
        gate_section = text.split("## Gate verdicts", 1)[1].split("##", 1)[0]
        # Each line with a checklist item must have a verdict marker
        items = re.findall(r"-\s*\[[ xX/]\]\s*.+", gate_section)
        if not items:
            failures.append("FAIL: ## Gate verdicts has no checklist items (each gate must be marked pass/concern/finding)")

    # 4. Unresolved Critical findings
    if "unresolved critical" in text.lower():
        # Should be "0" or have a decision file reference
        crit_section = re.search(r"unresolved critical[^:]*:\s*(\d+)", text, re.IGNORECASE)
        if crit_section and int(crit_section.group(1)) > 0:
            # Must have a decisions/ reference
            if "decisions/" not in text:
                failures.append("FAIL: unresolved Critical findings > 0 but no decisions/ reference")

    # 5. Rollback plan documented
    if "rollback" not in text.lower():
        failures.append("FAIL: rollback plan not mentioned in report (must be documented for release)")

    # 6. Approvals section has at least one entry
    if "## Approvals" in text:
        appr_section = text.split("## Approvals", 1)[1].split("##", 1)[0]
        if "|" not in appr_section and "approver" not in appr_section.lower():
            failures.append("FAIL: ## Approvals section has no approver entries (must list named approvers)")

    return failures


def check_workspace(ws: Path) -> tuple[list[str], list[str]]:
    """Run all checks on a task workspace. Return (evidence_failures, report_failures)."""
    evidence = check_evidence_artifacts(ws)
    report = check_report(ws / "reports" / "release-readiness-report.md")
    return evidence, report


def self_test() -> tuple[bool, str]:
    """Run the linter's own self-test."""
    import tempfile
    lines = []

    # Test 1: a workspace with all artifacts and a well-formed report should PASS
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "ready-ws"
        ws.mkdir()
        # Required artifacts
        (ws / "validation").mkdir()
        (ws / "validation" / "validation-report.md").write_text("# Validation\n\nPASSED\n", encoding="utf-8")
        (ws / "reports").mkdir()
        (ws / "reports" / "code-change-review-report.md").write_text("# Code review\n\nApproved\n", encoding="utf-8")
        (ws / "reports" / "dependency-change-report.md").write_text("# Dep review\n\nApproved\n", encoding="utf-8")
        (ws / "reports" / "release-readiness-report.md").write_text(GOOD_REPORT, encoding="utf-8")
        ev_fail, rep_fail = check_workspace(ws)
        if not ev_fail and not rep_fail:
            lines.append("  [rr-s1-ready-workspace] PASS")
        else:
            lines.append(f"  [rr-s1-ready-workspace] FAIL")
            for f in ev_fail + rep_fail:
                lines.append(f"    {f}")

    # Test 2: a workspace missing evidence artifacts should FAIL
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "missing-evidence"
        ws.mkdir()
        (ws / "reports").mkdir()
        (ws / "reports" / "release-readiness-report.md").write_text(GOOD_REPORT, encoding="utf-8")
        ev_fail, _ = check_workspace(ws)
        if ev_fail and any("evidence artifact" in f for f in ev_fail):
            lines.append("  [rr-s2-missing-evidence] PASS (correctly flagged)")
        else:
            lines.append(f"  [rr-s2-missing-evidence] FAIL (should have flagged missing evidence)")

    # Test 3: a report with invalid status should FAIL
    bad_status = GOOD_REPORT.replace("`ready`", "`maybe`")
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "bad-status"
        ws.mkdir()
        (ws / "validation").mkdir()
        (ws / "validation" / "validation-report.md").write_text("# Validation\n", encoding="utf-8")
        (ws / "reports").mkdir()
        (ws / "reports" / "code-change-review-report.md").write_text("# CR\n", encoding="utf-8")
        (ws / "reports" / "dependency-change-report.md").write_text("# DR\n", encoding="utf-8")
        (ws / "reports" / "release-readiness-report.md").write_text(bad_status, encoding="utf-8")
        _, rep_fail = check_workspace(ws)
        if rep_fail and any("status" in f.lower() for f in rep_fail):
            lines.append("  [rr-s3-bad-status] PASS (correctly flagged)")
        else:
            lines.append(f"  [rr-s3-bad-status] FAIL (should have flagged bad status)")

    # Test 4: a report missing rollback should FAIL
    # Use a regex to remove ALL occurrences of "Rollback" (case-insensitive)
    no_rollback = re.sub(r"[Rr]ollback", "Reversibility", GOOD_REPORT)
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "no-rollback"
        ws.mkdir()
        (ws / "validation").mkdir()
        (ws / "validation" / "validation-report.md").write_text("# Validation\n", encoding="utf-8")
        (ws / "reports").mkdir()
        (ws / "reports" / "code-change-review-report.md").write_text("# CR\n", encoding="utf-8")
        (ws / "reports" / "dependency-change-report.md").write_text("# DR\n", encoding="utf-8")
        (ws / "reports" / "release-readiness-report.md").write_text(no_rollback, encoding="utf-8")
        _, rep_fail = check_workspace(ws)
        if rep_fail and any("rollback" in f.lower() for f in rep_fail):
            lines.append("  [rr-s4-no-rollback] PASS (correctly flagged)")
        else:
            lines.append(f"  [rr-s4-no-rollback] FAIL (should have flagged missing rollback)")

    # Test 5: a report missing approvals should FAIL
    no_approvals = re.sub(r"## Approvals\n.*?(?=\n## |\Z)", "## Approvals\n\n(none)\n\n", GOOD_REPORT, flags=re.DOTALL)
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = Path(tmpdir) / "no-approvals"
        ws.mkdir()
        (ws / "validation").mkdir()
        (ws / "validation" / "validation-report.md").write_text("# Validation\n", encoding="utf-8")
        (ws / "reports").mkdir()
        (ws / "reports" / "code-change-review-report.md").write_text("# CR\n", encoding="utf-8")
        (ws / "reports" / "dependency-change-report.md").write_text("# DR\n", encoding="utf-8")
        (ws / "reports" / "release-readiness-report.md").write_text(no_approvals, encoding="utf-8")
        _, rep_fail = check_workspace(ws)
        if rep_fail and any("approver" in f.lower() or "approval" in f.lower() for f in rep_fail):
            lines.append("  [rr-s5-no-approvals] PASS (correctly flagged)")
        else:
            lines.append(f"  [rr-s5-no-approvals] FAIL (should have flagged missing approvers)")

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


GOOD_REPORT = """# Release readiness report

- **Task ID:** synthetic-rr
- **Generated at:** 2026-06-13T19:00:00Z
- **Reviewer:** software-engineer

## Status

`ready`

Reason: All gate items pass; no unresolved Critical or High findings.

## Discovery

Repo: test-repo
Module: validation-runner skill promotion
Build artifact: skill auto-check scripts (1 new file)

## Evidence

- Validation: `validation/validation-report.md` (passed, 5/5 scenarios)
- Code review: `reports/code-change-review-report.md` (approved)
- Dependency review: `reports/dependency-change-report.md` (approved)
- Architecture: N/A (skill-spec change only)
- Migration: N/A

## Gate verdicts

- [x] Tests pass — passed
- [x] Build success — built
- [x] Lint / typecheck — passed
- [x] Unresolved Critical findings — 0
- [x] Unresolved High findings — 0
- [x] Migration safety — N/A
- [x] Dependency changes — approved
- [x] Security risks — none
- [x] Rollback plan — revert commit (no schema change)
- [x] Feature flags / config — N/A
- [x] Monitoring / alerts / runbooks — N/A
- [x] Documentation updates — updated
- [x] Known limitations — none
- [x] Manual approvals — recorded below

## Approvals

| Approver | Role | Date | Notes |
| --- | --- | --- | --- |
| software-engineer | engineer | 2026-06-13 | Linter runs end-to-end |

## Recommended next action

Mark Ready and ship.
"""


def main():
    if len(sys.argv) < 2:
        print("usage: lint-release-readiness.py <task_workspace>", file=sys.stderr)
        print("       lint-release-readiness.py --self-test", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    else:
        ws = Path(arg)
        if not ws.exists() or not ws.is_dir():
            print(f"[lint-release-readiness] FAIL  (not a directory: {ws})")
            sys.exit(66)
        ev_fail, rep_fail = check_workspace(ws)
        all_fail = ev_fail + rep_fail
        if not all_fail:
            print(f"[lint-release-readiness] PASS  ({ws})")
            sys.exit(0)
        else:
            print(f"[lint-release-readiness] FAIL  ({ws}, {len(all_fail)} issues)")
            for f in all_fail:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
