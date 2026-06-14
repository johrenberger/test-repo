---
name: handoff-packet
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- executive-assistant-agent
- project-coordinator-agent
- communications-manager-agent
purpose: Standardize agent-to-agent task transfers. A handoff packet is a single markdown
  file that captures everything the receiving agent needs to continue work without
  re-asking the sending agent.
---

# handoff-packet

Standardize agent-to-agent task transfers. A handoff packet is a single
markdown file that captures everything the receiving agent needs to
continue work without re-asking the sending agent.

## Purpose

Eliminate vague handoffs like "test this" or "review this" that force the
receiving agent to re-discover context. Make every transfer auditable.

## Trigger

- An agent finishes its slice of a task and needs to transfer ownership.
- An agent needs another agent to take action (review, validation, deploy)
  and the receiving agent was not the original requester.
- A long-running task spans sessions and must be resumed with full context.

## Do Not Use When

- The receiver already has the same context (e.g. you are handing back to
  yourself in the same session — write a brief note in `task.md` instead).
- The work product is small enough to fit in a single chat message — link
  to it; do not packetize.

## Required Inputs

- `TASK_ID`
- `SOURCE_AGENT` — the agent writing the packet
- `TARGET_AGENT` — the agent expected to act next
- All 14 fields listed in **Handoff Contract → Required fields** below

## Preflight

- Verify `TASK_ID` is set.
- Verify the packet's output directory exists or can be created:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/handoffs/`.
- Generate a UTC timestamp and a packet filename:
  `<UTC-ts>-<source>-to-<target>.md`
  (lowercase, hyphen-separated, no spaces; example
  `2026-06-11T053900Z-software-engineer-to-test-automation.md`).
- Confirm the source agent owns the current `state.json` state, or include
  an explicit `Approval required: true` line for the takeover.

## Workflow

1. Copy `templates/handoff-packet.md` to the output path.
2. Fill every required field. Do not leave placeholders for required
   fields; "TBD" is allowed only with a brief reason in the same field.
3. If any required field is empty, the packet is invalid — abort and report
   which fields are missing.
4. Write the file. Append a one-line summary to
   `task.md > Handoffs` so the trail is discoverable.
5. If the transfer changes task ownership, transition `state.json` per
   `task-state-management`.

## Allowed Actions

- Create files under `handoffs/`.
- Read files anywhere under the task workspace.
- Append to `task.md` (do not rewrite it).
- Trigger a state transition via the `task-state-management` skill.

## Forbidden Actions

- Sending a packet with vague objectives ("test this", "review this",
  "handle it") that lack the context fields. Such packets are rejected.
- Including secrets, tokens, or credentials in the packet body. If a
  credential is referenced, point to the secret store by name only.
- Deleting earlier handoff packets — the trail is append-only.
- Skipping any of the 14 required fields. If a field genuinely does not
  apply, write `n/a` and a one-line reason.

## Stop Conditions

- The packet file exists at the canonical path.
- All 14 required fields are populated (or marked `n/a` with a reason).
- The packet's filename matches `<UTC-ts>-<source>-to-<target>.md`.
- The summary line is appended to `task.md`.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/handoffs/<UTC-ts>-<source>-to-<target>.md`
- An updated `task.md` with the new handoff in its Handoffs section.
- Optionally, an updated `state.json` reflecting the new owner.

## Handoff Contract

Required fields, in order. Every packet must populate all 14:

1. **Task ID**
2. **Source agent**
3. **Target agent**
4. **Objective** — one sentence; what the target must achieve
5. **Context summary** — paragraph or bullet list of relevant background
6. **Files read** — paths the source read during this slice
7. **Files changed** — paths the source modified (with one-line summary
   per file)
8. **Commands run** — exact commands executed, with results
9. **Validation results** — what passed, what was skipped, what failed
10. **Decisions made** — pointers to `decisions/` entries
11. **Risks** — known unknowns and their likelihood/impact
12. **Blockers** — pointers to `blockers/` entries (or `none`)
13. **Required next action** — concrete next step the target must take
14. **Approval required** — `yes | no`; if `yes`, the source retains
    ownership until the target confirms acceptance

## Validation

- Filename matches the pattern `<UTC-ts>-<source>-to-<target>.md`.
- All 14 required fields present in the body, in order, non-empty.
- No field contains obvious placeholders (`<...>`, `TODO`, `TBD` without
  reason) for required fields.
- `Approval required: yes` packets cannot advance `state.json` until the
  target writes an acceptance note (an empty `## Acceptance` section is
  not enough).

## Related artifacts (task-spec-packet template)

This skill also defines a second packet shape for **task spec
handoffs** — where one agent hands a complete task spec (with BDD
features and required commands) to a building agent. The
task-spec-packet template is at `templates/task-spec-packet.md` and
ships with a linter at `lint_task_spec.py` that enforces 5
**mandatory pinned values** (backend port, frontend port, python
binary, DOM env, test runner versions). These were added after the
2026-06-12 BDD-app cold-consumption test surfaced 5 gaps where a
fresh sub-agent had to make decisions the packet didn't pin. After
the template + lint were added, a 2026-06-13 cold-consumption test
on a different app (CSV-stats) hit **0 gaps** — the fix worked.

Lint usage:
```bash
python3 templates/lint_task_spec.py <packet.md>            # strict
python3 templates/lint_task_spec.py --allow-placeholders \
    templates/task-spec-packet.md                          # lint the template
```

The lint tests live at `templates/tests/test_lint_task_spec.py`.

## Completion Criteria

- Packet file written, summary line appended, audit trail intact.
- If ownership changed, `state.json` reflects the new owner.
- The receiving agent is named explicitly and is the only one expected
  to act next.
