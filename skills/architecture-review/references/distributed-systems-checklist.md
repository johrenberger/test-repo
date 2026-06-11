# Distributed systems checklist

Read on demand by
[`architecture-review`](../../SKILL.md) when the change adds
or modifies distributed-systems concerns: cross-service calls,
event-driven flows, message brokers, eventual consistency,
distributed transactions, leader election, sharding, or
multi-region deployment.

> **Default expectation:** most repos do not need distributed
> systems. The simplest design (a single deployable, a single
> database, in-process calls) is preferred. This checklist is
> applied **only when the design is already distributed** or
> the proposal is to introduce distribution.

## When this checklist applies

- The repo has more than one deployable service that talks
  over the network.
- The design uses a message broker, event bus, or stream
  platform.
- The design has eventual consistency, distributed
  transactions, or compensating transactions.
- The design has multiple regions, multiple data centers, or
  active/active deployment.

## What to check

### 1. Failure modes are explicit

- [ ] Network partitions: how does the system behave when two
  services cannot reach each other?
- [ ] Process crashes: what state is lost, and is the recovery
  path explicit?
- [ ] Downstream unavailability: does the system fail open,
  fail closed, or queue?
- [ ] Partial failures: what is the recovery path for a
  half-completed distributed transaction?
- [ ] Clock skew: are timestamps, retries, and ordering robust
  to clock skew?

### 2. Timeouts, retries, idempotency

- [ ] Every cross-service call has an explicit timeout.
- [ ] Retries are bounded with backoff.
- [ ] Idempotency keys are used for non-idempotent operations
  (POST, message production).
- [ ] At-least-once delivery is paired with idempotent
  consumers, or at-most-once is paired with explicit
  acceptance of message loss.

### 3. Consistency model is named

- [ ] The consistency model is explicit (strong, eventual,
  read-your-writes, etc.).
- [ ] The product / user-visible impact of the consistency
  model is documented.
- [ ] Conflicting writes have a resolution strategy
  (last-write-wins, vector clocks, CRDTs, manual merge).

### 4. Observability

- [ ] Correlation IDs propagate across service boundaries.
- [ ] Distributed traces are sampled at a sensible rate.
- [ ] Logs are structured and avoid secrets / PII.
- [ ] Metrics exist for queue depth, lag, retry rate, and
  error rate.
- [ ] Alerts are actionable; runbooks exist for each.

### 5. Deployment and rollout

- [ ] Rollout strategy is named (canary, blue/green,
  rolling).
- [ ] Schema / contract changes follow expand-and-contract.
- [ ] Rollback is rehearsed.
- [ ] Capacity planning is documented for the new behavior.

### 6. Operational capacity

- [ ] The team has on-call coverage for the new failure
  modes.
- [ ] The team can debug distributed traces and correlate
  logs across services.
- [ ] The team has runbooks for the new failure modes
  (see [`runbook-authoring`](../runbook-authoring/SKILL.md)).

### 7. The simpler design is justified

- [ ] The decision to distribute is recorded in an ADR.
- [ ] The decision lists what would change to require
  consolidation (team, scale, cost).
- [ ] The decision names the team's operational capacity for
  distributed systems (operators, on-call, SRE practices).

## Red flags (block approval)

- Distribution is introduced without a stated reason (team,
  scale, deploy independence).
- Failure modes are unanalyzed.
- Timeouts, retries, and idempotency are defaults.
- Correlation IDs are missing.
- Rollback strategy is "we'll figure it out."
- The team has no on-call coverage for the new failure
  modes.

## How to use

1. Confirm the design is distributed (or is a proposal to
   introduce distribution).
2. Run through each section; record verdicts in the
   architecture review report.
3. Any red flag fires a blocker; the change is not approved
   until resolved.
4. When this checklist applies,
   [`observability-review`](../observability-review/SKILL.md)
   and [`runbook-authoring`](../runbook-authoring/SKILL.md)
   are typically required as follow-up skills.
