# integration-implementation

Implement **cross-system integration** behavior safely. The
skill produces the smallest change that adds or modifies a
boundary between this system and another — through an API call,
a message, a webhook, a file, or a shared contract — while
respecting retries, idempotency, error handling, and contract
compatibility.

This skill is **narrowly scoped** to integration boundaries. It
does not edit pure backend logic, pure UI, or pure
infrastructure provisioning. If the task crosses into those
areas, stop and hand off to
[`implementation-orchestrator`](../implementation-orchestrator/SKILL.md).

## Purpose

Translate an approved integration-scoped plan (typically from a
product spec, a partner-integration brief, a code-review
fix-up, or a `dependency-change-review` artifact) into working
integration code that matches the existing repo's client / adapter
/ DTO / schema / retry / timeout patterns, and passes validation.

The skill is integration-only. The orchestrator decides when this
skill is the right one to invoke; this skill does not decide that
on its own.

## In scope

Cross-system work the skill will perform when invoked:

- **External API calls** — outbound HTTP/REST, GraphQL, gRPC
  calls to third-party services or partner systems
- **Service-to-service communication** — internal API calls
  between owned services (e.g. `service-a` calling `service-b`'s
  API), distinct from in-process backend logic
- **Webhooks** — outbound (this service emits webhooks to other
  systems) and inbound (this service receives webhooks from
  other systems)
- **Message queues / event streaming** — producers, consumers,
  schema registry, topic management, partitioning
- **Event processing** — handlers for events from internal or
  external sources, including event-sourced workflows
- **File imports / exports** — SFTP, S3, blob storage,
  CSV/JSON/XML parsers, scheduled file pickups
- **ETL / data movement** — extract, transform, load jobs
  between data stores (when crossing system boundaries)
- **Contract compatibility** — versioning API clients,
  backfilling missing fields, handling deprecations
- **Retries / timeouts / idempotency** — boundary-level
  resilience patterns
- **API client / server compatibility** — fixing a client to
  match a server's contract, or vice versa, when both are
  under the same ownership
- **Cross-module workflows** — orchestrations that span more
  than one integration boundary

## Out of scope (hard guardrail)

