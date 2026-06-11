# Incident severity guide

Read on demand by
[`incident-triage`](../../SKILL.md). Maps a real incident
to a severity level (`SEV-1` to `SEV-4`). The mapping is a
starting point; the actual severity is set by the
incident-triage report and confirmed by the on-call / owner
when the incident evolves.

## SEV-1 — Major

A SEV-1 incident is a major customer-impacting outage or a
material risk to the business. The response is all-hands.

Trigger:

- A primary service is fully unavailable to a large fraction
  of users.
- A material subset of users cannot complete a critical
  workflow.
- Data loss, data corruption, or a security breach is
  occurring.
- The system is in a state that requires immediate
  communication to executives, customers, or regulators.

Response:

- All-hands: on-call, engineering, security, legal /
  compliance (when applicable), communications.
- Hourly status updates internally; external status page
  updated as the situation evolves.
- A post-incident review is required; the timeline is the
  input.

Exit:

- Service restored to normal operation.
- Customer-facing impact is contained and communicated.
- A post-incident review is scheduled (within 5 business
  days, per industry default; adjust per repo convention).

## SEV-2 — Significant

A SEV-2 incident is a significant degradation that affects
a meaningful fraction of users or a meaningful workflow.

Trigger:

- A primary service is degraded; a meaningful subset of
  users sees failures or significant latency.
- A non-critical workflow is fully unavailable.
- A region / cell is down; failover is not automatic.
- A new failure mode is observed and the blast radius is
  unclear.

Response:

- On-call + relevant engineering.
- Status updates at least every 2 hours internally; external
  status page updated as the situation evolves.
- A post-incident review is required.

Exit:

- Service restored to normal operation, or the issue is
  understood and a follow-up is scheduled.
- A post-incident review is scheduled (within 10 business
  days).

## SEV-3 — Minor

A SEV-3 incident is a minor degradation that affects a small
fraction of users or a non-critical workflow.

Trigger:

- A non-critical workflow is degraded.
- An edge case is causing failures for a small subset of
  users.
- A non-production environment is broken in a way that
  blocks development.

Response:

- On-call + relevant engineering; not all-hands.
- Status updates as the situation evolves; the on-call
  decides the cadence.
- A post-incident review is recommended but not required.

Exit:

- Service restored, or a workaround is in place.
- A fix is scheduled (this week, this sprint, or as
  appropriate).

## SEV-4 — Low

A SEV-4 incident is a low-impact issue that does not
significantly affect users or the business.

Trigger:

- A cosmetic issue, a non-urgent bug, a low-priority alert.
- A non-blocking environment issue.

Response:

- The on-call or the relevant team acknowledges and
  schedules a fix.
- No status page update; no all-hands.

Exit:

- Fix is scheduled and tracked as a normal work item.

## Mapping rules

- **Customer impact matters more than internal impact.** A
  fully internal issue that blocks development is at most
  SEV-3; a customer-impacting issue starts at SEV-2.
- **Suspected data loss or security breach starts at
  SEV-1.** Confirm with `SECURITY_ANALYST_AGENT` and
  `LEGAL_COMPLIANCE_AGENT` before downgrading.
- **Severity can escalate, not silently downgrade.** The
  on-call can raise severity; downgrading requires
  documented evidence (the impact is contained, the user
  group is smaller than initially thought, etc.).
- **Severity is independent of resolution time.** A SEV-3
  that takes 3 weeks to fix is still SEV-3; the response
  effort is not the severity.
- **When in doubt, raise and confirm later.** A SEV-1 that
  turns out to be SEV-2 is fine; a SEV-2 that turns out to
  be SEV-1 is a missed escalation.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Triage report template:
  [`../templates/incident-triage-report.md`](../templates/incident-triage-report.md)
- Timeline template:
  [`../templates/timeline.md`](../templates/timeline.md)
- Action item template:
  [`../templates/action-item.md`](../templates/action-item.md)
- Release readiness:
  [`../../release-readiness/SKILL.md`](../../release-readiness/SKILL.md)
  (for post-incident follow-up that produces a release
  fix)
- Observability review:
  [`../../observability-review/SKILL.md`](../../observability-review/SKILL.md)
  (for incidents that surface missing observability)
- Runbook authoring:
  [`../../runbook-authoring/SKILL.md`](../../runbook-authoring/SKILL.md)
  (for incidents that surface missing runbooks)
