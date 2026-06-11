# backend-implementation

Implement **backend / server-side** behavior safely. The skill
produces the smallest backend change that satisfies the acceptance
criteria and fits the existing codebase.

This skill is **narrowly scoped** to backend code. It does not
edit UI, client state, frontend routing, or cross-system
integration flows. If the task crosses into those areas, stop and
hand off to [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md).

## Purpose

Translate an approved backend-scoped plan (typically from a
product spec, an architecture review, a code-review fix-up, or a
`database-migration-safety` artifact) into working backend code
that matches the existing repo's style, framework, and test
conventions, and passes validation.

The skill is backend-only. The orchestrator decides when this
skill is the right one to invoke; this skill does not decide that
on its own.

## In scope

Backend / server-side work the skill will perform when
invoked:

- **APIs** — REST, GraphQL, gRPC, RPC, server-sent events, websocket
  endpoints on the server side
- **Controllers / routes** — request handling, validation,
  serialization
- **Services / domain logic** — business rules, orchestration of
  internal collaborators
- **Persistence / repositories** — data access, transactions,
  queries, indexes
- **Database access** — schema-aware code (NOT schema changes;
  those route through
  [`database-migration-safety`](../database-migration-safety/SKILL.md))
- **Authentication / authorization** — server-side auth,
  session / token handling, RBAC / ABAC checks, permission gates
- **Backend validation / error handling** — input validation,
  error mapping, RFC-7807-style problem responses
- **Backend observability hooks** — structured logs, metrics,
  traces, audit events
- **Backend tests** — unit, integration, contract, and
  end-to-end tests that exercise backend behavior (added or
  updated by this skill in coordination with
  [`test-generation`](../test-generation/SKILL.md))

## Out of scope (hard guardrail)

