---
name: database-migration-safety
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- devops-agent
purpose: Read-only review of database schema, migration, and data-shape changes. Produces
  a ranked findings report focused on safety, with explicit escalation for destructive
  or irreversible changes.
---

# database-migration-safety

Read-only review of database schema, migration, and data-shape
changes. Produces a ranked findings report focused on safety, with
explicit escalation for destructive or irreversible changes.

## Purpose

Catch destructive, locking, or irreversible database changes before
they reach a production-like environment. The skill produces a
written safety case the change can be measured against, and is the
machine-readable first pass; a human reviewer is still required for
final sign-off.

## Trigger

- A change adds, modifies, or removes a migration (Flyway / Liquibase
  / Alembic / Django / Prisma / TypeORM / Sequelize / Rails / EF Core
  / raw SQL).
- A change modifies an ORM model, a database index, a constraint, or
  a default.
- A backfill is proposed.
- A handoff packet's "Required next action" calls for migration
  review.

## Do Not Use When

- The change is pure read-only code with no schema impact.
- The task is to execute the migration — this skill is read-only and
  never runs migrations.
- The proposed change is "drop a table to clean up" with no
  production traffic consideration — that's a destructive migration
  and the skill will still apply, but the report will be a blocker.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `SCOPE` (optional) — module, ORM model, or migration file
- `CHANGED_FILES` (optional) — explicit list of changed paths; if
  not provided, the skill derives the set from `git diff`

## Preflight

- Resolve the changed-file set. If the set is empty, abort with
  "no migration / schema changes to review."
- Read the `repo-discovery` report to confirm the migration tooling
  and database dialect.
- Read any `dependency-change-report.md` and `code-change-report.md`
  for the same task; they may surface constraints.
- For each file, parse the migration / model diff and identify
  added, removed, and modified schema elements.

## Workflow

1. **Inventory the change.** For each file in the set, list:
   - new tables, columns, indexes, constraints
   - removed tables, columns, indexes, constraints
   - type changes
   - default / nullability changes
   - backfill statements
   - rollback / down migration
2. **Detect migration tooling** from
   `references/migration-risk-checklist.md` and the discovery
   report.
3. **Apply the risk checklist** to the change. For each item,
   record: not in scope, not present, or finding (with evidence).
4. **Apply stop conditions** (see below). Any blocker stops the
   review and creates a blocker via `task-state-management`.
5. **Render the report** from
   `templates/migration-safety-report.md`.
6. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/migration-safety-report.md`.
7. **Default handoff.** If the change is approved, hand off to
   `code-change-review` for full review, or to
   `backend-implementation` for the migration code. If blocked, hand
   off to `ARCHITECT_AGENT` for the deployment-strategy decision.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Read existing reports under the task workspace.
- Run `git diff` and `git log` to resolve the change set.
- Create the report file under the task workspace.

## Forbidden Actions

- No executing migrations (`flyway migrate`, `alembic upgrade`,
  `prisma migrate dev`, `dotnet ef database update`, etc.).
- No dropping data.
- No generating destructive migrations.
- No assuming downtime is acceptable — every blocker must be
  considered against a zero-downtime default.
- No reading environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*`.

## Stop Conditions

- A destructive migration is proposed (drop column, drop table,
  truncate, etc.) → blocker, escalate to architecture.
- A migration causes data loss (type narrowing, NOT NULL without
  default, etc.) → blocker, escalate.
- A migration is irreversible (no `down` / `rollback` defined, or the
  `down` cannot restore data) → blocker, escalate.
- A large table rewrite is proposed (ALTER on a high-traffic table
  without a phased approach) → blocker, escalate.
- A production-impacting lock is likely (long `ACCESS EXCLUSIVE`,
  full-table rewrite) → blocker, escalate.
- Otherwise, the review continues and the report is rendered.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/migration-safety-report.md`
- An optional blocker file under the task workspace.
- An optional handoff packet via the `handoff-packet` skill.

## Handoff Contract

Receiving agents may rely on:

- `change_set` — list of changed migration / model files
- `tooling` — detected migration tool
- `findings` — array of `{category, severity, file, lines, summary,
  evidence, recommendation, approval_required}`
- `outcome` — `approved | changes_requested | blocked`
- `blocker_filed` — boolean
- `deployment_strategy_required` — `expand-and-contract | online |
  phased | none`

Receiving agents must not rely on:

- A clean review meaning the migration is safe in production (the
  skill is a first pass; real-database testing is required for
  sign-off).

## Validation

- The report file exists and parses as markdown.
- Every changed file from the input set appears in the report.
- Every Critical/High finding has a `file:lines` evidence pointer.
- `outcome` is one of `approved | changes_requested | blocked`.
- If any blocker was filed, `blocker_filed: true` and a blocker file
  exists.

## Completion Criteria

- Report written, outcome decided, blockers filed if needed.
- If `outcome` is `changes_requested` or `blocked`, the report names
  the follow-up target and the deployment strategy required.
