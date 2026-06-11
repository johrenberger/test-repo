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

- The task is clearly **backend-only** (API, service, persistence,
  auth, server-side logic) — invoke
  [`backend-implementation`](../backend-implementation/SKILL.md)
  directly.
- The task is clearly **frontend-only** (UI, client state, forms,
  routing) — invoke
  [`frontend-implementation`](../frontend-implementation/SKILL.md)
  directly.
- The task is clearly **integration-only** (external API call,
  webhook, queue, file batch, ETL) — invoke
  [`integration-implementation`](../integration-implementation/SKILL.md)
  directly.
- The task is **discovery-only** — use
  [`repo-discovery`](../repo-discovery/SKILL.md).
- The task is **review-only** — use
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md), or
  [`dependency-change-review`](../dependency-change-review/SKILL.md).
- The task is **validation-only** — use
  [`validation-runner`](../validation-runner/SKILL.md).
- The task is **migration-only** and there is no other code change
  — use
  [`database-migration-safety`](../database-migration-safety/SKILL.md)
  directly.

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

## Workflow

1. **Discovery gate.** Use `repo-discovery` unless a current
   artifact is already attached to the task. Record the artifact
   path in the routing report.

2. **Identify impacted layer(s).** Map the task to one or more of:

   - `backend` — server-side logic, API, persistence, auth
   - `frontend` — UI, client state, forms, routing
   - `integration` — cross-system calls, messaging, webhooks, file
     import/export
   - `database/migration` — schema change, data backfill, migration
   - `infrastructure/deployment` — provisioning, build, deploy
   - `documentation-only` — docs / comments / spec changes
   - `mixed` — two or more of the above

   The mapping must cite at least one concrete file or module per
   layer from the discovery artifact.

3. **Identify smallest impacted module / subtree.** For each
   impacted layer, name the module(s) the change should land in.
   If multiple layers are touched, name the owning module for each.

4. **Decide whether to route to a review skill first.** Apply these
   gates:

   - Task requires a **destructive or irreversible migration** →
     route to `database-migration-safety` first.
   - Task requires a **new dependency, new package manager, or
     build-tool change** → route to `dependency-change-review`
     first.
   - Task is **architecturally novel** (new pattern, new module
     boundary, new persistence model) → route to architecture
     review first (`ARCHITECT_AGENT`).
   - Task is **security-sensitive** (auth, secrets handling,
     cryptographic change, PII handling) → route to
     `security-review` first.

   The output of the review skill is a findings report and a
   decision; only then does the orchestrator dispatch the
   implementation work.

5. **Produce the routing decision.** Pick exactly one of:

   - `backend-implementation` (with the module(s) to change)
   - `frontend-implementation` (with the module(s) to change)
   - `integration-implementation` (with the integration boundary)
   - `database-migration-safety` (gate, then usually
     `backend-implementation`)
   - `dependency-change-review` (gate, then re-route)
   - architecture review via `ARCHITECT_AGENT` (gate, then re-route)

   If the task is `mixed` and the layers are roughly equal, the
   default is to **sequence** them: one orchestrator → one
   implementation skill → handoff packet → next orchestrator call
   for the next layer. This is intentional. A single
   implementation skill that tries to do two layers at once is
   the failure mode this skill is meant to prevent.

6. **Document risks and approval gates.** Use the shared
   [`approval-gate.md`](../../templates/approval-gate.md) template
   for any blocker-level finding. Cross-link to the
   [`risk-register.md`](../../templates/risk-register.md) for
   cross-skill risk aggregation.

7. **Hand off.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to the selected
   skill. The packet's `Required next action` is "implement per
   routing report" and links to the routing report and discovery
   artifact.

## Allowed Actions

- Read files in the repo.
- Read existing discovery, review, and decision artifacts.
- Run `repo-discovery` scripts (read-only).
- Write the routing report and handoff packet.
- Update `task.md` / `state.json` for the routed task.

## Forbidden Actions

- **Do not modify application code.** The orchestrator's only
  output is a routing report and handoff packet; it never edits
  source files.
- **Do not generate tests.** Tests are written by
  `test-generation` or by the implementation skill, scoped to its
  layer.
- **Do not implement features.** The orchestrator routes; the
  implementation skills implement.
- **Do not run destructive commands.** No installers, no `rm`, no
  schema changes, no `git push --force`, no deploys.
- **Do not route high-risk tasks directly to implementation
  without a review gate.** Migrations, dependency changes, and
  security-sensitive work must go through
  `database-migration-safety`, `dependency-change-review`, or
  `security-review` first.
- **Do not invent repo facts.** Routing decisions must cite
  files and modules from the discovery artifact.
- **Do not approve the task on behalf of any review skill.** The
  orchestrator can route to a review skill; it cannot stand in for
  one.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Acceptance criteria are unclear or contradictory.
- The task requires a destructive migration and no review has been
  scheduled.
- The task requires a new dependency / package-manager / build-tool
  change and no review has been scheduled.
- The task crosses multiple modules with unclear ownership and the
  module owners cannot be inferred from the discovery artifact.
- The task requires production credentials or deployment access.
- The discovery artifact contradicts the task description in a way
  that affects routing.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/implementation-routing-report.md`**
  — see
  [`templates/implementation-routing-report.md`](templates/implementation-routing-report.md).
- **Handoff packet** to the selected implementation or review
  skill, following
  [`handoff-packet`](../handoff-packet/SKILL.md).
- **State transition** in `state.json` from `backlog` / `ready` to
  the appropriate state, with the routing report path recorded.

## Handoff Contract

Fields the receiving skill may rely on:

- `routing_report_path` — absolute path to the routing report
- `selected_skill` — exactly one of
  `backend-implementation | frontend-implementation | integration-implementation | database-migration-safety | dependency-change-review | architecture-review`
- `selected_skill_rationale` — why this skill
- `target_modules` — list of `path:reason` for the modules to change
- `preflight_gates_required` — list of review skills that must run
  before implementation
- `discovery_artifact_path` — absolute path to the repo discovery
- `acceptance_criteria` — the testable conditions

Fields the receiving skill must not rely on:

- "approved by <review skill>" unless the review's output is
  attached to the packet.
- "no security implications" — the orchestrator does not make
  security claims; security is asserted only by `security-review`.

## Validation

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
- Shared
  [`approval-gate`](../../templates/approval-gate.md) and
  [`risk-register`](../../templates/risk-register.md) templates.

## Maturity

`draft` — initial spec, not yet run end-to-end.