The skill **must stop and hand off** to
[`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
when any of the following is part of the task:

- **Frontend UI work** — components, styling, layout, client
  routing, client state, forms, accessibility
- **Cross-system orchestration outside backend code** — calling
  external services, webhook emission/reception, message
  production/consumption, file import/export
- **Infrastructure provisioning** — Terraform, Helm charts, cloud
  config, deploy scripts
- **Production deployment** — running deploys, scaling, traffic
  shifting
- **Active security testing** — pen-testing, dynamic scanners,
  real credentials
- **Destructive migrations** — drop column, drop table, data
  backfill with risk; route to
  [`database-migration-safety`](../database-migration-safety/SKILL.md)
  first
- **New dependency, package-manager change, or build-tool change**
  — route to
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first
- **Architecture-novel work** — new module boundary, new
  persistence model, new cross-service pattern; route to
  `ARCHITECT_AGENT` first

A `backend-implementation` task that needs any of the above is
**not a single-skill task**. The orchestrator must sequence the
right skills. Trying to "just do it" inside this skill is the
specific failure mode the orchestrator exists to prevent.

## Trigger

- A routed implementation handoff from
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
  with `selected_skill: backend-implementation`.
- A clear backend-only task with concrete acceptance criteria
  (orchestrator can be skipped when ownership is obvious).
- A `code-change-review-report.md` or `security-review-report.md`
  fix-up that is unambiguously backend.
- A `database-migration-safety` artifact cleared and ready for
  follow-up backend code.

## Do Not Use When

- The task is unclear about which layer it touches — use
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
  first.
- The task is frontend-only — use
  [`frontend-implementation`](../frontend-implementation/SKILL.md).
- The task is integration-only — use
  [`integration-implementation`](../integration-implementation/SKILL.md).
- The task is discovery-only, review-only, or validation-only.
- The task is a destructive migration — use
  [`database-migration-safety`](../database-migration-safety/SKILL.md)
  first; this skill can do follow-up backend code only after the
  migration review is cleared.
- The task requires a new dependency — use
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first.

## Required Inputs

- **Task description** with concrete acceptance criteria.
- **Repo-discovery artifact** (current
  `discovery/repo-discovery.md`) for the task.
- **Routing report** (when invoked through the orchestrator) or
  equivalent target module list.
- **Stack profile** — at least one of the supported profiles
  matches the actual code:
  [`java-spring`](references/profiles/java-spring.md),
  [`node-typescript`](references/profiles/node-typescript.md),
  [`python`](references/profiles/python.md),
  [`go`](references/profiles/go.md),
  [`dotnet`](references/profiles/dotnet.md),
  [`mixed-monolith`](references/profiles/mixed-monolith.md).
  If none match, the skill stops and asks for guidance.
- **Prior review findings**, if any, with the IDs of fix-ups to
  address.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; this skill does not invent repo
   facts.
2. Confirm acceptance criteria are concrete and testable.
3. Confirm the task is backend-only. If not, stop and route to
   the orchestrator.
4. Confirm the stack profile matches reality. If the existing
   repo mixes stacks in a single module, prefer
   [`mixed-monolith`](references/profiles/mixed-monolith.md)
   and call out the multi-stack nature in the implementation
   report.
5. Confirm no destructive migration or new dependency is part of
   the task. If yes, route to the review skill first.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the target module is identified. The orchestrator's
   routing report or the explicit handoff names the target
   module; this skill must not change targets mid-flight.

2. **Backend ownership / module confirmation.** Confirm the
   module is genuinely backend. If the discovery says the module
   is mixed, narrow the change to the backend files only and
   list frontend / integration files as out of scope.

3. **Inspect existing backend patterns.** Read the relevant
   profile ([`java-spring`](references/profiles/java-spring.md),
   [`node-typescript`](references/profiles/node-typescript.md),
   [`python`](references/profiles/python.md),
   [`go`](references/profiles/go.md),
   [`dotnet`](references/profiles/dotnet.md), or
   [`mixed-monolith`](references/profiles/mixed-monolith.md)).
   The profile documents detection cues, naming conventions,
   forbidden actions, and a small example specific to the stack.

4. **Add or update tests where feasible.** Tests are added by this
   skill only for the backend code being changed. Frontend tests
   are out of scope; integration tests are out of scope. For
   shared test patterns, defer to
   [`test-generation`](../test-generation/SKILL.md) when the
   test surface spans layers.

5. **Implement smallest safe backend change.** Follow the
   profile's conventions. Do not introduce new dependencies,
   new frameworks, new package managers, new test frameworks,
   Lombok / MapStruct / Testcontainers / Flyway / Liquibase /
   new Spring starters (see
   [`java-spring`](references/profiles/java-spring.md) for the
   specific guardrails), or any other architectural change. The
   same kind of profile-specific guardrails exist in
   [`node-typescript`](references/profiles/node-typescript.md),
   [`python`](references/profiles/python.md),
   [`go`](references/profiles/go.md),
   [`dotnet`](references/profiles/dotnet.md), and
   [`mixed-monolith`](references/profiles/mixed-monolith.md).

6. **Run validation.** Use
   [`validation-runner`](../validation-runner/SKILL.md) to
   discover and run the repo's local validation commands. Do not
   install dependencies. If validation cannot be run, the report
   must explain why.

7. **Hand off for review and follow-up.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to
   `code-change-review`, `security-review`, or
   `test-generation` as appropriate. The packet's
   `Required next action` references the implementation report.

## Allowed Actions

- Read repo files.
- Add or update backend source files within the target module.
- Add or update backend tests within the target module.
- Run repo-local validation commands detected by
  [`validation-runner`](../validation-runner/SKILL.md).
- Run the repo's test suite locally; never install dependencies
  to make it pass.
- Write the implementation report and handoff packet.

## Forbidden Actions

- **Do not edit frontend code.** Components, styles, client
  state, client routing, and client API wrappers are out of
  scope. Handoff to
  [`frontend-implementation`](../frontend-implementation/SKILL.md).
- **Do not edit integration code.** External API clients,
  webhook handlers, queue producers / consumers, file
  importers / exporters are out of scope. Handoff to
  [`integration-implementation`](../integration-implementation/SKILL.md).
- **Do not introduce new dependencies, frameworks, package
  managers, build tools, or test frameworks** without routing to
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first.
- **Do not run destructive migrations** or schema changes; route
  to
  [`database-migration-safety`](../database-migration-safety/SKILL.md)
  first.
- **Do not run installers** (`npm install`, `pip install`,
  `go mod tidy`, `cargo add`, `dotnet add`).
- **Do not read or write credentials, secrets, tokens, or
  environment variables matching `*TOKEN*`, `*SECRET*`, `*KEY*`,
  `*PASSWORD*`.**
- **Do not deploy, run load tests, or call real production
  endpoints.**
- **Do not approve the task on behalf of any review skill.**
  The skill can resolve findings; it cannot stand in for the
  review that produced them.
- **Do not change the package manager or build tool.**
- **Do not bypass the orchestrator** when the task touches more
  than one layer. The orchestrator exists exactly so this skill
  does not have to make routing decisions.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- The target module is not actually backend, or is genuinely
  mixed with no clean backend boundary.
- The required profile does not match the repo and no
  `mixed-monolith` exception applies.
- Acceptance criteria are unclear.
- A destructive migration or new dependency is part of the task
  and no review has been scheduled.
- The task requires touching frontend or integration code as
  part of the same change; the orchestrator must sequence the
  skills.
- The repo's validation commands fail in a way that is not
  related to the change.
- Production credentials or live external services are required.

## Outputs

- **Source changes** — backend source files and tests within the
  target module, per the profile's conventions.
- **Implementation report** —
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/backend-implementation-report.md`
  (see
  [`templates/backend-implementation-report.md`](templates/backend-implementation-report.md)).
- **Handoff packet** to
  [`code-change-review`](../code-change-review/SKILL.md) or
  [`test-generation`](../test-generation/SKILL.md) as
  appropriate.

## Handoff Contract

Fields the receiving skill may rely on:

- `target_modules` — list of `path:reason` for the modules changed
- `profile_used` — exactly one of
  `java-spring | node-typescript | python | go | dotnet | mixed-monolith`
- `tests_added_or_updated` — list of test files touched
- `validation_result` — short summary of what
  [`validation-runner`](../validation-runner/SKILL.md) produced
- `out_of_scope` — list of files the skill refused to touch
  (frontend, integration, migrations, etc.)
- `acceptance_criteria` — the testable conditions

Fields the receiving skill must not rely on:

- "production-safe" — the skill can run local validation; it
  cannot make deployment claims.
- "secure" — security is asserted only by
  [`security-review`](../security-review/SKILL.md).
- "no regressions" — claims of no regression require
  `validation-runner` evidence in the implementation report.

## Validation

The skill is "validated" when:

1. The implementation report exists and references the target
   module, the profile used, and the tests added or updated.
2. `validation-runner` was run; its report is linked from the
   implementation report.
3. No forbidden action was performed (dependency install,
   package-manager swap, destructive migration, frontend or
   integration edit, secret read).
4. The handoff packet to the next skill has all 14 required
   fields.

## Completion Criteria

- The smallest backend change that satisfies the acceptance
  criteria is in the working tree.
- The stack profile's conventions are followed.
- Backend tests covering the change are present and pass locally.
- `validation-runner` ran without installer refusals.
- The implementation report is complete and the handoff packet
  is accepted by the next skill.

## Cross-references

- Routing:
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
- Sibling implementation skills:
  [`frontend-implementation`](../frontend-implementation/SKILL.md),
  [`integration-implementation`](../integration-implementation/SKILL.md)
- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Review gates:
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md),
  [`database-migration-safety`](../database-migration-safety/SKILL.md),
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
- Tests:
  [`test-generation`](../test-generation/SKILL.md)

## Profiles

Per-stack guidance, kept from the prior broad version of this
skill. **All profiles remain valid; only the orchestrator above
this skill changed.** Profiles are reference material — they are
read on demand, not loaded wholesale.

- [`references/profiles/java-spring.md`](references/profiles/java-spring.md)
- [`references/profiles/node-typescript.md`](references/profiles/node-typescript.md)
- [`references/profiles/python.md`](references/profiles/python.md)
- [`references/profiles/go.md`](references/profiles/go.md)
- [`references/profiles/dotnet.md`](references/profiles/dotnet.md)
- [`references/profiles/mixed-monolith.md`](references/profiles/mixed-monolith.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
