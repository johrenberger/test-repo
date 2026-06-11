# Skills

Reusable capabilities that any agent can invoke. Distinct from the agent
specs in `../agents/` — a skill is a tool, not a persona.

## When you add a skill

A skill lives in its own folder and is anchored by a `SKILL.md`:

```
skills/
└── <skill-name>/
    ├── SKILL.md           # required: see required sections below
    ├── _meta.json         # optional: metadata
    ├── scripts/           # optional: safe, read-only helper scripts
    └── templates/         # optional: longer markdown templates
```

The `SKILL.md` is what the agent reads first. Keep it short — the agent
loads it on demand, then drills into supporting files only when it needs
them.

**Naming:** lowercase, hyphen-separated, no version suffix in the folder
name (`repo-discovery`, not `RepoDiscovery_v2`).

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
11. **Handoff Contract** — fields callers may rely on; fields they must
    not rely on
12. **Validation** — how the skill proves it worked
13. **Completion Criteria** — what "done" looks like

If a section genuinely does not apply, write `n/a` and a one-line reason.

## Skill maturity levels

Every skill declares its maturity in `SKILL.md` (or in `_meta.json`):

| Level | Meaning |
| --- | --- |
| `draft` | Initial spec, not yet run end-to-end |
| `usable` | Spec is complete; skill has been run on at least one real task |
| `validated` | Skill has been reviewed by a second agent or run on multiple repos; failure modes are known |
| `deprecated` | Skill is retained for reference but new work should not use it; replacement is named in the spec |

A new skill is `draft` by default. Promotion to `usable` requires at least
one successful end-to-end run with a captured handoff packet.

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

A skill that genuinely needs a mutating action must name it explicitly in
its `Forbidden Actions` section as a permitted exception, and justify it
in the same section.

## Foundation skills (current)

| Skill | Purpose | Maturity |
| --- | --- | --- |
| [`repo-discovery`](repo-discovery/SKILL.md) | Detect repo stack, layout, and test commands from filesystem evidence | `draft` |
| [`task-state-management`](task-state-management/SKILL.md) | Per-task workspace layout, allowed states, state-transition rules | `draft` |
| [`handoff-packet`](handoff-packet/SKILL.md) | Standardize agent-to-agent task transfers with a 14-field packet | `draft` |
| [`validation-runner`](validation-runner/SKILL.md) | Run safe, evidence-discovered local validation commands and report | `draft` |

## Difference from agents

| | Agent | Skill |
| --- | --- | --- |
| **Lives at** | `agents/<ROLE>_AGENT.md` | `skills/<skill-name>/SKILL.md` |
| **Defines** | a role with purpose and capabilities | a reusable capability any agent can invoke |
| **Has identity?** | yes (name, role, mode) | no — it's a tool, not a persona |
| **Loaded** | once, at session start | on demand, when an agent needs it |

If something fits both — it's probably an agent (a role that reasons about
when to use tools) and the tools themselves are the skills.
