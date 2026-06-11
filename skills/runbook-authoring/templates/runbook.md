# Runbook

Canonical operational runbook template. Used by the
[`runbook-authoring`](../../../../skills/runbook-authoring/SKILL.md)
skill. Save in-repo at
`docs/runbooks/<service>-<scenario>.md` (or per repo
convention) or, when in-repo storage is not appropriate, at
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/<runbook-file>.md`.

## File naming

- `docs/runbooks/<service>-<scenario>.md` — preferred when
  the repo has a `docs/runbooks/` location
- `<service>-<scenario>.md` — placeholder; the actual file
  is named per the runbook's scope
- Filename is lowercase, hyphen-separated

## Template

```markdown
# Runbook: <short title>

- **Runbook ID:** <RB-<service>-<NNN>>
- **Service / process:** <name>
- **Scenario:** <failure mode, recovery task, or operational
  procedure>
- **Severity:** <SEV-1 | SEV-2 | SEV-3 | SEV-4>
- **Owner / team:** <role or person, or `unassigned —
  confirm with on-call`>
- **Last reviewed:** <YYYY-MM-DD>
- **Last verified:** <YYYY-MM-DD, or `never — first draft`>
- **Source evidence:** <list of paths — incident triage
  report, observability review, ADR, prior runbook>

## Purpose

<one paragraph: what this runbook is for.>

## Scope

<one paragraph: what is covered; what is explicitly out of
scope.>

## Symptoms

How the on-call knows to use this runbook:

- <symptom> — signal: <alert name | log pattern | metric
  threshold | user report>
- <symptom> — signal: <...>

## Severity guidance

The runbook's severity matches the triggering incident's
severity. Cross-reference
[`incident-triage`](../../../../skills/incident-triage/SKILL.md)
and the
[`incident-severity-guide`](../../../../skills/incident-triage/references/incident-severity-guide.md).

## Prerequisites / access requirements

- <access / credential / env> — source: <path or `on-call
  vault`>
- Or `none`.

## Safe diagnostic commands

Each command is labeled with its source and verification
status. Read-only or reversible commands are preferred.

### Step 1: <one-line purpose>

```bash
<command>
```

- **Source:** <file:lines | operator evidence |
  `validation-runner` report path>
- **Verified:** <yes — at <UTC-ts> | no — confirm before
  running>
- **Expected output:** <one paragraph or example>
- **Risk:** <none | read-only | reversible | destructive —
  see approval gate>

### Step 2: <one-line purpose>

<repeat the structure>

## Mitigation options

Each option is labeled with the trigger, action, expected
effect, rollback, and risk. The on-call picks the option
that matches the situation; the runbook does not pick for
them.

### Option A: <name>

- **Trigger:** <condition>
- **Action:** <step-by-step>
- **Expected effect:** <observable>
- **Rollback:** <step-by-step>
- **Risk:** <low | medium | high>
- **Approval gate:** <`approvals/<gate-id>.md` or `n/a —
  not destructive`>

### Option B: <name>

<repeat the structure>

## Rollback / escalation steps

- **Rollback:** <step-by-step, or `n/a — no destructive
  change`>
- **Escalation:** <role and contact, or `on-call
  coordinator`>
- **Escalation trigger:** <condition>

## Validation after mitigation

How to confirm the mitigation worked:

- <observable> — measured at: <metric / log / status check>
- <observable> — measured at: <metric / log / status check>

If any of these are not met, re-enter the diagnostic phase
or escalate.

## Known risks

- <risk> — accepted because: <one line>
- Or `none`.

## Owner / team / contact

- **Primary:** <role or person, or `unassigned`>
- **Secondary:** <role or person, or `unassigned`>
- **On-call channel:** <link or `on-call rotation`>
- **Communications:** <channel, or `incident commander`>

## Cross-references

- ADRs: <list of paths> or `none`
- Observability review: <path> or `none`
- Incident triage report (if post-incident): <path> or
  `none`
- Release readiness report: <path> or `none`
- Related runbooks: <list of paths> or `none`

## Change log

- `<UTC-ts>` — <change>
- Or `none yet — first draft`.

## Status

- `draft` | `verified` | `adopted`
- A runbook is `adopted` only after the on-call team or
  owner has reviewed and confirmed it.
```

## Field rules

- **Purpose** is required.
- **Symptoms** is required; the runbook must be findable
  from the on-call's signal.
- **Severity** is required; the runbook is triggered by an
  incident of at least this severity.
- **Prerequisites** is required; missing prerequisites are
  a blocker for adoption.
- **Safe diagnostic commands** is required; every command
  has a source and a verification status.
- **Mitigation options** is required when the runbook
  addresses a failure mode; each option has a trigger,
  action, expected effect, rollback, and risk.
- **Validation after mitigation** is required; the on-call
  must be able to confirm the fix worked.
- **Cross-references** is required; the runbook is part of
  the operational graph, not an island.
- **Status** is one of `draft | verified | adopted`. Free-form
  text is not acceptable.

## Verification workflow

A runbook is `verified` when:

1. Every command has been run in a non-production
   environment (staging, sandbox) or in production with
   read-only intent, and the expected output matches.
2. Every destructive command has an approval gate in
   `approvals/<gate-id>.md`.
3. Every cross-reference resolves to an existing artifact.
4. The on-call or owner has signed off in the change log.

A runbook is `adopted` when:

1. All `verified` conditions are met.
2. The on-call team has been briefed (or has read the
   runbook).
3. The runbook is linked from the relevant dashboards or
   alert definitions.