The skill **must stop and hand off** to
[`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
when any of the following is part of the task:

- **Pure backend internal logic** — service / domain / repository
  code that does not cross a system boundary; route to
  [`backend-implementation`](../backend-implementation/SKILL.md).
- **Pure frontend UI** — components, forms, client state, client
  routing; route to
  [`frontend-implementation`](../frontend-implementation/SKILL.md).
- **Pure infrastructure provisioning** — Terraform, Helm, cloud
  config, deploy scripts; out of scope.
- **Active pen testing** — out of scope; route to
  [`security-review`](../security-review/SKILL.md) and
  `PEN_TESTING_AGENT` instead.
- **Destructive data sync** — drop, replace, or rewrite data
  in a downstream system without an explicit approval gate.
- **New queues, brokers, SDKs, or new infrastructure
  dependencies** — route to
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first.
- **Architecture-novel work** — new integration pattern that
  has not been used in this repo before; route to
  `ARCHITECT_AGENT` first.

A `integration-implementation` task that needs any of the above
is **not a single-skill task**. The orchestrator must sequence
the right skills.

## Trigger

Use when the task involves any of:

- Calling an external API (third-party, partner, or another
  internal service over HTTP / gRPC / GraphQL)
- Service-to-service communication that crosses a process
  boundary
- Webhooks (outbound or inbound)
- Message queues, event streaming, pub/sub
- Event processing handlers
- File imports / exports (SFTP, S3, batch files)
- ETL / data movement between systems
- Contract compatibility fixes (client-side, server-side, or
  both)
- Retries / timeouts / idempotency for an existing integration
- API client / server compatibility under shared ownership
- Cross-module workflows that span integration boundaries

## Do Not Use When

- The task is purely backend internal logic — use
  [`backend-implementation`](../backend-implementation/SKILL.md).
- The task is purely frontend UI — use
  [`frontend-implementation`](../frontend-implementation/SKILL.md).
- The task is pure infrastructure provisioning — out of scope;
  route to a deployment / infra skill or a human owner.
- The task is **active pen testing** — use
  [`security-review`](../security-review/SKILL.md) and
  `PEN_TESTING_AGENT`.
- The task is unclear about which layer it touches — use
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
  first.
- The task requires a new dependency (new SDK, new broker) —
  use
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first.
- The task is discovery-only, review-only, or validation-only.

## Required Inputs

- **Task description** with concrete acceptance criteria.
- **Repo-discovery artifact** (current
  `discovery/repo-discovery.md`) for the task.
- **Routing report** (when invoked through the orchestrator) or
  equivalent target module list.
- **Integration boundary** — at least one of the supported
  profiles matches the actual code:
  [`rest-api`](references/profiles/rest-api.md),
  [`async-messaging`](references/profiles/async-messaging.md),
  [`webhook`](references/profiles/webhook.md),
  [`file-batch`](references/profiles/file-batch.md),
  [`contract-testing`](references/profiles/contract-testing.md).
  If none match, the skill stops and asks for guidance.
- **Partner / system contract** — documentation, OpenAPI spec,
  AsyncAPI spec, schema file, or prior implementation reference
  for the boundary being changed. If no contract reference
  exists, the skill stops and asks for one.
- **Prior review findings**, if any, with the IDs of fix-ups to
  address.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; this skill does not invent repo
   facts.
2. Confirm acceptance criteria are concrete and testable.
3. Confirm the task is integration-only. If the task also
   requires backend, frontend, or infra changes, stop and route
   to the orchestrator.
4. Confirm the integration profile matches reality.
5. Confirm the contract reference (OpenAPI / AsyncAPI / schema
   / docs) is attached. If not, the skill stops and asks for
   one.
6. Confirm no new dependency / SDK / broker is being introduced
   silently. If yes, route to
   [`dependency-change-review`](../dependency-change-review/SKILL.md)
   first.
7. Confirm the integration is not a destructive data sync
   without an explicit approval gate. If yes, stop and require
   an approval gate.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the target integration boundary is identified. The
   orchestrator's routing report or the explicit handoff names
   the boundary; this skill must not change boundaries
   mid-flight.

2. **Identify integration boundary.** Match the actual code to
   one of the supported profiles:
   [`rest-api`](references/profiles/rest-api.md),
   [`async-messaging`](references/profiles/async-messaging.md),
   [`webhook`](references/profiles/webhook.md),
   [`file-batch`](references/profiles/file-batch.md), or
   [`contract-testing`](references/profiles/contract-testing.md).
   If the integration spans multiple boundaries, the
   orchestrator's routing report must list them in order; this
   skill implements them in the order listed.

3. **Inspect existing integration patterns.** Read the
   relevant profile(s). Each profile documents detection cues,
   client / adapter / DTO / schema / retry / timeout / error
   handling conventions, and a small example.

4. **Identify failure modes.** For the boundary being changed,
   list the failure modes the change must address or document
   the existing handling for:

   - timeout
   - retry exhaustion
   - duplicate delivery
   - partial failure
   - invalid payload
   - auth failure
   - rate limit
   - downstream unavailable
   - schema / version mismatch
   - (broker-specific) DLQ, ordering, partition rebalance

5. **Required design checks.** The implementation must address:

   - **Timeout behavior** — explicit timeout, not the default
   - **Retry behavior** — bounded retries with backoff, or
     explicit no-retry rationale
   - **Idempotency** — idempotency key, dedup window, or
     explicit at-most-once rationale
   - **Error classification** — retryable vs non-retryable
   - **Logging without secrets** — payload fields that may
     contain secrets are redacted
   - **Observability / correlation IDs** — reuse the existing
     correlation pattern, do not invent a new one
   - **Schema / contract compatibility** — version pinning,
     additive changes only (do not break the contract)
   - **Backpressure / rate limit** — when relevant for the
     boundary

6. **Add or update tests where feasible.** Cover at least
   success + the most common failure modes. Test doubles
   (mocks, recorded fixtures, contract tests) preferred over
   real endpoints. **Do not call real production endpoints
   from tests.**

7. **Implement smallest safe integration change.** Follow the
   profile's conventions. Do not introduce new SDKs, brokers,
   serializers, or test frameworks. Reuse the existing client,
   DTO, error, and logging patterns.

8. **Run validation.** Use
   [`validation-runner`](../validation-runner/SKILL.md) to
   discover and run the repo's local validation commands. Do
   not install dependencies. If validation cannot be run, the
   report must explain why.

9. **Hand off for review and follow-up.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to
   `code-change-review`, `security-review`, or
   `test-generation` as appropriate.

## Allowed Actions

- Read repo files.
- Add or update integration code (clients, adapters, DTOs,
  schemas, retry / timeout wrappers, error handlers,
  observability hooks, tests) within the target boundary.
- Run repo-local validation commands detected by
  [`validation-runner`](../validation-runner/SKILL.md).
- Run the repo's test suite locally; never install dependencies
  to make it pass.
- Write the implementation report and handoff packet.

## Forbidden Actions

- **Do not edit pure backend code.** Service / domain /
  repository code that does not cross a boundary is out of
  scope. Handoff to
  [`backend-implementation`](../backend-implementation/SKILL.md).
- **Do not edit frontend code.** Out of scope. Handoff to
  [`frontend-implementation`](../frontend-implementation/SKILL.md).
- **Do not call real third-party production endpoints** during
  tests. Use mocks, recorded fixtures, or sandbox endpoints.
- **Do not commit credentials or tokens.** If a test needs a
  credential, use a placeholder / redacted form
  (`<REDACTED: kind>`) and document the env var the caller
  must set in their own environment.
- **Do not introduce queues, brokers, SDKs, or new
  infrastructure dependencies** without explicit approval and a
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  gate.
- **Do not change API contracts** without documenting the
  compatibility impact in the implementation report.
- **Do not implement destructive data sync behavior**
  (drop, replace, rewrite downstream data) without an
  explicit approval gate.
- **Do not run load tests or active external tests** unless
  explicitly requested as part of the task.
- **Do not run installers** (`npm install`, `pip install`,
  `go mod tidy`, `cargo add`, `dotnet add`).
- **Do not read or write credentials, secrets, tokens, or
  environment variables matching `*TOKEN*`, `*SECRET*`, `*KEY*`,
  `*PASSWORD*`.**
- **Do not deploy, run migrations, or modify production
  endpoints.**
- **Do not bypass the orchestrator** when the task also
  touches backend, frontend, or infra code.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- The target module is not actually integration, or is
  genuinely mixed with no clean boundary.
- The required profile does not match the repo.
- The contract reference (OpenAPI / AsyncAPI / schema / docs)
  is missing.
- Acceptance criteria are unclear.
- A new dependency / SDK / broker is part of the task and no
  review has been scheduled.
- A destructive data sync is required and no approval gate
  exists.
- The task requires touching pure backend or frontend code as
  part of the same change; the orchestrator must sequence the
  skills.
- The repo's validation commands fail in a way that is not
  related to the change.
- Production credentials or live external services are
  required for testing.

## Outputs

- **Source changes** — integration source files and tests
  within the target boundary, per the profile's conventions.
- **Implementation report** —
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/integration-implementation-report.md`
  (see
  [`templates/integration-implementation-report.md`](templates/integration-implementation-report.md)).
- **Handoff packet** to
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md), or
  [`test-generation`](../test-generation/SKILL.md) as
  appropriate.

