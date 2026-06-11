# Go / no-go checklist

Output of the
[`release-readiness`](../../../../skills/release-readiness/SKILL.md)
skill. Per-item pass / fail / concern record for the release
gate. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/go-no-go-checklist.md`.

This is a **derived view** from the release gate checklist
(see
[`references/release-gate-checklist.md`](../../../../skills/release-readiness/references/release-gate-checklist.md)).
The skill marks each item, links the evidence, and produces
the verdict the readiness report cites.

## Template

```markdown
# Go / no-go checklist for <TASK_ID>

- **Task / change:** <branch / build / project identifier>
- **Skill:** `release-readiness`
- **Generated at:** <ISO-8601>
- **Status:** <Ready | Ready with known risks | Not ready |
  Blocked pending approval / evidence>

## Gate items

For each item: verdict (`pass | concern | finding | n/a`),
evidence path, and a one-line note. When verdict is
`finding`, the finding is recorded in the
[`release-risk-register.md`](release-risk-register.md).

### 1. Tests pass

- **Verdict:** <pass | fail | not run>
- **Evidence:** `<path>` or `none`
- **Notes:** <one line>

### 2. Build success

- **Verdict:** <pass | fail | not run>
- **Evidence:** `<path>` or `none`
- **Notes:** <one line>

### 3. Lint / typecheck

- **Verdict:** <pass | fail | not run>
- **Evidence:** `<path>` or `none`
- **Notes:** <one line>

### 4. Unresolved Critical findings

- **Verdict:** <none | count>
- **Evidence:** <list of finding ids>
- **Notes:** <one line>

### 5. Unresolved High findings

- **Verdict:** <none | count>
- **Evidence:** <list of finding ids>
- **Notes:** <one line>

### 6. Migration safety

- **Verdict:** <pass | concern | finding | n/a>
- **Evidence:** `<path to migration-safety-report.md>` or
  `none` or `n/a — no migration`
- **Notes:** <one line>

### 7. Dependency changes

- **Verdict:** <pass | concern | finding | n/a>
- **Evidence:** `<path to dependency-change-report.md>` or
  `none` or `n/a — no dep change`
- **Notes:** <one line>

### 8. Security risks

- **Verdict:** <pass | concern | finding | n/a>
- **Evidence:** `<path to security-review-report.md>` or
  `none` or `n/a — no security change`
- **Notes:** <one line>

### 9. Architecture review

- **Verdict:** <pass | concern | finding | n/a>
- **Evidence:** `<path to architecture-review-report.md>` or
  `none` or `n/a — no architecture change`
- **Notes:** <one line>

### 10. Rollback plan

- **Verdict:** <documented | missing | n/a>
- **Evidence:** <path or `none`>
- **Notes:** <one line>

### 11. Feature flags / config

- **Verdict:** <planned | missing | n/a>
- **Evidence:** <path or `none`>
- **Notes:** <one line>

### 12. Monitoring / alerts / runbooks

- **Verdict:** <in place | partial | missing>
- **Evidence:** <paths to observability-review-report.md and
  runbook paths>
- **Notes:** <one line>

### 13. Documentation updates

- **Verdict:** <complete | partial | n/a>
- **Evidence:** `<path to documentation-impact-report.md>`
- **Notes:** <one line>

### 14. Known limitations

- **Verdict:** <recorded | unrecorded>
- **Evidence:** <list of limitations and acceptance
  decisions>
- **Notes:** <one line>

### 15. Manual approvals

- **Verdict:** <recorded | missing>
- **Evidence:** <list of decisions and approvers>
- **Notes:** <one line>

## Status summary

- **Pass count:** <number>
- **Concern count:** <number>
- **Finding count:** <number>
- **Not-run count:** <number>
- **N/A count:** <number>

## Status

`Ready | Ready with known risks | Not ready | Blocked pending approval / evidence`

Justification: <one paragraph>

## Cross-references

- Readiness report:
  [`release-readiness-report.md`](release-readiness-report.md)
- Risk register:
  [`release-risk-register.md`](release-risk-register.md)
- Release gate reference:
  [`../../../../skills/release-readiness/references/release-gate-checklist.md`](../../../../skills/release-readiness/references/release-gate-checklist.md)
- Evidence artifacts: <list of paths>

## Provenance

- Produced by `release-readiness` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/go-no-go-checklist.md`
  (recommended; not required).
- Derived from the release gate checklist reference and the
  evidence artifacts; the verdict and status flow into the
  readiness report.
```

## Field rules

- Every gate item has a verdict; missing verdicts are
  treated as `not run` and surface as blockers in the
  readiness report.
- When verdict is `finding`, the finding is recorded in the
  `release-risk-register.md` with id, severity, owner, and
  mitigation.
- `Status` is exactly one of the four values; the mapping
  rule is in the readiness report's `Status mapping` table.

## How to use

1. Walk through the gate items in order.
2. Cite the evidence for each item (or note `n/a` when
   applicable).
3. Aggregate verdicts into the status summary.
4. Apply the status mapping from the readiness report.
5. The readiness report links to this checklist as the
   per-item evidence trail.
