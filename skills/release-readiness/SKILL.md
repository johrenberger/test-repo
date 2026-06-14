---
name: release-readiness
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- devops-agent
- product-manager-agent
purpose: Assess whether a change, branch, build, or project is ready for release or
  handoff to deployment. The skill produces a go/no-go readiness report. **It never
  deploys.** Deployment is a human / operator action; this skill only informs it.
---

# release-readiness

Assess whether a change, branch, build, or project is ready
for release or handoff to deployment. The skill produces a
go/no-go readiness report. **It never deploys.** Deployment is
a human / operator action; this skill only informs it.

## Purpose

Provide a single, auditable answer to "are we ready to
release?" by:

- collecting evidence from validation, code review, security
  review, dependency review, migration safety, architecture
  review, and documentation update;
- evaluating the evidence against a release gate checklist;
- surfacing unresolved Critical / High findings, missing
  validation, missing rollback plans, and missing approvals;
- producing a clear status (`Ready`, `Ready with known risks`,
  `Not ready`, `Blocked pending approval / evidence`).

The skill is the **last stop before deployment**, not a
replacement for the individual review skills. When those
skills are missing, the skill flags the gap rather than
performing the review itself.

## Trigger

Use when:

- Implementation is complete and a release decision is
  needed.
- Code review is complete and the change is being considered
  for handoff to deployment.
- Validation results exist and need to be aggregated.
- A release / deployment decision is needed.
- DevOps or Project Coordinator requests a release
  assessment.
- Production-readiness is uncertain.
- A change has been sitting in `Ready` for too long and the
  blockers need to be surfaced.

## Do Not Use When

- The task is discovery-only — out of scope; use
  [`repo-discovery`](../repo-discovery/SKILL.md).
- Implementation has not started — out of scope; the readiness
  report would be empty.
- No validation or review evidence exists and no validation
  can be run — out of scope; the skill cannot mark ready
  without evidence.
- The task is to make a deployment decision — the skill
  produces the readiness report; a human or operator makes
  the deploy call.
- The task is purely operational (alerting, runbook) — use
  [`observability-review`](../observability-review/SKILL.md)
  or [`runbook-authoring`](../runbook-authoring/SKILL.md)
  first, then return to release-readiness if release impact
  is in question.

## Required Inputs

- **Task / change** — the branch, build, or project being
  assessed.
