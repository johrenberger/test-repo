# Architecture options analysis

Longer-form reasoning for an
[`architecture-decision`](../../../../skills/architecture-decision/SKILL.md)
ADR. The ADR is the summary; this document holds the full
options comparison, evidence, and rejection reasons. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-options-analysis.md`.

## Template

```markdown
# Architecture options analysis for <TASK_ID>

- **Task:** <TASK_ID>
- **Decision area:** <one-line area, e.g. "API style for the
  partner integration layer">
- **Generated at:** <ISO-8601>
- **Companion ADR:** `<path to adr>`
- **Source of constraints:** `<list of paths, or "task
  description">`

## Constraints

Functional:

- <requirement>

Non-functional:

- latency: <target or "unspecified">
- throughput: <target or "unspecified">
- scale: <target or "unspecified">
- reliability: <RTO / RPO / availability target, or "unspecified">
- security / compliance: <list, or "standard">
- cost: <budget, or "unspecified">
- team / tooling: <list, or "unspecified">
- deployment / runtime: <list, or "unspecified">

Reversibility class of the decision: <cheap | expensive |
irreversible>.

## Options

### Option A: <name>

**Description.** <one paragraph: what the option is and how it
works in this repo's context.>

**Strengths.**

- <strength> — evidence: <file:lines or external source>
- <strength>

**Weaknesses.**

- <weakness> — evidence: <file:lines or external source>
- <weakness>

**Cost.**

- Engineering effort: <rough estimate or T-shirt size>
- Runtime cost: <rough estimate or "negligible">
- Operational complexity: <low | medium | high>

**Reversibility.** <cheap | expensive | irreversible> — <one
paragraph: what reversal would require>

**Extension seams.** <what can be added later without
re-deciding>

**Validation approach.** <how this option is validated when
implemented>

**Verdict.** <chosen | rejected>

### Option B: <name>

<same structure>

### Option C: <name> (optional)

<same structure, only when there are more than two viable
options>

## Comparison matrix

| Criterion | Option A | Option B | Option C |
| --- | --- | --- | --- |
| Functional fit | <score or note> | | |
| Performance / latency | | | |
| Reliability / failure modes | | | |
| Security / compliance | | | |
| Cost (engineering) | | | |
| Cost (runtime) | | | |
| Operational complexity | | | |
| Reversibility | | | |
| Extension seams | | | |
| Team fit / familiarity | | | |
| Time-to-implement | | | |

Scores are advisory; the decision text is what counts. Use
`+`, `0`, `-`, or short notes.

## Rejected options — explicit reasons

If a familiar pattern is **not** selected, document it here
even if it has its own section above. The absence of reasoning
is itself a review-time finding.

### Microservices (rejected if not chosen)

- Reason: <why this option was rejected for this decision>

### Event sourcing (rejected if not chosen)

- Reason: <why>

### CQRS (rejected if not chosen)

- Reason: <why>

### Service mesh (rejected if not chosen)

- Reason: <why>

### Queue / broker (rejected if not chosen)

- Reason: <why>

### Cache layer (rejected if not chosen)

- Reason: <why>

### Sharding (rejected if not chosen)

- Reason: <why>

(Add or remove items based on the decision area. The list is
intentionally explicit so the reasoning is auditable.)

## Decision

- **Selected option:** <name>
- **One-sentence decision statement:** <as in the ADR>
- **Why this option beats the alternatives on the binding
  constraints:** <one paragraph>

## Validation plan (as in the ADR)

- <validation step> — owner: <role> — done when: <observable>

## Implementation impact

- <module / file> — <reason>
- <module / file> — <reason>

The implementation skill that should own the work:

- <`backend-implementation` | `frontend-implementation` |
  `integration-implementation` | `implementation-orchestrator`>
- Rationale: <one line>

## Review gates required

- [ ] `security-review` — when: <condition, or `n/a`>
- [ ] `dependency-change-review` — when: <condition, or `n/a`>
- [ ] `database-migration-safety` — when: <condition, or `n/a`>
- [ ] `architecture-review` — when: <condition, or `n/a`>

## Outstanding risks accepted by this decision

- <risk> — mitigation: <one line>
- <risk> — mitigation: <one line>

## Cross-references

- Companion ADR: `<path>`
- Discovery: `<path>` or `none`
- Prior review: `<list>` or `none`
- Prior ADRs in same area: `<list>` or `none`
```

## Field rules

- Every option must have **at least one** strength and
  **at least one** weakness documented. A option with only
  strengths is not a real comparison.
- The "Rejected options — explicit reasons" section is
  required when any of the listed common patterns is
  applicable but not selected. If a pattern is genuinely
  irrelevant (e.g. the decision has nothing to do with
  data partitioning, so sharding is not a candidate), state
  that explicitly: "Sharding: not applicable — <reason>."
- The decision statement is one sentence. Long rationale
  belongs in the option sections.
- The validation plan in this document must match the
  validation plan in the ADR. If they differ, the ADR is the
  source of truth and the analysis is updated to match.

## Provenance

- Produced by `architecture-decision` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-options-analysis.md`
  (recommended; not required).
- This is a **primary artifact** for the decision.
