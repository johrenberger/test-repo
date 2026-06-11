# johrenberger/test-repo

The OpenClaw / MiniMax **agent and skill registry**. This repo defines the
contracts (markdown specs, helper scripts, and templates) that downstream
runtimes and tooling parse and dispatch to.

## What this repo contains

- **Agent specs** — markdown contracts describing a role, its purpose, its
  capabilities, and its collaboration protocol.
- **Skill specs** — markdown contracts describing a reusable capability any
  agent can invoke, plus safe helper scripts and templates.
- **Helper scripts and templates** under each skill — small, non-destructive
  bash scripts and markdown templates an agent can use directly.

## What this repo does NOT contain

- The OpenClaw runtime itself (lives elsewhere).
- Production application code.
- External runtime dependencies (no `package.json`, `pyproject.toml`,
  `Cargo.toml`, etc. that pull in a runtime install).
- Secrets, credentials, or tokens of any kind.

The presence of helper bash scripts in `skills/*/scripts/` is for agents
to invoke on demand. These scripts are read-only by design and do not
constitute a deployable application.

## Layout

```
.
├── README.md                 # this file
├── agents/                   # agent specifications (20 files)
│   ├── README.md             # grouped index with one-line summaries
│   ├── ARCHITECT_AGENT.md
│   ├── CLOUD_SECURITY_AGENT.md
│   ├── CODE_REVIEW_AGENT.md
│   ├── COMMUNICATIONS_MANAGER_AGENT.md
│   ├── CREATIVE_DIRECTOR_AGENT.md
│   ├── DATA_ANALYST_AGENT.md
│   ├── DEVOPS_AGENT.md
│   ├── DOCUMENTATION_AGENT.md
│   ├── EXECUTIVE_ASSISTANT_AGENT.md
│   ├── FINANCIAL_ANALYST_AGENT.md
│   ├── KNOWLEDGE_MANAGER_AGENT.md
│   ├── LEGAL_COMPLIANCE_AGENT.md
│   ├── MONITORING_AGENT.md
│   ├── PEN_TESTING_AGENT.md
│   ├── PRODUCT_MANAGER_AGENT.md
│   ├── PROJECT_COORDINATOR_AGENT.md
│   ├── RESEARCH_ANALYST_AGENT.md
│   ├── SECURITY_ANALYST_AGENT.md
│   ├── SOFTWARE_ENGINEER_AGENT.md
│   └── TEST_AUTOMATION_AGENT.md
├── skills/                   # skill specifications + helper artifacts
│   ├── README.md             # skill index, required sections, maturity
│   ├── repo-discovery/       # detect repo stack, layout, commands
│   ├── task-state-management/# per-task workspace + state transitions
│   ├── handoff-packet/       # agent-to-agent transfer packet
│   ├── validation-runner/    # safe local validation runner
│   ├── test-gap-analysis/    # risk-weighted test gap report
│   ├── test-generation/      # generate tests in existing framework
│   ├── code-change-review/   # read-only review of code changes
│   ├── security-review/      # code/config security review
│   ├── implementation-orchestrator/  # route implementation work to the correct narrower skill
│   ├── backend-implementation/  # implement backend behavior safely
│   ├── frontend-implementation/  # implement frontend / client behavior safely
│   ├── integration-implementation/  # implement cross-system integration behavior safely
│   ├── dependency-change-review/  # review dependency/build/lockfile changes
│   ├── database-migration-safety/  # schema and migration safety review
│   ├── architecture-decision/   # evidence-based ADRs and options analyses
│   ├── architecture-review/     # read-only audit of proposed/implemented architecture
│   ├── documentation-update/    # update source-controlled docs based on evidence
│   ├── release-readiness/       # go/no-go readiness report; never deploys
│   ├── incident-triage/         # structure incident investigation; never executes
│   ├── observability-review/    # audit logging/metrics/tracing/alerts/runbooks
│   └── runbook-authoring/       # create/update runbooks from validated evidence
└── templates/                # shared templates for review / risk skills
    ├── findings-severity.md  # severity scale and required finding fields
    ├── approval-gate.md      # approval record for blocker-level findings
    └── risk-register.md      # consolidated cross-skill view of risk
```

