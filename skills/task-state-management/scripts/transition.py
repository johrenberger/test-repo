#!/usr/bin/env python3
"""
A small helper that performs a state transition for a task workspace
following the rules in
/data/.openclaw/workspace/test-repo/skills/task-state-management/SKILL.md.

  1. Verifies the from->to transition is in the allowed-transitions table.
  2. Updates current_state and updated_at.
  3. Appends a new history entry (append-only; never rewrites history).
  4. For `blocked` transitions: errors if no blocker file exists in
     blockers/ with status `open`.
  5. For transitions OUT of `blocked`: errors if no resolution note
     exists on the originating blocker file.

Usage:
  transition.py <state.json> <to_state> --by <agent> --reason <text>
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_TRANSITIONS = {
    "backlog":            ["ready", "closed"],
    "ready":              ["in_progress", "backlog", "closed"],
    "in_progress":        ["implementation_done", "blocked", "ready", "closed"],
    "blocked":            ["in_progress", "ready", "closed"],
    "implementation_done":["review_done", "in_progress", "closed"],
    "review_done":        ["testing_done", "implementation_done", "closed"],
    "testing_done":       ["security_done", "implementation_done", "closed"],
    "security_done":      ["release_ready", "implementation_done", "closed"],
    "release_ready":      ["deployed", "implementation_done", "closed"],
    "deployed":           ["verified", "release_ready", "closed"],
    "verified":           ["closed", "deployed"],
    "closed":             [],
}

# States that do NOT need a skip-state decision when transitioning to `closed`.
# All others (forward states other than `verified` and `backlog`) require one.
TERMINAL_TO_CLOSED_ALLOWED_WITHOUT_DECISION = {"verified", "backlog", "ready", "blocked"}


# Forward state path (used to detect skipped states when transitioning to `closed`).
FORWARD_PATH = [
    "in_progress",
    "implementation_done",
    "review_done",
    "testing_done",
    "security_done",
    "release_ready",
    "deployed",
    "verified",
    "closed",
]

ALLOWED_STATES = set(ALLOWED_TRANSITIONS.keys())


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def save_state(path: Path, state: dict) -> None:
    with path.open("w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def find_open_blocker(workspace: Path) -> Path | None:
    blockers_dir = workspace / "blockers"
    if not blockers_dir.exists():
        return None
    for bf in sorted(blockers_dir.glob("*.md")):
        content = bf.read_text()
        m = re.search(r"\*\*Status:\*\*\s*`?(open|resolved|deferred)`?", content)
        if m and m.group(1) == "open":
            return bf
    return None


def find_blocker_with_resolution(workspace: Path) -> Path | None:
    """Find a blocker file that has a Resolution section with real content.

    The Resolution section is considered to have real content if there is
    at least one non-empty, non-template-phrase line between
    '## Resolution' and the next '## <heading>' (or end of file).
    """
    TEMPLATE_PHRASES = {
        "filled in when status moves to `resolved`",
        "leave empty while `open`",
        "(filled in when status moves to `resolved`)",
    }
    blockers_dir = workspace / "blockers"
    if not blockers_dir.exists():
        return None
    for bf in sorted(blockers_dir.glob("*.md")):
        lines = bf.read_text().splitlines()
        in_resolution = False
        for line in lines:
            if line.startswith("## Resolution"):
                in_resolution = True
                continue
            if in_resolution and line.startswith("## "):
                # next section started
                break
            if in_resolution and line.strip() and line.strip() not in TEMPLATE_PHRASES:
                return bf
    return None


def transition(state_path: Path, to_state: str, by: str, reason: str) -> int:
    workspace = state_path.parent
    state = load_state(state_path)
    from_state = state["current_state"]

    if from_state == to_state:
        print(f"NO-OP: already in state '{to_state}'")
        return 0

    if to_state not in ALLOWED_STATES:
        print(f"INVALID: '{to_state}' is not a known state", file=sys.stderr)
        return 2

    allowed = ALLOWED_TRANSITIONS.get(from_state, [])
    if to_state not in allowed:
        print(f"INVALID TRANSITION: {from_state} -> {to_state}", file=sys.stderr)
        print(f"Allowed from {from_state}: {allowed}", file=sys.stderr)
        return 2

    # Special: when entering `blocked`, an open blocker file must exist
    if to_state == "blocked":
        if find_open_blocker(workspace) is None:
            print(f"INVALID: cannot transition to 'blocked' without an open blocker file in blockers/",
                  file=sys.stderr)
            return 2

    # Special: when leaving `blocked`, a blocker with a Resolution note must exist
    if from_state == "blocked":
        if find_blocker_with_resolution(workspace) is None:
            print(f"INVALID: cannot transition out of 'blocked' without a Resolution note in the blocker file",
                  file=sys.stderr)
            return 2

    # Special: when transitioning to `closed` from a forward state, a
    # skip-state decision must exist in `decisions/`.
    if to_state == "closed" and from_state not in TERMINAL_TO_CLOSED_ALLOWED_WITHOUT_DECISION:
        if not has_skip_state_decision(workspace, from_state, now_iso()):
            skipped = states_between(from_state, "closed")
            print(
                f"INVALID: cannot transition {from_state} -> closed without a skip-state decision "
                f"in decisions/ that names the skipped states ({', '.join(skipped)})",
                file=sys.stderr,
            )
            return 2

    # Append-only history
    new_entry = {
        "from": from_state,
        "to": to_state,
        "by": by,
        "at": now_iso(),
        "reason": reason,
    }
    state["history"].append(new_entry)
    state["current_state"] = to_state
    state["updated_at"] = new_entry["at"]
    save_state(state_path, state)
    print(f"OK: {from_state} -> {to_state} (by {by}, history now has {len(state['history'])} entries)")
    return 0


def states_between(from_state: str, to_state: str) -> list[str]:
    """Return the forward-path states between from_state and to_state
    (exclusive on both ends)."""
    if from_state not in FORWARD_PATH or to_state not in FORWARD_PATH:
        return []
    fi = FORWARD_PATH.index(from_state)
    ti = FORWARD_PATH.index(to_state)
    if ti <= fi:
        return []
    return FORWARD_PATH[fi + 1 : ti]


def has_skip_state_decision(workspace: Path, from_state: str, transition_at: str) -> bool:
    """Check `decisions/` for a decision that names `from_state -> closed`
    and the skipped states, with status `accepted`, dated on or before
    `transition_at`."""
    decisions_dir = workspace / "decisions"
    if not decisions_dir.exists():
        return False
    skipped = states_between(from_state, "closed")
    for df in sorted(decisions_dir.glob("*.md")):
        content = df.read_text()
        # Status must be `accepted`
        m = re.search(r"\*\*Status:\*\*\s*`?(proposed|accepted|superseded)`?", content)
        if not m or m.group(1) != "accepted":
            continue
        # Must reference the transition and at least one of the skipped states
        # (allow optional spaces around the arrow, and either ASCII `->` or Unicode `\u2192`)
        if not re.search(rf"\b{re.escape(from_state)}\s*(?:->|\u2192)\s*closed\b", content):
            continue
        if not any(s in content for s in skipped):
            continue
        # Decided-at must be on or before the transition
        d_m = re.search(r"\*\*Decided at:\*\*\s*`?([0-9TZ:\-]+)`?", content)
        if d_m and d_m.group(1) > transition_at:
            continue
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state_json", type=Path)
    ap.add_argument("to_state")
    ap.add_argument("--by", required=True)
    ap.add_argument("--reason", required=True)
    args = ap.parse_args()
    sys.exit(transition(args.state_json, args.to_state, args.by, args.reason))


if __name__ == "__main__":
    main()
