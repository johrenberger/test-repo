# Release readiness report

Output of the
[`release-readiness`](../../../../skills/release-readiness/SKILL.md)
skill. Records the change under assessment, the evidence
collected, the release gate verdicts, the status, and the
handoff. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-readiness-report.md`.

## Template

```markdown
# Release readiness report for <TASK_ID>

- **Task / change:** <branch / build / project identifier>
- **Release scope:** <one-line scope, e.g. "v1.4.2 hotfix
  for issue #1234">
- **Skill:** `release-readiness`
- **Generated at:** <ISO-8601>
- **Status:** <Ready | Ready with known risks | Not ready |
  Blocked pending approval / evidence>
- **Composite risk:** <critical | high | medium | low>

## Inputs

- **Acceptance criteria:** <list, or `none provided`>
- **Discovery artifact:** `<path>` or `none`
- **Release plan:** <rollout, rollback, monitoring — or
  `none provided`>
- **CI status (from repo files):** <summary, or `none`>

## Evidence collected

| Evidence | Path | Status | Key findings |
| --- | --- | --- | --- |
| validation | `<path>` or `none` | <pass / fail / not run> | <one line> |
| code-change-review | `<path>` or `none` | <pass / concern / finding> | <one line> |
| security-review | `<path>` or `none` | <pass / concern / finding> | <one line> |
| dependency-change-review | `<path>` or `none` | <pass / concern / finding> | <one line> |
| database-migration-safety | `<path>` or `none` | <pass / concern / finding> | <one line> |
| architecture-review | `<path>` or `none` | <pass / concern / finding> | <one line> |
| documentation-impact | `<path>` or `none` | <pass / concern / finding> | <one line> |
| observability-review | `<path>` or `none` | <pass / concern / finding> | <one line> |
| runbook availability | `<path>` or `none` | <available / missing> | <one line> |
| ADRs | `<list>` or `none` | <list of statuses> | <one line> |
| Manual approvals | `<list>` or `none` | <recorded / missing> | <one line> |

When an evidence artifact is missing, the row records
`none` in the `Path` column and `not run` / `missing` in the
`Status` column. Missing evidence is a blocker for
`Ready` / `Ready with known risks` status.

## Release gate verdicts

Use
[`references/release-gate-checklist.md`](../../../../skills/release-readiness/references/release-gate-checklist.md)
as the canonical gate list; the verdicts below are summarized
from the linked go / no-go checklist.

| Gate item | Verdict | Notes |
| --- | --- | --- |
| Tests pass | <pass / fail / not run> | <one line> |
| Build success | <pass / fail / not run> | <one line> |
| Lint / typecheck | <pass / fail / not run> | <one line> |
| Unresolved Critical findings | <none / count> | <one line> |
| Unresolved High findings | <none / count> | <one line> |
| Migration safety | <pass / concern / n/a> | <one line> |
| Dependency changes | <pass / concern / n/a> | <one line> |
| Security risks | <pass / concern / n/a> | <one line> |
| Architecture review | <pass / concern / n/a> | <one line> |
| Rollback plan | <documented / missing / n/a> | <one line> |
| Feature flags / config | <planned / missing / n/a> | <one line> |
| Monitoring / alerts / runbooks | <in place / partial / missing> | <one line> |
| Documentation updates | <complete / partial / n/a> | <one line> |
| Known limitations | <recorded / unrecorded> | <one line> |
| Manual approvals | <recorded / missing> | <one line> |

## Status rationale

<one paragraph: why the status is what it is, citing the
gate items and any acceptance decisions.>

When status is `Ready with known risks`, the accepted risks
are listed in the
[`release-risk-register.md`](release-risk-register.md) and
each has a `decisions/<id>.md` reference.

When status is `Not ready`, the open blockers are listed in
`Open blockers` below.

When status is `Blocked pending approval / evidence`, the
required approvals and missing evidence are listed below.

## Rollout plan

- **Strategy:** <canary / blue/green / rolling / feature
  flag / hotfix>
- **Stages:** <one paragraph or numbered list>
- **Trigger for next stage:** <one line>
- **Trigger for rollback:** <one line>

## Rollback plan

- **Time to rollback:** <estimate, or `rehearsed` if tested>
- **Steps:** <numbered list>
- **Data implications:** <destructive / additive / n/a>
- **Operator:** <role, or `on-call`>

## Monitoring plan

- **Dashboards:** <list, or `none — see observability-review`>
- **Alerts:** <list, or `none — see observability-review`>
- **On-call coverage:** <recorded / missing>
- **SLOs watched:** <list, or `n/a`>
- **First-hour checkpoints:** <time + metric, e.g.
  "T+15min: error rate < 0.1%; T+60min: p99 latency < 500ms">

## Known limitations

- <limitation> — accepted via: `<decisions/<id>.md>` or
  `ADR-NNNN`
- Or `none`.

## Open blockers

- `<blocker_id>` — <one-line summary>
- Or `none`.

## Required approvals

- `<role or person>` — reason: <one line> — status:
  approved / pending
- Or `none`.

## Open approval gates

- `<APPROVAL-...>` — <one-line summary>
- Or `none`.

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)
- Evidence artifacts: <list of paths>

## Handoff

- **Handoff packet:** <path to
  `handoffs/<UTC-ts>-release-readiness-to-<target>.md`>
- **Target:** <`DEVOPS_AGENT` | human operator>
- **Required next action:** <one line>
- **Deployment authority:** <role, or `operator only`>

## Cross-references

- Go / no-go checklist:
  [`go-no-go-checklist.md`](go-no-go-checklist.md)
- Risk register:
  [`release-risk-register.md`](release-risk-register.md)
- Evidence artifacts: <list of paths>
- ADRs: <list of paths>
- Handoff packet: <path>

## Provenance

- Produced by `release-readiness` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-readiness-report.md`
  (recommended; not required).
- This report is a **primary report** for the readiness
  step. It is not derived from another report; the receiving
  skill / operator treats it as input.
```

## Field rules

- `Status` must be exactly one of `Ready | Ready with known
  risks | Not ready | Blocked pending approval / evidence`.
- `Composite risk` equals the highest open finding severity
  from the evidence artifacts, unless explicitly de-rated by
  an acceptance decision.
- Every gate item has a verdict; missing verdicts are treated
  as `not run` and surface as blockers.
- When status is `Ready` or `Ready with known risks`, the
  report must list zero unresolved Critical findings without
  an acceptance decision.

## Status mapping

| Gate verdicts | Status |
| --- | --- |
| All `pass`, no open Critical / High | `Ready` |
| All `pass`, some accepted risks recorded | `Ready with known risks` |
| Any open Critical or High without acceptance | `Not ready` |
| Missing required evidence or approval | `Blocked pending approval / evidence` |
