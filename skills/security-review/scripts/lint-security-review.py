#!/usr/bin/env python3
"""
lint-security-review.py — auto-check for the
security-review skill.

This is a 2-in-1 linter:

1. **Report linter**: checks a `security-review-report.md` against
   the report contract from
   skills/security-review/SKILL.md (Validation section).

2. **Source-code scanner**: scans a repo for security findings
   using regex rules from the 3 references/ files. This is
   what the security-review agent does manually, but automated.

Usage:
  python3 lint-security-review.py --self-test
  python3 lint-security-review.py <report.md>
  python3 lint-security-review.py --scan <repo_root>
  python3 lint-security-review.py --check-source <file.py>

Exit codes:
  0  all checks pass (or self-test passes)
  1  one or more checks fail
  64 bad usage
  66 file not found

This is the auto-check the `validated` definition requires
for the security-review skill.

Calibration rubric:
  Report checks (from SKILL.md "Validation" section):
    1. Report file exists and parses as markdown
    2. Every Critical/High finding has file:lines evidence
    3. outcome is one of approved | changes_requested | blocked
    4. If blocker filed, blocker_filed: true and blocker file exists

  Source code checks (deterministic patterns from references/):
    1. Hardcoded credentials (AWS keys, API tokens, passwords)
    2. SQL injection sinks (string-concatenated SQL)
    3. Command injection sinks (shell=True, os.system, subprocess with user input)
    4. Insecure deserialization (pickle, yaml.load, marshal)
    5. Weak crypto (md5, sha1 for security, ECB mode)
    6. Eval/exec on user input
    7. Hardcoded private keys (PEM headers)
    8. Debug mode in production (DEBUG=True, Flask debug, etc.)
"""
from __future__ import annotations
import re
import sys
import json
import subprocess
from pathlib import Path

# Required H2 sections (per template)
REQUIRED_SECTIONS = [
    "## Scope",
    "## Evidence reviewed",
    "## Findings",
    "## Outcome",
    "## Recommended next action",
]

ALLOWED_OUTCOMES = {"approved", "changes_requested", "blocked"}

# Deterministic security patterns (regex)
# These are what a linter CAN check; the human review covers
# business logic, context-specific authz, etc.
SECURITY_PATTERNS = {
    # Hardcoded credentials
    "hardcoded_aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "hardcoded_private_key": re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "hardcoded_password": re.compile(r"(?i)(password|passwd|secret|api_key|api-key|apikey|token)\s*=\s*['\"][^'\"]{4,}['\"]"),
    # SQL injection
    "sql_injection": re.compile(r"(execute|cursor\.execute)\s*\(\s*['\"].*?%s.*?['\"]\s*%\s*"),
    "sql_concat": re.compile(r"(SELECT|INSERT|UPDATE|DELETE).*?['\"].*?\+\s*[a-zA-Z_]"),
    # Command injection
    "shell_true": re.compile(r"subprocess\.(call|run|Popen)\([^)]*shell\s*=\s*True"),
    "os_system": re.compile(r"os\.system\s*\(\s*['\"]"),
    # Insecure deserialization
    "pickle_loads": re.compile(r"pickle\.loads?\s*\("),
    "yaml_load": re.compile(r"yaml\.load\s*\("),  # without Loader=SafeLoader
    "marshal_load": re.compile(r"marshal\.loads?\s*\("),
    # Weak crypto
    "md5_usage": re.compile(r"hashlib\.md5\s*\(|Crypto\.Hash\.MD5"),
    "sha1_usage": re.compile(r"hashlib\.sha1\s*\("),
    "ecb_mode": re.compile(r"AES\.new\([^)]*AES\.MODE_ECB\)"),
    # Eval/exec
    "eval_call": re.compile(r"\beval\s*\(\s*[a-zA-Z_]"),
    "exec_call": re.compile(r"\bexec\s*\(\s*[a-zA-Z_]"),
    # Debug mode
    "flask_debug": re.compile(r"app\.run\([^)]*debug\s*=\s*True"),
    "django_debug": re.compile(r"DEBUG\s*=\s*True"),
}


