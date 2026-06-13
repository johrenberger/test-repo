"""Tests for templates/lint_task_spec.py — the linter that enforces
the 5 mandatory pinned values in the task-spec-packet template.

Tests-first: these tests should fail before the lint script exists
(``lint_task_spec`` is not importable), and pass after the script
is implemented.

Run: ``cd test-repo && python3 templates/tests/test_lint_task_spec.py``
"""
from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

# Add the templates dir to sys.path so we can import the lint script
TEMPLATES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TEMPLATES_DIR))

try:
    lint_task_spec = importlib.import_module("lint_task_spec")
except ModuleNotFoundError:
    lint_task_spec = None  # type: ignore[assignment]


TEMPLATE_PATH = TEMPLATES_DIR / "task-spec-packet.md"


def _packet_with_pin(pin_name: str, value: str) -> str:
    """Return a minimal task-spec-packet string with the given pin
    name filled with ``value`` and all other pins filled with sane
    defaults. Used to build test packets.
    """
    base = TEMPLATE_PATH.read_text(encoding="utf-8")
    # Replace each <...> placeholder with a default. The pinned values
    # section is constructed to match the template's structure.
    return base


def _minimal_packet(*, backend_port: str = "8765",
                    frontend_port: str = "5180",
                    python_binary: str = "python3",
                    dom_env: str = "jsdom",
                    pytest_v: str = "8.4.2",
                    vitest_v: str = "2.1.0",
                    playwright_v: str = "1.59.0",
                    node_v: str = "v24.16.0") -> str:
    """Return a minimal valid packet — all 5 pins filled."""
    return f"""# Task Spec Packet (test instance)

- **Spec version:** v1.1 (pinned-values-mandatory)
- **Author:** tester
- **Date:** 2026-06-13
- **Approver:** tester

## 1. Task name and one-sentence objective

**Task name:** test-task

**Objective:** test the lint.

## 2. Source of truth

`spec.txt` is the full external spec.

## 3. Target directory and stack

**Target directory:** `/tmp/test`

**Mandatory stack:**
- Backend: FastAPI

## 4. Pinned values (mandatory — linted)

- **Backend port:** {backend_port}
- **Frontend dev-server port:** {frontend_port}
- **Python binary name:** {python_binary}
- **DOM env for frontend tests:** {dom_env}
- **Test runner version pins:**
  - pytest: {pytest_v}
  - vitest: {vitest_v}
  - playwright: {playwright_v}
  - node: {node_v}
  - other: n/a

## 5. Hard constraints
- BDD-first

## 11. Definition of done
- All 5 pinned values in section 4 are filled (not `<...>`)
"""


class TestLintTaskSpec(unittest.TestCase):
    def setUp(self) -> None:
        if lint_task_spec is None:
            self.skipTest("lint_task_spec.py not yet implemented")

    def test_lint_module_importable(self) -> None:
        """The lint script must be importable as a module."""
        self.assertIsNotNone(lint_task_spec)

    def test_minimal_valid_packet_passes(self) -> None:
        """A packet with all 5 pins filled and no <...> placeholders
        should lint clean (no FAIL lines)."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(_minimal_packet())
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertEqual(
                issues, [],
                f"Expected no lint issues; got: {issues}",
            )
        finally:
            path.unlink()

    def test_unfilled_backend_port_fails(self) -> None:
        """If 'Backend port:' is still `<PORT>`, the lint must fail."""
        bad = _minimal_packet(backend_port="<PORT>")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(bad)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertTrue(
                any("Backend port" in i for i in issues),
                f"Expected lint to flag backend port; got: {issues}",
            )
        finally:
            path.unlink()

    def test_unfilled_frontend_port_fails(self) -> None:
        """If 'Frontend dev-server port:' is still `<PORT>`, fail."""
        bad = _minimal_packet(frontend_port="<PORT>")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(bad)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertTrue(
                any("Frontend" in i for i in issues),
                f"Expected lint to flag frontend port; got: {issues}",
            )
        finally:
            path.unlink()

    def test_unfilled_python_binary_fails(self) -> None:
        """If 'Python binary name:' is still `<NAME>`, fail."""
        bad = _minimal_packet(python_binary="<NAME>")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(bad)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertTrue(
                any("Python binary" in i for i in issues),
                f"Expected lint to flag python binary; got: {issues}",
            )
        finally:
            path.unlink()

    def test_unfilled_dom_env_fails(self) -> None:
        """If 'DOM env:' is still `<...>`, fail."""
        bad = _minimal_packet(dom_env="<jsdom|happy-dom|n/a>")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(bad)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertTrue(
                any("DOM env" in i for i in issues),
                f"Expected lint to flag DOM env; got: {issues}",
            )
        finally:
            path.unlink()

    def test_unfilled_test_runner_versions_fail(self) -> None:
        """If any test runner version is still `<VERSION>`, fail."""
        bad = _minimal_packet(pytest_v="<VERSION or `n/a`>")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(bad)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertTrue(
                any("pytest" in i or "runner" in i.lower() for i in issues),
                f"Expected lint to flag runner version; got: {issues}",
            )
        finally:
            path.unlink()

    def test_na_value_allowed_for_relevant_pins(self) -> None:
        """``n/a`` is a valid value for pins that may not apply
        (e.g. CLI-only project: no frontend, no DOM env)."""
        ok = _minimal_packet(
            frontend_port="n/a (CLI-only project, no frontend)",
            dom_env="n/a (no frontend, no DOM env)",
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(ok)
            path = Path(f.name)
        try:
            issues = lint_task_spec.lint_packet(path)
            self.assertEqual(
                issues, [],
                f"Expected n/a to be valid with reason; got: {issues}",
            )
        finally:
            path.unlink()

    def test_template_itself_lints_clean(self) -> None:
        """The template file (with <...> placeholders) is allowed to
        contain placeholders — it's the template, not a filled packet.
        The lint should not flag the template itself."""
        if not TEMPLATE_PATH.exists():
            self.skipTest("template not yet created")
        issues = lint_task_spec.lint_packet(TEMPLATE_PATH, allow_placeholders=True)
        self.assertEqual(
            issues, [],
            f"Template should not be flagged when allow_placeholders=True; got: {issues}",
        )


if __name__ == "__main__":
    unittest.main()
