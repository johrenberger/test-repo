# incident-triage

Structure incident investigation and response without making
unsafe production changes. The skill is **read-only by
default**; it produces a triage report, a timeline, action
items, and a handoff to the appropriate role. It does not
deploy, rollback, restart, scale, or otherwise mutate
production.

## Purpose

Coordinate incident response in a way that:

- separates facts from hypotheses;
- builds a clear timeline of what happened and when;
- identifies likely blast radius and impacted user groups;
- recommends next diagnostic steps;
- recommends mitigation options **without executing them**;
- records action items and routes them to the right role
  (Monitoring, DevOps, Security, Software Engineer, Project
  Coordinator);
- preserves evidence and decisions for the post-incident
  review.

The skill is the **coordination layer** of incident response.
The actual production actions are the operator's call, taken
under the on-call protocol.

## Trigger

Use when:

- A service is down or degraded.
- Tests / CI failures suggest systemic breakage (not an
  isolated test flake).
- Monitoring or logs indicate a production or staging issue.
- A user, partner, or stakeholder reports incident-like
  symptoms.
- A rollback / mitigation decision is needed.
- A post-incident analysis is requested.
- A near-miss or pre-incident signal needs triage.

## Do Not Use When

- The task is normal feature implementation — out of scope.
- The issue is already clearly isolated to a small code bug
  and no incident process is needed — use
  [`backend-implementation`](../backend-implementation/SKILL.md)
  or [`frontend-implementation`](../frontend-implementation/SKILL.md)
  directly.
- The task is purely a security investigation (e.g. suspected
  intrusion) — hand off to
  [`security-review`](../security-review/SKILL.md) and the
  security analyst on call; the security review owns the
  investigation.
- The task is a known operational problem with a runbook —
  follow the runbook (see
  [`runbook-authoring`](../runbook-authoring/SKILL.md)) and
  use this skill only if the runbook does not apply or is
  insufficient.

## Required Inputs

- **Incident summary** — what was reported, by whom, when.
- **Initial symptoms** — what the user or operator observed.
- **Impacted service / user group** — what is affected and
  who is impacted.
- **Start time** — when the issue started, if known.
- **Current status** — open, mitigated, monitoring, resolved.
- **Known recent changes** — recent deploys, config changes,
  dependency changes.
- **Available evidence** — logs, metrics, traces, support
  tickets, runbook references.
- **On-call / operator** — who is responding (or "unknown").
- **Severity** — initial severity, when known.

## Preflight

1. Confirm the incident is real (not a single test failure or
   user error). When the signal is ambiguous, the skill
   continues with low severity and updates the report as
   evidence arrives.
2. Confirm the on-call / operator is identified or the
   report routes to the on-call role. If neither is true,
   stop and request identification.
3. Confirm the skill will not execute production actions.
   The skill's outputs are recommendations; production
   actions are the operator's call.
4. Confirm no production credentials or live production
   access is required for the triage. If credentials are
   required, the report flags the access need; access is
   granted by the operator.

## Workflow

1. **Establish the facts.** Document the incident summary,
   severity, impacted service / user group, start time,
   current status, symptoms, known recent changes, suspected
   components, available evidence (logs / metrics / traces),
   and immediate safety constraints. Separate facts from
   hypotheses from the start.

2. **Build the timeline.** Use
   [`templates/timeline.md`](templates/timeline.md). The
   timeline is the load-bearing artifact; it is the basis
   for both diagnosis and post-incident review.

3. **Identify likely blast radius.** What services, users,
   partners, and downstream systems are affected? Is the
   impact contained or cascading?

4. **Identify suspected components.** Based on the symptoms
   and recent changes, list the components most likely to be
   the root cause. For each, cite the evidence (a metric
   anomaly, a recent deploy, a log pattern).

5. **Recommend next diagnostic steps.** List concrete,
   low-risk steps an operator or developer can take to
   narrow the cause. Steps must be:

   - Read-only when possible (logs, metrics, traces,
     dashboards, runbook references).
   - Reversible when not (a feature-flag toggle is
     reversible; a deploy is not — flag the latter as
     operator-only).
   - Scoped (touch one component or one user group, not the
     whole system).

6. **Recommend mitigation options.** List options the
   operator can take. Each option is labeled with the
   trigger, the action, the expected effect, the rollback
   plan, and the risk. **Do not execute.** The report is
   advice, not a runbook execution.

7. **Identify immediate safety constraints.** Are there
   data-loss risks, security implications, customer-impacting
   data exposure, or compliance triggers? If yes, the
   report escalates to a human / security / compliance
   owner immediately.

8. **Record action items.** Use
   [`templates/action-item.md`](templates/action-item.md).
   Each action item has an owner, a deadline, a status, and
   a link to the action.

