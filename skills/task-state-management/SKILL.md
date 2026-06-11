# task-state-management

Define the per-task filesystem layout, the allowed task states, and the
state-transition rules. Provide a single source of truth for any agent that
needs to record, advance, or query task progress.

Primarily used by the Project Coordinator. Usable by any agent that needs
to record state for a task it owns or contributes to.

## Purpose

Eliminate the "where do I write this, and what state are we in?" problem
that arises when multiple agents touch the same task across sessions.

## Trigger

- A task is opened and needs a workspace.
- An agent is about to begin work, hand off, or record a blocker / decision.
- A consumer wants to know the current state of a task before acting on it.

## Do Not Use When

- The task is purely conversational with no work product expected.
- A different skill is responsible for the state (e.g. `validation-runner`
  owns its own validation report, not task state).

## Required Inputs

- `TASK_ID` — the task identifier; matches
  `/data/.openclaw/workspace/tasks/<TASK_ID>/`.
- `AGENT_ID` — the agent writing or transitioning state.

## Preflight

- Verify `TASK_ID` is set and matches `[a-z0-9][a-z0-9-]{0,63}`.
- Verify the task directory exists or can be created
  (`mkdir -p` allowed; it is local and reversible).
- Read current `state.json` if present; do not overwrite a non-initial state
  with a stale value.

## Workflow

1. On first touch, create the task workspace:

   ```
   /data/.openclaw/workspace/tasks/<TASK_ID>/
     task.md
     state.json
     handoffs/
     blockers/
     decisions/
     discovery/
     validation/
     reports/
   ```

2. Write `task.md` from `templates/task.md`, filling in objective, owner,
   scope, and acceptance criteria.
3. Initialize `state.json` from `templates/state.json` with
   `current_state: "backlog"`, `owner: <AGENT_ID>`, and a UTC timestamp.
4. As work progresses, update `state.json` only via allowed transitions
   (see below). Append, never delete, `history`.
5. When the agent cannot proceed, create a blocker file from
   `templates/blocker.md` under `blockers/` and transition the task to
   `blocked`. Blockers are part of the audit trail — they are not deleted
   when resolved.
6. When a material choice is made (architecture, library, scope cut,
   rollback), append a decision entry from `templates/decision-log.md`
   under `decisions/`. Decisions are append-only.
7. Transitions are validated against the table below. An invalid transition
   is an error: surface it, do not silently coerce.

## Allowed states

| State | Meaning |
| --- | --- |
| `backlog` | Captured, not yet ready to start |
| `ready` | Scoped, has acceptance criteria, awaiting pickup |
| `in_progress` | An agent is actively working |
| `blocked` | Cannot proceed; see `blockers/` |
| `implementation_done` | Code changes complete, validation pending |
| `review_done` | Code review complete, testing pending |
| `testing_done` | Test suite complete, security review pending |
| `security_done` | Security review complete, release pending |
| `release_ready` | Approved, awaiting deploy |
| `deployed` | Deployed to target environment |
| `verified` | Post-deploy verification passed |
| `closed` | Terminal: completed and archived |

## Allowed transitions

- `backlog → ready | closed`
- `ready → in_progress | backlog | closed`
- `in_progress → implementation_done | blocked | ready`
- `blocked → in_progress | ready | closed` (only after blocker resolved)
- `implementation_done → review_done | in_progress` (rework)
- `review_done → testing_done | implementation_done` (rework)
- `testing_done → security_done | implementation_done` (rework)
- `security_done → release_ready | implementation_done` (rework)
- `release_ready → deployed | implementation_done` (rollback)
- `deployed → verified | release_ready` (rollback)
- `verified → closed | deployed` (post-verification regression)

Any transition not listed is **invalid** and must be rejected with a clear
error referencing this table.

## Forbidden Actions

- Deleting or rewriting history entries in `state.json` or `decisions/`.
- Skipping a state in the forward direction without justification
  (justification = an explicit decision-log entry).
- Moving out of `blocked` without first creating a resolution note in the
  originating blocker file.
- Editing a task owned by another agent without a `handoff-packet` to the
  receiving agent.

## Stop Conditions

- `state.json` reflects the post-transition state.
- `history` array has a new entry with `from`, `to`, `by`, `at`, `reason`.
- For `blocked`: at least one blocker file exists with status `open`.
- For any forward transition: any prior open blocker is either `resolved`
  or has an explicit `deferred` decision.

## Outputs

- `task.md` — objective, scope, acceptance criteria
- `state.json` — current state, owner, history (append-only)
- `blockers/<id>.md` — one per blocker, with status
- `decisions/<id>.md` — one per material decision, append-only
- Updated `state.json` with the new state and appended history entry

## Handoff Contract

Receiving agents may rely on:

- `state.json.current_state` — the canonical state at read time
- `state.json.owner` — who is currently responsible
- The presence of `blockers/` files for any open blockers
- The presence of `decisions/` files for any recorded choices

Receiving agents must not rely on:

- A specific state being held for more than the read instant — re-read
  before acting.

## Validation

- `state.json` parses as JSON.
- `current_state` is one of the allowed states.
- The most recent `history` entry's `to` field equals `current_state`.
- Every `from → to` pair in `history` is an allowed transition.
- Every open blocker has at least one owner field set.

## Completion Criteria

- The state change is durable (file written, fsynced where possible).
- Any required templates are filled, not left as placeholders.
- The agent that triggered the change emits a one-line confirmation
  including the new state.
