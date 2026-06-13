#!/usr/bin/env python3
"""
lint-observability-review.py — auto-check for the
observability-review skill.

This is a 2-in-1 linter:

1. **Report linter**: checks an `observability-review-report.md`
   against the report contract from
   skills/observability-review/SKILL.md (Validation section)
   and the template at
   templates/observability-review-report.md.

2. **Source scanner**: scans a service repo for observability
   patterns from
   references/logging-metrics-tracing-checklist.md.

Usage:
  python3 lint-observability-review.py --self-test
  python3 lint-observability-review.py <report.md>
  python3 lint-observability-review.py --scan <repo_root>

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found

Calibration rubric (from SKILL.md "Validation" section):
  Report checks:
    1. Report file exists and parses as markdown
    2. Every required H2 section present
    3. Composite risk is critical|high|medium|low
    4. Every finding has id, severity, file:lines, evidence,
       recommendation
    5. All 7 observability dimensions are evaluated

  Source code checks (deterministic patterns from checklist):
    1. print() statements in production code (logging issue)
    2. Bare except / pass (silent failures)
    3. requests/urllib without timeout (timeout issue)
    4. Hardcoded URLs in code (config issue)
"""
from __future__ import annotations
import re
import sys
import json
import subprocess
from pathlib import Path

# Required H2 sections (per template)
REQUIRED_SECTIONS = [
    "## Inputs",
    "## Change summary",
    "## Modules",
    "## Observability dimensions",
    "## Findings",
    "## Recommendations",
    "## Handoff",
    "## Cross-references",
    "## Provenance",
]

ALLOWED_RISK_LEVELS = {"critical", "high", "medium", "low"}

# 7 observability dimensions
REQUIRED_DIMENSIONS = [
    "logging",
    "metrics",
    "tracing",
    "health",
    "slo",
    "alerts",
    "dashboards",
]

# Deterministic observability anti-patterns (regex)
# These are the things a linter CAN check
OBSERVABILITY_PATTERNS = {
    # Logging issues
    "print_in_production": re.compile(r"^\s*print\s*\(", re.MULTILINE),
    # Bare except / silent failures
    "bare_except": re.compile(r"^\s*except\s*:\s*$", re.MULTILINE),
    "except_pass": re.compile(r"^\s*except[^:]*:\s*pass\s*$", re.MULTILINE),
    # HTTP without timeout
    "requests_no_timeout": re.compile(r"requests\.(get|post|put|delete|patch|head|request)\([^)]*\)"),
    # Config issues
    "hardcoded_url": re.compile(r"https?://(?!localhost|127\.0\.0\.1|example\.com|0\.0\.0\.0)[a-zA-Z0-9.-]+\.[a-z]{2,}[^\s)'\"`]*"),
}


