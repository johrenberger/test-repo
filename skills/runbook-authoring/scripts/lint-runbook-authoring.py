#!/usr/bin/env python3
"""
lint-runbook-authoring.py — auto-check for the
runbook-authoring skill.

This is a 2-in-1 linter:

1. **Report linter**: checks a `runbook-authoring-report.md`
   against the report contract from
   skills/runbook-authoring/SKILL.md (Validation section)
   and the template at
   templates/runbook-authoring-report.md.

2. **Runbook validator**: checks a `runbook.md` (the
   operational doc) against the runbook template
   contract.

Usage:
  python3 lint-runbook-authoring.py --self-test
  python3 lint-runbook-authoring.py <report.md>
  python3 lint-runbook-authoring.py --runbook <runbook.md>
  python3 lint-runbook-authoring.py --scan <repo_root>

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

# Required H2 sections for runbook-authoring-report
REPORT_REQUIRED_SECTIONS = [
    "## Inputs",
    "## Scope decision",
    "## Source evidence",
    "## Decisions made",
    "## Destructive steps",
    "## Cross-references",
    "## Handoff",
    "## Provenance",
]

# Required H2 sections for the runbook.md itself
RUNBOOK_REQUIRED_SECTIONS = [
    "## Purpose",
    "## Scope",
    "## Symptoms",
    "## Severity guidance",
    "## Prerequisites",
    "## Safe diagnostic",
    "## Mitigation",
    "## Rollback",
    "## Validation",
    "## Known risks",
    "## Owner",
    "## Cross-references",
]

# Destructive command patterns
DESTRUCTIVE_PATTERNS = [
    re.compile(r"\brm\s+-rf?\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bkubectl\s+delete\b", re.IGNORECASE),
    re.compile(r"\bterraform\s+destroy\b", re.IGNORECASE),
    re.compile(r"\brollback\b", re.IGNORECASE),
]


def check_report(report_path: Path) -> list[str]:
    """Check a runbook-authoring-report.md. Return list of FAIL strings."""
    failures = []
    if not report_path.exists():
        return [f"FAIL: report does not exist: {report_path}"]
    text = report_path.read_text()
    if not text.strip():
        return [f"FAIL: report is empty: {report_path}"]

    # 1. Required H2 sections (word-boundary match)
    for section in REPORT_REQUIRED_SECTIONS:
        pattern = re.escape(section) + r"\b"
        if not re.search(pattern, text, re.IGNORECASE):
            failures.append(f"FAIL: missing required section: {section}")

    # 2. Destructive steps section lists approval gates and rollbacks
    destructive_match = re.search(r"##\s+Destructive steps(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if destructive_match:
        section_text = destructive_match.group(1)
        if re.search(r"\b(rm\s+-rf|DELETE\s+FROM|DROP\s+TABLE|TRUNCATE|kubectl\s+delete|terraform\s+destroy)\b", section_text, re.IGNORECASE):
            # There are destructive commands; need an approval gate and rollback
            if not re.search(r"approval", section_text, re.IGNORECASE):
                failures.append("FAIL: destructive commands are listed but no approval gate is documented")
            if not re.search(r"rollback", section_text, re.IGNORECASE):
                failures.append("FAIL: destructive commands are listed but no rollback step is documented")

    # 3. Source evidence section has concrete artifacts
    evidence_match = re.search(r"##\s+Source evidence(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if evidence_match:
        section_text = evidence_match.group(1)
        # Should mention at least one of: incident, ADR, observability report
        if not re.search(r"\b(incident|adr|observability|triage|review)\b", section_text, re.IGNORECASE):
            failures.append("FAIL: Source evidence section is empty or vague (should cite incident/ADR/observability reports)")

    # 4. Cross-references section has actual links/references
    xref_match = re.search(r"##\s+Cross-references(.*?)(?=\n## |\Z)", text, re.DOTALL | re.IGNORECASE)
    if xref_match:
        section_text = xref_match.group(1)
        if not re.search(r"\b(report|adr|runbook|incident)\b", section_text, re.IGNORECASE):
            failures.append("FAIL: Cross-references section is empty or vague (should cite report/ADR/runbook/incident)")

    return failures


def check_runbook(runbook_path: Path) -> list[str]:
    """Check a runbook.md (the operational doc). Return list of FAIL strings."""
    failures = []
    if not runbook_path.exists():
        return [f"FAIL: runbook does not exist: {runbook_path}"]
    text = runbook_path.read_text()
    if not text.strip():
        return [f"FAIL: runbook is empty: {runbook_path}"]

    # 1. Required H2 sections
    for section in RUNBOOK_REQUIRED_SECTIONS:
        pattern = re.escape(section) + r"\b"
        if not re.search(pattern, text, re.IGNORECASE):
            failures.append(f"FAIL: missing required section: {section}")

    # 2. Commands are sourced (each command must have a `source:` annotation)
    # Look at all code blocks (backtick-fenced)
    code_block_pattern = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
    code_blocks = list(code_block_pattern.finditer(text))
    for i, m in enumerate(code_blocks, 1):
        block = m.group(1)
        # Look in the 300 chars BEFORE and 200 chars AFTER for source annotation
        start = m.start()
        end = m.end()
        surrounding = text[max(0, start - 300):min(len(text), end + 200)]
        if not re.search(r"(?i)(source:|sourced from|verified by|validated by|operator evidence|repo evidence)", surrounding):
            # Allow if the block is just a placeholder example
            if not re.search(r"(?i)example|placeholder|template", surrounding):
                failures.append(f"FAIL: code block #{i} has no source annotation nearby (need 'Source:' / 'verified by:' / 'sourced from:')")

    # 3. Destructive commands have approval gates
    for i, m in enumerate(code_blocks, 1):
        block = m.group(1)
        is_destructive = any(p.search(block) for p in DESTRUCTIVE_PATTERNS)
        if is_destructive:
            block_start = m.start()
            # Look in the 500 chars after the block for approval/rollback
            surrounding = text[max(0, block_start - 100):block_start + len(block) + 500]
            if not re.search(r"(?i)approval", surrounding):
                failures.append(f"FAIL: destructive code block #{i} has no approval gate within 500 chars after")
            if not re.search(r"(?i)rollback", surrounding):
                failures.append(f"FAIL: destructive code block #{i} has no rollback step within 500 chars after")

    return failures


GOOD_REPORT = """# Runbook authoring report for RB-2026-001

