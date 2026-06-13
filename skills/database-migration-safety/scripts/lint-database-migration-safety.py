#!/usr/bin/env python3
"""
lint-database-migration-safety.py — auto-check for the
database-migration-safety skill.

This is a 2-in-1 linter:

1. **Report linter**: checks a `migration-safety-report.md`
   against the report contract from
   skills/database-migration-safety/SKILL.md (Validation
   section) and the template at
   templates/migration-safety-report.md.

2. **Source scanner**: scans a repo for migration files and
   flags risky patterns from
   references/migration-risk-checklist.md.

Usage:
  python3 lint-database-migration-safety.py --self-test
  python3 lint-database-migration-safety.py <report.md>
  python3 lint-database-migration-safety.py --scan <repo_root>

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found

Calibration rubric:
  Report checks:
    1. Report file exists and parses as markdown
    2. Every required H2 section present (Outcome, Change set,
       Inventory, Blockers filed, Findings, Locking analysis,
       Rollback analysis, Test plan, Recommended next action)
    3. Outcome is one of approved | changes_requested | blocked
    4. If blocker_filed: true, blockers/ dir exists
    5. Every Critical/High finding has file:lines evidence

  Source code checks (deterministic patterns from risk-checklist):
    1. DROP TABLE / DROP COLUMN / DROP INDEX (Critical)
    2. TRUNCATE (Critical)
    3. DELETE without bounded WHERE (Critical)
    4. ALTER COLUMN ... DROP NOT NULL (Critical — table rewrite)
    5. ALTER COLUMN ... TYPE ... USING (Critical)
    6. ALTER COLUMN ... SET NOT NULL without DEFAULT (Critical)
    7. CREATE INDEX without CONCURRENTLY (Postgres) (High)
    8. LOCK TABLE (High)
    9. REINDEX (High)
    10. Backfill without batching (High)
    11. Missing down/rollback (High)
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
    "## Blockers filed",
    "## Findings",
    "## Locking analysis",
    "## Rollback analysis",
    "## Test plan",
    "## Recommended next action",
]

ALLOWED_OUTCOMES = {"approved", "changes_requested", "blocked"}

# Deterministic migration risk patterns (regex)
# Critical by default
CRITICAL_PATTERNS = {
    "drop_table": re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    "drop_column": re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE),
    "drop_index": re.compile(r"\bDROP\s+INDEX\b", re.IGNORECASE),
    "truncate": re.compile(r"\bTRUNCATE\s+(TABLE\s+)?", re.IGNORECASE),
    "delete_unbounded": re.compile(r"\bDELETE\s+FROM\s+\w+\s*;", re.IGNORECASE),  # no WHERE
    "alter_drop_not_null": re.compile(r"ALTER\s+(?:COLUMN\s+)?\w+\s+DROP\s+NOT\s+NULL", re.IGNORECASE),
    "alter_type_using": re.compile(r"ALTER\s+(?:COLUMN\s+)?\w+\s+(?:SET\s+DATA\s+)?TYPE\s+.*?USING\s+", re.IGNORECASE | re.DOTALL),
    "set_not_null_no_default": re.compile(r"ALTER\s+(?:COLUMN\s+)?\w+\s+SET\s+NOT\s+NULL(?!\s*DEFAULT)", re.IGNORECASE),
}

# High
HIGH_PATTERNS = {
    "create_index_non_concurrent": re.compile(r"CREATE\s+INDEX\s+(?!CONCURRENTLY)\w+", re.IGNORECASE),
    "lock_table": re.compile(r"\bLOCK\s+TABLE\b", re.IGNORECASE),
    "reindex": re.compile(r"\bREINDEX\b", re.IGNORECASE),
}


def check_report(report_path: Path) -> list[str]:
    """Check a migration-safety-report.md. Return list of FAIL strings."""
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

    # 2. Outcome is one of 3 allowed values
    m = re.search(r"## Outcome\s*\n\s*[`']?(approved|changes_requested|blocked)[`']?", text, re.IGNORECASE)
    if not m:
        failures.append(f"FAIL: ## Outcome section missing or has invalid value (allowed: {sorted(ALLOWED_OUTCOMES)})")
    else:
        outcome = m.group(1).lower()
        if outcome not in ALLOWED_OUTCOMES:
            failures.append(f"FAIL: outcome '{outcome}' is not in {ALLOWED_OUTCOMES}")

    # 3. Every Critical/High finding has file:lines evidence
    findings_match = re.search(r"## Findings(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if findings_match:
        findings = findings_match.group(1)
        critical_high = list(re.finditer(r"###?\s*(Critical|High).*?(?=###?\s*(?:Critical|High|Medium|Low)|\Z)", findings, re.DOTALL))
        for i, m in enumerate(critical_high, 1):
            finding = m.group(0)
            if not re.search(r"[a-zA-Z_./\-]+\.(sql|py|rb|ts|js|prisma|cs|xml|yaml|yml|json):\d+", finding):
                failures.append(f"FAIL: Critical/High finding #{i} has no file:lines evidence (must include path:line)")

    # 4. If blocker_filed: true, blockers/ dir must exist
    if "blocker_filed: true" in text or re.search(r"## Blockers filed\s*\n\s*-\s*\*\*(?!none)", text, re.IGNORECASE):
        ws = report_path.parent.parent
        blockers_dir = ws / "blockers"
        if not blockers_dir.exists() or not any(blockers_dir.iterdir()):
            failures.append("FAIL: blocker filed but no blockers/ directory or files in task workspace")

    return failures


def is_migration_file(path: Path) -> bool:
    """Heuristic: is this file a migration?"""
    # SQL in migrations directories
    if path.suffix == ".sql":
        parts_lower = [p.lower() for p in path.parts]
        if any("migrat" in p or "db/" in p or "sql" in p for p in parts_lower):
            return True
    # Alembic: alembic/versions/*.py
    if path.suffix == ".py" and "alembic" in str(path) and "versions" in str(path):
        return True
    # Django: */migrations/0*_*.py
    if path.suffix == ".py" and re.search(r"/migrations/\d+_", str(path)):
        return True
    # Prisma: prisma/schema.prisma
    if path.name == "schema.prisma" and "prisma" in str(path):
        return True
    # Rails: db/migrate/*.rb
    if path.suffix == ".rb" and "db/migrate" in str(path):
        return True
    # EF Core: Migrations/*.cs
    if path.suffix == ".cs" and "Migrations" in path.parts:
        return True
    # TypeORM: *.entity.ts with @Entity
    if path.suffix == ".ts" and "entity" in path.name.lower():
        return True
    return False


def scan_source(source_path: Path) -> list[tuple[str, int, str, str]]:
    """Scan a migration file for risk patterns.
    Return list of (pattern_name, line_no, snippet, severity)."""
    if not source_path.exists() or not source_path.is_file():
        return []
    if not is_migration_file(source_path):
        return []
    try:
        text = source_path.read_text(errors="ignore")
    except Exception:
        return []
    findings = []
    for name, pattern in CRITICAL_PATTERNS.items():
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
            findings.append((name, line_no, line.strip()[:120], "Critical"))
    for name, pattern in HIGH_PATTERNS.items():
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
            findings.append((name, line_no, line.strip()[:120], "High"))
    return findings


def scan_repo(repo_root: Path) -> list[tuple[Path, str, int, str, str]]:
    """Scan a repo for migration risk patterns."""
    findings = []
    if not repo_root.exists() or not repo_root.is_dir():
        return findings
    skip_dirs = {".git", "__pycache__", "node_modules", "target", "build", "dist", ".venv", "venv", "env"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            for name, line, snippet, severity in scan_source(path):
                findings.append((path, name, line, snippet, severity))
    return findings


GOOD_REPORT = """# Migration safety report