## Handoff Contract

Fields the receiving skill may rely on:

- `target_boundary` — list of `path:reason` for the integration
  files changed
- `profile_used` — exactly one of
  `rest-api | async-messaging | webhook | file-batch | contract-testing`
- `contract_reference` — path / URL to the OpenAPI / AsyncAPI /
  schema / doc that the change is implementing against
- `failure_modes_addressed` — list of failure modes from the
  workflow's failure-mode list
- `tests_added_or_updated` — list of test files touched
- `validation_result` — short summary of what
  [`validation-runner`](../validation-runner/SKILL.md) produced
- `out_of_scope` — list of files the skill refused to touch
- `compatibility_impact` — explicit "no contract change" or
  description of the contract change and its backwards-
  compatibility impact
- `acceptance_criteria` — the testable conditions

Fields the receiving skill must not rely on:

- "production-safe" — local validation is not a deployment
  claim.
- "secure" — security is asserted only by
  [`security-review`](../security-review/SKILL.md).
- "no regressions" — claims of no regression require
  `validation-runner` evidence in the implementation report.
- "no real endpoints called" — the test evidence must
  demonstrate this; the contract is not a substitute for the
  evidence.

## Validation

The skill is "validated" when:

1. The implementation report exists and references the target
   boundary, the profile used, the contract reference, the
   failure modes addressed, and the tests added or updated.
2. `validation-runner` was run; its report is linked from the
   implementation report.
3. No forbidden action was performed (dependency install,
   production-endpoint test call, real credential use,
   destructive sync without approval, backend or frontend
   edit, secret read).
4. The handoff packet to the next skill has all 14 required
   fields.

## Completion Criteria

- The smallest integration change that satisfies the acceptance
  criteria is in the working tree.
- The profile's conventions are followed.
- Integration tests covering the change are present and pass
  locally, using test doubles (not real production endpoints).
- `validation-runner` ran without installer refusals.
- The implementation report is complete and the handoff packet
  is accepted by the next skill.

## Cross-references

- Routing:
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
- Sibling implementation skills:
  [`backend-implementation`](../backend-implementation/SKILL.md),
  [`frontend-implementation`](../frontend-implementation/SKILL.md)
- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Review gates:
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md),
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
- Tests:
  [`test-generation`](../test-generation/SKILL.md)

## Profiles

Per-boundary guidance. Read on demand, not loaded wholesale.

- [`references/profiles/rest-api.md`](references/profiles/rest-api.md)
- [`references/profiles/async-messaging.md`](references/profiles/async-messaging.md)
- [`references/profiles/webhook.md`](references/profiles/webhook.md)
- [`references/profiles/file-batch.md`](references/profiles/file-batch.md)
- [`references/profiles/contract-testing.md`](references/profiles/contract-testing.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
