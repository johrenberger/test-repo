# SLO review

Output of the
[`observability-review`](../../../../skills/observability-review/SKILL.md)
skill when the review is SLO-focused. Records the existing
or proposed SLOs / SLIs, the evidence, the gaps, and the
recommendations. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/slo-review.md`.

## Template

```markdown
# SLO review for <TASK_ID>

- **Task / change:** <branch / PR / service>
- **Skill:** `observability-review`
- **Generated at:** <ISO-8601>
- **Composite SLO risk:** <critical | high | medium | low>

## Inputs

- **Service(s) in scope:** <list>
- **Existing SLOs / SLIs:** <list, or `none`>
- **Change set:** `<path or branch>`
- **SLO doc location:** `<path>` or `none`
- **Error budget policy:** `<path>` or `none`

## SLI inventory

For each user-facing capability, list:

- **Capability:** <name>
- **SLI:** <measurement, e.g. "fraction of requests with
  HTTP status < 500 and latency < 500ms p99">
- **Source:** <metric name, log query, trace query>
- **Coverage:** <requests covered, sampling, total volume>
- **SLO target:** <e.g. "99.9% over 30 days">
- **Current performance:** <observed value, with window>
- **Error budget burn rate:** <current burn rate, with
  window>
- **Verdict:** <pass | concern | finding>

## SLO gaps

| Capability | SLI defined? | SLI measurable? | SLO set? | Verdict |
| --- | --- | --- | --- | --- |
| <name> | <yes | no> | <yes | no> | <yes | no> | <verdict> |

## Findings

| ID | Severity | Category | Capability | Summary | Status |
| --- | --- | --- | --- | --- | --- |
| <id> | <sev> | <category> | <name> | <one line> | <open | resolved | accepted> |

Detail per finding:

### <id> — <summary>

- **Severity:** <critical | high | medium | low | nit>
- **Category:** <missing-sli | unmeasurable-sli |
  missing-slo | unrealistic-slo | error-budget-policy |
  alert-coverage | other>
- **Capability:** <name>
- **Source skill:** `observability-review`
- **Evidence:** <metric name, log query, or statement>
- **Recommendation:** <concrete fix>
- **Routed to:** <role>

## Recommendations (concrete, routed)

- **What:** <one line>
- **Owner:** <role>
- **Routed to:** <skill or role>
- **Acceptance:** <observable>

## Handoff

- **Handoff packet:** <path>
- **Target role:** <role>
- **Required next action:** <one line>

## Cross-references

- Observability review (parent):
  [`observability-review-report.md`](observability-review-report.md)
- SLO doc: `<path>` or `none`
- Error budget policy: `<path>` or `none`

## Provenance

- Produced by `observability-review` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/slo-review.md`
  (recommended; not required).
- This report is a **primary report** for the SLO review
  step. It is not derived from another report; the receiving
  role treats it as input.
```

## Field rules

- Every user-facing capability has a row in the SLI
  inventory; missing rows are recorded as `finding` in
  `SLO gaps`.
- The SLO target is a number with a window; "we'd like the
  system to be fast" is not a target.
- The error budget burn rate is a number; "we're burning"
  is not a measurement.

## When SLIs are missing

When the SLI is missing or unmeasurable, the recommendation
is the smallest change that produces a measurable SLI. New
metrics are routed to `MONITORING_AGENT` via handoff; the
skill does not add metrics itself.
