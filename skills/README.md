# Skills

Reusable capabilities that any agent can invoke. Distinct from the
agent specs in `../agents/` — a skill is a tool, not a persona.
Skills are invoked by agents to do specific work, never to be a
role.

## When you add a skill

A skill lives in its own folder and is anchored by a `SKILL.md`:

```
skills/
└── <skill-name>/
    ├── SKILL.md           # required: see required sections below
    ├── _meta.json         # optional: metadata
    ├── scripts/           # optional: safe, read-only helper scripts
    ├── references/        # optional: longer checklists, profiles, glossaries
    └── templates/         # optional: report / packet / log templates
```

The `SKILL.md` is what the agent reads first. Keep it short — the
agent loads it on demand, then drills into supporting files only
when it needs them.

**Naming:** lowercase, hyphen-separated, no version suffix in the
folder name (`repo-discovery`, not `RepoDiscovery_v2`).

## Required sections in every `SKILL.md`

Every skill spec must include these sections, in any order, with the
specified headings:

1. **Purpose** — what the skill is for, in one paragraph
2. **Trigger** — when the skill should be invoked
3. **Do Not Use When** — explicit negative scope
4. **Required Inputs** — what the caller must provide
5. **Preflight** — checks before running
6. **Workflow** — step-by-step procedure
7. **Allowed Actions** — what the skill may do
8. **Forbidden Actions** — what the skill must not do (secrets,
   installers, network, file mutations, etc.)
9. **Stop Conditions** — when to halt the workflow
10. **Outputs** — files / side effects produced
11. **Handoff Contract** — fields callers may rely on; fields they
    must not rely on
12. **Validation** — how the skill proves it worked
13. **Completion Criteria** — what "done" looks like

If a section genuinely does not apply, write `n/a` and a one-line
reason.

## Skill maturity levels

Every skill declares its maturity in `SKILL.md` (or in `_meta.json`):

| Level | Meaning |
| --- | --- |
| `draft` | Initial spec, not yet run end-to-end |
| `usable` | Spec is complete; skill has been run on at least one real task |
| `validated` | Skill has been reviewed by a second agent or run on multiple repos; failure modes are known |
| `deprecated` | Skill is retained for reference but new work should not use it; replacement is named in the spec |

A new skill is `draft` by default. Promotion to `usable` requires at
least one successful end-to-end run with a captured handoff packet.

## Cross-skill composition rules

The skills build on the foundation skills. By convention,
**every** skill (not just action-oriented ones) must:

- **Use `repo-discovery` before acting** unless a current
  discovery artifact already exists in the task workspace.
  Inventing repo facts is forbidden.
- **Use `handoff-packet` for any work passed to another
  agent.** Vague handoffs are rejected. The packet must
  include the 14 required fields.
- **Use `validation-runner` (or explain why validation
  could not be run)** for any change that should be
  validated. Hand-waving
  "should be fine" is forbidden.

A skill that depends on another skill's output must read the
output from the canonical path, not re-derive it.

## Scripts must be non-destructive by default

Any `scripts/*.sh` shipped with a skill must:

- be read-only with respect to the repo being acted on;
- refuse package installation (no `npm install`, `pip install`,
  `go mod tidy`, `cargo add`, `dotnet add`, etc.);
