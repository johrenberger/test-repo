# ADR index (shared)

Generic index of architecture decision records for a task or
project. Used by
[`architecture-decision`](../../../skills/architecture-decision/SKILL.md)
and consumers (`architecture-review`,
`release-readiness`, `documentation-update`) to navigate the
set of decisions.

The index is a **derived view**; the primary artifacts are
the individual ADRs in `decisions/<UTC-ts>-adr.md` (or
in-tree at `docs/adr/NNNN-*.md`).

## Template

```markdown
# ADR index for <TASK_ID or project>

- **Scope:** <task id, project name, or repo>
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>

## Active decisions

| ADR ID | Title | Status | Date | Owner |
| --- | --- | --- | --- | --- |
| <ADR-NNNN> | <title> | <proposed | accepted | superseded | rejected> | <YYYY-MM-DD> | <role> |

## Decisions by area

### Service boundaries

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### Database / persistence

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### API style

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### Messaging / eventing

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### Authentication / authorization

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### Deployment topology

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

### Other

- `<ADR-NNNN>` — <one-line summary>
- Or `none`.

## Superseded decisions

- `<ADR-NNNN>` — superseded by `<ADR-MMMM>` — reason: <one
  line>
- Or `none`.

## Rejected decisions

- `<ADR-NNNN>` — rejected because: <one line>
- Or `none`.

## Open proposed decisions

- `<ADR-NNNN>` — awaiting approval since <YYYY-MM-DD> —
  approver: <role>
- Or `none`.

## Cross-references

- Each ADR's path: <list of paths>
- Discovery: `<path>` or `none`
- Architecture review: `<path>` or `none`
- Release readiness: `<path>` or `none`

## Provenance

- Produced as a **derived view** from the primary ADRs.
- Output path: `<task path>/reports/adr-index.md` or
  `<repo>/docs/adr/INDEX.md` (when in-tree)
```

## Field rules

- `Active decisions` lists every ADR with status `proposed`
  or `accepted`. `superseded` and `rejected` ADRs are
  listed in their own sections.
- `Decisions by area` groups ADRs by topic; the topic
  headers are the recommendation; the actual repo / task
  may use different groupings.
- `Superseded decisions` records the chain of supersession
  (which ADR supersedes which).
- `Rejected decisions` records the rejection reason; an ADR
  rejected without a reason is incomplete.
- `Open proposed decisions` lists ADRs that have not been
  approved; each has a waiting period and an approver.

## When to update the index

- When a new ADR is created.
- When an ADR's status changes (`proposed → accepted`,
  `accepted → superseded`, etc.).
- When the project / task scope changes and a new area
  emerges.
- At release time (the
  [`release-readiness`](../release-readiness/SKILL.md)
  report links to the index).

## Cross-references

- ADR template: [`../skills/architecture-decision/templates/adr.md`](../skills/architecture-decision/templates/adr.md)
- Options analysis:
  [`../skills/architecture-decision/templates/architecture-options-analysis.md`](../skills/architecture-decision/templates/architecture-options-analysis.md)
- Decision quality checklist:
  [`../skills/architecture-decision/references/decision-quality-checklist.md`](../skills/architecture-decision/references/decision-quality-checklist.md)
