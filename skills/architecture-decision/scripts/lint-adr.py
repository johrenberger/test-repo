#!/usr/bin/env python3
"""
lint-adr.py — auto-check for the architecture-decision skill.

Enforces the ADR contract from
skills/architecture-decision/SKILL.md (Validation section) and
the template at skills/architecture-decision/templates/adr.md.

Rules (8):
  1. Title heading: starts with "# ADR-NNNN: <title>"
  2. Frontmatter (ADR ID, Status, Date, Task, Deciders) all present
  3. Status is one of {proposed, accepted, superseded, rejected}
  4. "## Context" section is populated
  5. "## Decision" section is populated
  6. "## Options considered" has a table with at least 2 rows
  7. "## Consequences" section is populated
  8. No template placeholders left (no `<...>` template syntax)

Usage:
  python3 lint-adr.py <adr_file>
  python3 lint-adr.py <directory>          # lint all *-adr.md files
  python3 lint-adr.py --self-test

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_STATUSES = {"proposed", "accepted", "superseded", "rejected"}
REQUIRED_FRONTMATTER = [
    "**ADR ID:**",
    "**Status:**",
    "**Date:**",
    "**Task:**",
    "**Deciders:**",
]
REQUIRED_SECTIONS = [
    "## Context",
    "## Decision",
    "## Options considered",
    "## Consequences",
]


def lint_adr(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: ADR does not exist: {path}"]
    content = path.read_text()
    lines = content.splitlines()

    # 1. Title heading
    first_non_blank = next((l for l in lines if l.strip()), "")
    if not re.match(r"^# ADR-\d+:", first_non_blank):
        issues.append(
            f"FAIL: title must start with '# ADR-NNNN: <title>' (got: '{first_non_blank[:60]}...')"
        )

    # 2. Frontmatter fields
    for field in REQUIRED_FRONTMATTER:
        if field not in content:
            issues.append(f"FAIL: missing frontmatter field '{field}'")

    # 3. Status is allowed
    m = re.search(r"\*\*Status:\*\*\s*`?(\w+)`?", content)
    if m and m.group(1) not in ALLOWED_STATUSES:
        issues.append(
            f"FAIL: status '{m.group(1)}' not in {sorted(ALLOWED_STATUSES)}"
        )

    # 4-7. Required sections populated
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"FAIL: missing section '{section}'")
            continue
        # Get the section body
        body = content.split(section, 1)[1].split("##", 1)[0]
        # Strip the heading line
        body_lines = [l for l in body.splitlines() if l.strip()]
        if len(body_lines) < 1:
            issues.append(f"FAIL: section '{section}' is empty")

    # 6. Options table has at least 2 rows
    if "## Options considered" in content:
        options_section = content.split("## Options considered", 1)[1].split("##", 1)[0]
        table_rows = [l for l in options_section.splitlines() if l.startswith("|") and "---" not in l]
        if len(table_rows) < 3:  # header + at least 2 option rows
            issues.append(
                f"FAIL: '## Options considered' must have a table with at least 2 option rows (got {len(table_rows) - 1} rows)"
            )
    # else: already reported by REQUIRED_SECTIONS check above

    # 8. No template placeholders left
    body_only = content.split("## Provenance")[0] if "## Provenance" in content else content
    placeholders = re.findall(r"<[A-Z][A-Z_-]*[A-Z]>", body_only)
    if placeholders:
        issues.append(
            f"FAIL: template placeholders left: {', '.join(sorted(set(placeholders)))}"
        )

    return issues


def run_self_test() -> tuple[bool, str]:
    """Run the canonical 5-scenario self-test."""
    import shutil
    tmp = Path("/tmp/lint-adr-self-test")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()

    # Good ADR
    good = tmp / "good-adr.md"
    good.write_text("""# ADR-0001: Use PostgreSQL for the user service

- **ADR ID:** ADR-0001
- **Status:** `accepted`
- **Date:** 2026-06-14
- **Task:** TASK-2026-001
- **Deciders:** ARCHITECT_AGENT

## Context

The user service needs a durable, transactional store with strong
referential integrity. We expect ~10K writes/sec at peak.

## Decision

We will use PostgreSQL 15 with read replicas for the user service,
because it provides the ACID guarantees and replication topology
that match the workload profile.

## Options considered

| Option | Summary | Verdict |
| --- | --- | --- |
| PostgreSQL 15 | ACID, JSON, read replicas | chosen |
| MongoDB | Flexible schema, no joins | rejected |
| DynamoDB | Serverless, pay-per-request | rejected |