- never reach the network;
- never read environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*`;
- never delete files;
- never deploy or run destructive commands.

A skill that genuinely needs a mutating action must name it
explicitly in its `Forbidden Actions` section as a permitted
exception, and justify it in the same section.

## Foundation Skills

Required companions for any engineering work. Every agent that
touches code or task state should be familiar with these.

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`repo-discovery`](repo-discovery/SKILL.md) | Detect repo stack, layout, and test commands from filesystem evidence | `usable` |
| [`task-state-management`](task-state-management/SKILL.md) | Per-task workspace layout, allowed states, state-transition rules | `usable` |
| [`handoff-packet`](handoff-packet/SKILL.md) | Standardize agent-to-agent task transfers with a 14-field packet (plus a task-spec-packet variant for BDD-style spec handoffs) | `validated` |
| [`validation-runner`](validation-runner/SKILL.md) | Run safe, evidence-discovered local validation commands and report | `usable` |

## Software Delivery Skills

The next layer: skills that move a task from "we know the repo" to
"the change is implemented, tested, and ready for review." They all
build on the Foundation Skills.

Implementation work is **routed**, not broad. A single
implementation skill owns exactly one layer (backend, frontend,
integration). Mixed or unclear tasks go through the orchestrator
first; the orchestrator decides the right narrower skill.

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`implementation-orchestrator`](implementation-orchestrator/SKILL.md) | Route implementation work to the correct narrower skill; never edits code | `usable` |
| [`backend-implementation`](backend-implementation/SKILL.md) | Implement **backend / server-side** behavior (API, service, persistence, auth) | `draft` |
| [`frontend-implementation`](frontend-implementation/SKILL.md) | Implement **frontend / client-side** behavior (UI, state, forms, routing) | `draft` |
| [`integration-implementation`](integration-implementation/SKILL.md) | Implement **cross-system integration** behavior (API clients, webhooks, queues, file batch) | `draft` |
| [`test-gap-analysis`](test-gap-analysis/SKILL.md) | Risk-weighted test gap analysis without writing tests | `usable` |
| [`test-generation`](test-generation/SKILL.md) | Generate or update tests in the existing framework and style | `validated` |

### When to use the orchestrator

Use [`implementation-orchestrator`](implementation-orchestrator/SKILL.md)
when a task asks to implement software behavior **and** any of:

- The impacted layer (backend / frontend / integration) is unclear.
- The task description mentions multiple layers.
- The change touches modules owned by different teams.

Use the narrower implementation skill directly when ownership is
obvious:

- **Clearly backend-only** → `backend-implementation`
- **Clearly frontend-only** → `frontend-implementation`
- **Clearly integration-only** → `integration-implementation`

The narrower skills stop and route back to the orchestrator when
the task crosses into another layer or needs a review gate
(migration, dependency change, security-sensitive work).

## Review and Risk Skills

The next layer: skills that evaluate a change for correctness,
security, and risk. They are read-only by default and produce
ranked findings reports.

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`code-change-review`](code-change-review/SKILL.md) | Read-only review of local code changes with severity-ranked findings | `draft` |
| [`security-review`](security-review/SKILL.md) | Code / config security review with OWASP, secrets, and authz checklists | `draft` |
| [`dependency-change-review`](dependency-change-review/SKILL.md) | Review of dependency, build, and lockfile changes | `draft` |
| [`database-migration-safety`](database-migration-safety/SKILL.md) | Schema and migration safety review with expand-and-contract guidance | `draft` |
| [`architecture-review`](architecture-review/SKILL.md) | Read-only audit of proposed / implemented architecture; may recommend an ADR | `draft` |
| [`observability-review`](observability-review/SKILL.md) | Audit logging, metrics, tracing, health, alerts, runbooks; recommends changes via handoff | `draft` |

## Architecture and Documentation Skills

Skills that make decisions, formalize them as ADRs, and keep
documentation aligned with the actual repo. They are
**evidence-driven** — every artifact cites the source.

- [`architecture-decision`](architecture-decision/SKILL.md) creates
  evidence-based ADRs and options analyses. Material decisions get
  an ADR; rejected common patterns (microservices, event
  sourcing, CQRS, service mesh, queues, caches, sharding) must
  be explicitly explained.
- [`architecture-review`](architecture-review/SKILL.md) audits a
  proposed or implemented architecture across 13 dimensions
  (alignment, boundaries, coupling, data ownership, contract
  stability, failure modes, scalability, security,
  observability, deployment, reversibility, migration,
  over-engineering) and may recommend that an ADR be created
  (via `architecture-decision`).
- [`documentation-update`](documentation-update/SKILL.md) updates
  source-controlled docs based on code, API, architecture, and
  config changes. It always produces a documentation impact
  report, even when no docs are changed.

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`architecture-decision`](architecture-decision/SKILL.md) | Create evidence-based ADRs and options analyses for material technical decisions | `draft` |
| [`architecture-review`](architecture-review/SKILL.md) | Read-only audit of proposed / implemented architecture with ranked findings | `draft` |
| [`documentation-update`](documentation-update/SKILL.md) | Update source-controlled docs based on code, API, architecture, and config changes | `draft` |

## Release and Operations Skills

Skills that coordinate release readiness, incident response,
and operational artifacts. **All of these are advisory /
review / coordination by default.** They do not deploy, do
not rollback, do not restart production services, do not
rotate secrets, do not change firewall rules, do not modify
infrastructure. Those actions are operator-only.

- [`release-readiness`](release-readiness/SKILL.md) aggregates
  evidence from validation, code review, security review,
  dependency review, migration safety, architecture review, and
  documentation update to produce a go / no-go readiness
  report. It is the **last stop before deployment**, not a
  replacement for the individual review skills. The status is
  one of `Ready | Ready with known risks | Not ready | Blocked
  pending approval / evidence`.
- [`incident-triage`](incident-triage/SKILL.md) structures
  incident investigation and response without making unsafe
  production changes. It produces a triage report, a timeline,
  action items, and a handoff to the appropriate role
  (Monitoring, DevOps, Security, Software Engineer, Project
  Coordinator). It does not execute mitigations.
- [`observability-review`](observability-review/SKILL.md) audits
  whether a service / change has adequate logging, metrics,
  tracing, health checks, and alert / runbook support. It is
  read-only; alert / dashboard / SLO changes are routed via
  handoff to `MONITORING_AGENT`.
- [`runbook-authoring`](runbook-authoring/SKILL.md) creates or
  updates operational runbooks and troubleshooting guides from
  validated system evidence. Destructive remediation steps
  require an explicit approval gate and a rollback step.

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`release-readiness`](release-readiness/SKILL.md) | Aggregate evidence into a go / no-go readiness report; never deploys | `draft` |
| [`incident-triage`](incident-triage/SKILL.md) | Structure incident investigation; never executes production changes | `draft` |
| [`observability-review`](observability-review/SKILL.md) | Audit logging, metrics, tracing, alerts, runbooks; never modifies monitoring systems | `draft` |
| [`runbook-authoring`](runbook-authoring/SKILL.md) | Create / update operational runbooks from validated evidence; gates destructive steps | `draft` |

## Future Skills

Skills that are anticipated but not yet defined. **Do not create
files under this section's heading** — it is a placeholder for
planning. When a future skill is added, it is moved to one of the
groups above.

Candidates:

- `incident-postmortem` — convert an incident timeline into a
  blameless postmortem
- `feature-flag-rollout` — phased rollout / kill-switch workflow
- `release-notes-generation` — produce release notes from merged
  PRs / commit history
- `slo-authoring` — author SLOs / SLIs from scratch (vs.
  reviewing them in `observability-review`)
- `chaos-experiment-authoring` — design chaos / failure-injection
  experiments from observed failure modes
- `cost-review` — review cloud / runtime cost impact of changes
- `compliance-evidence` — collect evidence for SOC2 / ISO27001 /
  HIPAA / PCI from existing artifacts

## Shared templates (used by multiple skills)

Generic templates that multiple review / risk / decision /
release / operations skills consume. They live at the repo
root in `../templates/`.

- [`../templates/findings-severity.md`](../templates/findings-severity.md) —
  severity scale and required finding fields
- [`../templates/approval-gate.md`](../templates/approval-gate.md) —
  approval record for blocker-level findings
- [`../templates/risk-register.md`](../templates/risk-register.md) —
  consolidated, cross-skill view of risk for a task
- [`../templates/adr-index.md`](../templates/adr-index.md) —
  index of ADRs (active, superseded, rejected, open proposals)
- [`../templates/go-no-go-summary.md`](../templates/go-no-go-summary.md) —
  one-page go / no-go summary for a release
- [`../templates/incident-summary.md`](../templates/incident-summary.md) —
  one-page incident summary for stakeholders
- [`../templates/operational-risk-register.md`](../templates/operational-risk-register.md) —
  consolidated cross-skill view of operational risk
  (observability, runbook, release, incident)

## Difference from agents

| | Agent | Skill |
| --- | --- | --- |
| **Lives at** | `agents/<ROLE>_AGENT.md` | `skills/<skill-name>/SKILL.md` |
| **Defines** | a role with purpose and capabilities | a reusable capability any agent can invoke |
| **Has identity?** | yes (name, role, mode) | no — it's a tool, not a persona |
| **Loaded** | once, at session start | on demand, when an agent needs it |

If something fits both — it's probably an agent (a role that
reasons about when to use tools) and the tools themselves are the
skills. Skills must not be designed to be personas.
