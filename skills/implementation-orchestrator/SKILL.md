---
name: implementation-orchestrator
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- project-coordinator-agent
- software-engineer-agent
purpose: Route implementation work to the correct narrower implementation skill. The
  orchestrator does **not** implement code — it classifies the task, identifies the
  owning module, and dispatches to one of `backend-implementation`, `frontend-implementation`,
  `integration-implementation`, or to a review skil
---

# implementation-orchestrator

Route implementation work to the correct narrower implementation
skill. The orchestrator does **not** implement code — it classifies
the task, identifies the owning module, and dispatches to one of
`backend-implementation`, `frontend-implementation`,
`integration-implementation`, or to a review skill
(`database-migration-safety`, `dependency-change-review`) when the
task needs a gate before implementation.

## Purpose

Replace broad, unfocused implementation edits with a routed model.
When a task is unclear about which layer (backend / frontend /
integration) it touches, attempting to implement it inside a single
broad skill tends to:

- expand scope into modules the agent does not own;
- mix API contract changes with UI changes with no clear handoff;
- bypass review gates for high-risk parts (migrations, dependency
  changes, security-sensitive work).

The orchestrator is the single entry point for such tasks. Its
output is a routing decision, a risk / approval note, and a
`handoff-packet` to the next skill. If the layer is obvious, the
caller should skip the orchestrator and use the narrower skill
directly.

## Trigger

Use when a task asks to implement software behavior **and** any of
the following is true:

- The impacted layer (backend / frontend / integration) is unclear
  from the task description.
