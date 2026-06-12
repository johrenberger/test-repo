#!/usr/bin/env python3
"""
Linter for implementation-routing reports.

Enforces the contract defined in skills/implementation-orchestrator/SKILL.md
and skills/implementation-orchestrator/templates/implementation-routing-report.md.

Rules (10):
  1. Required frontmatter fields present (Task ID, Routing skill, Generated at)
  2. Acceptance criteria section is populated (not the placeholder)
  3. Inputs received section has Discovery artifact, Prior review, Known target modules
  4. Impacted layers table has all 7 rows (backend, frontend, integration,
     database/migration, infrastructure/deployment, documentation-only, mixed)
  5. Smallest impacted module section is populated
  6. Preflight gates section is populated (either gates or "none")
  7. Routing decision has a selected skill from the allowed set
  8. Risks section is populated (or "none identified")
  9. Handoff section has all 7 required fields
 10. No template placeholders left (no `<...>` template syntax)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

EXERCISE = Path("/data/.openclaw/workspace/tasks/2026-06-12-impl-orchestrator-exercise")  # for --self-test

ALLOWED_SKILLS = {
    "backend-implementation",
    "frontend-implementation",
    "integration-implementation",
    "database-migration-safety",
    "dependency-change-review",
    "architecture-review",
    "security-review",  # a preflight gate can also be the final routing
}
ALLOWED_LAYERS = {
    "backend", "frontend", "integration",
    "database/migration", "infrastructure/deployment",
    "documentation-only", "mixed",
}
ALLOWED_GATES = {
    "database-migration-safety",
    "dependency-change-review",
    "security-review",
    "architecture-review",
}
REQUIRED_SECTIONS = [
    "## Task",
    "## Acceptance criteria",
    "## Inputs received",
    "## Impacted layers",
    "## Smallest impacted module / subtree",
    "## Preflight gates required",
    "## Routing decision",
    "## Risks",
    "## Open blockers",
    "## Open approval gates",
    "## Handoff",
    "## Audit trail",
    "## Cross-references",
    "## Provenance",
]


def lint_report(path: Path) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: report does not exist: {path}"]
    content = path.read_text()
    lines = content.splitlines()

    # 1. Frontmatter (under ## Task)
    task_section = content.split("## Task")[1].split("##")[0]
    for field in ("**Task ID:**", "**Routing skill:**", "**Generated at:**"):
        if field not in task_section:
            issues.append(f"FAIL: missing frontmatter field '{field}' in ## Task section")

    # 2. Acceptance criteria populated
    ac_section = content.split("## Acceptance criteria")[1].split("##")[0]
    if "unclear or contradictory" in ac_section and "-" not in ac_section:
        issues.append("FAIL: acceptance criteria is the placeholder, not populated")
    if "-" not in ac_section and "\n  " not in ac_section:
        issues.append("FAIL: acceptance criteria has no bullet items")

    # 3. Inputs received
    ir_section = content.split("## Inputs received")[1].split("##")[0]
    for field in ("**Task description:**", "**Discovery artifact:**", "**Prior review findings:**", "**Known target modules:**"):
        if field not in ir_section:
            issues.append(f"FAIL: missing 'Inputs received' field '{field}'")

    # 4. Impacted layers: must have 7 rows
    il_section = content.split("## Impacted layers")[1].split("##")[0]
    for layer in ALLOWED_LAYERS:
        if f"| {layer} " not in il_section and f"| {layer} |" not in il_section:
            issues.append(f"FAIL: impacted layers table missing row for '{layer}'")
    # Each row should have 'yes' or 'no'
    for m in re.finditer(r"\|\s*([a-z/]+)\s*\|\s*(\w+)\s*\|", il_section):
        layer, yes_no = m.group(1), m.group(2)
        if layer in ALLOWED_LAYERS and yes_no not in ("yes", "no"):
            issues.append(f"FAIL: layer '{layer}' has 'Touched?' value '{yes_no}' (must be yes or no)")

    # 5. Smallest impacted module: at least one bullet or "none"
    sim_section = content.split("## Smallest impacted module / subtree")[1].split("##")[0]
    if "-" not in sim_section and "none" not in sim_section.lower():
        issues.append("FAIL: smallest impacted module section is empty")

    # 6. Preflight gates: populated
    pg_section = content.split("## Preflight gates required")[1].split("##")[0]
    if "-" not in pg_section:
        issues.append("FAIL: preflight gates section is empty")
    # If a gate is checked (has "- [ ]"), it should be from ALLOWED_GATES
    for m in re.finditer(r"- \[(?: |x)\]\s*`?(\w[\w-]*)`?", pg_section):
        gate = m.group(1)
        if gate == "none":
            continue
        if gate not in ALLOWED_GATES:
            issues.append(f"FAIL: preflight gate '{gate}' is not in {ALLOWED_GATES}")

    # 7. Routing decision
    rd_section = content.split("## Routing decision")[1].split("##")[0]
    m = re.search(r"\*\*Selected skill:\*\*\s*`?(\w[\w-]*)`?", rd_section)
    if not m:
        issues.append("FAIL: routing decision missing 'Selected skill' field")
    elif m.group(1) not in ALLOWED_SKILLS:
        issues.append(f"FAIL: selected skill '{m.group(1)}' is not in {ALLOWED_SKILLS}")

    # 8. Risks populated
    risks_section = content.split("## Risks")[1].split("##")[0]
    if "-" not in risks_section and "none identified" not in risks_section.lower():
        issues.append("FAIL: risks section is empty AND not marked 'none identified'")

    # 9. Handoff has 7 required fields
    handoff_section = content.split("## Handoff")[1].split("##")[0]
    for field in ("routing_report_path", "selected_skill", "selected_skill_rationale",
                  "target_modules", "preflight_gates_required", "discovery_artifact_path",
                  "acceptance_criteria"):
        if f"`{field}`" not in handoff_section and field not in handoff_section:
            issues.append(f"FAIL: handoff section missing required field '{field}'")

    # 10. No template placeholders left (rough check for <...> in body)
    body = content.split("## Provenance")[0]  # only check the report body
    # Skip the Audit trail section — the format itself contains example
    # placeholders like `<id>`, `<file>`, `<gate-id>` that name a
    # type of record, not a substitution placeholder.
    body_no_audit = body.split("## Audit trail")[0] if "## Audit trail" in body else body
    placeholders = re.findall(r"<([^<>]{3,})>", body_no_audit)
    # Filter out allowed placeholders
    for ph in placeholders:
        if "absolute path" in ph.lower() or "list, or" in ph.lower():
            continue
        issues.append(f"FAIL: unprocessed template placeholder '<{ph}>' in report body")

    return issues


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Linter for implementation-routing reports.")
    parser.add_argument("path", nargs="?", help="Single report file or directory of reports")
    parser.add_argument("--self-test", action="store_true", help="Run the canonical 5-scenario self-test")
    args = parser.parse_args()

    if args.self_test:
        report_dirs = sorted(d for d in EXERCISE.iterdir() if d.is_dir() and d.name.startswith("ios-"))
        if not report_dirs:
            print("no ios-s* directories found")
            return 1
        overall = True
        for d in report_dirs:
            report_path = d / "reports/implementation-routing-report.md"
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

    if not args.path:
        parser.print_help()
        return 64

    target = Path(args.path)
    if target.is_file():
        issues = lint_report(target)
        if not issues:
            print(f"[{target.name}] PASS")
            return 0
        for i in issues:
            print(f"    {i}")
        return 1
    if target.is_dir():
        reports = sorted(target.glob("**/implementation-routing-report.md"))
        if not reports:
            print(f"no implementation-routing-report.md files found under {target}")
            return 1
        overall = True
        for r in reports:
            issues = lint_report(r)
            if not issues:
                print(f"  [{r}] PASS")
            else:
                overall = False
                print(f"  [{r}] FAIL")
                for i in issues:
                    print(f"      {i}")
        return 0 if overall else 1
    parser.print_help()
    return 64


if __name__ == "__main__":
    sys.exit(main())
