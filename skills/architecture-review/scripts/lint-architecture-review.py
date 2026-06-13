#!/usr/bin/env python3
"""
lint-architecture-review.py — auto-check for the
architecture-review skill.

This is a 2-in-1 linter:

1. **Report linter**: checks an `architecture-review-report.md`
   against the report contract from
   skills/architecture-review/SKILL.md (Validation section)
   and the template at
   templates/architecture-review-report.md.

2. **Source scanner**: scans a service repo for architecture
   anti-patterns from
   references/architecture-risk-checklist.md.

Usage:
  python3 lint-architecture-review.py --self-test
  python3 lint-architecture-review.py <report.md>
  python3 lint-architecture-review.py --scan <repo_root>

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Required H2 sections (per template — but only those the
# "Validation" section actually checks; template has more optional
# sections like "## Field rules", "## When the review is for a
# specific ADR" which are documentation of the format, not
# required for every report).
REQUIRED_SECTIONS = [
    "## Change set summary",
    "## Modules",
    "## Architectural dimensions",
    "## Findings",
    "## ADR recommendation",
    "## Handoff",
    "## Cross-references",
    "## Provenance",
]

ALLOWED_RISK_LEVELS = {"critical", "high", "medium", "low"}

# 13 architectural dimensions (from SKILL.md "Workflow" step 4)
REQUIRED_DIMENSIONS = [
    "alignment",
    "boundary",
    "coupling",
    "data ownership",
    "api contract",
    "failure",
    "scalability",
    "security",
    "observability",
    "deployment",
    "reversibility",
    "migration",
    "over-engineering",
]

# Architecture anti-patterns (deterministic regex from checklist)
ARCHITECTURE_PATTERNS = {
    # Coupling / boundary issues
    "tight_coupling_import": re.compile(r"from\s+\.\.importer\s+import"),
    # Hardcoded config / secrets (boundary violation)
    "hardcoded_secret": re.compile(r"(?:password|api_key|secret|token)\s*=\s*['\"][^'\"]{4,}['\"]", re.IGNORECASE),
    # God object (huge class)
    # captured via line count check, not regex
    # Blocking call inside async (failure mode issue)
    "sync_in_async": re.compile(r"def\s+\w+\s*\([^)]*\)\s*:\s*\n[^\n]*time\.sleep\(|def\s+\w+\s*\([^)]*\)\s*:\s*\n[^\n]*requests\."),
    # Direct DB access from controller (boundary violation)
    "db_in_routes": re.compile(r"@(?:app|router|blueprint)\.\w+\s*\([^)]*\)\s*\n[^\n]*?(?:SELECT|INSERT|UPDATE|DELETE)\s+"),
    # Mutable global state
    "global_state": re.compile(r"^(?:GLOBAL|_[A-Z_]+)\s*=\s*\[?\s*\{?"),
}


def check_report(report_path: Path) -> list[str]:
    """Check an architecture-review-report.md. Return list of FAIL strings."""
    failures = []
    if not report_path.exists():
        return [f"FAIL: report does not exist: {report_path}"]
    text = report_path.read_text()
    if not text.strip():
        return [f"FAIL: report is empty: {report_path}"]

    # 1. Required H2 sections (word-boundary match)
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

    # 3. All 13 architectural dimensions evaluated
    dims_match = re.search(r"## Architectural dimensions(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if dims_match:
        dims_section = dims_match.group(1)
        for dim in REQUIRED_DIMENSIONS:
            if not re.search(rf"\b{re.escape(dim)}\b", dims_section, re.IGNORECASE):
                failures.append(f"FAIL: architectural dimension '{dim}' not evaluated")
    else:
        failures.append("FAIL: ## Architectural dimensions section not found")

    # 4. Every finding has the required fields
    findings_match = re.search(r"## Findings(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if findings_match:
        findings_section = findings_match.group(1)
        finding_starts = list(re.finditer(r"###\s+([a-zA-Z0-9_-]+)\s*(?:—|-)?\s*([^\n]*)", findings_section))
        for i, m in enumerate(finding_starts, 1):
            finding_id = m.group(1)
            start = m.start()
            end = finding_starts[i].start() if i < len(finding_starts) else len(findings_section)
            finding_text = findings_section[start:end]
            for field in ["Severity", "Category", "Location", "Evidence", "Recommendation", "Routed to"]:
                if not re.search(rf"\*\*\s*{re.escape(field)}\s*:\*\*", finding_text):
                    failures.append(f"FAIL: finding '{finding_id}' missing field: {field}")

    # 5. ADR recommendation is justified (must say "yes"/"no"/"required" or similar)
    adr_match = re.search(r"## ADR recommendation(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if adr_match:
        adr_section = adr_match.group(1)
        if not re.search(r"\b(yes|no|required|not required|recommended)\b", adr_section, re.IGNORECASE):
            failures.append("FAIL: ADR recommendation section is present but not justified (should say yes/no/required/etc.)")

    return failures


def scan_source(source_path: Path) -> list[tuple[str, int, str]]:
    """Scan a source file for architecture anti-patterns."""
    if not source_path.exists() or not source_path.is_file():
        return []
    if source_path.suffix not in {".py", ".java", ".js", ".ts", ".go", ".rs", ".rb", ".cs", ".php", ".sh"}:
        return []
    try:
        text = source_path.read_text(errors="ignore")
    except Exception:
        return []
    findings = []
    lines = text.split("\n")
    # God object: class with > 300 lines
    for i, line in enumerate(lines):
        if re.match(r"^\s*class\s+\w+", line):
            # Count lines until next class definition at same/less indent
            indent = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines) and (lines[j].strip() == "" or len(lines[j]) - len(lines[j].lstrip()) > indent):
                j += 1
            if j - i > 300:
                findings.append(("god_object", i + 1, f"class spans {j - i} lines"))
    # Other patterns
    for name, pattern in ARCHITECTURE_PATTERNS.items():
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
            findings.append((name, line_no, line.strip()[:120]))
    return findings


def scan_repo(repo_root: Path) -> list[tuple[Path, str, int, str]]:
    """Scan a repo for architecture anti-patterns."""
    findings = []
    if not repo_root.exists() or not repo_root.is_dir():
        return findings
    skip_dirs = {".git", "__pycache__", "node_modules", "target", "build", "dist", ".venv", "venv", "env", "test", "tests", "scripts/test_fixtures"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            for name, line, snippet in scan_source(path):
                findings.append((path, name, line, snippet))
    return findings


GOOD_REPORT = """# Architecture review for synthetic-ar

