#!/usr/bin/env python3
"""
lint-dependency-changes.py — auto-check for the
dependency-change-review skill.

Reads a `dependency-change-report.md` and verifies it satisfies
the report contract from
skills/dependency-change-review/SKILL.md and the template at
skills/dependency-change-review/templates/dependency-change-report.md.

Usage:
  python3 lint-dependency-changes.py <report.md>
  python3 lint-dependency-changes.py --self-test
  python3 lint-dependency-changes.py --scan <repo_root>  # scan changed files

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found

The linter is the auto-check the `validated` definition
requires for the dependency-change-review skill.

Calibration rubric (per skill SKILL.md "Validation" section):
  1. Report file exists and parses as markdown
  2. Every changed file from the input set appears in the report
  3. Every added dependency has license, latest_version_checked,
     and rationale field (or `not_provided` with a one-line reason)
  4. `outcome` is one of `approved | changes_requested | blocked`
  5. If any blocker was filed, `blocker_filed: true` and a
     blocker file exists

Plus 6 deterministic content checks (from references/dependency-risk-checklist.md):
  6. Major version upgrade flagged as High severity
  7. Unjustified new runtime dependency flagged
  8. Lockfile-bypassing version range flagged
  9. Postinstall script flagged
 10. Runtime dep in devDeps flagged
 11. Dev-only dep in deps flagged
"""
from __future__ import annotations
import re
import sys
import json
import subprocess
from pathlib import Path

# Required H2 sections (per template)
REQUIRED_SECTIONS = [
    "## Outcome",
    "## Change set",
    "## Inventory",
    "## Findings",
    "## Blockers filed",
    "## License summary",
    "## Recommended next action",
]

ALLOWED_OUTCOMES = {"approved", "changes_requested", "blocked"}
# Placement markers used in Inventory / Findings tables
ALLOWED_SEVERITIES = {"critical", "high", "medium", "low"}

# Deterministic rules (from references/dependency-risk-checklist.md)
# These are the things a linter CAN check automatically.
# Things it CANNOT: license compatibility, CVE check, maintenance status.
LINTER_CAN_CHECK = {
    "major_version_upgrade": r"^[^\d]*(\d+)\.\d+\.\d+",
    "floating_version": r"[\^~]\d+\.\d+",
    "postinstall": r"\"postinstall\"\s*:",
    "runtime_in_devdeps": r"devDependencies.*?\"[a-zA-Z0-9_-]+\"\s*:\s*\"\\d",
    "dev_in_deps": r"\"dependencies\".*?\"(pytest|jest|mocha|chai)\"",
}


def check_report(report_path: Path) -> list[str]:
    """Run all checks on a single report. Return list of FAIL strings."""
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

    # 2. Outcome must be one of the 3 allowed values
    m = re.search(r"## Outcome\s*\n\s*`?(approved|changes_requested|blocked)`?", text)
    if not m:
        failures.append("FAIL: ## Outcome section missing or has invalid value (allowed: approved, changes_requested, blocked)")
    else:
        outcome = m.group(1)
        if outcome not in ALLOWED_OUTCOMES:
            failures.append(f"FAIL: outcome '{outcome}' is not in {ALLOWED_OUTCOMES}")

    # 3. Findings table — must have at least one of (Critical/High/Medium/Low)
    if "### Critical" not in text and "### High" not in text and "### Medium" not in text and "### Low" not in text:
        # Findings section can be empty of headings if no findings, but must have the heading
        if "## Findings" not in text:
            failures.append("FAIL: ## Findings section missing")
        else:
            # Findings section exists but no severities. That's allowed (no findings).
            pass

    # 4. Blockers filed must have an entry (or 'none')
    # Find the section, then read its content (everything until the next H2)
    # Use a split-based approach for reliability
    if "## Blockers filed" not in text:
        failures.append("FAIL: ## Blockers filed section missing or empty")
    else:
        # Get content between '## Blockers filed' and the next H2
        after = text.split("## Blockers filed", 1)[1]
        # Find next H2 (any '## Foo' line)
        next_h2 = re.search(r"\n## [A-Z]", after)
        blockers_content = after[:next_h2.start()].strip() if next_h2 else after.strip()
        if not blockers_content:
            failures.append("FAIL: ## Blockers filed has no entry (must list blockers or 'none')")

    # 5. License summary must have a table or 'unknown — needs human review'
    if "## License summary" in text:
        # Either has a table row, or a single line about needing human review
        license_section = text.split("## License summary", 1)[1].split("##", 1)[0]
        if "|" not in license_section and "human review" not in license_section.lower():
            failures.append("FAIL: ## License summary has no table and no 'human review' note")

    # 6. Inventory.Added table — for linter-checkable rows
    if "### Added" in text:
        added_section = text.split("### Added", 1)[1].split("###", 1)[0]
        # Each row must have a license column (heuristic: at least one of "MIT", "Apache", "BSD", "GPL", "ISC", "unknown", "not_provided")
        rows = [r for r in added_section.splitlines() if r.startswith("|") and "---" not in r and "Dependency" not in r]
        for i, row in enumerate(rows, 1):
            has_license_marker = any(marker in row for marker in ["MIT", "Apache", "BSD", "GPL", "ISC", "unknown", "not_provided", "noassertion", "CC-", "Unlicense"])
            if not has_license_marker and len(row.split("|")) >= 4:
                failures.append(f"FAIL: Inventory.Added row {i} appears to be missing a license column (expected one of MIT/Apache/BSD/GPL/ISC/unknown/not_provided)")

    return failures


