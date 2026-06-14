---
name: architecture-decision
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- tech-lead-agent
purpose: Create evidence-based architecture decisions and Architecture Decision Records
  (ADRs) for material technical choices. The skill produces decision artifacts; it
  does not implement code or alter the running architecture.
---

# architecture-decision

Create evidence-based architecture decisions and Architecture
Decision Records (ADRs) for material technical choices. The
skill produces decision artifacts; it does not implement code or
alter the running architecture.

This skill is for **deciding**. For **auditing an existing or
proposed** architecture (read-only review), use
[`architecture-review`](../architecture-review/SKILL.md). For
**implementing** the chosen design, route through
[`implementation-orchestrator`](../implementation-orchestrator/SKILL.md).

## Purpose

Make architectural decisions in a way that:

- surfaces the constraints and tradeoffs that drove the decision;
- records at least the viable options considered (including
  rejected ones);
- states the reversibility and implementation impact
  explicitly;
- produces an ADR artifact for any material decision, so the
  decision is reviewable later, not just recoverable from chat
  history;
- prefers the **simplest design that satisfies requirements and
  leaves extension seams** over speculative future-proofing.

## Trigger

Use when a task involves any of:

- Service boundaries (new service, split, merge, extract,
  consolidate)
- Database or storage selection (RDBMS, document, key-value,
  graph, search index, time-series, blob)
- API style selection (REST, GraphQL, gRPC, RPC, event-stream,
  hybrid)
- Messaging / eventing (queue, topic, event bus, stream
  platform, schema registry)
- Authentication / authorization architecture (SSO, OAuth, OIDC,
  mTLS, RBAC, ABAC, multi-tenant)
- Major dependency or framework choice
- Deployment topology (single-region, multi-region, active/active,
  active/passive, edge)
- Scalability / reliability / security tradeoffs
- Irreversible or hard-to-reverse technical decisions
- An existing architecture-review-report.md recommends
  formalizing a decision via an ADR

## Do Not Use When

- The task is small implementation without architectural impact
  — use the implementation skills directly.
- The decision has already been made and only implementation is
  required — use the implementation skills directly.
- The task is pure documentation formatting — use
  [`documentation-update`](../documentation-update/SKILL.md).
- The decision is purely operational and not a technical design
  choice — use
  [`observability-review`](../observability-review/SKILL.md) or
  [`runbook-authoring`](../runbook-authoring/SKILL.md) as
  appropriate.
- The decision requires active security or compliance specialist
  review — route to
  [`security-review`](../security-review/SKILL.md) or
  `SECURITY_ANALYST_AGENT` first; this skill records the
  decision but does not stand in for the security review.

## Required Inputs

- **Task description** — the question or change driving the
  decision.
- **Acceptance criteria** — what "good" looks like for the
  decision.
