# Implementation routing report

Output of the
[`implementation-orchestrator`](../../../../skills/implementation-orchestrator/SKILL.md)
skill. Records the impacted layer, owning module, the selected
implementation or review skill, and any preflight gates that must
run before implementation.

## Task

- **Task ID:** <TASK_ID>
- **Routing skill:** `implementation-orchestrator`
- **Generated at:** <ISO-8601>

## Acceptance criteria

<bullet list of testable conditions. If acceptance criteria are
unclear or contradictory, the orchestrator must stop and file a
blocker; do not invent criteria here.>

## Inputs received

- **Task description:** <path or text>
- **Discovery artifact:** <absolute path to
  `discovery/repo-discovery.md` or `none`>
- **Prior review findings:** <paths to `code-change-review-report.md`
  / `security-review-report.md` / etc., or `none`>
- **Known target modules:** <list, or `none provided`>

## Impacted layers

| Layer | Touched? | Evidence (file:lines) | Notes |
| --- | --- | --- | --- |
| backend | yes / no | <file:lines> | <one line> |
| frontend | yes / no | <file:lines> | <one line> |
| integration | yes / no | <file:lines> | <one line> |
| database / migration | yes / no | <file:lines> | <one line> |
| infrastructure / deployment | yes / no | <file:lines> | <one line> |
| documentation-only | yes / no | <file:lines> | <one line> |
| mixed | yes / no | — | <one-line summary of mix> |

If `mixed: yes`, list the ordered sequence of implementation
skills the orchestrator will hand off to (e.g. `backend →
frontend → integration`). Do not plan a single
implementation skill to do two layers at once.

## Smallest impacted module / subtree

For each `yes` layer, list the modules the change should land in:

- **<layer>:** `<module path>` — <one-line reason>
- Or `none — see above` if the layer is not touched.

## Preflight gates required

A preflight gate is a review skill that must run **before**
implementation begins. The orchestrator does not perform the
review; it routes to the review skill and waits for the artifact.

- [ ] `database-migration-safety` — required if the task requires
  a destructive or irreversible migration
- [ ] `dependency-change-review` — required if the task requires
  a new dependency, package-manager change, or build-tool change
- [ ] `security-review` — required if the task is
  security-sensitive (auth, secrets, crypto, PII)
- [ ] `architecture review` (`ARCHITECT_AGENT`) — required if the
  task is architecturally novel
- [ ] `none` — none of the above apply

For each required gate, link the expected output path under
`reports/`.

## Routing decision

- **Selected skill:** <one of
  `backend-implementation | frontend-implementation | integration-implementation | database-migration-safety | dependency-change-review | architecture-review`>
- **Rationale:** <one paragraph explaining why this skill and not
  another>
- **Target modules:** <list of `path:reason`>
- **Out of scope (must not touch):** <list of files or modules the
  selected skill must not edit, even if they are in the
  impacted-layer set>
- **Sequence (if mixed):** <ordered list of implementation skills,
  or `n/a — single skill`>

## Risks

Bullets covering non-obvious risks the selected skill should be
aware of. Each risk should map to either an existing
`decisions/<id>.md` or an `approval-gate` record. Plain text risks
without ownership are not accepted.

- <risk> — owner: <agent or human> — mitigation: <one line>
- Or `none identified`.

## Open blockers

- `<blocker_id>` — <one-line summary>
- Or `none`.

## Open approval gates

- `<APPROVAL-...>` — <one-line summary> (link to
  `approvals/<gate-id>.md`)
- Or `none`.

## Handoff

The receiving skill receives a
[`handoff-packet`](../../../../skills/handoff-packet/SKILL.md)
with the following fields set:

- `routing_report_path`: absolute path to this file
- `selected_skill`: as above
- `selected_skill_rationale`: as above
- `target_modules`: as above
- `preflight_gates_required`: as above (each must be `satisfied` or
  `waived` before the receiving skill begins)
- `discovery_artifact_path`: absolute path
- `acceptance_criteria`: as above

The receiving skill must reject the handoff if any required
preflight gate is neither `satisfied` (with attached review
artifact) nor `waived` (with attached `decisions/<id>.md`).

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `handoffs/<file>.md` — <one line>
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Discovery: `<path to discovery/repo-discovery.md>`
- Prior review: `<paths>` or `none`
- Handoff packet: `<path to handoffs/...>`

## Provenance

- Produced by `implementation-orchestrator` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/implementation-routing-report.md`
  (recommended; not required).
- This report is a **primary report** for the routing step. It is
  not derived from another report; the receiving skill treats it
  as input.