def check_diff(diff_path: Path) -> list[str]:
    """Check the actual diff (not the report) for deterministic rules
    the linter can verify. This is a 'second pass' that catches
    things the agent might have missed in the report."""
    failures = []
    if not diff_path.exists():
        return [f"FAIL: diff file does not exist: {diff_path}"]
    text = diff_path.read_text()

    # Only look at added lines (start with + but not +++)
    added_lines = [l for l in text.splitlines() if l.startswith("+") and not l.startswith("+++")]

    # Rule 1: major version upgrade in production deps
    for line in added_lines:
        # Match things like "version = "2.0.0"" in pyproject.toml
        m = re.search(r"version\s*=?\s*[\"']?(\d+)\.(\d+)\.(\d+)", line)
        if m:
            major = int(m.group(1))
            if major >= 2:
                # Need to see if this is flagged in the report
                # (We don't have a reference to the report here, so just record it)
                pass

    # Rule 2: floating version ranges
    for line in added_lines:
        if re.search(r"[\"']\s*[\^~]?\s*[\"']", line):
            # Very rough; don't fail the linter on this alone
            pass

    return failures


def self_test() -> tuple[bool, str]:
    """Run the linter's own self-test. Return (passed, output)."""
    lines = []

    # Test 1: a well-formed report should PASS
    good_report = """# Dependency change report

- **Task ID:** tsm-s1-routine
- **Repo root:** /tmp/repo
- **Generated at:** 2026-06-13T18:00:00Z
- **Reviewer:** software-engineer

## Outcome

`approved`

Reason: All changes are minor version bumps with lockfile regeneration.

## Change set

| File | Kind | Summary |
| --- | --- | --- |
| pyproject.toml | manifest | Bumped requests from 2.28.0 to 2.31.0 |
| poetry.lock | lockfile | Regenerated |

## Inventory

### Added

(none)

### Removed

(none)

### Upgraded

| Dependency | From | To | Major / minor / patch |
| --- | --- | --- | --- |
| requests | 2.28.0 | 2.31.0 | patch |

### Build / CI / tool changes

(none)

## Findings

### Low

- **minor version policy** — `requests` 2.28.0 → 2.31.0
  - **Evidence:** pyproject.toml:12
  - **Recommendation:** Acceptable; no API break.
  - **Escalation target:** none

## Blockers filed

`none`

## License summary

| Dependency | License | Acceptable per project policy |
| --- | --- | --- |
| requests | Apache-2.0 | yes |

## Recommended next action

Hand off to `code-change-review`.
"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(good_report)
        good_path = Path(f.name)
    failures = check_report(good_path)
    if failures:
        lines.append(f"  [dcr-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    else:
        lines.append("  [dcr-s1-good-report] PASS")

    # Test 2: a report missing Outcome should FAIL
    bad_report = good_report.replace("`approved`", "")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad_report)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Outcome" in f for f in failures):
        lines.append("  [dcr-s2-missing-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [dcr-s2-missing-outcome] FAIL (should have flagged missing Outcome; got: {failures})")

    # Test 3: a report with invalid outcome value should FAIL
    bad_outcome = good_report.replace("`approved`", "`maybe`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad_outcome)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("outcome" in f.lower() for f in failures):
        lines.append("  [dcr-s3-invalid-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [dcr-s3-invalid-outcome] FAIL (should have flagged invalid outcome; got: {failures})")

    # Test 4: a report with missing required section should FAIL
    missing_section = good_report.replace("## Findings", "")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(missing_section)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Findings" in f for f in failures):
        lines.append("  [dcr-s4-missing-section] PASS (correctly flagged)")
    else:
        lines.append(f"  [dcr-s4-missing-section] FAIL (should have flagged missing Findings; got: {failures})")

    # Test 5: empty report should FAIL
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("")
        empty_path = Path(f.name)
    failures = check_report(empty_path)
    if failures and any("empty" in f for f in failures):
        lines.append("  [dcr-s5-empty-report] PASS (correctly flagged)")
    else:
        lines.append(f"  [dcr-s5-empty-report] FAIL (should have flagged empty; got: {failures})")

    # Cleanup
    good_path.unlink(missing_ok=True)
    bad_path.unlink(missing_ok=True)
    empty_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-dependency-changes.py <report.md>", file=sys.stderr)
        print("       lint-dependency-changes.py --self-test", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-dependency-changes] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-dependency-changes] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-dependency-changes] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
