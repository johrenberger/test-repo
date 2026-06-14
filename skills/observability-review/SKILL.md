---
name: observability-review
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- data-analyst-agent
- monitoring-agent
- financial-analyst-agent
purpose: Review whether a service or change has adequate logging, metrics, tracing,
  health checks, and alert / runbook support. The skill is **read-only by default**;
  it produces an observability review report and recommendations. It does not modify
  production monitoring systems.
---

# observability-review

Review whether a service or change has adequate logging,
metrics, tracing, health checks, and alert / runbook support.
The skill is **read-only by default**; it produces an
observability review report and recommendations. It does not
modify production monitoring systems.

## Purpose

Ensure that:

- failures in the new behavior are observable;
- logs avoid secrets and PII;
- key events are logged;
- metrics exist for critical paths;
- traces / correlation IDs are preserved across boundaries;
- health checks reflect dependencies appropriately;
- alerts are actionable and have runbooks.

The skill is the operational counterpart to
[`security-review`](../security-review/SKILL.md): it audits
whether the change can be **seen** in production, not just
**shipped** to production.

## Trigger

Use when:

- New backend / integration behavior is added.
- Release-readiness requires operational review.
- Incident-triage identifies missing observability.
- Monitoring agent requests a service review.
- Production-readiness is being assessed.
- A new dependency or service is integrated.
- A change touches authentication, persistence, or any
  failure-prone boundary.

## Do Not Use When

- The task is UI-only with no operational signal change —
  out of scope; the UI may still need observability for
  client-side error reporting, but that is a different
  review surface.
- The repo has no service / runtime component and no
  monitoring concern — out of scope.
- The task is to add a specific log line or metric — small
  enough to be done directly; record the change in the
  implementation report, not in a full review.
- The task is to author a runbook — use
  [`runbook-authoring`](../runbook-authoring/SKILL.md) for
  that; this skill audits observability, not runbooks.
- The task is purely security-focused — use
  [`security-review`](../security-review/SKILL.md); this
  skill audits operational observability, not security.

## Required Inputs

- **Service / change** — what is being reviewed.
- **Acceptance criteria** — what "adequate observability"
  means for this review.
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`.
- **Change set or design doc** — diff, branch, PR, or
  design markdown.
- **Existing observability artifacts** — current dashboards,
  alert definitions, runbook paths, SLO / SLI definitions
  (when the repo stores them).
- **Prior review findings** — `code-change-review-report.md`,
  `security-review-report.md`,
  `architecture-review-report.md`,
  `incident-triage-report.md` (when the review is
  post-incident), or `release-readiness-report.md`.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If
   not, run `repo-discovery` first.
2. Confirm the change set or service boundary is attached.
3. Confirm the review is read-only. Modifications to
   monitoring systems, alerts, or dashboards are routed to
   the appropriate team via handoff.
4. Read existing runbooks and SLO / SLI definitions to
   avoid contradicting them.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact
   and confirm the relevant modules, services, and config
   files are identified.

2. **Map the change to observable signals.** For each
   affected module / service, list the entry points, the
   critical paths, and the dependencies.

3. **Inspect existing observability patterns.** Read the
   relevant reference:
   [`references/logging-metrics-tracing-checklist.md`](references/logging-metrics-tracing-checklist.md).
   For each, record evidence (`file:lines` for the existing
   pattern).

4. **Evaluate** the change against the observability
   dimensions:

   - **Logging** — are key events logged? Are logs
     structured? Do logs avoid secrets and PII? Is the
     redaction list explicit?
   - **Metrics** — do metrics exist for the critical paths
     (latency, error rate, throughput, queue depth,
     saturation)?
   - **Tracing** — do traces propagate correlation IDs
     across boundaries? Are spans named usefully?
   - **Health checks** — liveness, readiness, and
     dependency-aware health checks (DB, queue, downstream
     service).
   - **SLOs / SLIs** — are there stated objectives
     (availability, latency, error rate)? Are they
     measured?
   - **Alerts** — are alerts actionable, with runbooks?
     Are alert thresholds sane (not noisy, not silent)?
   - **Dashboards** — are the dashboards usable for
     triage?

5. **Rank findings** using
   [`findings-severity`](../../templates/findings-severity.md)
   levels.

6. **Recommend changes or handoffs.** For each finding:

   - The change can be done by the implementation skill →
     record the recommendation and hand off.
   - The change requires monitoring / dashboard / alert
     config (out of repo) → hand off to
     `MONITORING_AGENT`.
   - The change requires a new runbook → hand off to
     [`runbook-authoring`](../runbook-authoring/SKILL.md).
   - The change is security-relevant (secrets in logs) →
     hand off to
     [`security-review`](../security-review/SKILL.md).

7. **Produce the observability review report.** Use
   [`templates/observability-review-report.md`](templates/observability-review-report.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/observability-review-report.md`.

