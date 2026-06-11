# Modular monolith checklist

Read on demand by
[`architecture-review`](../../SKILL.md) when the change is in
a modular-monolith codebase (one deployable, multiple
modules with internal boundaries) or when the proposal is to
move toward or away from a modular monolith.

## When this checklist applies

- The repo is one deployable (one service, one process group,
  one build artifact).
- The repo has internal module boundaries (packages,
  directories, namespaces) with explicit ownership.
- The proposal is to add a module, split a module, or extract
  a module into a separate service.

## What to check

### 1. Module boundaries are real

- [ ] Modules have explicit, named boundaries (packages,
  directories, build targets).
- [ ] Cross-module calls go through documented interfaces
  (public APIs, events, ports).
- [ ] A module's internals are not imported by other modules
  except through the documented interface.
- [ ] Module ownership is named in the repo
  (`CODEOWNERS`, `OWNERS`, or equivalent).

### 2. Build / test isolation is real

- [ ] Each module has its own unit tests that do not require
  the whole monolith to run.
- [ ] Integration tests are scoped to the modules they
  exercise.
- [ ] The build supports building and testing a single module
  in isolation when feasible.

### 3. Data ownership is explicit

- [ ] Each module owns its tables / collections / files.
- [ ] Cross-module data access goes through the owning
  module's API, not direct DB access.
- [ ] Schema migrations are owned by the data-owning module.

### 4. Deployment is single-artifact but configurable

- [ ] Config can enable / disable a module at deploy time
  when the design allows.
- [ ] Feature flags are used to roll out module changes
  incrementally.
- [ ] Rollback is at the artifact level (one deployable).

### 5. Extractability is a property, not a fact

- [ ] The module's public surface is small and well-defined.
- [ ] Cross-module communication is async or via stable APIs
  (not shared in-memory state).
- [ ] When extraction is later required, the cost is
  identified (a refactor, not a rewrite).

### 6. The simpler design is justified

- [ ] The decision to use a modular monolith (rather than
  microservices) is recorded in an ADR.
- [ ] The decision lists what would change to require
  splitting (scale, team, deploy independence).
- [ ] The decision names the team's operational capacity for
  distributed systems (a single monolith is a single failure
  domain; the team must be able to operate it).

## Red flags (block approval)

- Modules are directories only, with no real boundary (free
  imports, shared mutable state, no CODEOWNERS).
- Cross-module data access via direct DB / shared cache.
- Schema migrations owned by one module that change another
  module's tables.
- Proposal to split into microservices without a stated
  team / scale / deploy reason.
- Proposal to merge modules without an explicit ownership
  transition plan.

## How to use

1. Confirm the change is in a modular-monolith repo (or is a
   proposal to move toward or away from one).
2. Run through each section; record verdicts in the
   architecture review report.
3. Any red flag fires a blocker; the change is not approved
   until resolved.