- **Task / change:** PR #42
- **Skill:** `architecture-review`
- **Generated at:** 2026-06-13T20:00:00Z
- **Composite risk:** `high`

## Change set summary

The service moves a critical business operation from a
synchronous in-process call to an async event-driven design
using a new queue.

## Modules / files in scope

| Path / service | Role | Notes |
| --- | --- | --- |
| `order_service.py` | synchronous order processor | refactored to async |
| `event_publisher.py` | new module | publishes OrderPlaced event |
| `event_consumer.py` | new module | consumes event, updates inventory |

## Architectural dimensions

| Dimension | Verdict | Evidence |
| --- | --- | --- |
| Alignment with existing architecture | concern | event-driven is new pattern |
| Boundary clarity | finding | shared DB between modules |
| Coupling / cohesion | pass | modules have single responsibilities |
| Data ownership | finding | `orders` table shared between 2 modules |
| API contract stability | pass | external API unchanged |
| Failure modes | finding | no retry/poison-pill strategy for events |
| Scalability assumptions | pass | queue allows horizontal scale |
| Security boundaries | concern | no auth on event consumer |
| Observability needs | finding | no metrics on event processing |
| Deployment / runtime implications | concern | requires new broker dep |
| Reversibility | finding | data ownership change is hard to reverse |
| Migration path | pass | canary rollout possible |
| Over-engineering risk | concern | synchronous may have been sufficient |

## Findings

| ID | Severity | Category | File:lines / artifact | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| AR-001 | High | boundary | `order_service.py:42` | shared DB with consumer | open |
| AR-002 | High | failure | `event_consumer.py:1-50` | no retry strategy | open |
| AR-003 | Medium | observability | `event_consumer.py:1-50` | no metrics | open |
| AR-004 | High | data ownership | `db/schema.sql:23` | orders table shared | open |

### AR-001 — shared DB between producer and consumer

- **Severity:** High
- **Category:** boundary
- **Location:** `order_service.py:42`
- **Source skill:** `architecture-review`
- **Evidence:** `consumer` writes directly to `orders` table
- **Recommendation:** Use event-driven state ownership; consumer updates a derived state, not the source table
- **Routed to:** `architecture-decision`
- **Cross-reference:** AR-004

### AR-002 — no retry strategy