- **Constraints** — at least functional and non-functional; the
  more concrete, the better the decision.
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`. Required when the decision depends on repo
  context (most architectural decisions do).
- **Existing ADRs** — if the repo stores them
  (`docs/adr/`, `docs/decisions/`, `adr/`, ad-hoc paths). Read
  them so the new decision is consistent with prior ones.
- **Existing review findings** — `architecture-review-report.md`
  if this decision is closing an open finding, or any other
  review report that frames the decision.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; the decision must not invent repo
   facts.
2. Read any existing ADRs in the repo to avoid contradicting
   prior decisions.
3. Confirm the constraints are concrete enough to make a
   decision. If the requirements are too ambiguous, stop and
   request clarification; the skill is not a substitute for
   requirements work.
4. Confirm the decision does not require active pen-testing,
   production credentials, or live production behavior data.
5. Confirm the decision is material enough to warrant an ADR. If
   the change is trivial and reversible, an ADR may still be
   useful for traceability, but the workflow may be lighter
   (single option, brief consequences).

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the relevant code, ADRs, and modules are identified.
   Cite concrete files / paths in the decision.

2. **Identify constraints.** Collect and document:

   - Functional requirements
   - Non-functional requirements (latency, throughput, scale)
   - SLO expectations
   - Reliability requirements (RTO / RPO, availability target)
   - Security / compliance constraints
   - Cost constraints
   - Team / tooling constraints
   - Deployment / runtime constraints
   - Reversibility class (cheap, expensive, irreversible)

3. **Generate options.** List at least two viable options when
   meaningful. For each, document:

   - Description (one paragraph)
   - Strengths (with evidence or repo facts)
   - Weaknesses (with evidence or repo facts)
   - Cost (engineering effort, runtime cost, operational
     complexity)
   - Reversibility (cheap / expensive / irreversible)
   - Extension seams (what can be added later without
     re-deciding)

4. **Document rejected options explicitly.** If a familiar
   pattern (microservices, event sourcing, CQRS, service mesh,
   sharding, cache layer, message queue) is rejected, document
   the rejection reason. **Do not silently omit common
   alternatives** — the absence of reasoning is itself a
   review-time finding.

5. **Pick the simplest design that satisfies the constraints.**
   This is the default. Speculative future-proofing without a
   named requirement is rejected. If a complex design is
   selected, the decision must explain why a simpler design
   failed.

6. **State the decision explicitly.** Write a one-sentence
   decision statement ("We will use X for Y because Z"). The
   decision is the load-bearing part of the ADR.

7. **Document consequences and tradeoffs.** Honest listing of
   what becomes easier, what becomes harder, what we are
   locking in, and what we are giving up.

8. **State validation approach.** How the decision will be
   validated when implemented: which test, which load test,
   which metric, which SLO. A decision without a validation plan
   is not reviewable.

9. **State implementation impact.** Which modules / files will
   be touched, which agent / skill should implement
   (`backend-implementation`, `integration-implementation`,
   etc.), and which review gates are required
   (`security-review`, `database-migration-safety`,
   `dependency-change-review`).

10. **Produce the ADR.** Use
    [`templates/adr.md`](templates/adr.md). Save to
    `/data/.openclaw/workspace/tasks/<TASK_ID>/decisions/<UTC-ts>-adr.md`.
    If the repo stores ADRs in-tree
    (e.g. `docs/adr/NNNN-title.md`), the ADR can be mirrored
    there only when the task explicitly approves in-tree
    storage; otherwise the in-task ADR is the canonical record.

11. **Produce the options analysis.** Use
    [`templates/architecture-options-analysis.md`](templates/architecture-options-analysis.md).
    Save to
    `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-options-analysis.md`.
    The options analysis is the longer-form reasoning; the ADR
    is the summary.

12. **Hand off.** Produce a
    [`handoff-packet`](../handoff-packet/SKILL.md) to the next
    skill (`implementation-orchestrator` for mixed work, or
    directly to a narrower implementation skill when scope is
    obvious). Include a link to the ADR and the options
    analysis.

## Allowed Actions

- Read repo files, ADRs, and existing review reports.
- Run `repo-discovery` scripts (read-only).
- Write the ADR, options analysis, and handoff packet.
- Update `task.md` / `state.json` to reflect the decision.

## Forbidden Actions

- **Do not implement code.** The decision is a planning
  artifact, not an implementation.
- **Do not alter architecture silently.** The decision is
  recorded; acting on it requires the orchestrator or the
  appropriate implementation skill.
- **Do not introduce new infrastructure dependencies** (new
  cloud service, new broker, new datastore, new queue) without
  explicit approval and a
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  gate.
- **Do not present speculation as fact.** If a number
  (latency, throughput, cost) is estimated, label it
  `estimate` and document the source / assumption. If a
  tradeoff is opinion, label it `opinion` and explain.
- **Do not omit material tradeoffs.** Every decision has
  tradeoffs; recording only the upsides is not a decision
  record.
- **Do not recommend complex architecture** (microservices,
  event sourcing, CQRS, service mesh, queues, caches,
  sharding) **without evidence** that the simpler design fails
  a stated requirement.
- **Do not bypass review gates.** Security, migration,
  dependency, and architecture-novel work still go through
  their respective review skills.
- **Do not write a single-option ADR as if it were a
  comparison.** Either compare at least two options, or mark
  the decision as a `directive` and explain why no comparison
  was meaningful.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Requirements are too ambiguous to make a decision.
- The decision would introduce new runtime infrastructure
  without an approved gate.
- The decision has security / compliance impact requiring
  specialist review and the review has not run.
- The decision is irreversible or high-cost and no explicit
  approval exists.
- Constraints contradict each other in a way that cannot be
  resolved without a product / architecture owner.

## Outputs

- **`/data/.openclaw/workspace/tasks/<TASK_ID>/decisions/<UTC-ts>-adr.md`**
  — see [`templates/adr.md`](templates/adr.md).
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/architecture-options-analysis.md`**
  — see
  [`templates/architecture-options-analysis.md`](templates/architecture-options-analysis.md).
