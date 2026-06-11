# Migration risk checklist

Used by `database-migration-safety`.

## Detected tools

- **Flyway** — `flyway.conf`, `V*__*.sql` in `db/migration/` /
  `src/main/resources/db/migration/`
- **Liquibase** — `changelog*.xml`, `changelog*.yaml`,
  `changelog*.json`, `*.sql` in `src/main/resources/db/changelog/`
- **Alembic** — `alembic/versions/*.py` and `alembic.ini`
- **Django migrations** — `*/migrations/0*_*.py` and `django` in
  `INSTALLED_APPS`
- **Prisma** — `prisma/schema.prisma` and `@prisma/client`
- **TypeORM** — `*.entity.ts` with `@Entity` decorator and
  `typeorm` in deps
- **Sequelize** — `migrations/*.js` and `sequelize` in deps
- **Rails ActiveRecord** — `db/migrate/*.rb` and Rails markers
- **EF Core** — `Migrations/*.cs` and `Microsoft.EntityFrameworkCore`
- **Raw SQL** — `.sql` files in any `migrations/` / `db/` /
  `sql/` directory

## Severity scale

| Level | Use when |
| --- | --- |
| Critical | Destructive operation, data loss, irreversible change, large table rewrite, production-impacting lock without mitigation |
| High | Long-running operation on a non-trivial table, default / nullability change, missing rollback, backfill that may conflict with writes |
| Medium | Index creation that may lock writes, type widening that changes query plans, missing NOT NULL constraint verification |
| Low | Naming / comment hygiene, default reorder, missing IF EXISTS guard |

## Categories

### Destructive operations

- `DROP TABLE` / `DROP COLUMN` / `DROP INDEX` / `DROP CONSTRAINT`
- `TRUNCATE`
- `DELETE` (without a clear, bounded `WHERE`)
- `ALTER COLUMN ... DROP NOT NULL` (may rewrite the table)
- `ALTER COLUMN ... TYPE ... USING ...` (may rewrite the table)

**All of these are Critical by default.** The only acceptable
mitigation is a documented, multi-step expand-and-contract
deployment with the destructive step last, behind a feature flag,
and gated on human approval.

### Locking

- `ALTER TABLE` that requires `ACCESS EXCLUSIVE` for a long time
- `CREATE INDEX` without `CONCURRENTLY` (Postgres) or equivalent
- `LOCK TABLE`
- `REINDEX`

A "long" lock is anything that would block writes for more than the
deployment window. Without a real-database estimate, treat any
single-statement migration on a high-traffic table as Critical.

### Default / nullability

- `ALTER COLUMN ... SET NOT NULL` without a default — Critical
  (the migration will fail or block on existing rows)
- `ALTER COLUMN ... SET DEFAULT` — Medium
- `ALTER COLUMN ... DROP DEFAULT` — Medium
- `ALTER COLUMN ... DROP NOT NULL` — High (table rewrite risk)

### Backfill

- A backfill that updates a large number of rows in a single
  statement — High
- A backfill without batching — High
- A backfill that conflicts with concurrent writes (no version
  column / no `WHERE` filter) — High
- A backfill without a follow-up "set NOT NULL" step in a later
  migration — High

### Rollback / down

- A migration with no `down` / `rollback` / `revert` defined —
  High (the project must support rollback, or the change must be
  declared forward-only with a recovery plan)
- A `down` that does not restore data — High (data loss on
  rollback)
- A `down` that requires downtime — High

### Referential integrity

- `DROP CONSTRAINT ... FOREIGN KEY` — High
- Adding a `FOREIGN KEY` without a matching index — Medium
- Orphan rows in the source table at the time of the migration —
  Critical (the migration will fail)

### Data compatibility

- A type change that loses precision (e.g. `BIGINT` → `INT`,
  `DOUBLE` → `FLOAT`, `TEXT` → `VARCHAR(N)`) — Critical
- A type change that breaks serialization (e.g. `JSON` → `TEXT`,
  `TIMESTAMP` → `VARCHAR`) — High
- A length limit (e.g. `VARCHAR(255)` → `VARCHAR(100)`) — Critical

### Deployment ordering

- A migration that must run before / after application code is
  deployed — High if not stated in the report
- A migration that must run on multiple databases (sharded,
  replicated) — High if not stated in the report
- A migration with a feature flag in code that has not yet been
  added — High

### Testability

- A migration that has not been tested on a copy of production
  data — High
- A migration without a forward / backward test in CI — High
- A migration that cannot be tested in CI (e.g. requires a real
  database of a particular version) — record the limitation, do
  not block on it unless the migration is destructive

## Required fields for a finding

```yaml
- category: <category from the list above>
  severity: <critical|high|medium|low>
  file: <path>
  lines: "<start>-<end>"
  summary: <one line>
  evidence: <code excerpt or migration statement>
  recommendation: <concrete recommendation>
  approval_required: <yes | no>  # yes for any blocker-level finding
  deployment_strategy: <expand-and-contract | online | phased | none>
```

## Deployment strategy glossary

- **expand-and-contract** — additive first, dual-write, then
  destructive last, behind a feature flag. Default for any
  schema change that is more than additive.
- **online** — uses online schema migration tooling (e.g.
  `pg_repack`, `gh-ost`, `pt-online-schema-change`).
- **phased** — split into multiple migrations, each deployable
  independently, with verification between.
- **none** — the migration is additive and reversible; no special
  strategy is required.
