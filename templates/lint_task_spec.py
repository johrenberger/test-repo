#!/usr/bin/env python3
"""Linter for the task-spec-packet template.

Enforces the 5 mandatory pinned values that the gap-fix patch added
to ``task-spec-packet.md``:

  1. Backend port
  2. Frontend dev-server port
  3. Python binary name
  4. DOM env for frontend tests
  5. Test runner version pins (pytest, vitest, playwright, node, other)

A packet that leaves any of these as a ``<...>`` placeholder is
rejected. ``n/a`` is allowed only if accompanied by a one-line reason
in the same field (e.g. ``n/a (CLI-only project, no frontend)``).

Usage:
    python3 lint_task_spec.py <packet.md>
    python3 lint_task_spec.py --self-test

Exit code 0 = clean. Non-zero = at least one FAIL line.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# Regex that matches an unprocessed template placeholder like <PORT>,
# <NAME>, <VERSION or `n/a`>. We allow placeholders when
# ``allow_placeholders`` is True (used for linting the template
# itself). When the packet is a filled-in instance, placeholders in
# the pinned-values section are FAIL.
PLACEHOLDER_RE = re.compile(r"<([^<>\n]{2,80})>")

# The 5 pinned-value field labels as they appear in section 4 of the
# template. Each must have a non-placeholder value on the same line
# (or in the case of multi-line runner versions, in the following
# indented bullets).
PIN_FIELDS = [
    "Backend port",
    "Frontend dev-server port",
    "Python binary name",
    "DOM env for frontend tests",
]

# Test runner version pins. Each is a label that must appear with a
# non-placeholder value somewhere in section 4.
RUNNER_VERSION_LABELS = [
    "pytest",
    "vitest",
    "playwright",
    "node",
]


def lint_packet(path: Path, allow_placeholders: bool = False) -> list[str]:
    """Return a list of FAIL strings. Empty list = clean."""
    issues: list[str] = []
    if not path.exists():
        return [f"FAIL: packet does not exist: {path}"]

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find section 4 (Pinned values)
    in_section_4 = False
    section_4_lines: list[str] = []
    for line in lines:
        if line.startswith("## 4. Pinned values"):
            in_section_4 = True
            continue
        if in_section_4 and line.startswith("## "):
            break
        if in_section_4:
            section_4_lines.append(line)
    section_4 = "\n".join(section_4_lines)

    if not section_4:
        return [f"FAIL: section '## 4. Pinned values' missing or empty in {path}"]

    # Check each top-level pin field
    for label in PIN_FIELDS:
        # Find "**Label:**" and look for value after the colon
        pattern = re.compile(
            rf"\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", re.MULTILINE
        )
        m = pattern.search(section_4)
        if not m:
            issues.append(f"FAIL: pinned field '{label}:' not found in section 4")
            continue
        value = m.group(1).strip()
        if not value:
            issues.append(f"FAIL: pinned field '{label}:' is empty")
            continue
        if not allow_placeholders and value.startswith("<") and value.endswith(">"):
            issues.append(
                f"FAIL: pinned field '{label}:' still has placeholder "
                f"'{value}' (must be a concrete value or 'n/a' with reason)"
            )
            continue
        # 'n/a' must be followed by a one-line reason in parentheses
        if value.lower().startswith("n/a"):
            if "(" not in value and "reason" not in value.lower():
                issues.append(
                    f"FAIL: pinned field '{label}:' is 'n/a' but has no "
                    f"one-line reason in parentheses (e.g. 'n/a (CLI-only, no frontend)')"
                )

    # Check runner version labels (each appears as a bullet "- pytest: ...")
    for runner in RUNNER_VERSION_LABELS:
        # Match "  - pytest:" (or "  - pytest :")
        pattern = re.compile(
            rf"-\s+{re.escape(runner)}\s*:\s*(.+?)\s*$", re.MULTILINE
        )
        m = pattern.search(section_4)
        if not m:
            issues.append(
                f"FAIL: test runner version '- {runner}:' not found in section 4"
            )
            continue
        value = m.group(1).strip()
        if not value:
            issues.append(f"FAIL: '- {runner}:' is empty")
            continue
        if not allow_placeholders and value.startswith("<") and value.endswith(">"):
            issues.append(
                f"FAIL: test runner version '- {runner}:' still has placeholder "
                f"'{value}' (must be a concrete version or 'n/a' with reason)"
            )
            continue
        if value.lower().startswith("n/a"):
            if "(" not in value:
                issues.append(
                    f"FAIL: '- {runner}:' is 'n/a' but has no one-line reason"
                )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Linter for task-spec-packet files."
    )
    parser.add_argument("path", help="Packet file to lint")
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow <...> placeholders in pinned values (use when linting the template itself)",
    )
    args = parser.parse_args()

    issues = lint_packet(Path(args.path), allow_placeholders=args.allow_placeholders)
    if issues:
        for i in issues:
            print(i)
        return 1
    print(f"OK: {args.path} lints clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
