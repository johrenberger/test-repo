# Runbook quality checklist

Read on demand by
[`runbook-authoring`](../../SKILL.md). The checklist is
applied to a runbook before it is handed off for adoption.
It is not a substitute for the runbook template; it is a
lens.

## 1. The runbook is findable

- [ ] Filename matches the repo's existing runbook naming
  convention.
- [ ] The runbook is at the canonical repo location
  (`docs/runbooks/`, `runbooks/`, or equivalent).
- [ ] The runbook is linked from the relevant alert
  definitions or dashboards (when the repo has them).
- [ ] The runbook is linked from the
  [`release-readiness`](../release-readiness/SKILL.md)
  report when the runbook was created for a release.

## 2. The purpose and scope are clear

- [ ] Purpose is a single paragraph.
- [ ] Scope is explicit (what is covered; what is out of
  scope).
- [ ] The runbook is for one service / process / failure
  mode; broader scope is split into multiple runbooks.

## 3. Symptoms are concrete

- [ ] The on-call can identify the runbook from the signal
  (alert, log, metric, user report).
- [ ] Symptoms are not "the system is broken"; they are
  observable, named, and linkable to dashboards or alerts.

## 4. Severity guidance is set

- [ ] The runbook's severity matches the triggering
  incident's severity.
- [ ] The severity guidance cross-references
  [`incident-triage`](../incident-triage/SKILL.md).

## 5. Prerequisites are listed

- [ ] Required credentials, access, and env vars are
  listed.
- [ ] Placeholders are used for sensitive values
  (`<REDACTED: kind>`).
- [ ] Missing prerequisites are flagged as blockers for
  adoption.

## 6. Diagnostic commands are safe and sourced

- [ ] Diagnostic commands are read-only or reversible.
- [ ] Every command has a source (file:lines, operator
  evidence, or `validation-runner` report).
- [ ] Unverified commands are explicitly labeled
  `unverified — confirm before running`.
- [ ] Expected output is documented for each command.

## 7. Mitigation options are concrete

- [ ] Each option has a trigger, action, expected effect,
  rollback, and risk.
- [ ] The runbook does not pick the option for the on-call;
  it presents the options and lets the on-call decide.
- [ ] Destructive options have an approval gate and a
  rollback step.

## 8. Rollback / escalation is explicit

- [ ] Every destructive step has a rollback.
- [ ] Every mitigation has a "verify after" step.
- [ ] Escalation target and trigger are documented.

## 9. Validation after mitigation is observable

- [ ] The on-call can confirm the fix worked using
  existing observability.
- [ ] The validation is concrete (a metric, a log pattern,
  a status check), not "we'll see."

## 10. Cross-references are real

- [ ] ADRs, observability reviews, release reports,
  incident reports, and related runbooks are linked.
- [ ] Every cross-reference resolves to an existing
  artifact.

## 11. Owner and contact are present

- [ ] Primary owner / team is named (or `unassigned —
  confirm with on-call`).
- [ ] Secondary owner / team is named.
- [ ] On-call channel and communications channel are
  documented.

## 12. No secrets in the runbook

- [ ] No real tokens, keys, passwords, hostnames, internal
  URLs, or credentials in the runbook.
- [ ] Placeholders (`<REDACTED: kind>`) are used for
  sensitive values.

## Red flags (block adoption)

- Destructive command without an approval gate.
- Unverified command labeled as verified.
- No rollback step for a destructive mitigation.
- No "verify after" step.
- Real-looking credentials in the runbook.
- Owner / team is `unassigned` with no plan to assign.
- Symptoms are vague ("the system is broken") and not
  linkable to a signal.

## How to use

1. After writing the runbook, run through this checklist.
2. Mark each item `pass | concern | finding` in the
   authoring report.
3. Any red flag fires a blocker; the runbook is not adopted
   until the red flag is resolved.
4. The on-call or owner signs off in the runbook's change
   log when the runbook moves from `draft` to `verified`.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Runbook template: [`../templates/runbook.md`](../templates/runbook.md)
- Troubleshooting template:
  [`../templates/troubleshooting-guide.md`](../templates/troubleshooting-guide.md)
- Authoring report:
  [`../templates/runbook-authoring-report.md`](../templates/runbook-authoring-report.md)
- Observability review:
  [`../../observability-review/SKILL.md`](../../observability-review/SKILL.md)
- Incident triage:
  [`../../incident-triage/SKILL.md`](../../incident-triage/SKILL.md)
- Release readiness:
  [`../../release-readiness/SKILL.md`](../../release-readiness/SKILL.md)
