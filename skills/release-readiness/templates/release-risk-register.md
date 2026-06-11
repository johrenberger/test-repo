# Release risk register

Output of the
[`release-readiness`](../../../../skills/release-readiness/SKILL.md)
skill. Consolidated view of risk for the release. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-risk-register.md`.

This is a **derived view** from the evidence artifacts (not
a primary report). The primary reports are the per-skill
findings; this register is the consolidated release-level
view. The shared
[`operational-risk-register`](../../../../templates/operational-risk-register.md)
template provides the generic structure; this template
customizes it for the release-readiness context.

## Template

```markdown
# Release risk register for <TASK_ID>

- **Task / change:** <branch / build / project identifier>
- **Release scope:** <one line>
- **Skill:** `release-readiness`
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>

## Composite risk

`<critical | high | medium | low>`

The composite is the highest open finding severity from the
evidence artifacts, unless explicitly de-rated by an
acceptance decision (in which case the composite is the
de-rated level with the decision reference noted).

## Open risks

| ID | Source | Severity | Summary | Owner | Mitigation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| <id> | <skill>-report.md | <sev> | <one line> | <role> | <one line> | <open | accepted | resolved> |

For each open risk, link to the source finding in the
appropriate per-skill report.

## Accepted risks (with rationale)

- `<id>` — accepted via `<decisions/<id>.md>` or
  `<ADR-NNNN>` — <one-line reason>
- Or `none`.

## Resolved risks

- `<id>` — resolved in `<commit sha or report path>` — <one
  line>
- Or `none`.

## Risks by source

### From `validation-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `code-change-review-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `security-review-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `dependency-change-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `migration-safety-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `architecture-review-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `documentation-impact-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From `observability-review-report.md`

- <id> — <severity> — <summary>
- Or `none`.

### From runbook review

- <id> — <severity> — <summary>
- Or `none`.

## Cross-skill duplicates

When the same finding appears in multiple reports, list it
once here and reference it from each report:

- `<canonical-id>` — canonical in
  `<source-skill>-report.md` — cross-referenced in
  `<other-skill>-report.md`

Or `none`.

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

- Readiness report:
  [`release-readiness-report.md`](release-readiness-report.md)
- Go / no-go checklist:
  [`go-no-go-checklist.md`](go-no-go-checklist.md)
- Source findings: <list of paths>

## Provenance

- Produced by `release-readiness` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-risk-register.md`
  (recommended; not required).
- Derived from primary evidence reports (not a primary
  report itself).
```

## Field rules

- `Composite risk` equals the highest severity of any
  open finding, unless explicitly de-rated.
- `Status` is one of `open | accepted | resolved`; an
  `accepted` finding must reference a `decisions/<id>.md`
  or `ADR-NNNN` that recorded the acceptance; a `resolved`
  finding must reference the change that resolved it.
- `Cross-skill duplicates` is required when the same finding
  appears in more than one report; it prevents the same
  Critical finding from being "fixed" in one report and
  still showing as open in another.

## When NOT to use

- A single review skill produced a single report with no
  findings needing cross-skill aggregation — the primary
  report is sufficient.
- The release is in `Backlog` and no reports exist yet —
  wait for reports before building the register.