def check_report(report_path: Path) -> list[str]:
    """Check a security-review-report.md. Return list of FAIL strings."""
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

    # 2. outcome is one of 3 allowed values
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
        # Find all Critical and High findings (use finditer to get the full match, not just the captured group)
        critical_high = list(re.finditer(r"###?\s*(Critical|High).*?(?=###?\s*(?:Critical|High|Medium|Low)|\Z)", findings, re.DOTALL))
        for i, m in enumerate(critical_high, 1):
            finding = m.group(0)
            # Must have a "file:line" pattern
            if not re.search(r"[a-zA-Z_./\-]+\.(py|java|js|ts|go|rs|cs|cpp|c|h|rb|php|sh|tf|yml|yaml|json|xml|toml|sql|md):\d+", finding):
                failures.append(f"FAIL: Critical/High finding #{i} has no file:lines evidence (must include path:line)")

    # 4. If blocker_filed: true, a blocker file must exist
    if "blocker_filed: true" in text or "blocker filed" in text.lower():
        # Look for a blockers/ directory in the task workspace (parent of reports/)
        ws = report_path.parent.parent  # reports/ -> task_workspace
        blockers_dir = ws / "blockers"
        if not blockers_dir.exists() or not any(blockers_dir.iterdir()):
            failures.append("FAIL: blocker_filed: true but no blockers/ directory or files in task workspace")

    return failures


def scan_source(source_path: Path) -> list[tuple[str, int, str]]:
    """Scan a source file for security patterns. Return list of (pattern_name, line_no, snippet)."""
    if not source_path.exists() or not source_path.is_file():
        return []
    if source_path.suffix not in {".py", ".java", ".js", ".ts", ".go", ".rs", ".cs", ".rb", ".php", ".sh", ".tf", ".yml", ".yaml", ".json", ".xml", ".toml", ".sql", ".md", ".txt", ".cfg", ".ini", ".env"}:
        return []
    try:
        text = source_path.read_text(errors="ignore")
    except Exception:
        return []
    findings = []
    for name, pattern in SECURITY_PATTERNS.items():
        for m in pattern.finditer(text):
            # Find the line number
            line_no = text[:m.start()].count("\n") + 1
            # Snippet: the matched line, with redaction
            line = text.split("\n")[line_no - 1] if line_no <= len(text.split("\n")) else ""
            # Redact secrets in the snippet
            if "key" in name or "password" in name or "private" in name:
                redacted = re.sub(r"['\"][^'\"]+['\"]", "'<REDACTED>'", line)
            else:
                redacted = line.strip()[:120]
            findings.append((name, line_no, redacted))
    return findings


def scan_repo(repo_root: Path) -> list[tuple[Path, str, int, str]]:
    """Scan a repo for security patterns. Return list of (path, pattern_name, line_no, snippet)."""
    findings = []
    if not repo_root.exists() or not repo_root.is_dir():
        return findings
    skip_dirs = {".git", "__pycache__", "node_modules", "target", "build", "dist", ".venv", "venv", "env"}
    for path in repo_root.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.is_file():
            for name, line, snippet in scan_source(path):
                findings.append((path, name, line, snippet))
    return findings


