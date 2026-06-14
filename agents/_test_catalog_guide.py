"""BDD tests for the agent catalog decision guide.

The agent catalog is the 20 agents in `agents/`. A decision guide
sits in `agents/CATALOG.md` and answers "if I have task X, which
agent should I use?" with a quick-decision table.

These tests verify:
1. The guide file exists at the right path
2. The guide has a quick-decision table
3. The table has Situation, Agent, and First-step columns
4. The table covers at least 10 situations
5. The table references real agents (each link target exists)
6. The guide has a section for "engineering" and "business operations"
7. The guide has at least 3 pairings (multi-agent flows)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


CATALOG_GUIDE_PATH = Path(__file__).resolve().parents[1] / "agents" / "CATALOG.md"
AGENTS_DIR = Path(__file__).resolve().parents[1] / "agents"


def _extract_markdown_table(text: str, header: str) -> list[list[str]]:
    """Extract a markdown pipe-table whose header contains `header`.

    Returns a list of rows (each a list of cells).
    """
    lines = text.splitlines()
    out: list[list[str]] = []
    in_table = False
    for line in lines:
        s = line.strip()
        if s.startswith("|") and header.lower() in s.lower():
            in_table = True
            out.append([c.strip() for c in s.strip("|").split("|")])
            continue
        if in_table:
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if all(re.match(r"^:?-+:?$", c) for c in cells):
                    continue
                out.append(cells)
            else:
                break
    return out


def _read_guide() -> str:
    """Read the catalog guide. Skips the test if it doesn't exist."""
    if not CATALOG_GUIDE_PATH.exists():
        pytest.skip(f"Catalog guide not yet at {CATALOG_GUIDE_PATH}")
    return CATALOG_GUIDE_PATH.read_text(encoding="utf-8")


class TestCatalogGuideFile:
    """The guide file exists with the right structure."""

    def test_guide_file_exists(self) -> None:
        """Given the agent catalog directory
        When we look for the decision guide
        Then `agents/CATALOG.md` exists.
        """
        assert CATALOG_GUIDE_PATH.exists(), (
            f"Catalog guide not found at {CATALOG_GUIDE_PATH}"
        )

    def test_guide_has_intro(self) -> None:
        """Given the guide
        When we read the top
        Then it has a heading and a 1-2 paragraph intro explaining
        what the guide is for.
        """
        text = _read_guide()
        assert text.startswith("# "), "Expected guide to start with a top-level heading"
        lines = text.splitlines()
        title_idx = next((i for i, line in enumerate(lines) if line.startswith("# ")), 0)
        first_para_idx = next(
            (i for i, line in enumerate(lines[title_idx + 1:], start=title_idx + 1)
             if line.strip() and not line.startswith("#")),
            None,
        )
        assert first_para_idx is not None, "Expected an introductory paragraph after the title"
        first_para = lines[first_para_idx].lower()
        assert any(kw in first_para for kw in [
            "use this", "decision", "task", "agent", "guide", "help"
        ]), f"Intro paragraph doesn't explain the guide's purpose: {lines[first_para_idx]!r}"


class TestQuickDecisionTable:
    """The guide has a quick-decision table mapping situations to agents."""

    def test_guide_has_quick_decision_table(self) -> None:
        """Given the guide
        When we parse it
        Then there is a markdown table with a header that includes
        'Situation' or 'When you need'.
        """
        text = _read_guide()
        rows = _extract_markdown_table(text, "Situation") or _extract_markdown_table(text, "When you need")
        assert rows, (
            "Expected a markdown table with header 'Situation' or 'When you need'."
        )

    def test_quick_decision_table_has_three_columns(self) -> None:
        """Given the quick-decision table
        When we read the header
        Then it has at least 3 columns (Situation / Agent / First-step).
        """
        text = _read_guide()
        rows = _extract_markdown_table(text, "Situation") or _extract_markdown_table(text, "When you need")
        assert rows, "No table found"
        assert len(rows[0]) >= 3, (
            f"Expected at least 3 columns, got {len(rows[0])}: {rows[0]}"
        )

    def test_quick_decision_table_has_at_least_10_rows(self) -> None:
        """Given the quick-decision table
        When we count data rows (excluding header)
        Then there are at least 10 (we have 20 agents, so we
        should cover at least half of the common situations).
        """
        text = _read_guide()
        rows = _extract_markdown_table(text, "Situation") or _extract_markdown_table(text, "When you need")
        assert rows, "No table found"
        data_rows = rows[1:]
        assert len(data_rows) >= 10, (
            f"Expected at least 10 data rows, got {len(data_rows)}"
        )

    def test_quick_decision_table_references_real_agents(self) -> None:
        """Given the quick-decision table
        When we check each Agent cell
        Then it references an actual agent file (or a link to one).
        """
        text = _read_guide()
        rows = _extract_markdown_table(text, "Situation") or _extract_markdown_table(text, "When you need")
        assert rows, "No table found"
        actual_agent_files = {f.name for f in AGENTS_DIR.glob("*AGENT.md")}
        for row in rows[1:]:
            agent_cell = row[1] if len(row) > 1 else ""
            link_targets = re.findall(r"\(([^)]+\.md)\)", agent_cell)
            for target in link_targets:
                target_path = (CATALOG_GUIDE_PATH.parent / target).resolve()
                assert target_path.name in actual_agent_files, (
                    f"Agent link '{target}' in quick-decision table "
                    f"points to a file that doesn't exist in {AGENTS_DIR}."
                )


class TestCatalogGuideSections:
    """The guide has sections for each major domain."""

    def test_guide_has_engineering_section(self) -> None:
        """Given the guide
        When we look at section headings
        Then there is a section for engineering agents.
        """
        text = _read_guide()
        assert "## Engineering" in text or "### Engineering" in text, (
            "Expected an engineering section in the catalog guide"
        )

    def test_guide_has_business_operations_section(self) -> None:
        """Given the guide
        When we look at section headings
        Then there is a section for business operations agents.
        """
        text = _read_guide()
        assert "## Business Operations" in text or "### Business Operations" in text, (
            "Expected a business operations section in the catalog guide"
        )

    def test_guide_has_data_research_section(self) -> None:
        """Given the guide
        When we look at section headings
        Then there is a section for data/research agents.
        """
        text = _read_guide()
        assert "## Data" in text or "### Data" in text, (
            "Expected a data/research section in the catalog guide"
        )


class TestPairingsSection:
    """The guide includes at least 3 multi-agent pairings (common flows)."""

    def test_guide_has_pairings_section(self) -> None:
        """Given the guide
        When we look at section headings
        Then there is a `## Pairings` (or similar) section.
        """
        text = _read_guide()
        assert re.search(r"^#{2,3}\s+Pair", text, re.MULTILINE), (
            "Expected a pairings section in the catalog guide"
        )

    def test_pairings_section_has_at_least_3_pairings(self) -> None:
        """Given the pairings section
        When we count the pairings
        Then there are at least 3 (the most common multi-agent flows).
        """
        text = _read_guide()
        m = re.search(
            r"^#{2,3}\s+Pair.*?\n(.*?)(?=^#{2,3}\s|\Z)",
            text, re.MULTILINE | re.DOTALL,
        )
        assert m, "No pairings section found"
        section = m.group(1)
        items = re.findall(r"^[\s]*[-*]\s+", section, re.MULTILINE)
        assert len(items) >= 3, (
            f"Expected at least 3 pairing entries, got {len(items)}.\n"
            f"Section: {section[:500]}"
        )
