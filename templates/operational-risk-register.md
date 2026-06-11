# Operational risk register (shared)

Consolidated risk register for operational concerns
(observability, runbook availability, on-call coverage,
release readiness, incident-related risks). Used by
[`release-readiness`](../release-readiness/SKILL.md),
[`incident-triage`](../incident-triage/SKILL.md),
[`observability-review`](../observability-review/SKILL.md),
and
[`runbook-authoring`](../runbook-authoring/SKILL.md) to
aggregate cross-skill operational risk.

The register is a **derived view**; the primary artifacts are
the per-skill reports.

## Template

```markdown
# Operational risk register for <TASK_ID or service>

- **Scope:** <task id, service, or release>
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>
- **Composite risk:** <critical | high | medium | low>

## Open risks

| ID | Source | Severity | Category | Summary | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <id> | <skill>-report.md | <sev> | <category> | <one line> | <role> | <one line> | <open | accepted | resolved> |

Categories used by operational skills:

- Observability: `logging | metrics | tracing | health |
  slo | alerts | dashboards`
- Runbook: `missing-runbook | unverified-command |
  destructive-step | owner-unassigned`
- Release: `validation-missing | rollback-missing |
  approval-missing | documentation-incomplete`
- Incident: `blast-radius | suspected-component |
  unmitigated | data-loss | security-suspected`

## Accepted risks (with rationale)

- `<id>` — accepted via `<decisions/<id>.md>` or
  `<ADR-NNNN>` — <one-line reason>
- Or `none`.

## Resolved risks

- `<id>` — resolved in `<commit sha or report path>` — <one
  line>
- Or `none`.

## Risks by source

### From `observability-review-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `runbook-authoring-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `release-readiness-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `incident-triage-report.md`

- <id> — <severity> — <summary>
- Or `none`.

## Cross-skill duplicates

When the same finding appears in multiple reports, list it
once here and reference it from each report:

- `<canonical-id>` — canonical in
  `<source-skill>-report.md` — cross-referenced in
  `<other-skill>-report.md`
- Or `none`.

## Open blockers

- `<blocker_id>` — <one-line summary>
- Or `none`.

## Open approval gates

- `<APPROVAL-...>` — <one-line summary>
- Or `none`.

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)
- Source findings: <list of paths>

## Cross-references

- Source findings: <list of paths>
- Handoff packet: <path>
- Task workspace: <path>

## Provenance

- Produced as a **derived view** from primary reports.
- Output path: `<task path>/reports/operational-risk-register.md`
  (recommended; not required).
- The register is a coordination artifact; the primary
  reports are the source of truth.
```

## Field rules

- `Composite risk` equals the highest severity of any open
  risk, unless explicitly de-rated by an acceptance
  decision.
- `Status` is one of `open | accepted | resolved`; an
  `accepted` risk references a `decisions/<id>.md` or
  `ADR-NNNN`; a `resolved` risk references the change that
  resolved it.
- `Cross-skill duplicates` is required when the same
  finding appears in more than one report; it prevents the
  same Critical risk from being "fixed" in one report and
  still showing as open in another.
- `Categories` is the union of the operational skills'
  categories; the register is the place they aggregate.

## When NOT to use

- A single review skill produced a single report with no
  findings needing cross-skill aggregation — the primary
  report is sufficient.
- The task is in `Backlog` and no reports exist yet — wait
  for reports before building the register.

## Cross-references

- Release risk register (specialization):
  [`../release-readiness/templates/release-risk-register.md`](../release-readiness/templates/release-risk-register.md)
- General risk register (cross-skill, including
  non-operational):
  [`risk-register.md`](risk-register.md)
- Findings severity scale:
  [`findings-severity.md`](findings-severity.md)
- Approval gate:
  [`approval-gate.md`](approval-gate.md)