8. **Produce an SLO review when relevant.** Use
   [`templates/slo-review.md`](templates/slo-review.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/slo-review.md` (when
   the review is SLO-focused).

9. **Hand off.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to the
   next role.

## Allowed Actions

- Read repo files, dashboards, alert definitions, runbook
  references, SLO / SLI definitions.
- Run `repo-discovery` scripts (read-only).
- Write the observability review report, SLO review, and
  handoff packet.
- Update `task.md` / `state.json` to reflect the review
  outcome.

## Forbidden Actions

- **Do not modify production monitoring systems.** No
  dashboard changes, no alert changes, no SLO changes; route
  via handoff.
- **Do not add noisy alerts without runbook guidance.** A
  new alert without a runbook is a pager-bomb; the review
  flags the gap and the handoff routes the runbook work to
  `runbook-authoring`.
- **Do not log secrets or sensitive payloads.** A finding
  that the existing pattern logs secrets is recorded as
  `Critical`; the recommendation is to redact, and the
  security review is engaged.
- **Do not introduce vendors / agents / libraries** without
  explicit approval and a
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  gate. New observability tooling is a significant
  dependency.
- **Do not present speculation as fact.** If a finding is
  based on inference, label it `inference` and explain.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Observability changes require infrastructure or vendor
  configuration that is not in scope for this skill.
- Alerting changes could page on-call teams; operator
  approval is required.
- A sensitive logging risk (secrets in logs) is found and
  the security review has not been engaged.
- The change requires production access or credentials to
  validate.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/observability-review-report.md`**
  — see
  [`templates/observability-review-report.md`](templates/observability-review-report.md).
- **Optional**
  **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/slo-review.md`**
  when the review is SLO-focused — see
  [`templates/slo-review.md`](templates/slo-review.md).
- **Handoff packet** to the appropriate role.

## Handoff Contract

Fields the receiving role may rely on:

- `review_report_path` — absolute path to the review report
- `slo_review_path` — absolute path to the SLO review, or
  `none`
- `composite_risk` — highest open finding severity
- `open_findings` — list of finding ids with severity and
  category
- `recommendations` — list of concrete recommendations
- `monitoring_changes_required` — list of changes that
  require `MONITORING_AGENT` action
- `runbook_changes_required` — list of changes that
  require `runbook-authoring` action
- `security_findings` — list of findings routed to
  `security-review`
- `out_of_scope_findings` — list of findings routed to
  other skills

Fields the receiving role must not rely on:

- "monitored in production" — this is a review, not a
  deployment claim.
- "alerts in place" — alerts may be added via the handoff
  to `MONITORING_AGENT`; until that handoff is acted on,
  the recommendation is not in effect.
- "no security implication" — security is asserted by
  [`security-review`](../security-review/SKILL.md).

## Validation

The observability review is "validated" when:

1. The report covers all observability dimensions
   (logging, metrics, tracing, health, SLO, alerts,
   dashboards).
2. Every finding has an id, severity, file:lines, evidence,
   and recommendation.
3. The composite risk is the highest open finding severity
   unless explicitly de-rated.
4. The handoff packet has all 14 required fields.
5. No recommendation requires the skill to bypass its
   read-only contract.

The skill itself runs no shell commands.

## Completion Criteria

- The change is mapped to observable signals.
- All observability dimensions are evaluated with evidence.
- Findings are ranked and recorded with required fields.
- Recommendations are concrete and routed to the right
  role.
- The observability review report and (when relevant) the
  SLO review are written.
- A handoff packet is produced and the next role accepts
  it.
- The task's `state.json` reflects the review outcome.

## Cross-references

- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md)
- Operational:
  [`runbook-authoring`](../runbook-authoring/SKILL.md),
  [`incident-triage`](../incident-triage/SKILL.md)
- Review:
  [`security-review`](../security-review/SKILL.md),
  [`code-change-review`](../code-change-review/SKILL.md),
  [`architecture-review`](../architecture-review/SKILL.md)
- Decisions: [`architecture-decision`](../architecture-decision/SKILL.md)
- Release: [`release-readiness`](../release-readiness/SKILL.md)
- Reference:
  [`references/logging-metrics-tracing-checklist.md`](references/logging-metrics-tracing-checklist.md)
- Templates:
  [`templates/observability-review-report.md`](templates/observability-review-report.md),
  [`templates/slo-review.md`](templates/slo-review.md)
- Shared: [`findings-severity`](../../templates/findings-severity.md),
  [`operational-risk-register`](../../templates/operational-risk-register.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
