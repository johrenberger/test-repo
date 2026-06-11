# Incident action item

Output of the
[`incident-triage`](../../../../skills/incident-triage/SKILL.md)
skill. One file per follow-up action item. Save as
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/action-items/<UTC-ts>-<id>.md`.

## Template

```markdown
# Action item: <short title>

- **Action ID:** <AI-YYYYMMDD-NNN>
- **Incident:** <INC-YYYYMMDD-NNN>
- **Task:** <TASK_ID>
- **Created at:** <ISO-8601>
- **Owner:** <role or person>
- **Deadline:** <UTC-ts or relative, e.g. "T+7d from
  resolution">
- **Status:** <open | in-progress | blocked | done |
  cancelled>

## Description

<one paragraph: what needs to be done, why, and the link to
the incident finding that produced it.>

## Acceptance criteria

- [ ] <observable>
- [ ] <observable>

## Dependencies

- <action item id or task id>
- Or `none`.

## Linked artifacts

- Incident triage report: `<path>`
- Timeline: `<path>`
- Decision (if any): `<path>`
- Runbook (if any): `<path>`

## Status history

- `<UTC-ts>` — `<status>` — <one line>
- `<UTC-ts>` — `<status>` — <one line>

## Provenance

- Produced by `incident-triage` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/action-items/<UTC-ts>-<id>.md`
  (recommended; not required).
- This is a **primary artifact** for the action item. The
  receiving role (typically the action item owner) treats
  it as input.
```

## Field rules

- `Status` is exactly one of `open | in-progress | blocked |
  done | cancelled`. Free-form text is not acceptable.
- `Owner` names a role or a person. "Team" or "we" is not
  acceptable.
- `Acceptance criteria` is required; an action item without
  observable acceptance is not actionable.
- `Status history` is updated whenever the status changes;
  the change has a timestamp and a one-line reason.

## Lifecycle

```
open
  └─ in-progress
       ├─ blocked
       │    └─ in-progress
       └─ done
open (direct path)
  └─ cancelled
```

A `cancelled` action item must have a reason in the
`Status history`.
