# Incident triage report

Output of the
[`incident-triage`](../../../../skills/incident-triage/SKILL.md)
skill. Records the incident summary, severity, blast radius,
suspected components, recommended next steps, action items,
and handoff. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-triage-report.md`.

## Template

```markdown
# Incident triage for <TASK_ID>

- **Incident ID:** <INC-YYYYMMDD-NNN>
- **Task:** <TASK_ID>
- **Skill:** `incident-triage`
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>
- **Severity:** <SEV-1 | SEV-2 | SEV-3 | SEV-4>
- **Status:** <investigating | mitigating | monitoring |
  resolved | post-incident>
- **On-call:** <role or person, or `unknown`>
- **Operator:** <role or person, or `unknown`>

## Summary

<one paragraph: what happened, who is impacted, and where
the investigation stands.>

## Facts (sourced)

Each fact is a timestamped event with a source. Do not
speculate here; this section is evidence only.

- `<UTC-ts>` — <fact> — source: `<log line | metric | ticket
  | commit | deploy id>` — file: <path, or `n/a`>
- `<UTC-ts>` — <fact> — source: `<...>`

## Hypotheses (labeled)

Each hypothesis is labeled `hypothesis`; the level of
confidence is named. A hypothesis without an evidence path is
not a hypothesis; it is a guess.

- **H1 (low | medium | high confidence):** <hypothesis> —
  evidence: `<file:lines | log | metric>`. Test with:
  `<low-risk step>`.
- **H2 (low | medium | high confidence):** <hypothesis> —
  evidence: `<...>`. Test with: `<...>`.

## Severity guidance

Cite the
[`references/incident-severity-guide.md`](../../../../skills/incident-triage/references/incident-severity-guide.md)
used to set the severity. State the reason for the current
severity in one line.

## Blast radius

- **Impacted service(s):** <list>
- **Impacted user group(s):** <list>
- **Impacted partner(s) / downstream:** <list, or `none`>
- **Likely scope:** <contained | partial | widespread |
  unknown>
- **Customer-facing:** <yes | no | partial>

## Impacted service / user group

<one paragraph: what is affected, in user terms. Cite the
source of the impact signal (a status page, a support
ticket, a metric).>

## Suspected components

| Component | Why suspected | Evidence |
| --- | --- | --- |
| <name> | <one line> | <file:lines | log | metric> |

For each suspected component, name the next test that would
confirm or rule it out.

## Known recent changes

- `<deploy / config / commit / dep change>` — <UTC-ts> —
  <one line>
- Or `none identified`.

## Available evidence

- **Logs:** <paths, or `unavailable`>
- **Metrics:** <dashboard / metric names, or `unavailable`>
- **Traces:** <trace ids, or `unavailable`>
- **Support tickets:** <ids, or `none`>
- **Runbooks:** <paths, or `none`>
- **Status page:** <current state, or `n/a`>

## Recommended next diagnostic steps

Each step is read-only or reversible, scoped to one
component, and labeled with the hypothesis it tests.

1. <step> — tests: <hypothesis id> — owner: <role> —
   expected output: <observable>
2. <step> — tests: <hypothesis id> — owner: <role> —
   expected output: <observable>

## Recommended mitigation options (operator call)

Each option is labeled with the trigger, action, expected
effect, rollback, and risk. **The skill does not execute.**

| Option | Trigger | Action | Expected effect | Rollback | Risk |
| --- | --- | --- | --- | --- | --- |
| <name> | <condition> | <step> | <observable> | <step> | <low | medium | high> |

Operator approval is required for every option. The skill
records the options; the operator decides.

## Immediate safety constraints

- <constraint> — escalation: <role>
- Or `none`.

## Action items

| ID | Action | Owner | Deadline | Status |
| --- | --- | --- | --- | --- |
| <id> | <one line> | <role> | <UTC-ts> | <open | in-progress | done> |

Detail per action item is in
`reports/action-items/<UTC-ts>-<id>.md` (per
[`templates/action-item.md`](action-item.md)).

## Escalation

- **Escalation needed:** <yes | no>
- **Escalation target:** <role, or `none`>
- **Reason:** <one line>

## Communication

- **Internal status updates:** <frequency, channel>
- **External status page:** <yes | no | not yet>
- **Customer comms:** <owner, or `n/a`>

## Handoff

- **Handoff packet:** <path to
  `handoffs/<UTC-ts>-incident-triage-to-<target>.md`>
- **Target role:** <MONITORING_AGENT | DEVOPS_AGENT |
  SECURITY_ANALYST_AGENT | SOFTWARE_ENGINEER_AGENT |
  PROJECT_COORDINATOR_AGENT | human operator>
- **Required next action:** <one line>

## Open blockers

- `<blocker_id>` — <one-line summary>
- Or `none`.

## Open approval gates

- `<APPROVAL-...>` — <one-line summary> (link to
  `approvals/<gate-id>.md`)
- Or `none`.

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Timeline: [`incident-timeline.md`](incident-timeline.md)
- Action items: <list of paths>
- Handoff packet: <path>

## Provenance

- Produced by `incident-triage` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-triage-report.md`
  (recommended; not required).
- This report is a **primary report** for the incident
  triage step. It is not derived from another report; the
  receiving role treats it as input.
```

## Field rules

- `Severity` is exactly one of `SEV-1 | SEV-2 | SEV-3 |
  SEV-4`. The `incident-severity-guide.md` is the source of
  the mapping; deviations are documented in `Severity
  guidance`.
- `Facts (sourced)` is required; every fact has a timestamp
  and a source. Facts without sources are not facts.
- `Hypotheses (labeled)` is required; every hypothesis has
  a confidence level and an evidence path. Hypotheses without
  evidence are not hypotheses.
- `Recommended mitigation options` is required; every option
  has a trigger, action, expected effect, rollback, and
  risk. The skill does not execute; the operator does.
- `Action items` are required when follow-up work is
  identified; each item has an owner and a deadline.

## When to update the report

The triage report is a living document during an active
incident. Update it whenever:

- A new fact is observed (logs, metrics, traces).
- A hypothesis is confirmed or ruled out.
- A mitigation option is taken or rejected by the operator.
- An action item changes status.
- The severity changes (with a `Severity guidance` note).
- The handoff target changes.

The handoff packet is updated alongside, not replaced.
