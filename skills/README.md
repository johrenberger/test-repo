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

The new software-delivery skills build on the foundation skills.
By convention, every action-oriented skill must:

- **Use `repo-discovery` before acting** unless a current discovery
  artifact already exists in the task workspace. Inventing repo
  facts is forbidden.
- **Use `handoff-packet` for any work passed to another agent.**
  Vague handoffs are rejected. The packet must include the 14
  required fields.
- **Use `validation-runner` (or explain why validation could not be
  run) for any change that should be validated.** Hand-waving
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
| [`repo-discovery`](repo-discovery/SKILL.md) | Detect repo stack, layout, and test commands from filesystem evidence | `draft` |
| [`task-state-management`](task-state-management/SKILL.md) | Per-task workspace layout, allowed states, state-transition rules | `draft` |
| [`handoff-packet`](handoff-packet/SKILL.md) | Standardize agent-to-agent task transfers with a 14-field packet | `draft` |
| [`validation-runner`](validation-runner/SKILL.md) | Run safe, evidence-discovered local validation commands and report | `draft` |

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
| [`implementation-orchestrator`](implementation-orchestrator/SKILL.md) | Route implementation work to the correct narrower skill; never edits code | `draft` |
| [`backend-implementation`](backend-implementation/SKILL.md) | Implement **backend / server-side** behavior (API, service, persistence, auth) | `draft` |
| [`frontend-implementation`](frontend-implementation/SKILL.md) | Implement **frontend / client-side** behavior (UI, state, forms, routing) | `draft` |
| [`integration-implementation`](integration-implementation/SKILL.md) | Implement **cross-system integration** behavior (API clients, webhooks, queues, file batch) | `draft` |
| [`test-gap-analysis`](test-gap-analysis/SKILL.md) | Risk-weighted test gap analysis without writing tests | `draft` |
| [`test-generation`](test-generation/SKILL.md) | Generate or update tests in the existing framework and style | `draft` |

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
- `runbook-authoring` — capture operational procedures from
  observed actions
- `architecture-decision-record` — ADR authoring and review

## Shared templates (used by multiple skills)

Generic templates that multiple review / risk skills consume. They
live at the repo root in `../templates/`.

- [`../templates/findings-severity.md`](../templates/findings-severity.md) —
  severity scale and required finding fields
- [`../templates/approval-gate.md`](../templates/approval-gate.md) —
  approval record for blocker-level findings
- [`../templates/risk-register.md`](../templates/risk-register.md) —
  consolidated, cross-skill view of risk for a task

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