GOOD_REPORT = """# Security review report

- **Task ID:** synthetic-sr
- **Generated at:** 2026-06-13T20:00:00Z
- **Reviewer:** software-engineer

## Scope

`/path/to/source.py` lines 1-50

## Evidence reviewed

- /path/to/source.py
- /path/to/test_source.py

## Findings

### Critical

- **hardcoded-aws-key** — `AKIAIOSFODNN7EXAMPLE` committed in code
  - **Evidence:** /path/to/source.py:5
  - **Exploitability:** Any reader of the repo can use the key
  - **Impact:** AWS account compromise
  - **Recommended fix:** Move to env var or secrets manager
  - **Approval required:** yes

### Medium

- **md5-usage** — `hashlib.md5(...)` for password hashing
  - **Evidence:** /path/to/source.py:23
  - **Exploitability:** Trivial to reverse
  - **Impact:** Weak password storage
  - **Recommended fix:** Use bcrypt or argon2
  - **Approval required:** no

## Outcome

`changes_requested`

Reason: Critical finding (hardcoded AWS key) requires fix.

## Recommended next action

Hand off to `backend-implementation` for the fix.
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
        lines.append("  [sr-s1-good-report] PASS")
    else:
        lines.append(f"  [sr-s1-good-report] FAIL ({len(failures)} failures)")
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
        lines.append("  [sr-s2-missing-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [sr-s2-missing-outcome] FAIL (should have flagged missing Outcome)")
    bad_path.unlink(missing_ok=True)

    # Test 3: invalid outcome value should FAIL
    bad = GOOD_REPORT.replace("`changes_requested`", "`maybe`")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("outcome" in f.lower() for f in failures):
        lines.append("  [sr-s3-invalid-outcome] PASS (correctly flagged)")
    else:
        lines.append(f"  [sr-s3-invalid-outcome] FAIL (should have flagged invalid outcome)")
    bad_path.unlink(missing_ok=True)

    # Test 4: Critical finding without file:lines should FAIL
    bad = re.sub(r"- \*\*Evidence:\*\* /path/to/source\.py:5", "- **Evidence:** (no line numbers)", GOOD_REPORT)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(bad)
        bad_path = Path(f.name)
    failures = check_report(bad_path)
    if failures and any("file:lines" in f for f in failures):
        lines.append("  [sr-s4-no-evidence-pointer] PASS (correctly flagged)")
    else:
        lines.append(f"  [sr-s4-no-evidence-pointer] FAIL (should have flagged missing file:lines)")
    bad_path.unlink(missing_ok=True)

    # Test 5: source scan should find hardcoded AWS key
    test_code = """
import boto3

AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
client = boto3.client('s3', aws_access_key_id=AWS_KEY)
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    if any(f[0] == "hardcoded_aws_key" for f in findings):
        lines.append("  [sr-s5-source-scan-aws-key] PASS (found hardcoded AWS key)")
    else:
        lines.append(f"  [sr-s5-source-scan-aws-key] FAIL (should have found AWS key; got: {findings})")
    test_path.unlink(missing_ok=True)

    # Test 6: source scan should find shell=True
    test_code = """
import subprocess
subprocess.call(f"echo {user_input}", shell=True)
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        test_path = Path(f.name)
    findings = scan_source(test_path)
    if any(f[0] == "shell_true" for f in findings):
        lines.append("  [sr-s6-source-scan-shell-true] PASS (found shell=True)")
    else:
        lines.append(f"  [sr-s6-source-scan-shell-true] FAIL (should have found shell=True; got: {findings})")
    test_path.unlink(missing_ok=True)

    overall_pass = all("PASS" in line for line in lines)
    output = "\n".join(lines) + f"\n\nOVERALL: {'PASS' if overall_pass else 'FAIL'}"
    return overall_pass, output


def main():
    if len(sys.argv) < 2:
        print("usage: lint-security-review.py <report.md>", file=sys.stderr)
        print("       lint-security-review.py --self-test", file=sys.stderr)
        print("       lint-security-review.py --scan <repo_root>", file=sys.stderr)
        sys.exit(64)

    arg = sys.argv[1]
    if arg == "--self-test":
        passed, output = self_test()
        print(output)
        sys.exit(0 if passed else 1)
    elif arg == "--scan":
        repo = Path(sys.argv[2])
        if not repo.exists():
            print(f"[lint-security-review] FAIL  (not a directory: {repo})")
            sys.exit(66)
        findings = scan_repo(repo)
        if not findings:
            print(f"[lint-security-review] scan: no findings in {repo}")
            sys.exit(0)
        print(f"[lint-security-review] scan: {len(findings)} findings in {repo}")
        for path, name, line, snippet in findings:
            print(f"  {path}:{line}  {name}: {snippet}")
        sys.exit(1)  # findings = exit 1
    else:
        report_path = Path(arg)
        if not report_path.exists():
            print(f"[lint-security-review] FAIL  (file not found: {report_path})")
            sys.exit(66)
        failures = check_report(report_path)
        if not failures:
            print(f"[lint-security-review] PASS  ({report_path})")
            sys.exit(0)
        else:
            print(f"[lint-security-review] FAIL  ({report_path}, {len(failures)} issues)")
            for f in failures:
                print(f"  {f}")
            sys.exit(1)


if __name__ == "__main__":
    main()
