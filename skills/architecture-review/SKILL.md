# architecture-review

Review proposed or implemented architecture for correctness,
simplicity, scalability, security, maintainability, and
operational fit. The skill is **read-only by default**; it
produces a findings report and may recommend a formal decision
via
[`architecture-decision`](../architecture-decision/SKILL.md).

## Purpose

Audit architecture-level work so that:

- the proposal is grounded in the repo's actual state, not in
  imagined system properties;
- boundary clarity, coupling, data ownership, contract
  stability, and operational failure modes are evaluated
  explicitly;
- recommendations for microservices, event sourcing, CQRS,
  service mesh, queues, caches, and sharding are made only
  when the simpler design fails a stated requirement;
- an ADR is recommended (or required) when the change is
  material;
- the receiving implementation or decision skill has a
  ranked findings report it can act on.

## Trigger

Use when reviewing:

- A new service or module design
- API or data-model boundary changes
- Proposed architecture changes
- Implementation that may have architecture drift
- Large refactors
- Cross-module or cross-service changes
- Event-driven or async designs
- Major persistence changes
- A specific architecture decision is in flight and a second
  opinion is required

## Do Not Use When

- The task is code-style review only — use
  [`code-change-review`](../code-change-review/SKILL.md).
- The task is test-only — use
  [`test-generation`](../test-generation/SKILL.md) or
  [`validation-runner`](../validation-runner/SKILL.md).
- The task has no architecture implications — out of scope.
- The task is implementing a decision that has already been
  made — use the implementation skills directly.
- The task is purely operational — use
  [`observability-review`](../observability-review/SKILL.md)
  or [`runbook-authoring`](../runbook-authoring/SKILL.md).
- The task is purely security-focused — use
  [`security-review`](../security-review/SKILL.md); the
  architecture review may reference the security review's
  findings but should not duplicate them.

## Required Inputs

- **Task description** — the change or proposal under review.
- **Acceptance criteria** — what the change is supposed to
  achieve.
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`.
- **Change set or design doc** — diff, branch, PR link,
  proposal markdown, ADR draft, or sequence diagram.
- **Existing ADRs** — if the repo stores them
  (`docs/adr/`, `docs/decisions/`). Read so the review is
  consistent with prior decisions.
- **Existing review findings** —
  `code-change-review-report.md`,
  `security-review-report.md`,
  `dependency-change-review-report.md`,
  `database-migration-safety-report.md`,
  `architecture-decision` artifacts, or a `decisions/<id>.md`
  entry that frames the review.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; the review must not invent repo
   facts.
2. Confirm the change set or design doc is attached. If only a
   verbal description is available, stop and request the
   artifact; an architecture review without a concrete change
   is not useful.
3. Read existing ADRs and recent decisions in the same area
   to avoid contradicting prior decisions.
4. Confirm the review is read-only; no implementation skill
   is allowed in this workflow.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the relevant modules, ADRs, and dependency graph
   evidence are identified.

2. **Map the change set to modules.** For each affected
   module, note the entry points, callers, callees, and
   ownership. Cite concrete files / paths from the discovery
   artifact or the change set.

3. **Inspect the relevant architecture docs and contracts.**
   Read ADRs, API specs, schema files, sequence diagrams, and
   any docs the repo stores as source of truth. Do not invent
   behavior that is not in the repo.

4. **Evaluate** the change against the architectural
   dimensions below. For each, record evidence and a verdict
   (`pass | concern | finding`).

   - **Alignment with existing architecture** — does the change
     fit, or does it introduce a new pattern?
   - **Boundary clarity** — are module / service / API
     boundaries explicit, with stable contracts?
   - **Coupling / cohesion** — is the change in the right
     module? Are callers colocated with callees when
     appropriate?
   - **Data ownership** — is the data owned by exactly one
     module, with documented ownership for derived / cached
     data?
   - **API contract stability** — does the change keep
     existing contracts working, with additive changes
     preferred over breaking ones?
   - **Failure modes** — what fails, and how? Timeouts,
     retries, partial failures, schema drift, network
     partitions, and downstream unavailability must be
     considered.
   - **Scalability assumptions** — does the design scale at
     the documented scale? Are the assumptions explicit?
   - **Security boundaries** — are trust boundaries explicit?
     Auth, secrets, PII, and input validation considered?
   - **Observability needs** — are logs, metrics, traces, and
     health checks adequate for the new behavior?
   - **Deployment / runtime implications** — what changes at
     deploy time, in config, in infrastructure?
   - **Reversibility** — is the change cheap, expensive, or
     irreversible to reverse?
   - **Migration path** — is there a way to roll the change
     out incrementally, with rollback?
   - **Over-engineering risk** — does the change introduce
     complexity that is not justified by a stated
     requirement?

5. **Rank findings** using
   [`findings-severity`](../../templates/findings-severity.md)
   levels: `Critical | High | Medium | Low | Nit`.

6. **Decide whether an ADR is required.** Material changes
   (new service, new datastore, new boundary, new contract,
   new pattern) require an ADR. Light changes (refactor within
   a module, additive field on a stable contract) may not.

7. **Hand off as appropriate:**

   - If a new decision is required → hand off to
     [`architecture-decision`](../architecture-decision/SKILL.md).
   - If migration safety is in question → hand off to
     [`database-migration-safety`](../database-migration-safety/SKILL.md).
   - If security is in question → hand off to
     [`security-review`](../security-review/SKILL.md).
   - If a dependency change is in question → hand off to
     [`dependency-change-review`](../dependency-change-review/SKILL.md).
   - If implementation is the next step → hand off to
     [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
     with the review report attached.

8. **Produce the report.** Use
   [`templates/architecture-review-report.md`](templates/architecture-review-report.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-review-report.md`.

