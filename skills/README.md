# Skills

This directory is reserved for **skills** — reusable capabilities that an agent
can invoke, distinct from the agent specs in `../agents/`.

## Current status

**No skills are defined in this repository yet.** This directory exists so the
layout is in place when the first skill shows up, and to make the distinction
between *agents* (who does the work) and *skills* (what they can do) explicit.

## When you add a skill

A skill lives in its own folder and is anchored by a `SKILL.md`:

```
skills/
└── <skill-name>/
    ├── SKILL.md           # required: frontmatter + description
    ├── _meta.json         # optional: metadata
    └── ...                # optional: scripts, templates, references
```

The `SKILL.md` is what the agent reads first. Keep it short — the agent loads
it on demand, then drills into supporting files only when it needs them.

Naming: lowercase, hyphen-separated, no version suffix in the folder name
(`pdf-summarizer`, not `PdfSummarizer_v2`).

## Difference from agents

| | Agent | Skill |
| --- | --- | --- |
| **Lives at** | `agents/<ROLE>_AGENT.md` | `skills/<skill-name>/SKILL.md` |
| **Defines** | a role with purpose and capabilities | a reusable capability any agent can invoke |
| **Has identity?** | yes (name, role, mode) | no — it's a tool, not a persona |
| **Loaded** | once, at session start | on demand, when an agent needs it |

If something fits both — it's probably an agent (a role that reasons about
when to use tools) and the tools themselves are the skills.