## Consequences

What becomes easier:

- Strong consistency for user data

What becomes harder:

- Schema migrations require downtime coordination
""")

    # Bad ADR 1: missing Status
    bad1 = tmp / "bad1-missing-status.md"
    bad1.write_text("""# ADR-0002: Use Redis for caching

- **ADR ID:** ADR-0002
- **Date:** 2026-06-14
- **Task:** TASK-2026-002
- **Deciders:** ARCHITECT_AGENT

## Context

We need a cache layer.

## Decision

We will use Redis.

## Options considered

| Option | Summary | Verdict |
| --- | --- | --- |
| Redis | In-memory, fast | chosen |
| Memcached | Simpler, but no persistence | rejected |

## Consequences

Faster reads.
""")

    # Bad ADR 2: invalid status
    bad2 = tmp / "bad2-invalid-status.md"
    bad2.write_text("""# ADR-0003: Use Kafka

- **ADR ID:** ADR-0003
- **Status:** `maybe`
- **Date:** 2026-06-14
- **Task:** TASK-2026-003
- **Deciders:** ARCHITECT_AGENT

## Context

Need a message bus.

## Decision

We will use Kafka.

## Options considered

| Option | Summary | Verdict |
| --- | --- | --- |
| Kafka | High throughput | chosen |
| RabbitMQ | Lower throughput, simpler | rejected |

## Consequences

High throughput.
""")

    # Bad ADR 3: missing sections
    bad3 = tmp / "bad3-missing-section.md"
    bad3.write_text("""# ADR-0004: Use gRPC

- **ADR ID:** ADR-0004
- **Status:** `proposed`
- **Date:** 2026-06-14
- **Task:** TASK-2026-004
- **Deciders:** ARCHITECT_AGENT

## Context

We need RPC.

## Decision

We will use gRPC.
""")

    # Bad ADR 4: leftover placeholders
    bad4 = tmp / "bad4-placeholders.md"
    bad4.write_text("""# ADR-0005: Use OAuth2

- **ADR ID:** ADR-0005
- **Status:** `proposed`
- **Date:** 2026-06-14
- **Task:** TASK-2026-005
- **Deciders:** ARCHITECT_AGENT

## Context

We need <AUTH-PROVIDER> for authentication.

## Decision

We will use <AUTH-PROVIDER>.

## Options considered

| Option | Summary | Verdict |
| --- | --- | --- |
| OAuth2 | Standard | chosen |
| Custom | Flexible | rejected |

## Consequences

Standard auth flow.
""")

    tests = [
        (good, "ads-s1-good-adr", True),
        (bad1, "ads-s2-missing-status", False),
        (bad2, "ads-s3-invalid-status", False),
        (bad3, "ads-s4-missing-section", False),
        (bad4, "ads-s5-placeholders", False),
    ]
    all_pass = True
    output_lines = []
    for path, label, should_pass in tests:
        issues = lint_adr(path)
        passed = (not issues) == should_pass
        mark = "PASS" if passed else "FAIL"
        output_lines.append(f"  [{label}] {mark}")
        if not passed:
            all_pass = False
            for issue in issues:
                output_lines.append(f"    {issue}")

    shutil.rmtree(tmp)
    return all_pass, "\n".join(output_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Linter for ADR files")
    parser.add_argument("path", nargs="?", help="ADR file or directory")
    parser.add_argument("--self-test", action="store_true", help="Run the canonical 5-scenario self-test")
    args = parser.parse_args()

    if args.self_test:
        ok, out = run_self_test()
        print(out)
        print()
        print("OVERALL: PASS" if ok else "OVERALL: FAIL")
        return 0 if ok else 1

    if not args.path:
        print("usage: lint-adr.py <adr_file_or_dir> | --self-test", file=sys.stderr)
        return 64

    target = Path(args.path)
    if not target.exists():
        print(f"FAIL: path does not exist: {target}", file=sys.stderr)
        return 66

    paths = [target] if target.is_file() else sorted(target.glob("**/*-adr.md"))
    if not paths:
        print(f"no *-adr.md files found under {target}")
        return 1

    overall_pass = True
    for p in paths:
        issues = lint_adr(p)
        if issues:
            print(f"[{p}] FAIL")
            for i in issues:
                print(f"  {i}")
            overall_pass = False
        else:
            print(f"[{p}] PASS")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
