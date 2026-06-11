# Architecture review report

Output of the
[`architecture-review`](../../../../skills/architecture-review/SKILL.md)
skill. Records the change set under review, the architectural
dimensions evaluated, the ranked findings, the ADR
recommendation, and the handoff. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-review-report.md`.

## Template

```markdown
# Architecture review for <TASK_ID>

- **Task:** <TASK_ID>
- **Reviewer:** `architecture-review` skill
- **Generated at:** <ISO-8601>
- **Change set under review:** <branch / PR / proposal path>
- **Discovery artifact:** `<path>` or `none`
- **Prior decisions in area:** `<list>` or `none`
- **Composite risk:** <critical | high | medium | low>

## Change set summary

<one paragraph: what the change is, what it touches, and what
acceptance criteria it claims to satisfy.>

## Modules / files in scope

| Path | Role | Notes |
| --- | --- | --- |
| <file> | <owner / role> | <one line> |

## Architectural dimensions

For each dimension, mark `pass | concern | finding` and cite
evidence. A dimension is `finding` only when the issue is
specific enough to act on; `concern` is for soft signals that
need discussion.

| Dimension | Verdict | Evidence |
| --- | --- | --- |
| Alignment with existing architecture | <verdict> | <file:lines or ADR id> |
| Boundary clarity | <verdict> | <evidence> |
| Coupling / cohesion | <verdict> | <evidence> |
| Data ownership | <verdict> | <evidence> |
| API contract stability | <verdict> | <evidence> |
| Failure modes | <verdict> | <evidence> |
| Scalability assumptions | <verdict> | <evidence> |
| Security boundaries | <verdict> | <evidence> |
| Observability needs | <verdict> | <evidence> |
| Deployment / runtime implications | <verdict> | <evidence> |
| Reversibility | <verdict> | <evidence> |
| Migration path | <verdict> | <evidence> |
| Over-engineering risk | <verdict> | <evidence> |

## Findings

Each finding uses the shared
[`findings-severity`](../../../../templates/findings-severity.md)
format. Cross-skill duplicates are noted in the
`Cross-skill duplicates` section.

| ID | Severity | Category | File:lines | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| <id> | <sev> | <category> | <file:lines> | <one line> | <open | resolved | accepted> |

Detail for each finding:

### <id> — <summary>

- **Severity:** <critical | high | medium | low | nit>
- **Category:** <boundary | coupling | data-ownership |
  contract | failure-mode | scalability | security |
  observability | deployment | reversibility | migration |
  over-engineering | other>
- **File:lines:** `<file>:<start>-<end>`
- **Source skill:** `architecture-review`
- **Evidence:** <code excerpt or statement, secrets redacted>
- **Recommendation:** <concrete fix, not "consider X">
- **Approval required:** <yes | no>
- **Cross-reference:** `<other-finding-id>` if duplicated, or
  `none`

## ADR recommendation

- **ADR required:** `yes | no | required`
- **Rationale:** <one paragraph explaining the recommendation>
- **Suggested ADR area:** <scope, e.g. "API style for the
  partner integration layer">
- **If required, blocking implementation until ADR is
  accepted:** <yes | no>

## Review gates required

- [ ] `security-review` — when: <condition, or `n/a`>
- [ ] `dependency-change-review` — when: <condition, or `n/a`>
- [ ] `database-migration-safety` — when: <condition, or `n/a`>
- [ ] `code-change-review` — when: <condition, or `n/a`>
- [ ] `observability-review` — when: <condition, or `n/a`>

## Cross-skill duplicates

When the same finding appears in another report:

- `<canonical-id>` — canonical in
  `<source-skill>-report.md` — cross-referenced in
  `architecture-review-report.md`

Or `none`.

## Out-of-scope findings (routed elsewhere)

- `<id>` — routed to `<skill>` for handling
- Or `none`.

## Handoff

- **Next skill:** <`architecture-decision` |
  `implementation-orchestrator` | `security-review` |
  `dependency-change-review` | `database-migration-safety` |
  `code-change-review` | `observability-review` | `closed`>
- **Handoff packet:** `<path>`
- **Required next action:** <one line>

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

## Cross-references

- Discovery: `<path>` or `none`
- Prior ADRs: `<list>` or `none`
- Prior review: `<list>` or `none`
- Handoff packet: `<path>`

## Provenance

- Produced by `architecture-review` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-review-report.md`
  (recommended; not required).
- This report is a **primary report** for the architecture
  review step. It is not derived from another report; the
  receiving skill treats it as input.
```

## Field rules

- `Composite risk` equals the highest severity of any open
  finding, unless explicitly de-rated by an approval gate
  (in which case the composite is the de-rated level with the
  gate reference noted).
- `Findings` rows must each have an id, severity, category,
  file:lines, summary, and status. Detail blocks are
  required for `Critical` and `High` findings; `Medium`,
  `Low`, and `Nit` may use the table row only.
- `Status` is one of `open | resolved | accepted`; a
  `resolved` finding must reference the change that resolved
  it; an `accepted` finding must reference the
  `decisions/<id>.md` that recorded the acceptance.
- `Cross-skill duplicates` is required when the same finding
  appears in another report.

## When the review is for a specific ADR

If the change is implementing a decision recorded in an ADR,
the report's `Change set summary` must include a link to the
ADR. Findings that contradict the ADR are recorded as `High`
or `Critical` depending on impact, and the report recommends
either updating the ADR (via `architecture-decision`) or
revising the change.