- **Handoff packet** to `implementation-orchestrator` or the
  narrower implementation skill that will act on the decision.

## Handoff Contract

Fields the receiving skill may rely on:

- `decision_path` — absolute path to the ADR
- `options_analysis_path` — absolute path to the options
  analysis
- `decision_summary` — one-sentence decision statement
- `selected_option` — name of the chosen option from the
  analysis
- `rejected_options` — list of `{name, rejection_reason}` for
  the alternatives
- `reversibility` — `cheap | expensive | irreversible`
- `validation_plan` — how the decision is validated when
  implemented
- `implementation_impact` — list of `path:reason` for files /
  modules the decision implies changes in
- `review_gates_required` — list of review skills that must run
  before / during implementation
- `outstanding_risks` — list of risks the decision accepts, with
  mitigations

Fields the receiving skill must not rely on:

- "approved" — the decision artifact is a record, not an
  approval. Approval is asserted by a `decisions/<id>.md` entry
  naming an approver.
- "no security implications" — security is asserted only by
  [`security-review`](../security-review/SKILL.md).
- "scales" — claims of scale require a load test, SLO, or named
  capacity plan; the decision artifact is not evidence of
  scale.

## Validation

The decision is "validated" when:

1. The ADR has all required sections filled in (Title, Status,
   Context, Decision, Options considered, Consequences,
   Tradeoffs, Reversibility, Validation plan, Related files /
   systems, Follow-up actions).
2. The options analysis covers at least two viable options
   (or a single option with explicit "no comparison meaningful"
   justification).
3. Every selected option is paired with explicit rejection
   reasons for the alternatives.
4. The validation plan names concrete validation steps
   (which test, which load test, which metric, which SLO).
5. The handoff packet has all 14 required fields.
6. The decision does not contradict any existing in-repo ADR
   in the same area.

The skill itself runs no shell commands. The validation plan
documents how the **implemented** decision is validated; the
decision artifact's structure is validated by this checklist
plus the receiving skill.

## Completion Criteria

- Constraints are documented concretely.
- At least two viable options are analyzed (or single option
  justified).
- Selected option is named, with rejection reasons for the
  alternatives.
- ADR is written to `decisions/<UTC-ts>-adr.md`.
- Options analysis is written to
  `reports/architecture-options-analysis.md`.
- Validation plan and implementation impact are documented.
- A handoff packet is produced and the next skill accepts it.
- The task's `state.json` reflects the decision state.

## Cross-references

- Read-only audit: [`architecture-review`](../architecture-review/SKILL.md)
- Implementation entry point:
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
- Narrower implementation skills:
  [`backend-implementation`](../backend-implementation/SKILL.md),
  [`frontend-implementation`](../frontend-implementation/SKILL.md),
  [`integration-implementation`](../integration-implementation/SKILL.md)
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
- Reference: [`references/decision-quality-checklist.md`](references/decision-quality-checklist.md)
- Templates: [`templates/adr.md`](templates/adr.md),
  [`templates/architecture-options-analysis.md`](templates/architecture-options-analysis.md)

## Maturity

`usable` — initial spec, run end-to-end on past decisions; promotion to
`validated` requires a real exercise artifact and a passing linter
(see Helper scripts below).

## Helper scripts

- `scripts/lint-adr.py` — 8-rule linter for ADR files. Three
  invocation modes: single file, directory (lints all `*-adr.md`
  under it), `--self-test`. Exit codes: 0 (pass), 1 (failure), 64
  (bad usage), 66 (file not found). The linter checks the title
  format (`# ADR-NNNN: <title>`), the 5 required frontmatter
  fields, the status is in the allowed set, the 4 required
  sections are populated, the Options table has at least 2 rows,
  and no template placeholders remain.
