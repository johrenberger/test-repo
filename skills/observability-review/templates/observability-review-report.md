# Observability review report

Output of the
[`observability-review`](../../../../skills/observability-review/SKILL.md)
skill. Records the change under review, the observability
dimensions evaluated, the ranked findings, the
recommendations, and the handoff. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/observability-review-report.md`.

## Template

```markdown
# Observability review for <TASK_ID>

- **Task / change:** <branch / PR / service>
- **Skill:** `observability-review`
- **Generated at:** <ISO-8601>
- **Composite risk:** <critical | high | medium | low>

## Inputs

- **Acceptance criteria:** <list, or `none provided`>
- **Discovery artifact:** `<path>` or `none`
- **Change set:** `<path or branch>`
- **Existing dashboards:** <list, or `none`>
- **Existing alerts:** <list, or `none`>
- **Existing runbooks:** <list, or `none`>
- **Existing SLO / SLI:** <list, or `none`>

## Change summary

<one paragraph: what changed, what is now observable, what
the new failure modes are.>

## Modules / services in scope

| Path / service | Role | Notes |
| --- | --- | --- |
| <path> | <role> | <one line> |

## Observability dimensions

For each dimension, mark `pass | concern | finding` and cite
evidence.

| Dimension | Verdict | Evidence |
| --- | --- | --- |
| Logging (key events, structure, redaction) | <verdict> | <file:lines or dashboard name> |
| Metrics (critical paths, RED / USE) | <verdict> | <metric name or file:lines> |
| Tracing (correlation IDs, span coverage) | <verdict> | <trace or file:lines> |
| Health checks (liveness, readiness, dependencies) | <verdict> | <file:lines or endpoint> |
| SLO / SLI | <verdict> | <SLO doc> or `none` |
| Alerts (actionable, runbook-backed) | <verdict> | <alert name> |
| Dashboards (usable for triage) | <verdict> | <dashboard name> |

## Findings

| ID | Severity | Category | File:lines / artifact | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| <id> | <sev> | <category> | <file:lines> | <one line> | <open | resolved | accepted> |

Detail for each finding:

### <id> — <summary>

- **Severity:** <critical | high | medium | low | nit>
- **Category:** <logging | metrics | tracing | health |
  slo | alerts | dashboards | other>
- **Location:** `<file:lines>` or `<alert name>` or
  `<dashboard name>`
- **Source skill:** `observability-review`
- **Evidence:** <code excerpt, metric definition, or
  statement; secrets redacted>
- **Recommendation:** <concrete fix>
- **Routed to:** <`MONITORING_AGENT` | `runbook-authoring` |
  `security-review` | implementation skill | `closed`>
- **Cross-reference:** `<other-finding-id>` if duplicated,
  or `none`

## Recommendations (concrete, routed)

For each recommendation:

- **What:** <one line>
- **Where:** <file:lines or config location>
- **Owner:** <role>
- **Routed to:** <skill or role>
- **Acceptance:** <observable>

## Monitoring changes required

List of changes that require `MONITORING_AGENT` action:

- <change> — owner: <role>
- Or `none`.

## Runbook changes required

List of changes that require
[`runbook-authoring`](../runbook-authoring/SKILL.md) action:

- <change> — owner: <role>
- Or `none`.

## Security findings (routed to security-review)

- <id> — <one line>
- Or `none`.

## Cross-skill duplicates

- `<canonical-id>` — canonical in
  `<source-skill>-report.md` — cross-referenced in
  `observability-review-report.md`
- Or `none`.

## Handoff

- **Handoff packet:** <path>
- **Target role:** <MONITORING_AGENT | implementation skill
  | runbook-authoring | security-review | closed>
- **Required next action:** <one line>

## Open blockers

- `<blocker_id>` — <one-line summary>
- Or `none`.

## Open approval gates

- `<APPROVAL-...>` — <one-line summary>
- Or `none`.

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Discovery: `<path>` or `none`
- Prior review: <list of paths>
- Handoff packet: <path>

## Provenance

- Produced by `observability-review` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/observability-review-report.md`
  (recommended; not required).
- This report is a **primary report** for the observability
  review step. It is not derived from another report; the
  receiving role treats it as input.
```

## Field rules

- `Composite risk` equals the highest severity of any open
  finding, unless explicitly de-rated.
- Every finding has an id, severity, category, location,
  evidence, and recommendation.
- Findings routed to another skill are listed in
  `Security findings` or `Runbook changes required` so the
  next role has a clear starting point.

## When the review is post-incident

When the review is a follow-up to an incident, the report's
`Change summary` and `Findings` should reference the
[`incident-triage-report.md`](../incident-triage/templates/incident-triage-report.md)
and the timeline. The findings should be the missing
observability that the incident surfaced.
