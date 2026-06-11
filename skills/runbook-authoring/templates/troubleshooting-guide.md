# Troubleshooting guide

Diagnostic-only companion to a
[`runbook`](runbook.md). The troubleshooting guide walks an
on-call through diagnosing a problem without applying a
fix; the runbook picks up after the diagnosis is complete
and applies the mitigation.

Save in-repo at
`docs/runbooks/<service>-troubleshooting.md` (or per repo
convention) or, when in-repo storage is not appropriate, at
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/<file>.md`.

## When to use a troubleshooting guide vs a runbook

- **Troubleshooting guide** — diagnostic; reads logs /
  metrics / traces, narrows the cause, hands off to the
  matching runbook.
- **Runbook** — applies the mitigation; gated destructive
  steps; rollback; validation.

Some repos combine them; the separation is the
recommendation because the on-call's first job is to
**understand** what is wrong, not to **fix** it.

## Template

```markdown
# Troubleshooting: <short title>

- **Guide ID:** <TG-<service>-<NNN>>
- **Service / process:** <name>
- **Failure mode:** <one-line>
- **Owner / team:** <role or person, or `unassigned`>
- **Source evidence:** <list of paths>

## Purpose

<one paragraph: what this guide helps the on-call diagnose.>

## Symptoms

- <symptom> — signal: <alert name | log pattern | metric
  threshold | user report>

## Decision tree

A flowchart-like list of "if you see X, go to Y." Each
branch is a hypothesis with a low-cost test.

1. **Is <observable A> true?**
   - Yes → go to step 2.
   - No → go to step 3.

2. **<one-line diagnostic>**
   - <expected output> → confirm and go to
     `[runbook: <runbook-id>]`.
   - <unexpected output> → escalate or go to step 4.

3. **<one-line diagnostic>**
   - <expected output> → confirm and go to
     `[runbook: <runbook-id>]`.
   - <unexpected output> → escalate or go to step 4.

4. **<one-line diagnostic>**
   - <expected output> → confirm and go to
     `[runbook: <runbook-id>]`.
   - <unexpected output> → escalate.

## Diagnostic commands

Read-only commands. Each labeled with source and
verification status.

### Step 1: <one-line purpose>

```bash
<command>
```

- **Source:** <file:lines | operator evidence |
  `validation-runner` report path>
- **Verified:** <yes | no>
- **Expected output:** <one paragraph or example>

### Step 2: <one-line purpose>

<repeat the structure>

## Hypotheses to test

| ID | Hypothesis | Test | Cost |
| --- | --- | --- | --- |
| H1 | <hypothesis> | <step> | <low | medium | high> |
| H2 | <hypothesis> | <step> | <low | medium | high> |

Each hypothesis is tested in order of cost; the
lowest-cost test runs first.

## Mitigation runbook pointers

When the diagnosis identifies the cause, hand off to:

- `[runbook: <runbook-id> — <title>]` — for `<cause>`
- `[runbook: <runbook-id> — <title>]` — for `<cause>`
- Or `none — escalate`.

## Escalation

- **Escalation target:** <role>
- **Escalation trigger:** <condition>
- **Channel:** <link or `on-call coordinator`>

## Cross-references

- ADRs: <list> or `none`
- Observability review: <path> or `none`
- Related runbooks: <list> or `none`

## Status

- `draft` | `verified` | `adopted`
```

## Field rules

- **Decision tree** is required; the troubleshooting guide
  is a decision aid, not a free-form list of commands.
- **Diagnostic commands** is required; every command has a
  source and verification status.
- **Hypotheses to test** is required when the failure mode
  has more than one plausible cause; the table orders
  hypotheses by cost.
- **Mitigation runbook pointers** is required; the
  troubleshooting guide hands off to a runbook (or to
  escalation), not directly to a fix.
- **Status** is one of `draft | verified | adopted`.