- **Severity:** High
- **Category:** failure
- **Location:** `event_consumer.py:1-50`
- **Source skill:** `architecture-review`
- **Evidence:** `process()` raises on error; no retry
- **Recommendation:** Add a DLQ + bounded retry
- **Routed to:** `backend-implementation`
- **Cross-reference:** none

### AR-003 — no metrics on event processing

- **Severity:** Medium
- **Category:** observability
- **Location:** `event_consumer.py:1-50`
- **Source skill:** `architecture-review`
- **Evidence:** no `Counter` or `Histogram` for events
- **Recommendation:** Add `events_processed_total`, `events_failed_total`, `event_processing_seconds`
- **Routed to:** `backend-implementation`
- **Cross-reference:** none

### AR-004 — orders table shared

- **Severity:** High
- **Category:** data ownership
- **Location:** `db/schema.sql:23`
- **Source skill:** `architecture-review`
- **Evidence:** `orders` table has writes from 2 modules
- **Recommendation:** Migrate to event-sourced state ownership
- **Routed to:** `architecture-decision`
- **Cross-reference:** AR-001

## ADR recommendation

**ADR required.** This change introduces a new pattern (event
sourcing) and a new shared-state model. The ADR must document
the data ownership decision and the failure-mode strategy.

## Review gates required

- **Architecture review board** — approve the data ownership change
- **Security review** — review the event consumer auth model

## Handoff

- **Handoff packet file:** `handoffs/test.md`
- **Target skill:** `architecture-decision`
- **Required next action:** Author ADR-0005 for event-sourced order state

## Cross-references

- Discovery: `discovery/repo-discovery.md`
- Handoff packet: `handoffs/test.md`

## Provenance

- Produced by `architecture-review` (draft).
"""


def self_test() -> tuple[bool, str]:
    import tempfile
    lines = []

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(GOOD_REPORT)
        good_path = Path(f.name)
    failures = check_report(good_path)
    if not failures:
        lines.append("  [ar-s1-good-report] PASS")
    else:
        lines.append(f"  [ar-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("**Composite risk:** `high`", "**Composite risk:** `unknown`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("risk" in f.lower() for f in failures):
        lines.append("  [ar-s2-invalid-risk] PASS (correctly flagged)")
    else:
        lines.append(f"  [ar-s2-invalid-risk] FAIL (should have flagged invalid risk)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("| Over-engineering", "| Underwater-basket-weaving")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("over-engineering" in f for f in failures):
        lines.append("  [ar-s3-missing-dimension] PASS (correctly flagged)")
    else:
        lines.append(f"  [ar-s3-missing-dimension] FAIL (should have flagged missing over-engineering)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("- **Severity:** High", "- **Severityzzzz:** High")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Severity" in f for f in failures):
        lines.append("  [ar-s4-finding-missing-field] PASS (correctly flagged)")
    else:
        lines.append(f"  [ar-s4-finding-missing-field] FAIL (should have flagged missing Severity)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("**ADR required.**", "TODO")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("ADR" in f for f in failures):
        lines.append("  [ar-s5-adr-not-justified] PASS (correctly flagged)")
    else:
        lines.append(f"  [ar-s5-adr-not-justified] FAIL (should have flagged unjustified ADR)")
    bad_path.unlink(missing_ok=True)

    test_code = '''
def process():
    password = "supersecret123"
    api_key = "abc123def456"
    return password
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    found_secret = any(f[0] == "hardcoded_secret" for f in findings)
    if found_secret:
        lines.append("  [ar-s6-source-scan-secret] PASS (found hardcoded secret)")
    else:
        lines.append(f"  [ar-s6-source-scan-secret] FAIL (should have found hardcoded secret; got: {findings})")
    test_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-architecture-review.py <report.md>", file=sys.stderr)
        print("       lint-architecture-review.py --self-test", file=sys.stderr)
        print("       lint-architecture-review.py --scan <repo_root>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--scan":
        repo = Path(sys.argv[2])
        if not repo.exists():
            print(f"[lint-architecture-review] FAIL  (not a directory: {repo})")
            sys.exit(66)
        findings = scan_repo(repo)
        if not findings:
            print(f"[lint-architecture-review] scan: no findings in {repo}")
            sys.exit(0)
        print(f"[lint-architecture-review] scan: {len(findings)} findings in {repo}")
        for path, name, line, snippet in findings:
            print(f"  {path}:{line}  {name}: {snippet}")
        sys.exit(1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-architecture-review] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-architecture-review] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-architecture-review] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
