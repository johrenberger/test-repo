#!/usr/bin/env python3
"""
A2 task-state-management exercise: linter that checks all 3
task workspaces against the contract in
skills/task-state-management/SKILL.md.

For each workspace:
  1. state.json is valid JSON
  2. current_state is one of the 12 allowed states
  3. The most recent history entry's `to` equals current_state
  4. Every from->to pair in history is an allowed transition
     (per the Allowed transitions table in SKILL.md lines 100-115)
  5. If current_state is `blocked`, at least one blocker file
     exists in blockers/ with status `open`
  6. If a transition out of `blocked` happened, the blocker
     file has a non-empty Resolution section
  7. task.md exists and is non-empty
  8. history is append-only (every entry's `at` is >= the
     previous entry's `at`; first entry's from is None)

Prints per-workspace pass/fail and a summary.
"""
import json
import re
import sys
from pathlib import Path

WORKSPACE_ROOT = Path("/data/.openclaw/workspace/tasks/2026-06-12-task-state-management-exercise")

ALLOWED_STATES = [
    "backlog", "ready", "in_progress", "blocked",
    "implementation_done", "review_done", "testing_done",
    "security_done", "release_ready", "deployed", "verified", "closed",
]
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
# States that can transition to `closed` without a skip-state decision.
TERMINAL_TO_CLOSED_ALLOWED_WITHOUT_DECISION = {"verified", "backlog", "ready", "blocked"}
FORWARD_PATH = [
    "in_progress", "implementation_done", "review_done", "testing_done",
    "security_done", "release_ready", "deployed", "verified", "closed",
]


