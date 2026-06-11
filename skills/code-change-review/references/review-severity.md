# Review severity scale

Used by `code-change-review`. The same scale is reused (with a
slight expansion) by `security-review`.

## Severity levels

| Level | Definition | Required evidence | Blocks merge |
| --- | --- | --- | --- |
| Critical | Correctness, security, or data-loss bug that will occur in production for a realistic input. Architecture violation that must be addressed before merge. | file:line, code excerpt, one-line justification | Yes |
| High | Clear bug or significant design problem that will affect most users or cause maintainability pain. Missing test for a critical path. | file:line, code excerpt, one-line justification | Yes |
| Medium | Real concern that should be addressed before merge if scope allows, but not strictly blocking. Inconsistent error handling, weak validation. | file:line, code excerpt | Recommended |
| Low | Real concern that can be addressed in a follow-up. Unclear naming that affects a public API, minor performance smell. | file:line | No |
| Nit | Subjective preference. Only record if it materially affects maintainability or violates an explicit repo convention. | file:line, link to convention | No |

## Review categories

Apply each category to the diff. A finding can map to multiple
categories; record all of them.

- **correctness** — wrong behavior for a realistic input
- **architecture drift** — change moves the system away from its stated
  layering or invariants
- **missing tests** — new behavior with no test (or test only of the
  happy path)
- **weak tests** — tests that would not catch the bugs they appear to
  test (e.g. always-true assertions, mock-everything)
- **error handling** — swallowed errors, wrong error type, missing
  error context
- **auth / authz** — authentication or authorization missing or
  incorrectly enforced
- **data validation** — input not validated at the boundary, or
  validated with a permissive regex
- **persistence behavior** — DB writes that skip transactions, drop
  constraints, or use `destroy` semantics
- **dependency / tooling changes** — package, lockfile, or build
  changes (route to `dependency-change-review` for full coverage)
- **performance risks** — N+1 queries, blocking calls on a hot path,
  unbounded loops
- **observability / logging** — silent failures, missing or misleading
  log lines, PII / secret leakage in logs
- **security-sensitive gaps** — anything that would also be a finding
  in `security-review`
- **hidden breaking changes** — API contract changes, default value
  changes, behavior changes not mentioned in commit message or spec
- **maintainability** — duplication, magic numbers, missing constants,
  unhelpful names

## Mode-specific guidance

- `diff-only` — only flag the diff. Pre-existing issues are out of
  scope; do not mention them. (If they would be a Critical finding if
  they were new, suggest a follow-up task in the report's
  `Follow-up suggestions` section, but do not put them in `findings`.)
- `full-context` — flag the diff and pre-existing issues adjacent to
  the change. Pre-existing issues must be tagged `pre-existing: true`
  in the finding.
- `test-focused` — narrow scope to test files. Apply `missing tests`
  and `weak tests` aggressively. Other categories only when the test
  itself is buggy.
- `security-focused` — narrow scope to security-sensitive categories.
  Use `security-review` in addition for a full pass.
- `architecture-focused` — narrow scope to layering, abstractions, and
  dependency direction. Use `ARCHITECT_AGENT` review as a follow-up if
  the diff is large.

## What is NOT a finding

- "I'd write this differently." (Subjective; not a finding unless it
  falls into `architecture drift` with evidence.)
- "Why didn't you use pattern X?" (Lacks evidence the pattern is
  required by the repo.)
- "Add a comment here." (Not a finding unless the function's purpose
  is genuinely opaque from the code.)
- "Run the formatter." (Style only; not a finding.)

## When validation matters

If a `validation-runner` report exists with `outcome: failed`, the
review report must include a top-level `validation_blocker` finding
in the Critical category that quotes the failed command and its exit
code. Do not soften this to a "Medium" because the test "might be
flaky" — that is a separate investigation.
