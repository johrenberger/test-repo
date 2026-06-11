# Risk register (shared)

A consolidated risk register for a task. Multiple review and risk
skills (`code-change-review`, `security-review`,
`dependency-change-review`, `database-migration-safety`) produce
findings. This template is the place to consolidate them into one
view per task, prioritized by composite risk.

## When to use

- A task produces findings from more than one review / risk skill.
- The project coordinator or a human reviewer wants a single
  task-level view of risk.
- An approval gate references multiple findings and the gate record
  needs a clean pointer to "all the risk this gate is about."

This is **not** a primary report — it is a derived view. Skills
produce primary reports; this template is filled in by the
coordinator or by the agent producing the handoff to the next
phase.

## Template

```markdown
# Risk register for <TASK_ID>

- **Task:** <TASK_ID>
- **Owner:** <AGENT_ID>
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>

## Composite risk

`<critical | high | medium | low>`

The composite is the highest single-finding severity in the register,
unless explicitly de-rated by an approval gate (in which case the
composite is the de-rated level with the gate reference noted).

## Findings

| ID | Source skill | Severity | Category | File:lines | Summary | Status |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <skill> | <sev> | <category> | <file:lines> | <one line> | <open | resolved | accepted> |

`Status: accepted` means the finding was not fixed but was formally
accepted via a decision-log entry. The decision-log ID is recorded
in the audit section below.

## Findings by source

### From `code-change-review-report.md`

- <id> — <severity> — <summary>
- Or `none`

### From `security-review-report.md`

- <id> — <severity> — <summary>
- Or `none`

### From `dependency-change-report.md`

- <id> — <severity> — <summary>
- Or `none`

### From `migration-safety-report.md`

- <id> — <severity> — <summary>
- Or `none`

## Open blockers

- `<blocker_id>` — <one-line summary> (or `none`)

## Open approval gates

- `<APPROVAL-...>` — <one-line summary> (or `none`)

## Accepted findings (with rationale)

- `<finding_id>` — accepted via `<decision-log id>` — <one-line reason>
- Or `none`

## Resolved findings

- `<finding_id>` — resolved in `<commit sha or report path>`
- Or `none`

## Audit trail

- `decisions/<id>.md` — <one line>
- `blockers/<id>.md` — <one line>
- `handoffs/<file>.md` — <one line>
- `approvals/<gate-id>.md` — <one line>

## Cross-skill duplicates

When the same finding appears in multiple reports, list it here
once and reference it from each report:

- `<canonical-id>` — canonical in `<source-skill>-report.md` —
  cross-referenced in `<other-skill>-report.md`

Or `none`.

## Provenance

- Derived from primary reports (not a primary report itself).
- Primary reports: <list of paths>
- Output path: `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/risk-register.md`
  (recommended; not required)
```

## Field rules

- `Composite risk` must equal the highest severity of any open or
  accepted finding, unless explicitly de-rated.
- `Status` is one of `open | resolved | accepted`; a `resolved`
  finding must reference the change that resolved it.
- `Cross-skill duplicates` is required when the same finding
  appears in more than one report; it prevents the same Critical
  finding from being "fixed once" in one report but still showing
  as open in another.

## When NOT to use

- A single review skill produced a single report with no findings
  needing cross-skill aggregation — the primary report is
  sufficient.
- The task is in `backlog` and no reports exist yet — wait for
  reports before building the register.
