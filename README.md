# johrenberger/test-repo

A curated registry of **agent specifications** for the Clawdexter multi-agent
system. Each agent is a markdown contract — identity, purpose, core
capabilities, and collaboration protocol — that downstream tooling can parse
and dispatch to.

This repo is **spec-only**. It contains no code, no skills, and no runtime
artifacts. The Clawdexter runtime lives elsewhere; this repo defines the
contracts.

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
└── skills/                   # skills (currently empty — see skills/README.md)
    └── README.md
```

See [`agents/README.md`](agents/README.md) for the full agent index, grouped
by domain (Engineering, Business Operations, Data & Research).

## Conventions

- **Agents** live as `agents/<ROLE>_AGENT.md` — one role, one file.
- **Skills** would live as `skills/<skill-name>/SKILL.md` (see `skills/README.md`).
- Specs should be markdown that a human can read end-to-end in under five
  minutes. Prefer clear prose over schema-heavy YAML.

## Status

- ✅ 20 agent specs, all using the unified `*_AGENT.md` naming
- 🟡 No skills yet — `skills/` exists as a placeholder directory
- 🟡 No CI / validation pipeline (open question: should specs be linted?)
