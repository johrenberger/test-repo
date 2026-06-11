# Runbook authoring report

Output of the
[`runbook-authoring`](../../../../skills/runbook-authoring/SKILL.md)
skill. Records the runbook scope, source evidence, decisions
made during authoring, unresolved questions, and the handoff.
Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/runbook-authoring-report.md`.

## Template

```markdown
# Runbook authoring report for <TASK_ID>

- **Task:** <TASK_ID>
- **Skill:** `runbook-authoring`
- **Generated at:** <ISO-8601>
- **Runbook path:** `<repo path or task path>`
- **Runbook status:** <draft | verified | adopted>

## Inputs

- **Service / process:** <name>
- **Scenario:** <failure mode, recovery task, or operational
  procedure>
- **Source evidence:** <list of paths>
- **Owner / team:** <role or person, or `unassigned`>
- **Acceptance criteria:** <list, or `none provided`>

## Scope decision

<one paragraph: what is in scope for this runbook; what is
explicitly out of scope; whether the runbook is split from
or merged with an existing runbook.>

## Existing runbooks

| Path | Topic | Status | Relationship |
| --- | --- | --- | --- |
| <path> | <topic> | <draft | verified | adopted> | <supersedes | extends | references | none> |

## Source evidence used

| Evidence | Path | Used for |
| --- | --- | --- |
| Incident triage report | <path> | <one line> |
| Observability review | <path> | <one line> |
| ADR | <path> | <one line> |
| Prior runbook | <path> | <one line> |
| Operator-provided procedure | <path> | <one line> |
| Validation runner report | <path> | <one line> |

## Decisions made during authoring

For each decision, document the choice, the alternatives,
and the reason.

- **Decision:** <one line>
  - **Chosen:** <option>
  - **Alternatives:** <list>
  - **Reason:** <one line>

## Unverified commands

| Step | Command | Reason unverified | Required action |
| --- | --- | --- | --- |
| <step> | <command> | <reason> | <who verifies and when> |

## Destructive steps

| Step | Action | Approval gate | Rollback | Risk |
| --- | --- | --- | --- | --- |
| <step> | <action> | `<approvals/<gate-id>.md>` | <rollback steps> | <low | medium | high> |

## Cross-references added

- ADRs: <list> or `none`
- Observability review: <path> or `none`
- Release readiness: <path> or `none`
- Incident triage: <path> or `none`
- Related runbooks: <list> or `none`

## Outstanding questions

- <question> — owner: <role> — needed by: <date>
- Or `none`.

## Storage decision

- **In-repo:** <yes | no>
- **Path:** <path>
- **Reason:** <one line, e.g. "matches existing runbook
  location" or "task requires in-repo storage">

## Handoff

- **Handoff packet:** <path>
- **Target role:** <DEVOPS_AGENT | MONITORING_AGENT | other>
- **Required next action:** <one line>

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Source evidence: <list of paths>
- Runbook: `<path>`
- Handoff packet: <path>

## Provenance

- Produced by `runbook-authoring` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/runbook-authoring-report.md`
  (recommended; not required).
- This report is a **primary report** for the runbook
  authoring step. It is not derived from another report; the
  receiving role treats it as input.
```

## Field rules

- `Runbook path` is the absolute path to the runbook; the
  receiving role reads the runbook from this path.
- `Runbook status` is one of `draft | verified | adopted`;
  the authoring skill typically produces `draft`; the
  on-call review moves it to `verified` and then `adopted`.
- `Source evidence used` is required; every fact in the
  runbook must trace to evidence.
- `Decisions made during authoring` is required when the
  runbook made a non-obvious choice (e.g. chose one
  mitigation option over another, picked a specific command
  syntax).
- `Unverified commands` is required; unverified commands
  are flagged in the runbook and listed here.
- `Destructive steps` is required; every destructive step
  has an approval gate and a rollback.
- `Storage decision` is required; the runbook lives at the
  named path, and the reason is documented.

## When the runbook is an update to an existing runbook

The `Existing runbooks` table includes the prior runbook
with `Relationship: supersedes` or `extends`. The
`Source evidence used` table includes the prior runbook
when the update preserves content.
