# Approval gate (shared)

Generic approval record used by review and risk skills. A finding
with `approval_required: yes` is gated until this record is
completed by the named approver.

## When to use

Use this template when:

- A finding has `severity: critical` or `severity: high` AND a
  `recommendation` that materially changes behavior, architecture, or
  scope.
- A blocker is filed in `task-state-management` and the resolution
  requires a non-routine sign-off (architecture, security, product,
  on-call).
- A migration, dependency, or config change is irreversible or
  carries production risk.

## Template

```markdown
# Approval gate: <short id>

- **Gate ID:** <APPROVAL-YYYYMMDD-NNN>
- **Task:** <TASK_ID>
- **Triggered by:** <skill name> (<report path>)
- **Triggering finding(s):** <id list, file:line refs>
- **Risk class:** <architecture | security | data-loss | compliance | cost>
- **Decision required by:** <role or named approver>
- **Decision deadline:** <ISO-8601> or "before merge"
- **Created at:** <ISO-8601>

## What is being approved

<one paragraph: what change is being requested, why, and what the
alternatives are>

## Risks of approving

<bullet list of the risks if the change goes ahead as proposed>

## Risks of rejecting

<bullet list of the risks if the change is rejected or delayed>

## Mitigation if approved

- <mitigation, e.g. "expand-and-contract deployment", "feature flag",
  "phased rollout", "monitoring added">
- <mitigation>

## Rollback plan

<concrete rollback steps, or `n/a — change is forward-only`>

## Decision

- **Decision:** `<approved | approved_with_conditions | rejected | deferred>`
- **Decided by:** <role or named approver>
- **Decided at:** <ISO-8601>
- **Conditions (if any):** <list, or `none`>
- **Notes:** <free-form>

## Audit

- This gate is part of the task audit trail. It is not deleted after
  resolution; it is preserved alongside `decisions/<id>.md` and the
  triggering report.
```

## Field rules

- `Decision` must be one of `approved`, `approved_with_conditions`,
  `rejected`, `deferred`. Free-form text is not acceptable.
- `Conditions` is required when `Decision: approved_with_conditions`
  and forbidden otherwise.
- `Decided by` must name a role (e.g. `ARCHITECT_AGENT`) or a real
  person. "Team" or "we" is not acceptable.
- The gate is not considered closed until `Decision` is filled in.

## Linking to other records

- The task's `state.json` history entry that records moving past
  the blocker must reference the `Gate ID`.
- The triggering report must include a link to this gate under
  "Approval required" or "Handoff target".
- The handoff packet (via the `handoff-packet` skill) sent to the
  approver must include the gate file path.

## Lifecycle

```
draft
  └─ submitted  (Decision still empty, but Decided by is assigned)
       └─ approved | approved_with_conditions | rejected | deferred
            └─ resolved  (the change is implemented, the gate is closed)
```

A `rejected` gate does not stop the task — the task proceeds with
the original finding unresolved, and the gate record becomes part
of the audit trail explaining why.