def check_workspace(ws: Path) -> list[str]:
    issues = []

    # 1. state.json is valid JSON
    state_path = ws / "state.json"
    if not state_path.exists():
        return [f"FAIL: state.json does not exist"]
    try:
        state = json.loads(state_path.read_text())
    except json.JSONDecodeError as e:
        return [f"FAIL: state.json is not valid JSON: {e}"]

    # 2. current_state is one of the allowed states
    if state.get("current_state") not in ALLOWED_STATES:
        issues.append(f"FAIL: current_state '{state.get('current_state')}' is not in the allowed states list")

    # 3. The most recent history entry's `to` equals current_state
    history = state.get("history", [])
    if not history:
        issues.append("FAIL: history is empty")
    else:
        last_to = history[-1].get("to")
        if last_to != state["current_state"]:
            issues.append(f"FAIL: last history entry 'to'={last_to!r} does not equal current_state={state['current_state']!r}")

    # 4. Every from->to in history is an allowed transition
    for i, h in enumerate(history):
        fr = h.get("from")
        to = h.get("to")
        if fr is None and i == 0:
            # First entry has from=None; that's the workspace-init
            continue
        if fr is None:
            issues.append(f"FAIL: history[{i}] has from=null but is not the first entry")
            continue
        if fr not in ALLOWED_TRANSITIONS:
            issues.append(f"FAIL: history[{i}] from={fr!r} is not a known state")
            continue
        if to not in ALLOWED_TRANSITIONS[fr]:
            issues.append(f"FAIL: history[{i}] {fr} -> {to} is not an allowed transition "
                          f"(allowed from {fr}: {ALLOWED_TRANSITIONS[fr]})")

    # 5. If current_state is `blocked`, at least one blocker file exists with status `open`
    if state.get("current_state") == "blocked":
        blockers_dir = ws / "blockers"
        has_open = False
        if blockers_dir.exists():
            for bf in blockers_dir.glob("*.md"):
                content = bf.read_text()
                m = re.search(r"\*\*Status:\*\*\s*`?(open|resolved|deferred)`?", content)
                if m and m.group(1) == "open":
                    has_open = True
                    break
        if not has_open:
            issues.append("FAIL: current_state is 'blocked' but no open blocker file exists in blockers/")

    # 6. If a transition out of `blocked` happened, blocker file has a non-empty Resolution
    has_blocked_to_something = any(
        h.get("from") == "blocked" for h in history
    )
    if has_blocked_to_something:
        blockers_dir = ws / "blockers"
        if not blockers_dir.exists():
            issues.append("FAIL: a blocked->X transition happened but blockers/ does not exist")
        else:
            found_resolution = False
            for bf in blockers_dir.glob("*.md"):
                content = bf.read_text()
                if re.search(r"^##\s*Resolution\s*\n[^\n]+", content, re.MULTILINE):
                    # Check the line after ## Resolution is non-empty and non-template
                    m = re.search(r"^##\s*Resolution\s*\n(.+?)(?=^##|\Z)", content, re.MULTILINE | re.DOTALL)
                    if m and m.group(1).strip() and "filled in when status moves" not in m.group(1):
                        found_resolution = True
                        break
            if not found_resolution:
                issues.append("FAIL: a blocked->X transition happened but no blocker has a non-empty Resolution section")

    # 7. task.md exists and is non-empty
    task_path = ws / "task.md"
    if not task_path.exists():
        issues.append("FAIL: task.md does not exist")
    elif len(task_path.read_text().strip()) < 50:
        issues.append("FAIL: task.md is suspiciously short (<50 chars)")

    # 8. history is append-only (timestamps non-decreasing)
    for i in range(1, len(history)):
        prev_at = history[i-1].get("at", "")
        cur_at = history[i].get("at", "")
        if cur_at < prev_at:
            issues.append(f"FAIL: history[{i}].at={cur_at!r} is before history[{i-1}].at={prev_at!r} "
                          "(history is not append-only)")

    # 9. For any history entry that transitions to `closed` from a forward
    #    state (other than `verified`/`backlog`/`ready`/`blocked`), a
    #    skip-state decision must exist in `decisions/`.
    for i, h in enumerate(history):
        fr = h.get("from")
        to = h.get("to")
        if to == "closed" and fr and fr not in TERMINAL_TO_CLOSED_ALLOWED_WITHOUT_DECISION:
            decisions_dir = ws / "decisions"
            skipped_states = []
            if fr in FORWARD_PATH and "closed" in FORWARD_PATH:
                fi = FORWARD_PATH.index(fr)
                ti = FORWARD_PATH.index("closed")
                if ti > fi:
                    skipped_states = FORWARD_PATH[fi + 1 : ti]
            found = False
            if decisions_dir.exists():
                for df in decisions_dir.glob("*.md"):
                    content = df.read_text()
                    m = re.search(r"\*\*Status:\*\*\s*`?(proposed|accepted|superseded)`?", content)
                    if not m or m.group(1) != "accepted":
                        continue
                    if not re.search(rf"\b{re.escape(fr)}\s*(?:->|\u2192)\s*closed\b", content):
                        continue
                    if not any(s in content for s in skipped_states):
                        continue
                    d_m = re.search(r"\*\*Decided at:\*\*\s*`?([0-9TZ:\-]+)`?", content)
                    if d_m and d_m.group(1) > h.get("at", ""):
                        continue
                    found = True
                    break
            if not found:
                issues.append(
                    f"FAIL: history[{i}] {fr} -> closed requires a skip-state decision in decisions/ "
                    f"naming the skipped states ({', '.join(skipped_states)})"
                )

    return issues


def main():
    workspaces = sorted(WORKSPACE_ROOT.glob("tsm-s*"))
    if not workspaces:
        print("FAIL: no tsm-s* workspaces found", file=sys.stderr)
        sys.exit(1)

    all_pass = True
    for ws in workspaces:
        issues = check_workspace(ws)
        if not issues:
            state = json.loads((ws / "state.json").read_text())
            print(f"  [{ws.name}] PASS  (current_state={state['current_state']}, "
                  f"history len={len(state.get('history', []))})")
        else:
            all_pass = False
            state = json.loads((ws / "state.json").read_text())
            print(f"  [{ws.name}] FAIL  (current_state={state['current_state']}, "
                  f"history len={len(state.get('history', []))})")
            for issue in issues:
                print(f"      {issue}")

    print()
    print("OVERALL:", "PASS" if all_pass else "FAIL")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
