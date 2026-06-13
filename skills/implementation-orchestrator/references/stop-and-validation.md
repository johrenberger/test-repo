# Stop conditions and validation — long form

> Long form of the `implementation-orchestrator` Stop Conditions
> and Validation sections. The main `SKILL.md` keeps a compact
> summary; consult this file when triaging a stuck routing
> decision or when validating a routing report.

## Stop conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Acceptance criteria are unclear or contradictory.
- The task requires a destructive migration and no review has been
  scheduled.
- The task requires a new dependency / package-manager / build-tool
  change and no review has been scheduled.
- The task crosses multiple modules with unclear ownership and the
  module owners cannot be inferred from the discovery artifact.
- The task requires production credentials or deployment access.
- The discovery artifact contradicts the task description in a way
  that affects routing.

## Validation

Routing is "validated" when:

1. The routing report cites a discovery artifact and lists concrete
   files / modules per layer.
2. The selected skill exists and is a routed implementation or
   review skill.
3. Every preflight gate is either satisfied (review artifact
   attached) or explicitly waived with a `decisions/<id>.md`
   entry.
4. The handoff packet has all 14 required fields.

The orchestrator itself runs no shell commands. Validation is
performed by the receiving skill (typically
`validation-runner` at the end of the implementation cycle).