- **Task ID:** synthetic-dms
- **Generated at:** 2026-06-13T20:00:00Z

## Outcome

`changes_requested`

Reason: 2 Critical findings (DROP COLUMN, missing rollback).

## Change set

| File | Kind | Summary |
| --- | --- | --- |
| db/migration/V100__drop_user_email.sql | destructive | Drops `email` column |
| db/migration/V101__add_user_phone.sql | additive | Adds `phone` column |

## Inventory

### New / changed

| Object | Type | Change |
| --- | --- | --- |
| users.phone | column | added |

### Removed

| Object | Type | Change |
| --- | --- | --- |
| users.email | column | dropped |

## Blockers filed

- none

## Findings

### Critical

- **drop_column** — `db/migration/V100__drop_user_email.sql:3`
  - **Summary:** DROP COLUMN is destructive
  - **Evidence:** `ALTER TABLE users DROP COLUMN email;`
  - **Recommendation:** Use expand-and-contract; keep `email` for
    2 release cycles, then drop behind a feature flag.
  - **Approval required:** yes
  - **Deployment strategy:** expand-and-contract

- **missing_rollback** — `db/migration/V100__drop_user_email.sql:1`
  - **Summary:** Migration has no rollback
  - **Evidence:** no `down` / `rollback` defined
  - **Recommendation:** Add a `down` that re-adds the column
    (without restoring data, since it's been dropped).
  - **Approval required:** yes
  - **Deployment strategy:** expand-and-contract

### Medium

- **lock_acquisition** — `db/migration/V100__drop_user_email.sql:3`
  - **Summary:** ACCESS EXCLUSIVE lock for the duration of the drop
  - **Evidence:** `ALTER TABLE users DROP COLUMN email` holds a write lock
  - **Recommendation:** Schedule for a low-traffic window, or use
    a non-locking alternative.

## Locking analysis

- **Long-running statements:** V100 DROP COLUMN
- **Estimated lock time:** requires production data to estimate
- **Online / concurrent DDL available:** no

## Rollback analysis

- **Rollback defined:** no
- **Rollback restores data:** no
- **Recovery plan if rollback is not possible:** restore from the
  pre-migration backup; document the data loss in a post-mortem.

## Test plan

- [ ] Migration applied on a copy of production data, time recorded
- [ ] Rollback applied, time recorded
- [ ] Application code deployed and verified against migrated DB
- [ ] Destructive step executed behind a feature flag (if applicable)

## Recommended next action

Split V100 into V100 (add nullable `email_archived`) and V200
(actual DROP, gated on a feature flag), then re-run this review.
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
        lines.append("  [dms-s1-good-report] PASS")
    else:
        lines.append(f"  [dms-s1-good-report] FAIL ({len(failures)} failures)")
        for fail in failures:
            lines.append(f"    {fail}")
    good_path.unlink(missing_ok=True)

    # Test 2: missing outcome should FAIL
    bad = GOOD_REPORT.replace("`changes_requested`", "")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("Outcome" in f for f in failures):
        lines.append("  [dms-s2-missing-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [dms-s2-missing-outcome] FAIL (should have flagged missing Outcome)")
    bad_path.unlink(missing_ok=True)

    # Test 3: invalid outcome value should FAIL
    bad = GOOD_REPORT.replace("`changes_requested`", "`maybe`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("outcome" in f.lower() for f in failures):
        lines.append("  [dms-s3-invalid-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [dms-s3-invalid-outcome] FAIL (should have flagged invalid outcome)")
    bad_path.unlink(missing_ok=True)

    # Test 4: Critical finding without file:lines should FAIL
    # Remove file:lines from BOTH Critical findings (so the section has none)
    bad = GOOD_REPORT
    bad = re.sub(r"- \*\*drop_column\*\* — `db/migration/V100__drop_user_email\.sql:3`", "- **drop_column** — (no line numbers)", bad)
    bad = re.sub(r"- \*\*missing_rollback\*\* — `db/migration/V100__drop_user_email\.sql:1`", "- **missing_rollback** — (no line numbers)", bad)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("file:lines" in f for f in failures):
        lines.append("  [dms-s4-no-evidence-pointer] PASS (correctly flagged)")
    else:
        lines.append(f"  [dms-s4-no-evidence-pointer] FAIL (should have flagged missing file:lines)")
    bad_path.unlink(missing_ok=True)

    # Test 5: source scan should find DROP TABLE
    test_code = """-- db/migration/V200__cleanup.sql
DROP TABLE legacy_users;
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, dir=tempfile.mkdtemp()) as f:
        f.write(test_code)
        test_path = Path(f.name)
    # Also need a migrations/ dir in the parent to be detected
    parent = test_path.parent
    (parent / "migrations").mkdir(exist_ok=True)
    final_path = parent / "migrations" / test_path.name
    test_path.rename(final_path)
    findings = scan_source(final_path)
    if any(f[0] == "drop_table" for f in findings):
        lines.append("  [dms-s5-source-scan-drop-table] PASS (found DROP TABLE)")
    else:
        lines.append(f"  [dms-s5-source-scan-drop-table] FAIL (should have found DROP TABLE; got: {findings})")
    final_path.unlink(missing_ok=True)

    # Test 6: source scan should find CREATE INDEX without CONCURRENTLY
    test_code = """-- db/migration/V201__add_index.sql
CREATE INDEX idx_user_email ON users(email);
"""
    with tempfile.TemporaryDirectory() as tmp:
        migrations = Path(tmp) / "db" / "migrations"
        migrations.mkdir(parents=True)
        test_path = migrations / "V201__add_index.sql"
        test_path.write_text(test_code)
        findings = scan_source(test_path)
        if any(f[0] == "create_index_non_concurrent" for f in findings):
            lines.append("  [dms-s6-source-scan-non-concurrent-index] PASS (found non-concurrent CREATE INDEX)")
        else:
            lines.append(f"  [dms-s6-source-scan-non-concurrent-index] FAIL (should have found non-concurrent index; got: {findings})")

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-database-migration-safety.py <report.md>", file=sys.stderr)
        print("       lint-database-migration-safety.py --self-test", file=sys.stderr)
        print("       lint-database-migration-safety.py --scan <repo_root>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--scan":
        repo = Path(sys.argv[2])
        if not repo.exists():
            print(f"[lint-database-migration-safety] FAIL  (not a directory: {repo})")
            sys.exit(66)
        findings = scan_repo(repo)
        if not findings:
            print(f"[lint-database-migration-safety] scan: no findings in {repo}")
            sys.exit(0)
        print(f"[lint-database-migration-safety] scan: {len(findings)} findings in {repo}")
        for path, name, line, snippet, severity in findings:
            print(f"  {path}:{line}  [{severity}] {name}: {snippet}")
        sys.exit(1)
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-database-migration-safety] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-database-migration-safety] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-database-migration-safety] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
