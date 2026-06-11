# ADR — Architecture Decision Record

Canonical record of a single architecture decision. Use
[`architecture-decision`](../../../../skills/architecture-decision/SKILL.md)
to produce this artifact. The longer-form reasoning belongs in
[`architecture-options-analysis.md`](architecture-options-analysis.md);
this ADR is the summary that future readers will find.

## File naming

Save as:

```
/data/.openclaw/workspace/tasks/<TASK_ID>/decisions/<UTC-ts>-adr.md
```

Where `<UTC-ts>` is the UTC timestamp of the decision in
`YYYYMMDDTHHMMSSZ` form (e.g. `20260611T090000Z`).

If the repo stores ADRs in-tree (e.g. `docs/adr/NNNN-title.md`),
the in-task ADR is the canonical record; in-tree storage is a
mirror and requires explicit task approval.

## Template

```markdown
# ADR-NNNN: <title>

- **ADR ID:** <ADR-NNNN> (sequential within the task, or use
  repo convention if in-tree)
- **Status:** <proposed | accepted | superseded | rejected>
- **Date:** <YYYY-MM-DD>
- **Task:** <TASK_ID>
- **Deciders:** <role list — e.g. `ARCHITECT_AGENT` plus named
  approver when the decision is irreversible>

## Context

<one to three paragraphs: what is happening in the environment
that drives this decision? What constraints are at play? What
are we trying to achieve? Cite the discovery artifact and
relevant files / modules.>

## Decision

<one sentence — the load-bearing statement of what we will do.>

We will <chosen approach> for <scope>, because <primary
reason tied to constraints>.

## Options considered

| Option | Summary | Verdict |
| --- | --- | --- |
| <name> | <one line> | chosen / rejected |
| <name> | <one line> | rejected |
| <name> | <one line> | rejected |

For each rejected option, link to the row in the options
analysis for the full rejection reason. The ADR does not
duplicate the analysis.

## Consequences

What becomes easier:

- <consequence>

What becomes harder:

- <consequence>

What we are locking in:

- <commitment>

What we are giving up:

- <tradeoff accepted>

## Tradeoffs

Honest listing of the tradeoffs, including ones that favor the
rejected options. If a tradeoff is opinion, label it
`opinion` and explain. If a number is estimated, label it
`estimate` and source it.

- <tradeoff> — `evidence | opinion | estimate` — <explanation>

## Reversibility

- **Class:** `cheap | expensive | irreversible`
- **Reversal cost (if cheap or expensive):** <one paragraph:
  what would it take to reverse this decision later?>
- **Mitigations if irreversible:** <list, or `n/a`>

## Validation plan

How the decision is validated when implemented:

- <validation step> — owner: <role> — done when: <observable>
- <validation step> — owner: <role> — done when: <observable>

A decision without a validation plan is not reviewable.

## Related files / systems

- <path or system> — <reason>
- <path or system> — <reason>

Cite the `repo-discovery` artifact when possible.

## Follow-up actions

- [ ] <action> — owner: <role> — by: <date or `before merge`>
- [ ] <action> — owner: <role> — by: <date or `before merge`>

## Cross-references

- Options analysis:
  `reports/architecture-options-analysis.md`
- Discovery artifact: `<path>` or `none`
- Prior ADRs: `<list>` or `none`
- Prior review: `<list>` or `none`

## Provenance

- Produced by `architecture-decision` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/decisions/<UTC-ts>-adr.md`
  (recommended; not required when mirrored in-tree).
- This is a **primary artifact** for the decision. Future
  decisions should read this ADR before making related ones in
  the same area.
```

## Required-field rules

- `Status` must be exactly one of `proposed`, `accepted`,
  `superseded`, `rejected`. Free-form text is not acceptable.
- `Decision` is one or two sentences. Long rationale belongs
  in the options analysis.
- `Reversibility` must be exactly `cheap`, `expensive`, or
  `irreversible`. The `Reversal cost` paragraph is required
  for `cheap` and `expensive`; for `irreversible` the
  `Mitigations if irreversible` list is required.
- `Validation plan` is required. A decision without a
  validation plan is not reviewable.
- `Related files / systems` is required when the decision
  implies code or configuration changes; if the decision is
  purely organizational, the field may be `n/a — organizational
  only` with a one-line reason.
- `Follow-up actions` may be `none` when the decision has no
  follow-up, but the field itself is required.

## Status transitions

- `proposed` → `accepted` (when an approver signs off)
- `proposed` → `rejected` (when the decision is not adopted)
- `accepted` → `superseded` (when a new ADR replaces this one;
  the new ADR links to this one in `Cross-references`)
- `rejected` is terminal
- `superseded` is terminal

The status transition is recorded in the same file (edit the
header) and the handoff packet for the implementation skill
points to the updated ADR.