- **Acceptance criteria** — what "ready" means for this
  release (e.g. "no Critical findings, rollback plan
  documented, on-call coverage confirmed").
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`.
- **Evidence artifacts** — produced by other skills. The
  skill expects to find at least:
  - `validation/validation-report.md` (or a
    `validation-runner` run with a report)
  - `reports/code-change-review-report.md` (or the reviewer
    is documented)
  - `reports/security-review-report.md` (when security
    applies)
  - `reports/dependency-change-report.md` (when deps
    changed)
  - `reports/migration-safety-report.md` (when migration
    applies)
  - `reports/architecture-review-report.md` (when
    architecture applies)
  - `reports/documentation-impact-report.md` (when docs
    changed)
  - any ADR(s) produced by
    [`architecture-decision`](../architecture-decision/SKILL.md)
- **CI status** — when available through repo files
  (`.github/workflows/`, `.gitlab-ci.yml`, etc.) or
  provided externally.
- **Release plan** — what the release is (hotfix, minor,
  major), the rollout strategy, the rollback plan, the
  monitoring plan.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If
   not, run `repo-discovery` first.
2. Confirm the evidence artifacts are attached. If a required
   artifact is missing, the skill records the gap as a
   blocker; it does not run the missing review itself.
3. Confirm the release plan (rollout, rollback, monitoring)
   is documented. If not, the skill flags the gap.
4. Confirm the skill will not deploy. The skill's output is
   a report; deployment is out of scope.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact
   and confirm the relevant modules, build artifacts, and
   release infrastructure are identified.

2. **Collect evidence.** For each evidence area, locate the
   artifact and summarize the relevant findings:

   - Validation results (tests, lint, typecheck, build)
   - Code review findings
   - Security review findings
   - Dependency review findings
   - Migration safety findings
   - Architecture review findings and ADRs
   - Documentation impact report
   - Observability review (when present)
   - Runbook availability (when the change touches ops)
   - CI status when available
   - Manual approvals recorded in `decisions/<id>.md`

3. **Evaluate the release gate.** For each gate item, mark
   `pass | concern | finding`. The gate items live in
   [`references/release-gate-checklist.md`](references/release-gate-checklist.md).

   The default gate items are:

   - Tests / build / lint / typecheck status
   - Unresolved Critical / High findings
   - Migration safety
   - Dependency changes
   - Security risks
   - Rollback plan
   - Feature flags / config
   - Monitoring / alerts / runbooks
   - Documentation updates
   - Known limitations
   - Manual approvals required

4. **Determine status.** Map the gate verdicts to one of:

   - `Ready` — all gate items pass; no unresolved Critical
     or High findings.
   - `Ready with known risks` — gate items pass; some
     documented risks remain that the team has explicitly
     accepted via `decisions/<id>.md` or an ADR. The risks
     are listed in the report.
   - `Not ready` — at least one Critical or High finding is
     unresolved, and no acceptance decision exists.
   - `Blocked pending approval / evidence` — the readiness
     report is incomplete because approval, evidence, or
     review is missing.

5. **Produce the go / no-go checklist.** Use
   [`templates/go-no-go-checklist.md`](templates/go-no-go-checklist.md)
   as the per-item pass / fail record.

6. **Produce the release readiness report.** Use
   [`templates/release-readiness-report.md`](templates/release-readiness-report.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-readiness-report.md`.

7. **Produce the release risk register.** Use
   [`templates/release-risk-register.md`](templates/release-risk-register.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-risk-register.md`.

8. **Hand off.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to
   `DEVOPS_AGENT` (deployment) or to a human operator. The
   packet's `Required next action` is "review readiness
   report; deploy only after operator approval."

## Allowed Actions

- Read repo files, evidence artifacts, and CI configuration.
- Run `repo-discovery` scripts (read-only).
- Read the repo's CI workflow files (read-only) to confirm
  the gate items match the actual CI.
- Write the readiness report, risk register, go/no-go
  checklist, and handoff packet.
- Update `task.md` / `state.json` to reflect the readiness
  outcome.

## Forbidden Actions

- **Do not deploy.** Deployment is a human / operator action.
- **Do not run production commands.** No deploys, no
  rollbacks, no restarts, no scaling, no traffic shifts.
- **Do not override failed validation.** A failed test is
  not a release blocker to be "manually approved around";
  the report records the failure and the release is not
  ready.
- **Do not mark ready with unresolved Critical findings.** A
  Critical finding must be resolved or formally accepted via
  `decisions/<id>.md` before the skill can mark the release
  `Ready` or `Ready with known risks`.
- **Do not hide unvalidated areas.** When validation was not
  run, the report flags the gap; the skill does not claim
  validation that did not happen.
- **Do not introduce new infrastructure dependencies** as
  part of the readiness assessment.
- **Do not modify code, configuration, or runbooks.** The
  skill is read-only; updates to those are routed to
  other skills.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Validation is missing for a high-risk change (security,
  migration, dependency, architecture).
- An unresolved Critical or High security / migration /
  dependency / architecture finding has no acceptance
  decision.
- No rollback path exists for a risky release.
- Production approval is required and no operator / approver
  is identified.
- A required evidence artifact is missing and cannot be
  produced in this skill's scope.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-readiness-report.md`**
  — see
  [`templates/release-readiness-report.md`](templates/release-readiness-report.md).
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/release-risk-register.md`**
  — see
  [`templates/release-risk-register.md`](templates/release-risk-register.md).
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/go-no-go-checklist.md`**
  — see
  [`templates/go-no-go-checklist.md`](templates/go-no-go-checklist.md).
- **Handoff packet** to `DEVOPS_AGENT` (deployment) or a
  human operator.

## Handoff Contract

Fields the receiving skill / operator may rely on:

- `readiness_report_path` — absolute path to the readiness
  report
- `go_no_go_checklist_path` — absolute path to the checklist
- `risk_register_path` — absolute path to the risk register
- `status` — exactly one of
  `Ready | Ready with known risks | Not ready | Blocked pending approval / evidence`
- `open_blockers` — list of blocker ids
- `required_approvals` — list of approvals still needed
- `rollout_plan` — concrete rollout steps
- `rollback_plan` — concrete rollback steps
- `monitoring_plan` — what is being watched during rollout
- `evidence_artifacts` — list of paths to evidence reports
- `known_limitations` — list of limitations the team has
  accepted

Fields the receiving skill / operator must not rely on:

- "deployed" — the skill does not deploy. Deployment is the
  operator's call.
- "approved" — the skill produces a status; approval is
  asserted by a `decisions/<id>.md` entry.
- "no risk" — the risk register is the source of risk truth;
  the readiness report summarizes it.

## Validation

The readiness report is "validated" when:

1. Every gate item in the go / no-go checklist has a verdict
   (`pass | concern | finding`).
2. Every finding has an id, severity, owner, and disposition
   (resolved, accepted, or open).
3. The status maps to the gate verdicts; the mapping rule is
   applied (no Critical / High open without acceptance).
4. The evidence artifacts are cited.
5. The handoff packet has all 14 required fields.

The skill itself runs no shell commands; it may invoke
[`validation-runner`](../validation-runner/SKILL.md) to gather
additional evidence when the existing artifacts are
insufficient.

## Completion Criteria

- All evidence artifacts are summarized.
- The release gate is evaluated against
  [`references/release-gate-checklist.md`](references/release-gate-checklist.md).
- The status is determined and justified.
- The readiness report, risk register, and go / no-go
  checklist are written.
- A handoff packet is produced and the next actor (DEVOPS or
  a human operator) accepts it.
- The task's `state.json` reflects the readiness outcome.

## Cross-references

- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Review skills (evidence sources):
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md),
  [`dependency-change-review`](../dependency-change-review/SKILL.md),
  [`database-migration-safety`](../database-migration-safety/SKILL.md),
  [`architecture-review`](../architecture-review/SKILL.md),
  [`documentation-update`](../documentation-update/SKILL.md)
- Decisions: [`architecture-decision`](../architecture-decision/SKILL.md)
- Operational:
  [`observability-review`](../observability-review/SKILL.md),
  [`runbook-authoring`](../runbook-authoring/SKILL.md),
  [`incident-triage`](../incident-triage/SKILL.md)
- Reference:
  [`references/release-gate-checklist.md`](references/release-gate-checklist.md)
- Templates:
  [`templates/release-readiness-report.md`](templates/release-readiness-report.md),
  [`templates/release-risk-register.md`](templates/release-risk-register.md),
  [`templates/go-no-go-checklist.md`](templates/go-no-go-checklist.md)
- Shared: [`operational-risk-register`](../../templates/operational-risk-register.md),
  [`go-no-go-summary`](../../templates/go-no-go-summary.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
