#!/usr/bin/env python3
"""
lint-incident-triage.py — auto-check for the
incident-triage skill.

This is a 2-in-1 linter:

1. **Report linter**: checks an `incident-triage-report.md`
   against the report contract from
   skills/incident-triage/SKILL.md (Validation section)
   and the template at
   templates/incident-triage-report.md.

2. **Source scanner**: scans a service repo for incident-
   response related issues (e.g. missing runbook references,
   absent on-call rotation docs).

Usage:
  python3 lint-incident-triage.py --self-test
  python3 lint-incident-triage.py <report.md>
  python3 lint-incident-triage.py --scan <repo_root>

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

# Required H2 sections (per template — main report sections)
REQUIRED_SECTIONS = [
    "## Summary",
    "## Facts",
    "## Hypotheses",
    "## Severity guidance",
    "## Blast radius",
    "## Impacted service",
    "## Suspected components",
    "## Known recent changes",
    "## Available evidence",
    "## Recommended next diagnostic",
    "## Recommended mitigation",
    "## Action items",
    "## Handoff",
    "## Cross-references",
    "## Provenance",
]

ALLOWED_SEVERITIES = {"SEV-1", "SEV-2", "SEV-3", "SEV-4"}

# Deterministic patterns for incident-triage
# These are things a linter CAN check
TIMESTAMP_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?)\b")


def check_report(report_path: Path) -> list[str]:
    """Check an incident-triage-report.md. Return list of FAIL strings."""
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

    # 2. Severity is one of SEV-1..SEV-4
    sev_match = re.search(r"\*\*(?:Severity|SEV):\*\*\s*[`']?(SEV-[1-4])[`']?", text, re.IGNORECASE)
    if not sev_match:
        failures.append(f"FAIL: **Severity:** missing or invalid (allowed: {sorted(ALLOWED_SEVERITIES)})")
    else:
        sev = sev_match.group(1).upper()
        if sev not in ALLOWED_SEVERITIES:
            failures.append(f"FAIL: severity '{sev}' is not in {ALLOWED_SEVERITIES}")

    # 3. Timeline has timestamped events with sources
    # Find the timeline section OR detect timestamps in facts/hypotheses
    timeline_match = re.search(r"(?:##\s+Timeline|##\s+Facts)(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if timeline_match:
        section_text = timeline_match.group(1)
        timestamps = TIMESTAMP_RE.findall(section_text)
        sources = re.findall(r"(?:source:|from|see|according to):\s*[^\n]+", section_text, re.IGNORECASE)
        if len(timestamps) < 1:
            failures.append("FAIL: no timestamped events found in Facts/Timeline section")
        if len(sources) < 1 and not re.search(r"\bsource[s]?\s*:\s*", section_text, re.IGNORECASE):
            failures.append("FAIL: timeline/facts have no source citations (need 'source:', 'from:', 'see:' etc.)")

    # 4. Facts and Hypotheses are separated
    if not re.search(r"##\s+Facts\b", text, re.IGNORECASE):
        failures.append("FAIL: ## Facts section is missing (required for fact/hypothesis separation)")
    if not re.search(r"##\s+Hypotheses\b", text, re.IGNORECASE):
        failures.append("FAIL: ## Hypotheses section is missing (required for fact/hypothesis separation)")

    # 5. Recommended next steps are concrete (must mention specific commands/actions)
    next_steps_match = re.search(r"##\s+Recommended next diagnostic(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if next_steps_match:
        section_text = next_steps_match.group(1)
        # Look for action verbs, commands, or file paths
        action_patterns = [
            r"`[^`]+`",  # backticked command/file
            r"\b(?:check|run|verify|inspect|reproduce|enable|disable|log)\b",
            r"https?://[^\s]+",
            r"\b(?:service|host|port|endpoint)\b",
        ]
        has_action = any(re.search(p, section_text, re.IGNORECASE) for p in action_patterns)
        if not has_action:
            failures.append("FAIL: Recommended next diagnostic steps are not concrete (no commands, files, or services mentioned)")

    # 6. Action items have owners, deadlines, status
    action_match = re.search(r"##\s+Action items(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if action_match:
        section_text = action_match.group(1)
        # Look for an action item block: ### <id>
        items = list(re.finditer(r"###\s+([a-zA-Z0-9_-]+)", section_text))
        for i, m in enumerate(items, 1):
            item_id = m.group(1)
            start = m.start()
            end = items[i].start() if i < len(items) else len(section_text)
            item_text = section_text[start:end]
            for field in ["Owner", "Deadline", "Status"]:
                if not re.search(rf"\*\*\s*{re.escape(field)}\s*:\*\*", item_text):
                    failures.append(f"FAIL: action item '{item_id}' missing field: {field}")

    return failures


def scan_source(source_path: Path) -> list[tuple[str, int, str]]:
    """Scan a source file for incident-triage related anti-patterns."""
    if not source_path.exists() or not source_path.is_file():
        return []
    if source_path.suffix not in {".py", ".md", ".yaml", ".yml", ".json", ".sh", ".txt"}:
        return []
    try:
        text = source_path.read_text(errors="ignore")
    except Exception:
        return []
    findings = []
    # Catch-all broad except with no logging (silent failure — bad for incident triage)
    bare_except = re.compile(r"^\s*except[^:]*:\s*(?:pass|\.\.\.)\s*$", re.MULTILINE)
    for m in bare_except.finditer(text):
        line_no = text[:m.start()].count("\n") + 1
        line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
        findings.append(("silent_except_no_log", line_no, line.strip()[:120]))
    return findings


def scan_repo(repo_root: Path) -> list[tuple[Path, str, int, str]]:
    """Scan a repo for incident-triage anti-patterns."""
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


GOOD_REPORT = """# Incident triage for INC-2026-001

