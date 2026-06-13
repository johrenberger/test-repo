# Handoff contract and forbidden actions — long form

> Long form of the `implementation-orchestrator` Handoff Contract
> and Forbidden Actions sections. The main `SKILL.md` keeps a
> compact summary; consult this file when triaging a stuck
> handoff or when auditing whether the orchestrator overstepped.

## Handoff Contract

Fields the receiving skill may rely on:

- `routing_report_path` — absolute path to the routing report
- `selected_skill` — exactly one of
  `backend-implementation | frontend-implementation | integration-implementation | database-migration-safety | dependency-change-review | architecture-review`
- `selected_skill_rationale` — why this skill
- `target_modules` — list of `path:reason` for the modules to change
- `preflight_gates_required` — list of review skills that must run
  before implementation
- `discovery_artifact_path` — absolute path to the repo discovery
- `acceptance_criteria` — the testable conditions

Fields the receiving skill must not rely on:

- "approved by <review skill>" unless the review's output is
  attached to the packet.
- "no security implications" — the orchestrator does not make
  security claims; security is asserted only by `security-review`.

## Forbidden Actions

- **Do not modify application code.** The orchestrator's only
  output is a routing report and handoff packet; it never edits
  source files.
- **Do not generate tests.** Tests are written by
  `test-generation` or by the implementation skill, scoped to its
  layer.
- **Do not implement features.** The orchestrator routes; the
  implementation skills implement.
- **Do not run destructive commands.** No installers, no `rm`, no
  schema changes, no `git push --force`, no deploys.
- **Do not route high-risk tasks directly to implementation
  without a review gate.** Migrations, dependency changes, and
  security-sensitive work must go through
  `database-migration-safety`, `dependency-change-review`, or
  `security-review` first.
- **Do not invent repo facts.** Routing decisions must cite
  files and modules from the discovery artifact.
- **Do not approve the task on behalf of any review skill.** The
  orchestrator can route to a review skill; it cannot stand in for
  one.