- The task description mentions multiple layers ("add a UI button
  that calls a new API endpoint and triggers a downstream sync").
- The change touches modules owned by different teams or
  responsibilities.
- A previous review or discovery artifact flagged unclear ownership.
- A blocker is being resolved that requires non-trivial code in
  more than one layer.

## Do Not Use When

Route directly to the narrower skill:

| Task shape | Skill |
| --- | --- |
| Backend-only (API, service, persistence, auth, server logic) | [`backend-implementation`](../backend-implementation/SKILL.md) |
| Frontend-only (UI, client state, forms, routing) | [`frontend-implementation`](../frontend-implementation/SKILL.md) |
| Integration-only (external API, webhook, queue, file batch, ETL) | [`integration-implementation`](../integration-implementation/SKILL.md) |
| Migration-only, no other code | [`database-migration-safety`](../database-migration-safety/SKILL.md) |
| Discovery-only | [`repo-discovery`](../repo-discovery/SKILL.md) |
| Review-only | [`code-change-review`](../code-change-review/SKILL.md), [`security-review`](../security-review/SKILL.md), or [`dependency-change-review`](../dependency-change-review/SKILL.md) |
| Validation-only | [`validation-runner`](../validation-runner/SKILL.md) |

## Required Inputs

- **Task description** — what the user / upstream skill asked for.
- **Acceptance criteria** — concrete, testable conditions.
- **Repo-discovery artifact** — a current
  `discovery/repo-discovery.md` for the task, **or** permission to
  run `repo-discovery` first.
- **Known changed files or target modules** — if the caller already
  knows the area, list them. Optional but speeds routing.
- **Any existing review findings** — `code-change-review-report.md`,
  `security-review-report.md`, `risk-register.md`, or
  `decisions/<id>.md` that constrain the change.

## Preflight

Before routing:

1. Confirm a current `repo-discovery` artifact exists. If not, run
   `repo-discovery` first; routing on guessed repo facts is
   forbidden.
2. Confirm acceptance criteria are concrete and testable. If they
   are not, stop and request clarification.
3. Confirm the task is not destructive-by-default (migration
   deletion, dependency swap, security-sensitive change). If it is,
   route to a review skill first (see step 4 of Workflow).

## Routing decision — quick reference

This table is the short form of the Workflow. For rationale, edge
cases, and the B1-exercise known limitations, see
[`references/workflow.md`](references/workflow.md).

| Step | Action | Output |
| --- | --- | --- |
| 1 | Discovery gate | `discovery/repo-discovery.md` path in routing report |
| 2 | Identify impacted layer(s) | One of: `backend`, `frontend`, `integration`, `database/migration`, `infrastructure/deployment`, `documentation-only`, `mixed` |
| 3 | Identify smallest impacted module | Module path(s) cited from discovery artifact |
| 4 | Apply review-skill gates | Migrations → `database-migration-safety`; new deps → `dependency-change-review`; architecturally novel → `architecture-review`; security-sensitive → `security-review` |
| 5 | Pick exactly one routed skill | See [Allowed routing targets](#allowed-routing-targets) below |
| 6 | Document risks | Use [`templates/approval-gate.md`](../../templates/approval-gate.md) for any blocker-level finding |
| 7 | Hand off | Produce a [`handoff-packet`](../handoff-packet/SKILL.md) to the selected skill |

For `mixed` tasks, sequence the layers: one orchestrator call per
layer, with handoff packets between. Do not let a single
implementation skill span two layers.

### Allowed routing targets

Pick **exactly one** of:

- `backend-implementation` (default for unclear `backend` work)
- `frontend-implementation` (default for UI/client work)
- `integration-implementation` (default for cross-system work)
- `database-migration-safety` (gate, then usually `backend-implementation`)
- `dependency-change-review` (gate, then re-route)
- `security-review` (gate; the implementation skill is decided
  after the security review is satisfied)
- `architecture-review` (gate; the implementation skill is decided
  after the architecture review is satisfied)

If the discovery flags a layer with no dedicated skill
(infrastructure/deployment, documentation-only), fall back to
`backend-implementation` and flag the routing in the report's
Risks section.

## Stop Conditions (summary)

Halt and surface a blocker (via `task-state-management`) when:

- Acceptance criteria are unclear or contradictory.
- A required review gate has not been scheduled for a destructive
  migration, dependency change, security-sensitive change, or
  architecturally novel change.
- Module ownership is unclear and the module owners cannot be
  inferred from the discovery artifact.
- The task requires production credentials or deployment access.
- The discovery artifact contradicts the task description in a way
  that affects routing.

For the full stop-condition list, see
[`references/stop-and-validation.md`](references/stop-and-validation.md).

## Allowed Actions

- Read files in the repo.
- Read existing discovery, review, and decision artifacts.
- Run `repo-discovery` scripts (read-only).
- Write the routing report and handoff packet.
- Update `task.md` / `state.json` for the routed task.

For the full list of forbidden actions and the handoff contract
the receiving skill may rely on, see
[`references/handoff-and-forbidden.md`](references/handoff-and-forbidden.md).

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/implementation-routing-report.md`**
  — see
  [`templates/implementation-routing-report.md`](templates/implementation-routing-report.md).
- **Handoff packet** to the selected implementation or review
  skill, following
  [`handoff-packet`](../handoff-packet/SKILL.md).
- **State transition** in `state.json` from `backlog` / `ready` to
  the appropriate state, with the routing report path recorded.

## Validation (summary)

Routing is "validated" when:

1. The routing report cites a discovery artifact and lists concrete
   files / modules per layer.
2. The selected skill exists and is a routed implementation or
   review skill.
3. Every preflight gate is either satisfied (review artifact
   attached) or explicitly waived with a `decisions/<id>.md`
   entry.
4. The handoff packet has all 14 required fields.

The orchestrator itself runs no shell commands. Validation is
performed by the receiving skill (typically
`validation-runner` at the end of the implementation cycle).

For the full validation rules, see
[`references/stop-and-validation.md`](references/stop-and-validation.md).

## Completion Criteria

- Impacted layer identified and documented.
- Owning module / subtree identified and documented.
- The correct implementation or review skill is selected.
- All preflight gates (migration, dependency, security,
  architecture) are either satisfied or explicitly waived.
- A `handoff-packet` is produced and the receiving skill accepts
  it.
- The task's `state.json` reflects the routing outcome.

## Cross-references

- [`backend-implementation`](../backend-implementation/SKILL.md)
- [`frontend-implementation`](../frontend-implementation/SKILL.md)
- [`integration-implementation`](../integration-implementation/SKILL.md)
- [`repo-discovery`](../repo-discovery/SKILL.md)
- [`handoff-packet`](../handoff-packet/SKILL.md)
- [`database-migration-safety`](../database-migration-safety/SKILL.md)
- [`dependency-change-review`](../dependency-change-review/SKILL.md)
- [`security-review`](../security-review/SKILL.md)
- Long-form workflow: [`references/workflow.md`](references/workflow.md)
- Long-form stop conditions / validation:
  [`references/stop-and-validation.md`](references/stop-and-validation.md)
- Long-form handoff contract / forbidden actions:
  [`references/handoff-and-forbidden.md`](references/handoff-and-forbidden.md)
- Shared [`approval-gate`](../../templates/approval-gate.md) and
  [`risk-register`](../../templates/risk-register.md) templates.

## Maturity

`draft` — initial spec, not yet run end-to-end.

## Helper scripts

- `scripts/lint-routing-report.py` — 10-rule linter for the
  routing report. Three invocation modes: single file, directory,
  `--self-test`. Exit codes: 0 (pass), 1 (failure), 64 (bad
  usage). The linter checks frontmatter, all 7 layer rows in
  the impacted-layers table, the selected skill is in the
  allowed set, the handoff section has all 7 required fields,
  and no template placeholders remain in the report body.
  Promoted from the B1 exercise
  (`/data/.openclaw/workspace/tasks/2026-06-12-impl-orchestrator-exercise/reports/lint-routing-reports.py`).