- **Task / change:** Create runbook for latency-spike
- **Skill:** `runbook-authoring`
- **Generated at:** 2026-06-13T20:00:00Z

## Inputs

- **System:** order-checkout service
- **Acceptance criteria:** all commands verified, destructive steps gated
- **Source evidence:** incident triage report INC-2026-001
- **Operator contact:** alice@oncall

## Scope decision

Single runbook for one failure mode (latency spike on order
checkout). Not splitting further; the runbook is ~30 commands
and 1 destructive step.

## Existing runbooks

- `runbooks/db-failover.md` (similar format)
- `runbooks/disk-cleanup.md` (similar format)

## Source evidence used

- Incident triage report INC-2026-001 (source: tasks/.../incident-triage-report.md)
- Observability review OR-2026-001 (source: tasks/.../observability-review-report.md)
- ADR-0005 (source: docs/adr/0005-event-sourced-orders.md)

## Decisions made during authoring

- Destructive step: `kubectl rollout undo` requires approval
  from on-call before execution.
- Diagnostic step: `kubectl logs` is safe (no approval needed).
- Runbook storage: `runbooks/latency-spike.md` (per existing
  convention).

## Destructive steps

### `kubectl rollout undo deployment/order-service`

- **Approval gate:** on-call (alice@oncall) must approve
- **Rollback step:** `kubectl rollout undo deployment/order-service --to-revision=2`
- **Source:** repo command verified in test environment

## Cross-references added

- ADR-0005 (event-sourced orders)
- Incident triage report INC-2026-001
- Observability review OR-2026-001

## Handoff

- **Handoff packet file:** `handoffs/test.md`
- **Target skill:** DevOps team
- **Required next action:** review runbook, schedule dry-run

## Provenance

- Produced by `runbook-authoring` (draft).
"""


GOOD_RUNBOOK = """# Runbook: latency-spike

## Purpose

Triage and mitigate latency spikes on the order-checkout
service.

## Scope

order-checkout service in production. EU region only.

## Symptoms

- p99 latency > 500ms (was 200ms)
- Order processing slow / timing out
- EU customers affected

## Severity guidance

SEV-2: significant user impact, partial service degradation.

## Prerequisites / access requirements

- kubectl access to production cluster
- PagerDuty access (for ack)
- on-call rotation member

## Safe diagnostic commands

Check current latency:

```bash
kubectl logs -l app=order-service --since=1h | grep "slow"
```

Source: operator evidence (verified in incident INC-2026-001).

## Mitigation options

Option 1: rollback to v2.2.9 (low risk, fast)

## Rollback / escalation steps