## Allowed Actions

- Read repo files, ADRs, and existing review reports.
- Run `repo-discovery` scripts (read-only).
- Write the architecture review report and handoff packet.
- Update `task.md` / `state.json` to reflect the review
  outcome.

## Forbidden Actions

- **Do not modify code.** The review is read-only.
- **Do not make architecture decisions silently.** When the
  review identifies a decision point, hand off to
  [`architecture-decision`](../architecture-decision/SKILL.md);
  the review records findings, not decisions.
- **Do not recommend microservices, event sourcing, CQRS,
  service mesh, queues, caches, or sharding without
  evidence** that the simpler design fails a stated
  requirement. The recommendation must be cited in the
  report and linked to the constraint.
- **Do not ignore operational failure modes.** A review
  without a failure-mode analysis is incomplete.
- **Do not duplicate security review.** When the finding is
  security-critical, hand off to
  [`security-review`](../security-review/SKILL.md) and
  cross-reference; do not stand in for it.
- **Do not present speculation as fact.** If a finding is
  based on inference, label it `inference` and explain the
  assumption.
- **Do not bypass review gates.** The architecture review
  recommends reviews; it does not replace them.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- The change set or design doc is not attached.
- The change requires approval (architecture-novel work) and
  no approval has been scheduled.
- Required context (ADRs, contracts, runbooks) is missing.
- The review identifies a production-safety risk that
  requires immediate operator notification.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-review-report.md`**
  — see
  [`templates/architecture-review-report.md`](templates/architecture-review-report.md).
- **Handoff packet** to `architecture-decision` (when a new
  decision is required), to a narrower implementation skill
  (when the review clears the change for implementation), or
  to a review skill (when security / migration / dependency
  review is required).

## Handoff Contract

Fields the receiving skill may rely on:

- `review_report_path` — absolute path to the review report
- `composite_risk` — highest open finding severity
- `open_findings` — list of finding ids with severity and
  category
- `adr_recommended` — `yes | no | required`
- `adr_path` — absolute path to the ADR, when one exists
- `review_gates_required` — list of review skills that must
  run before implementation
- `out_of_scope_findings` — list of finding ids that were
  routed to other review skills

Fields the receiving skill must not rely on:

- "approved" — the review is a findings report, not an
  approval. Approval is asserted by a `decisions/<id>.md`
  entry or by an explicit `accepted` ADR.
- "secure" — security is asserted only by
  [`security-review`](../security-review/SKILL.md).
- "scales" — claims of scale require a load test, SLO, or
  named capacity plan; the review is not evidence of scale.

## Validation

The review is "validated" when:

1. The report covers all 13 architectural dimensions in the
   workflow (pass / concern / finding verdict for each).
2. Every finding has an id, severity, file:lines, evidence,
   and recommendation.
3. The composite risk is the highest open finding severity
   unless explicitly de-rated.
4. The ADR recommendation is justified.
5. The handoff packet has all 14 required fields.
6. No finding is recorded with severity `Critical` or `High`
   without a routed review gate or an explicit
   `decisions/<id>.md` acceptance entry.

The skill itself runs no shell commands.

## Completion Criteria

- The change set is mapped to concrete modules / files.
- All 13 architectural dimensions are evaluated.
- Findings are ranked and recorded with required fields.
- The ADR recommendation is made and justified.
- The handoff packet points to the right next skill.
- The task's `state.json` reflects the review outcome.

## Cross-references

- Decision creation: [`architecture-decision`](../architecture-decision/SKILL.md)
- Implementation entry point:
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
- Review gates:
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md),
  [`database-migration-safety`](../database-migration-safety/SKILL.md),
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Reference: [`references/architecture-risk-checklist.md`](references/architecture-risk-checklist.md)
- Profile: [`references/modular-monolith-checklist.md`](references/modular-monolith-checklist.md)
- Profile: [`references/distributed-systems-checklist.md`](references/distributed-systems-checklist.md)
- Template: [`templates/architecture-review-report.md`](templates/architecture-review-report.md)
- Shared: [`findings-severity`](../../templates/findings-severity.md),
  [`risk-register`](../../templates/risk-register.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
