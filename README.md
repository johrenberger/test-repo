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
│   ├── backend-implementation/# implement backend behavior safely
│   ├── dependency-change-review/  # review dependency/build/lockfile changes
│   └── database-migration-safety/  # schema and migration safety review
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

## Status

- ✅ 20 agent specs, all using the unified `*_AGENT.md` naming
- ✅ Foundation skills exist: `repo-discovery`, `task-state-management`,
  `handoff-packet`, `validation-runner` (all currently `draft`)
- ✅ Software delivery skills exist: `test-gap-analysis`,
  `test-generation`, `backend-implementation` (all currently `draft`)
- ✅ Review and risk skills exist: `code-change-review`,
  `security-review`, `dependency-change-review`,
  `database-migration-safety` (all currently `draft`)
- ✅ Shared templates exist: `findings-severity`, `approval-gate`,
  `risk-register`
- 🟡 No CI / validation pipeline yet (open question: should specs be
  linted, scripts gated by `bash -n`, and required `SKILL.md` sections
  checked in CI?)
- 🟡 All skills are `draft` maturity — promotion to `usable` requires at
  least one end-to-end run with a captured handoff packet

This repo contains **agent specs, skill specs, templates, and safe
helper scripts**. It does not contain the OpenClaw runtime.