If mitigation fails:

1. Page on-call lead
2. Escalate to SEV-1
3. Notify status page

## Validation after mitigation

Verify latency is back to normal:

```bash
kubectl logs -l app=order-service --since=1m | grep "slow"
```

Source: operator evidence.

## Known risks

- Rollback may lose recent orders (v2.3.0 has new schema)
- Cache flush may cause brief spike

## Owner / team / contact

- Owner: alice@oncall
- Team: order-checkout

## Cross-references

- ADR-0005
- Incident INC-2026-001
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
        lines.append("  [rb-s1-good-report] PASS")
    else:
        lines.append(f"  [rb-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_path.unlink(missing_ok=True)

    # Test 2: destructive command without approval gate should FAIL
    bad = """# Bad

## Inputs

x

## Scope decision

x

## Source evidence used

incident triage report

## Decisions made

x

## Destructive steps

### `rm -rf /var/log/app/*`

- Rollback step: restore from backup
- Source: command

## Cross-references added

incident

## Handoff

handoff

## Provenance

x
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("approval" in f for f in failures):
        lines.append("  [rb-s2-destructive-no-approval] PASS (correctly flagged)")
    else:
        lines.append(f"  [rb-s2-destructive-no-approval] FAIL (should have flagged missing approval)")
    bad_path.unlink(missing_ok=True)

    # Test 3: empty source evidence should FAIL
    bad = GOOD_REPORT.replace("- Incident triage report INC-2026-001 (source: tasks/.../incident-triage-report.md)\n- Observability review OR-2026-001 (source: tasks/.../observability-review-report.md)\n- ADR-0005 (source: docs/adr/0005-event-sourced-orders.md)", "(empty)")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Source evidence" in f for f in failures):
        lines.append("  [rb-s3-empty-source-evidence] PASS (correctly flagged)")
    else:
        lines.append(f"  [rb-s3-empty-source-evidence] FAIL (should have flagged empty source evidence)")
    bad_path.unlink(missing_ok=True)

    # Test 4: empty cross-references should FAIL
    bad = GOOD_REPORT.replace("- ADR-0005 (event-sourced orders)\n- Incident triage report INC-2026-001\n- Observability review OR-2026-001", "(empty)")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Cross-references" in f for f in failures):
        lines.append("  [rb-s4-empty-cross-refs] PASS (correctly flagged)")
    else:
        lines.append(f"  [rb-s4-empty-cross-refs] FAIL (should have flagged empty cross-references)")
    bad_path.unlink(missing_ok=True)

    # Test 5: missing required section should FAIL
    bad = GOOD_REPORT.replace("## Handoff", "## Pass-off")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Handoff" in f for f in failures):
        lines.append("  [rb-s5-missing-section] PASS (correctly flagged)")
    else:
        lines.append(f"  [rb-s5-missing-section] FAIL (should have flagged missing Handoff)")
    bad_path.unlink(missing_ok=True)

    # Test 6: well-formed runbook should PASS
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(GOOD_RUNBOOK)
        good_runbook = Path(f.name)
    failures = check_runbook(good_runbook)
    if not failures:
        lines.append("  [rb-s6-good-runbook] PASS")
    else:
        lines.append(f"  [rb-s6-good-runbook] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_runbook.unlink(missing_ok=True)

    # Test 7: runbook missing rollback section should FAIL
    bad = GOOD_RUNBOOK.replace("## Rollback / escalation steps", "## Rollbackzzz")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_runbook(bad_path)
    if failures and any("Rollback" in f for f in failures):
        lines.append("  [rb-s7-runbook-missing-rollback] PASS (correctly flagged)")
    else:
        lines.append(f"  [rb-s7-runbook-missing-rollback] FAIL (should have flagged missing Rollback)")
    bad_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-runbook-authoring.py <report.md>", file=sys.stderr)
        print("       lint-runbook-authoring.py --self-test", file=sys.stderr)
        print("       lint-runbook-authoring.py --runbook <runbook.md>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--runbook":
        runbook_path = Path(sys.argv[2])
        if not runbook_path.exists():
            print(f"[lint-runbook-authoring] FAIL  (file not found: {runbook_path})")
            sys.exit(66)
        failures = check_runbook(runbook_path)
        if not failures:
            print(f"[lint-runbook-authoring] PASS  ({runbook_path})")
            sys.exit(0)
        else:
            print(f"[lint-runbook-authoring] FAIL  ({runbook_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-runbook-authoring] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-runbook-authoring] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-runbook-authoring] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
