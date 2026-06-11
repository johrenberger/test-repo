# Architecture risk checklist

Read on demand by
[`architecture-review`](../../SKILL.md). The checklist is
applied to a change set when the review runs. It is not a
substitute for the report template; it is a lens.

## 1. Boundary clarity

- [ ] Each module / service has an explicit ownership area.
- [ ] Cross-module calls go through a documented interface
  (API, event, file), not direct DB access or shared mutable
  state.
- [ ] Module boundaries are visible in the directory structure
  or build / package config.

## 2. Coupling / cohesion

- [ ] Each module groups related behavior (high cohesion).
- [ ] Modules do not reach into each other's internals (low
  coupling).
- [ ] Circular dependencies between modules are absent, or
  documented with a reason.

## 3. Data ownership

- [ ] Each piece of data is owned by exactly one module.
- [ ] Derived or cached data has a documented source of truth
  and an invalidation policy.
- [ ] Schema migrations are owned by the data-owning module.

## 4. API contract stability

- [ ] Existing contracts are kept working.
- [ ] Additive changes are preferred over breaking changes.
- [ ] Breaking changes are documented with a migration plan
  and an ADR.

## 5. Failure modes

- [ ] Timeout behavior is explicit, not default.
- [ ] Retry behavior is bounded with backoff.
- [ ] Idempotency is established for retried operations.
- [ ] Partial failures have a recovery path.
- [ ] Downstream unavailability is handled.
- [ ] Schema / version mismatches are handled (forward and
  backward compat).
- [ ] Auth failure modes are explicit.

## 6. Scalability assumptions

- [ ] The design's scale target is named (e.g. "10k req/s
  p50 < 50ms").
- [ ] The bottlenecks are identified, with current sizing.
- [ ] The scale target is validated (load test, capacity plan,
  or named SLO).

## 7. Security boundaries

- [ ] Trust boundaries are explicit (internal vs external,
  user vs admin, service vs service).
- [ ] Authn / authz are explicit at every boundary.
- [ ] Secrets are not in code, env, or logs.
- [ ] PII is handled with documented retention and redaction
  rules.
- [ ] Input validation is at the boundary, not deep in the
  service.
- [ ] Cryptographic choices are explicit (algorithm, key
  length, rotation).

## 8. Observability needs

- [ ] Logs are structured and avoid secrets / PII.
- [ ] Metrics exist for the critical paths.
- [ ] Traces propagate correlation IDs across boundaries.
- [ ] Health checks reflect dependencies appropriately.
- [ ] Alerts are actionable and have runbooks.

## 9. Deployment / runtime implications

- [ ] Config changes are explicit and documented.
- [ ] Rollout strategy is named (canary, blue/green,
  expand-and-contract).
- [ ] Rollback strategy is named and rehearsed when feasible.
- [ ] Resource requirements (CPU / memory / disk / network)
  are stated.

## 10. Reversibility

- [ ] Reversibility class is `cheap`, `expensive`, or
  `irreversible`.
- [ ] For `expensive` or `irreversible`, mitigations are
  named.
- [ ] For irreversible decisions, an ADR is required.

## 11. Migration path

- [ ] The change can be rolled out incrementally.
- [ ] Old behavior can be turned off without downtime.
- [ ] Database migrations follow expand-and-contract
  (additive first, switchover, then remove old).

## 12. Over-engineering risk

- [ ] No microservices split without a stated team or
  deployment reason.
- [ ] No event sourcing, CQRS, service mesh, queue, cache
  layer, or sharding without a stated requirement that the
  simpler design fails.
- [ ] No new framework or platform without an explicit ADR.

## Red flags (block approval)

- The change introduces new infrastructure (cloud service,
  broker, datastore, queue) without a
  `dependency-change-review` gate.
- A new pattern is introduced without an ADR.
- Operational failure modes are unanalyzed.
- Security boundaries are implicit or absent.
- Reversibility is `irreversible` without explicit approval.
- The simpler design is rejected without a stated reason.

## How to use

1. After mapping the change set to modules, run through this
   checklist.
2. Each row becomes a `pass | concern | finding` verdict in
   the review report's architectural-dimensions table.
3. `concern` rows are recorded as `Low` or `Medium` findings
   in the report; `finding` rows are recorded with a
   severity tied to impact.
4. Any red flag fires a blocker; the change is not approved
   until the red flag is resolved.