See [`agents/README.md`](agents/README.md) for the full agent index, grouped
by domain (Engineering, Business Operations, Data & Research).
See [`skills/README.md`](skills/README.md) for the skill index, grouped
into Foundation, Software Delivery, and Review and Risk skills, with
required `SKILL.md` sections, maturity levels, and the non-destructive
script rule.

## Conventions

- **Agents** live as `agents/<ROLE>_AGENT.md` — one role, one file.
- **Skills** live as `skills/<skill-name>/SKILL.md`, optionally with
  `scripts/` and `templates/` siblings.
- Specs should be markdown that a human can read end-to-end in under five
  minutes. Prefer clear prose over schema-heavy YAML.
- Helper scripts must be non-destructive by default; any mutation must be
  declared in the skill's `Forbidden Actions` exception.

## Implementation work is split into narrower skills

Implementation is **routed**, not broad:

- [`implementation-orchestrator`](skills/implementation-orchestrator/SKILL.md)
  — classifies the task and dispatches to one narrower skill; never
  edits code.
- [`backend-implementation`](skills/backend-implementation/SKILL.md) —
  API, service, persistence, auth (backend / server-side only).
- [`frontend-implementation`](skills/frontend-implementation/SKILL.md) —
  UI, client state, forms, routing (frontend / client-side only).
- [`integration-implementation`](skills/integration-implementation/SKILL.md) —
  external API clients, webhooks, queues, file batch
  (cross-system only).

Use the **orchestrator** when a task mixes layers or ownership is
unclear. Use the narrower skill directly when ownership is obvious.
Each narrower skill stops and routes back to the orchestrator when
the task crosses into another layer or needs a review gate
(migration, dependency change, security-sensitive work).

This split improves OpenClaw / MiniMax reliability by:

- **Reducing skill scope** — each implementation skill is small
  enough to read end-to-end, and the "what does this skill do?"
  question has a short, honest answer.
- **Preventing broad edits** — a single implementation skill never
  touches more than one layer in a session.
- **Routing high-risk work to a review skill first** — migrations,
  dependency changes, and security-sensitive work cannot reach an
  implementation skill without a review gate.
- **Making ownership visible** — the routing report names the owning
  module per layer, so a handoff to another agent has concrete
  targets.

## Status

- ✅ 20 agent specs, all using the unified `*_AGENT.md` naming
- ✅ Foundation skills exist: `repo-discovery`, `task-state-management`,
  `handoff-packet`, `validation-runner` (all currently `draft`)
- ✅ Software delivery skills exist: `test-gap-analysis`,
  `test-generation`, `implementation-orchestrator`,
  `backend-implementation`, `frontend-implementation`,
  `integration-implementation` (all currently `draft`)
- ✅ Review and risk skills exist: `code-change-review`,
  `security-review`, `dependency-change-review`,
  `database-migration-safety`, `architecture-review`,
  `observability-review` (all currently `draft`)
- ✅ Architecture and documentation skills exist: `architecture-decision`,
  `architecture-review`, `documentation-update` (all currently
  `draft`)
- ✅ Release and operations skills exist: `release-readiness`,
  `incident-triage`, `observability-review`, `runbook-authoring` (all
  currently `draft`)
- ✅ Shared templates exist: `findings-severity`, `approval-gate`,
  `risk-register`, `adr-index`, `go-no-go-summary`,
  `incident-summary`, `operational-risk-register`
- 🟡 No CI / validation pipeline yet (open question: should specs be
  linted, scripts gated by `bash -n`, and required `SKILL.md` sections
  checked in CI?)
- 🟡 All skills are `draft` maturity — promotion to `usable` requires at
  least one end-to-end run with a captured handoff packet

## Safety contract for release and operations skills

Release, incident, observability, and runbook skills are
**advisory / review / coordination by default.** They must
not:

- deploy,
- rollback,
- restart production services,
- rotate secrets,
- change firewall rules,
- or modify infrastructure

without explicit operator approval. The skills produce
reports, recommendations, and handoffs; the operator (human
or automated under operator control) makes the production
change.

This contract is restated in each of those skills'
`Forbidden Actions` sections.

## What this repo contains

This repo contains **agent specs, skill specs, templates,
references, and safe helper scripts.** It does not contain
the OpenClaw runtime, production application code, or
external runtime dependencies.

This repo contains **agent specs, skill specs, templates, and safe
helper scripts**. It does not contain the OpenClaw runtime.
