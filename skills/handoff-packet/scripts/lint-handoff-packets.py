#!/usr/bin/env python3
"""
Linter for handoff-packet files.

Enforces the 14-field contract from skills/handoff-packet/SKILL.md
and skills/handoff-packet/templates/handoff-packet.md.

Rules:
  1. Filename matches <UTC-ts>-<source>-to-<target>.md
  2. All 14 numbered fields are present
  3. Required frontmatter fields present (Packet timestamp, Source
     agent, Target agent, Approval required)
  4. No obvious placeholders (<...>, TODO, TBD) without reason
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 14 required field titles (must match exactly)
# These match the actual template in skills/handoff-packet/templates/handoff-packet.md
REQUIRED_FIELDS = [
    "## 1. Task ID",
    "## 2. Source agent",
    "## 3. Target agent",
    "## 4. Objective",
    "## 5. Context summary",
    "## 6. Files read",
    "## 7. Files changed",
    "## 8. Commands run",
    "## 9. Validation results",
    "## 10. Decisions made",
    "## 11. Risks",
    "## 12. Blockers",
    "## 13. Required next action",
    "## 14. Approval required",
]
FRONTMATTER_FIELDS = [
    "**Date (UTC):**",
    "**From:**",
    "**To:**",
]
FILENAME_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}T(?:\d{2}-?\d{2}-?\d{2}Z))-([\w-]+)-to-([\w-]+)\.md$"
)
PLACEHOLDER_RE = re.compile(r"<(?!absolute path)([^<>]{3,})>")
TODO_RE = re.compile(r"\b(TODO|TBD|FIXME)\b")


def lint_packet(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: packet does not exist: {path}"]

    # 1. Filename
    m = FILENAME_RE.match(path.name)
    if not m:
        issues.append(
            f"FAIL: filename '{path.name}' does not match "
            "<UTC-ts>-<source>-to-<target>.md "
            "(e.g. 2026-06-12T03-45-00Z-source-to-target.md)"
        )

    content = path.read_text()
    lines = content.splitlines()

    # Frontmatter
    for field in FRONTMATTER_FIELDS:
        if field not in content:
            issues.append(f"FAIL: missing frontmatter field '{field}'")

    # 2. All 14 numbered fields
    for field in REQUIRED_FIELDS:
        if field not in content:
            issues.append(f"FAIL: missing required field '{field}'")

    # 3. Body fields must be populated (not just the header)
    for field in REQUIRED_FIELDS:
        if field not in content:
            continue
        section = content.split(field, 1)[1].split("## ", 1)[0]
        # Strip empty lines and check there's some content
        body = [l for l in section.split("\n") if l.strip()]
        if not body:
            issues.append(f"FAIL: '{field}' section is empty")

    # 4. No obvious placeholders (audit-trail format placeholders are allowed)
    audit_section = ""
    if "## 14. Audit trail" in content:
        audit_section = content.split("## 14. Audit trail", 1)[1]
    placeholders = PLACEHOLDER_RE.findall(content)
    for ph in placeholders:
        if "absolute path" in ph.lower():
            continue
        # audit-trail format placeholders: <id>, <file>, <gate-id>
        if f"<{ph}>" in audit_section and ph in ("id", "file", "gate-id"):
            continue
        issues.append(f"FAIL: unprocessed template placeholder '<{ph}>'")

    if TODO_RE.search(content):
        issues.append("FAIL: TODO/TBD/FIXME marker found in packet body")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Linter for handoff-packet files.")
    parser.add_argument("path", nargs="?", help="Single packet file or directory of packets")
    parser.add_argument("--self-test", action="store_true",
                        help="Run the canonical 3-scenario self-test (A3 exercise)")
    args = parser.parse_args()

    if args.self_test:
        # Backwards-compat: run the A3 exercise scenarios
        EXERCISE = Path("/data/.openclaw/workspace/tasks/2026-06-12-handoff-packet-exercise")
        scenarios = sorted(EXERCISE.glob("scenario-*/handoffs/*.md"))
        overall = True
        for p in scenarios:
            issues = lint_packet(p)
            if not issues:
                print(f"  [{p.parent.parent.name}] PASS  ({p.name})")
            else:
                overall = False
                print(f"  [{p.parent.parent.name}] FAIL  ({p.name})")
                for i in issues:
                    print(f"      {i}")
        print()
        if overall:
            print("OVERALL: PASS")
            return 0
        print("OVERALL: FAIL")
        return 1

    target = Path(args.path)
    if target.is_file():
        issues = lint_packet(target)
        if not issues:
            print(f"[{target.name}] PASS")
            return 0
        for i in issues:
            print(f"    {i}")
        return 1
    if target.is_dir():
        packets = sorted(target.glob("*.md"))
        if not packets:
            print(f"no .md files found under {target}")
            return 1
        overall = True
        for p in packets:
            issues = lint_packet(p)
            if not issues:
                print(f"  [{p.name}] PASS")
            else:
                overall = False
                print(f"  [{p.name}] FAIL")
                for i in issues:
                    print(f"      {i}")
        return 0 if overall else 1
    parser.print_help()
    return 64


if __name__ == "__main__":
    sys.exit(main())