def check_report(report_path: Path) -> list[str]:
    """Check an observability-review-report.md. Return list of FAIL strings."""
    failures = []

    if not report_path.exists():
        return [f"FAIL: report does not exist: {report_path}"]
    text = report_path.read_text()
    if not text.strip():
        return [f"FAIL: report is empty: {report_path}"]

    # 1. Required H2 sections
    for section in REQUIRED_SECTIONS:
        pattern = re.escape(section) + r"\b"
        if not re.search(pattern, text, re.IGNORECASE):
            failures.append(f"FAIL: missing required section: {section}")

    # 2. Composite risk is one of 4 allowed values
    m = re.search(r"\*\*Composite risk:\*\*\s*[`']?(critical|high|medium|low)[`']?", text, re.IGNORECASE)
    if not m:
        failures.append(f"FAIL: **Composite risk:** missing or invalid (allowed: {sorted(ALLOWED_RISK_LEVELS)})")
    else:
        risk = m.group(1).lower()
        if risk not in ALLOWED_RISK_LEVELS:
            failures.append(f"FAIL: risk '{risk}' is not in {ALLOWED_RISK_LEVELS}")

    # 3. All 7 observability dimensions evaluated
    dims_match = re.search(r"## Observability dimensions(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if dims_match:
        dims_section = dims_match.group(1)
        for dim in REQUIRED_DIMENSIONS:
            if not re.search(rf"\b{re.escape(dim)}\b", dims_section, re.IGNORECASE):
                failures.append(f"FAIL: observability dimension '{dim}' not evaluated")
    else:
        failures.append("FAIL: ## Observability dimensions section not found")

    # 4. Every finding has the required fields
    findings_match = re.search(r"## Findings(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if findings_match:
        findings_section = findings_match.group(1)
        # Find all finding detail blocks: ### <id> — <summary>
        # A block is from the `###` line up to the next `###` or end of section
        finding_starts = list(re.finditer(r"###\s+([a-zA-Z0-9_-]+)\s*(?:—|-)?\s*([^\n]*)", findings_section))
        for i, m in enumerate(finding_starts, 1):
            finding_id = m.group(1)
            # Get the full block: from this start to the next ### or end
            start = m.start()
            end = finding_starts[i].start() if i < len(finding_starts) else len(findings_section)
            finding_text = findings_section[start:end]
            # Required: Severity, Category, Location, Evidence, Recommendation, Routed to
            for field in ["Severity", "Category", "Location", "Evidence", "Recommendation", "Routed to"]:
                if not re.search(rf"\*\*\s*{re.escape(field)}\s*:\*\*", finding_text):
                    failures.append(f"FAIL: finding '{finding_id}' missing field: {field}")

    return failures


def scan_source(source_path: Path) -> list[tuple[str, int, str]]:
    """Scan a source file for observability anti-patterns.
    Return list of (pattern_name, line_no, snippet)."""
    if not source_path.exists() or not source_path.is_file():
        return []
    if source_path.suffix not in {".py", ".java", ".js", ".ts", ".go", ".rs", ".rb", ".cs", ".php", ".sh"}:
        return []
    try:
        text = source_path.read_text(errors="ignore")
    except Exception:
        return []
    findings = []
    for name, pattern in OBSERVABILITY_PATTERNS.items():
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
            findings.append((name, line_no, line.strip()[:120]))
    return findings


def scan_repo(repo_root: Path) -> list[tuple[Path, str, int, str]]:
    """Scan a repo for observability anti-patterns."""
    findings = []
    if not repo_root.exists() or not repo_root.is_dir():
        return findings
    skip_dirs = {".git", "__pycache__", "node_modules", "target", "build", "dist", ".venv", "venv", "env", "test", "tests"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            for name, line, snippet in scan_source(path):
                findings.append((path, name, line, snippet))
    return findings


GOOD_REPORT = """# Observability review for synthetic-or

- **Task / change:** PR #42
- **Skill:** `observability-review`
- **Generated at:** 2026-06-13T20:00:00Z
- **Composite risk:** `medium`

## Inputs

- **Acceptance criteria:** service is observable end-to-end
- **Discovery artifact:** `discovery/repo-discovery.md`
- **Change set:** `git diff main..feature`
- **Existing dashboards:** Grafana "Service Health"
- **Existing alerts:** none
- **Existing runbooks:** none
- **Existing SLO / SLI:** none

## Change summary

The service gained a new background worker that pulls from
an external queue. No new metrics, traces, or alerts were
added. This is the gap the review calls out.

## Modules / services in scope

| Path / service | Role | Notes |
| --- | --- | --- |
| `worker.py` | background worker | new |
| `api.py` | public API | unchanged |

## Observability dimensions

| Dimension | Verdict | Evidence |
| --- | --- | --- |
| Logging (key events, structure, redaction) | finding | `worker.py:23` uses `print()` |
| Metrics (critical paths, RED / USE) | finding | no metrics for the new worker |
| Tracing (correlation IDs, span coverage) | pass | OTel SDK already in use |
| Health checks (liveness, readiness, dependencies) | pass | `/healthz` checks all deps |
| SLO / SLI | concern | no SLO defined for the new worker |
| Alerts (actionable, runbook-backed) | finding | no alerts on worker failures |
| Dashboards (usable for triage) | concern | no panel for the new worker |

## Findings

| ID | Severity | Category | File:lines / artifact | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| OR-001 | High | logging | `worker.py:23` | `print()` for worker state | open |
| OR-002 | High | metrics | `worker.py` | no worker metrics | open |
| OR-003 | Medium | slo | none | no SLO for worker | open |
| OR-004 | High | alerts | none | no alerts on worker failure | open |

### OR-001 — print() in production

- **Severity:** High
- **Category:** logging
- **Location:** `worker.py:23`
- **Source skill:** `observability-review`
- **Evidence:** `print(f"Worker state: {state}")`
- **Recommendation:** Replace with structured `logger.info(...)` call
- **Routed to:** `backend-implementation`
- **Cross-reference:** none

### OR-002 — missing worker metrics

- **Severity:** High
- **Category:** metrics
- **Location:** `worker.py:1-50`
- **Source skill:** `observability-review`
- **Evidence:** no `Counter`, `Histogram`, or `Gauge` for the worker
- **Recommendation:** Add `worker_processed_total`, `worker_duration_seconds`, `worker_errors_total`
- **Routed to:** `backend-implementation`
- **Cross-reference:** none

### OR-003 — no SLO for worker

- **Severity:** Medium
- **Category:** slo
- **Location:** none
- **Source skill:** `observability-review`
- **Evidence:** no SLO document
- **Recommendation:** Define a 99% successful-process rate SLO
- **Routed to:** `architecture-decision`
- **Cross-reference:** none

### OR-004 — no alerts on worker failure

- **Severity:** High
- **Category:** alerts
- **Location:** none
- **Source skill:** `observability-review`
- **Evidence:** alertmanager has no rule for `worker_errors_total`
- **Recommendation:** Add a high-priority alert when `worker_errors_total` increases
- **Routed to:** `backend-implementation`
- **Cross-reference:** none

## Recommendations

- **PRIMARY:** `backend-implementation` — fix OR-001, OR-002, OR-004
- **SECONDARY:** `architecture-decision` — define an SLO for the worker

## Handoff

- **Handoff packet file:** `handoffs/test.md`
- **Target skill:** `backend-implementation`
- **Required next action:** Implement OR-001, OR-002, OR-004

## Cross-references

- Discovery: `discovery/repo-discovery.md`
- Handoff packet: `handoffs/test.md`

## Provenance

- Produced by `observability-review` (draft).
"""


def self_test() -> tuple[bool, str]:
    import tempfile
    lines = []

    # Test 1: well-formed report should PASS
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(GOOD_REPORT)
        good_path = Path(f.name)
    failures = check_report(good_path)
    if not failures:
        lines.append("  [or-s1-good-report] PASS")
    else:
        lines.append(f"  [or-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_path.unlink(missing_ok=True)

    # Test 2: invalid risk level should FAIL
    bad = GOOD_REPORT.replace("**Composite risk:** `medium`", "**Composite risk:** `unknown`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("risk" in f.lower() for f in failures):
        lines.append("  [or-s2-invalid-risk] PASS (correctly flagged)")
    else:
        lines.append(f"  [or-s2-invalid-risk] FAIL (should have flagged invalid risk)")
    bad_path.unlink(missing_ok=True)

    # Test 3: missing dimension should FAIL
    bad = GOOD_REPORT.replace("| Dashboards", "| SLO / SLI")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("dashboards" in f for f in failures):
        lines.append("  [or-s3-missing-dimension] PASS (correctly flagged)")
    else:
        lines.append(f"  [or-s3-missing-dimension] FAIL (should have flagged missing dashboards)")
    bad_path.unlink(missing_ok=True)

    # Test 4: finding missing Severity should FAIL
    bad = GOOD_REPORT.replace("- **Severity:** High", "- **Severityzzzz:** High")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Severity" in f for f in failures):
        lines.append("  [or-s4-finding-missing-field] PASS (correctly flagged)")
    else:
        lines.append(f"  [or-s4-finding-missing-field] FAIL (should have flagged missing Severity)")
    bad_path.unlink(missing_ok=True)

    # Test 5: source scan should find print() in production code
    test_code = """
import requests

def process():
    print("Worker state: starting")
    r = requests.get("https://api.example.com/data")
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    found_print = any(f[0] == "print_in_production" for f in findings)
    if found_print:
        lines.append("  [or-s5-source-scan-print] PASS (found print() in production)")
    else:
        lines.append(f"  [or-s5-source-scan-print] FAIL (should have found print(); got: {findings})")
    test_path.unlink(missing_ok=True)

    # Test 6: source scan should find bare except
    test_code = """
def safe():
    try:
        risky()
    except:
        pass
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    found_bare = any(f[0] in ("bare_except", "except_pass") for f in findings)
    if found_bare:
        lines.append("  [or-s6-source-scan-bare-except] PASS (found bare except)")
    else:
        lines.append(f"  [or-s6-source-scan-bare-except] FAIL (should have found bare except; got: {findings})")
    test_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-observability-review.py <report.md>", file=sys.stderr)
        print("       lint-observability-review.py --self-test", file=sys.stderr)
        print("       lint-observability-review.py --scan <repo_root>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--scan":
        repo = Path(sys.argv[2])
        if not repo.exists():
            print(f"[lint-observability-review] FAIL  (not a directory: {repo})")
            sys.exit(66)
        findings = scan_repo(repo)
        if not findings:
            print(f"[lint-observability-review] scan: no findings in {repo}")
            sys.exit(0)
        print(f"[lint-observability-review] scan: {len(findings)} findings in {repo}")
        for path, name, line, snippet in findings:
            print(f"  {path}:{line}  {name}: {snippet}")
        sys.exit(1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-observability-review] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-observability-review] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-observability-review] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