9. **Produce the incident triage report.** Use
   [`templates/incident-triage-report.md`](templates/incident-triage-report.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-triage-report.md`.

10. **Produce the incident timeline.** Save to
    `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-timeline.md`.

11. **Hand off.** Produce a
    [`handoff-packet`](../handoff-packet/SKILL.md) to the
    appropriate role:

    - `MONITORING_AGENT` — for observability review
      (missing alerts, missing dashboards, unclear SLOs)
    - `DEVOPS_AGENT` — for mitigation execution (operator
      approval required)
    - `SECURITY_ANALYST_AGENT` — for suspected security
      involvement
    - `SOFTWARE_ENGINEER_AGENT` — for code-side investigation
    - `PROJECT_COORDINATOR_AGENT` — for follow-up tracking
      and post-incident review

    The packet's `Required next action` is the next concrete
    step (typically: "operator executes mitigation X" or
    "engineer investigates hypothesis Y").

## Allowed Actions

- Read logs, metrics, traces, dashboards, runbooks (when
  access is available; the skill does not bypass access
  controls).
- Read the repo, recent deploys, recent config changes,
  recent commits.
- Write the incident triage report, timeline, action items,
  and handoff packet.
- Update `task.md` / `state.json` to reflect the incident
  status.

## Forbidden Actions

- **Do not deploy, rollback, restart production services,
  rotate secrets, change firewall rules, or modify
  infrastructure** unless explicitly approved by an operator
  / approver. The skill is advice, not execution.
- **Do not run destructive commands.** No `rm`, no
  `kubectl delete`, no DB drop, no mass update, no log
  purge.
- **Do not expose secrets or sensitive incident details
  unnecessarily.** Use `<REDACTED: kind>` placeholders in
  reports when the detail is sensitive. Customer identifiers
  are redacted.
- **Do not speculate without labeling hypotheses.** Every
  hypothesis is tagged `hypothesis`; every fact is tagged
  `fact`. A timeline that conflates the two is not useful.
- **Do not bypass access controls.** If the skill needs logs
  or dashboards it cannot reach, the report flags the access
  gap; the operator grants access.
- **Do not publish incident details externally.** Public
  status pages and customer communications are out of
  scope; route to the human owner.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management` and direct escalation) when:

- Customer, security, or data-loss impact is suspected.
- Production access or credentials are required and the
  operator / approver is not available.
- Immediate mitigation requires operator approval and the
  operator is unreachable.
- Legal, compliance, or regulatory notification may be
  required (e.g. data breach, payment impact).
- The incident is suspected to be security-driven
  (intrusion, ransomware, credential leak) — escalate to
  `SECURITY_ANALYST_AGENT` and follow the security incident
  process.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-triage-report.md`**
  — see
  [`templates/incident-triage-report.md`](templates/incident-triage-report.md).
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-timeline.md`**
  — see [`templates/timeline.md`](templates/timeline.md).
- **Action items** — list of
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/action-items/<UTC-ts>-<id>.md`
  (one per item), per
  [`templates/action-item.md`](templates/action-item.md).
- **Handoff packet** to the appropriate role (Monitoring,
  DevOps, Security, Software Engineer, Project Coordinator).

## Handoff Contract

Fields the receiving role may rely on:

- `triage_report_path` — absolute path to the triage report
- `timeline_path` — absolute path to the timeline
- `incident_summary` — one-paragraph summary
- `severity` — current severity (may evolve)
- `impacted_service_or_user_group` — what is impacted
- `blast_radius` — likely blast radius
- `suspected_components` — list of suspected components with
  evidence
- `recommended_diagnostic_steps` — list of low-risk next
  steps
- `recommended_mitigation_options` — list of operator-call
  options
- `immediate_safety_constraints` — list of safety flags
- `action_items` — list of action-item paths
- `escalation_needed` — `yes | no` and to whom
- `facts` vs `hypotheses` — separated throughout

Fields the receiving role must not rely on:

- "resolved" — the skill does not resolve incidents; the
  operator does. The skill's status is "triaged, awaiting
  operator action."
- "approved" — the skill does not approve mitigations; the
  operator does.
- "no security implication" — security is asserted by
  `SECURITY_ANALYST_AGENT`, not by this skill.

## Validation

The triage report is "validated" when:

1. The timeline has timestamped events with sources cited.
2. Facts and hypotheses are separated throughout.
3. The blast radius and suspected components are documented
   with evidence.
4. The recommended next steps are concrete, low-risk, and
   reversible when possible.
5. The handoff packet has all 14 required fields.
6. The action items have owners, deadlines, and status.

The skill itself runs no shell commands; it may invoke
[`repo-discovery`](../repo-discovery/SKILL.md) to identify
files, recent commits, and recent changes, but it does not
run any production-touching command.

## Completion Criteria

- The incident is summarized with severity and blast radius.
- The timeline is built with timestamped, sourced events.
- Suspected components and recommended next steps are
  documented.
- Action items are created with owners and deadlines.
- The triage report and timeline are written.
- A handoff packet is produced and the next role accepts
  it.
- The task's `state.json` reflects the triage outcome
  (typically a non-`closed` state until the incident is
  resolved).

## Cross-references

- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md)
- Operational:
  [`observability-review`](../observability-review/SKILL.md),
  [`runbook-authoring`](../runbook-authoring/SKILL.md)
- Review: [`security-review`](../security-review/SKILL.md)
- Release: [`release-readiness`](../release-readiness/SKILL.md)
- Decisions: [`architecture-decision`](../architecture-decision/SKILL.md)
- Reference:
  [`references/incident-severity-guide.md`](references/incident-severity-guide.md)
- Templates:
  [`templates/incident-triage-report.md`](templates/incident-triage-report.md),
  [`templates/timeline.md`](templates/timeline.md),
  [`templates/action-item.md`](templates/action-item.md)
- Shared: [`incident-summary`](../../templates/incident-summary.md),
  [`operational-risk-register`](../../templates/operational-risk-register.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