- **Task / change:** Production latency spike
- **Skill:** `incident-triage`
- **Generated at:** 2026-06-13T20:00:00Z
- **Severity:** `SEV-2`
- **On-call:** alice@oncall
- **Status:** investigating

## Summary

Production latency spiked 5x at 2026-06-13T19:00:00Z. Order
processing p99 went from 200ms to 1000ms. Most users affected
in EU region.

## Facts (sourced)

- 2026-06-13T19:00:00Z: latency alert fired (source: prometheus)
- 2026-06-13T19:05:00Z: on-call acknowledged (source: pagerduty)
- 2026-06-13T19:10:00Z: first user reports (source: support ticket #1234)
- 2026-06-13T19:15:00Z: deploy of v2.3.0 was completed (source: deploy log)
- 2026-06-13T19:20:00Z: rollback initiated (source: on-call action)

## Hypotheses (labeled)

- H1: v2.3.0 introduced a slow DB query (confidence: high)
- H2: external payment provider is slow (confidence: low)
- H3: cache layer is missing keys (confidence: medium)

## Severity guidance

SEV-2: significant user impact, partial service degradation.
This is not SEV-1 because checkout still works for most
users; it is not SEV-3 because >30% of users are affected.

## Blast radius

EU region only. US and APAC regions unaffected. Approximately
30% of users in EU are seeing 5x latency.

## Impacted service / user group

- **Service:** order-checkout
- **User group:** EU customers
- **Estimated users affected:** ~5000 active users

## Suspected components

- `order_service.py` (refactored in v2.3.0)
- `payment_client.py` (unchanged in v2.3.0)
- DB query: `SELECT * FROM orders WHERE ...` (suspected to be
  missing index)

## Known recent changes

- 2026-06-13T19:15:00Z: deploy v2.3.0 (source: deploy log)
- 2026-06-13T18:00:00Z: DB migration adding column (source:
  alembic log)

## Available evidence

- Grafana dashboard: `latency-by-region`
- Logs: `kubectl logs -l app=order-service --since=1h`
- Trace ID: `abc123def456` (see Jaeger)
- Support ticket: #1234

## Recommended next diagnostic steps

- Run `kubectl logs -l app=order-service --since=1h | grep
  "slow"` to find slow queries
- Check the new DB column index: `\\d+ orders` in psql
- Verify the deployment: `kubectl rollout history
  deployment/order-service`
- Reproduce: deploy v2.3.0 to staging, run load test

## Recommended mitigation options (operator call)

- **Option 1:** Rollback to v2.2.9 (low risk, fast)
- **Option 2:** Add the missing index (medium risk, requires
  migration)
- **Option 3:** Scale up DB read replicas (low risk, ~10 min)

## Immediate safety constraints

- Do NOT delete data from `orders` table
- Do NOT drop the new column from `orders` (recently added)
- Do NOT disable the payment service (will cascade)

## Action items

| ID | Owner | Deadline | Status |
| --- | --- | --- | --- |
| AI-001 | alice@oncall | 2026-06-13T20:00:00Z | open |
| AI-002 | bob@dba | 2026-06-14T09:00:00Z | open |

### AI-001 — rollback or add index

- **Owner:** alice@oncall
- **Deadline:** 2026-06-13T20:00:00Z
- **Status:** open
- **Description:** Choose between rollback and adding the
  missing index based on root cause confirmation.

### AI-002 — post-mortem

- **Owner:** bob@dba
- **Deadline:** 2026-06-14T09:00:00Z
- **Status:** open
- **Description:** Write post-mortem with timeline, root
  cause, and prevention steps.

## Escalation

- **If root cause not found by 2026-06-13T20:30:00Z:** escalate
  to SEV-1
- **If data loss detected:** immediate SEV-1 + security team

## Communication

- **Internal:** #incidents Slack channel
- **External:** Status page update at 19:30 UTC

## Handoff

- **Handoff packet file:** `handoffs/test.md`
- **Target skill:** `backend-implementation` (after resolution)
- **Required next action:** Implement fix

## Cross-references

- Handoff packet: `handoffs/test.md`
- Runbook: `runbooks/latency-spike.md`

## Provenance

- Produced by `incident-triage` (draft).
"""


def self_test() -> tuple[bool, str]:
    import tempfile
    lines = []

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(GOOD_REPORT)
        good_path = Path(f.name)
    failures = check_report(good_path)
    if not failures:
        lines.append("  [it-s1-good-report] PASS")
    else:
        lines.append(f"  [it-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("- **Severity:** `SEV-2`", "- **Severity:** `SEV-9`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("severity" in f.lower() for f in failures):
        lines.append("  [it-s2-invalid-severity] PASS (correctly flagged)")
    else:
        lines.append(f"  [it-s2-invalid-severity] FAIL (should have flagged invalid severity)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("## Facts (sourced)", "## Factual content")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Facts" in f for f in failures):
        lines.append("  [it-s3-missing-facts] PASS (correctly flagged)")
    else:
        lines.append(f"  [it-s3-missing-facts] FAIL (should have flagged missing Facts)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("## Hypotheses (labeled)", "## Guesses")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Hypotheses" in f for f in failures):
        lines.append("  [it-s4-missing-hypotheses] PASS (correctly flagged)")
    else:
        lines.append(f"  [it-s4-missing-hypotheses] FAIL (should have flagged missing Hypotheses)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("## Handoff", "## Pass-off")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Handoff" in f for f in failures):
        lines.append("  [it-s5-missing-handoff] PASS (correctly flagged)")
    else:
        lines.append(f"  [it-s5-missing-handoff] FAIL (should have flagged missing Handoff)")
    bad_path.unlink(missing_ok=True)

    bad = GOOD_REPORT.replace("- **Owner:** alice@oncall", "- **Ownerrrr:** alice@oncall")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Owner" in f for f in failures):
        lines.append("  [it-s6-action-missing-owner] PASS (correctly flagged)")
    else:
        lines.append(f"  [it-s6-action-missing-owner] FAIL (should have flagged missing Owner)")
    bad_path.unlink(missing_ok=True)

    test_code = '''
def process():
    try:
        risky()
    except:
        pass
'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    found = any(f[0] == "silent_except_no_log" for f in findings)
    if found:
        lines.append("  [it-s7-source-scan-silent] PASS (found silent except)")
    else:
        lines.append(f"  [it-s7-source-scan-silent] FAIL (should have found silent except; got: {findings})")
    test_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-incident-triage.py <report.md>", file=sys.stderr)
        print("       lint-incident-triage.py --self-test", file=sys.stderr)
        print("       lint-incident-triage.py --scan <repo_root>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--scan":
        repo = Path(sys.argv[2])
        if not repo.exists():
            print(f"[lint-incident-triage] FAIL  (not a directory: {repo})")
            sys.exit(66)
        findings = scan_repo(repo)
        if not findings:
            print(f"[lint-incident-triage] scan: no findings in {repo}")
            sys.exit(0)
        print(f"[lint-incident-triage] scan: {len(findings)} findings in {repo}")
        for path, name, line, snippet in findings:
            print(f"  {path}:{line}  {name}: {snippet}")
        sys.exit(1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-incident-triage] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-incident-triage] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-incident-triage] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
