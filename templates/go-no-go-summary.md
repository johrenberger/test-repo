# Go / no-go summary (shared)

One-page executive summary of a release's go / no-go status.
Produced by
[`release-readiness`](../release-readiness/SKILL.md) and
intended for quick review by approvers and stakeholders. The
detailed per-item checklist lives in
[`release-readiness/templates/go-no-go-checklist.md`](../release-readiness/templates/go-no-go-checklist.md);
this template is the **summary**.

The summary is a **derived view**; the primary report is
[`release-readiness-report.md`](../release-readiness/templates/release-readiness-report.md).

## Template

```markdown
# Go / no-go summary for <TASK_ID>

- **Release:** <branch / build / version>
- **Release scope:** <one line>
- **Date:** <YYYY-MM-DD>
- **Skill:** `release-readiness`
- **Status:** <Ready | Ready with known risks | Not ready |
  Blocked pending approval / evidence>

## One-line recommendation

<one sentence: "Ship it" / "Ship with caveats X, Y" / "Hold
until Z" / "Blocked by A, B">.

## Composite risk

`<critical | high | medium | low>`

## Open blockers (count: <number>)

- <blocker title> — owner: <role>
- Or `none`.

## Unresolved Critical findings (count: <number>)

- <finding id> — <one line>
- Or `none`.

## Unresolved High findings (count: <number>)

- <finding id> — <one line>
- Or `none`.

## Accepted risks (with rationale)

- <risk title> — accepted via `<decisions/<id>.md>` or
  `<ADR-NNNN>`
- Or `none`.

## Required approvals still pending

- <role or person> — reason: <one line>
- Or `none`.

## Rollout plan (one line)

<strategy> — triggers: <condition for next stage> and
<condition for rollback>.

## Rollback plan (one line)

<estimated time> — operator: <role> — data implications:
<destructive | additive | n/a>.

## Monitoring plan (one line)

<dashboards / alerts / on-call coverage summary>.

## Cross-references

- Full readiness report:
  [`release-readiness-report.md`](../release-readiness/templates/release-readiness-report.md)
- Go / no-go checklist:
  [`go-no-go-checklist.md`](../release-readiness/templates/go-no-go-checklist.md)
- Risk register:
  [`release-risk-register.md`](../release-readiness/templates/release-risk-register.md)
- Handoff packet: <path>

## Provenance

- Produced as a **derived view** by
  [`release-readiness`](../release-readiness/SKILL.md).
- Output path: `<task path>/reports/go-no-go-summary.md`
  (recommended; not required).
- The summary is intended for fast review; the per-item
  evidence lives in the full report and the per-finding
  records.
```

## Field rules

- `One-line recommendation` is one sentence; the goal is a
  decision-ready statement.
- `Status` is exactly one of the four values from the
  release-readiness skill.
- Counts (open blockers, Critical findings, etc.) are
  numbers, not vibes.
- `Cross-references` point to the primary reports; the
  summary is a pointer, not a primary artifact.

## How to use

1. The release-readiness skill produces this summary at
   the end of its workflow, alongside the full report.
2. The summary is shared with the approver and stakeholders
   for the go / no-go call.
3. The full report and the per-finding records are linked
   from the summary for evidence.
