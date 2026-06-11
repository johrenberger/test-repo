# test-generation

Generate or update tests in the repository's existing test framework and
style. The skill fits the new tests into the existing test layout and
naming conventions, and runs targeted validation after writing.

## Purpose

Close test gaps identified by `test-gap-analysis` (or a manual request)
by producing tests that match the project's existing test style, run
locally, and exercise the right behaviors.

## Trigger

- A `test-gap-report.md` identifies gaps the team wants closed.
- A code change introduces new behavior that must have tests before
  merge.
- A handoff packet's "Required next action" calls for test generation.

## Do Not Use When

- The repo has not been discovered — run `repo-discovery` first.
- The behavior to test is not yet implemented and the task is
  implementation-first (use `backend-implementation` first, then
  `test-generation` for the tests).
- The repo has no test framework and none has been approved (this skill
  does not introduce new frameworks).
- The task is documentation-only or pure refactor with no behavior
  change.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `SCOPE` — what to test (file, module, endpoint, or behavior area)
- `BEHAVIORS` — list of behaviors to cover (from `test-gap-report.md` or
  manual specification)
- `TEST_TYPE` — one of: `unit | integration | contract | regression |
  security-negative` (default: from the gap report)

## Preflight

- Read the `repo-discovery` report for this task. If absent, abort.
- If a `test-gap-report.md` exists for this task, read it. The behaviors
  in `BEHAVIORS` should align with that report; if they do not, record
  the deviation in the report.
- Identify the existing test framework from the inventory — never assume.
  See the language-specific references for detection cues.
- Verify the test directory for the in-scope module exists or can be
  inferred from project convention.
- Verify `validation-runner` has produced a command set (or run it).

## Workflow

1. **Discover.** Re-read the discovery report and inventory of existing
   tests adjacent to the scope. Match naming conventions and directory
   layout exactly.
2. **Pick the reference profile.** Choose the language/framework profile
   in `references/` that matches the detected stack. If none fits
   cleanly, stop and create a blocker.
3. **Plan tests.** For each behavior in `BEHAVIORS`, choose the
   appropriate test type. Use the coverage checklist in this skill's
   `Workflow` (happy path, validation failure, auth failure, etc.) to
   enumerate cases — but only the cases that are relevant to the
   behavior. Do not over-test.
4. **Write tests** in the existing framework, using existing fixtures
   and helpers. Do not introduce a new framework, assertion library, or
   mocking library.
5. **Avoid fragile mocks.** Mock at the network / IO boundary, not at
   every internal call. Prefer fakes and in-memory implementations when
   they exist. Test behavior, not implementation details.
6. **Run targeted validation.** Use `validation-runner` to run the
   test/lint/typecheck command set. Iterate on the new tests until they
   pass; do not weaken tests to make them pass — fix the implementation
   or revert the test.
7. **Render the report** from `templates/test-generation-report.md`,
   including the run results.
8. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/test-generation-report.md`.
9. **Default handoff** to `validation-runner` for full validation, then
   to the test owner for review. Use the `handoff-packet` skill.

## Coverage checklist (per behavior)

Apply only the relevant items. If a behavior does not have auth (e.g. a
pure function), skip the auth case.

- happy path
- validation failure
- authentication failure (if endpoint / role-protected)
- authorization / ownership failure
- not-found behavior
- conflict / duplicate behavior (if stateful)
- persistence behavior (if stateful)
- external dependency failure (if it has any)
- boundary values
- regression case (a concrete prior bug or recently-changed behavior)

## Allowed Actions

- Create new test files inside the discovered test directories.
- Edit existing test files when adding cases to a file is the natural
  fit (e.g. adding a case to an existing `describe` / `class`).
- Read files anywhere under `REPO_ROOT`.
- Run the discovered validation commands via `validation-runner`.
- Create the report file under the task workspace.

## Forbidden Actions

- No new test framework, assertion library, or mocking library without
  explicit approval.
- No large E2E suites unless the task explicitly requests them and the
  repo already supports them.
- No changes to production code unless the task explicitly includes
  "make failing tests pass" — and even then, only the smallest change
  that makes the tests pass.
- No changes to package manager, module system, or build tool.
- No formatter runs that mutate code outside the new test files.
- No coverage instrumentation (no `nyc`, `coverage.py`, `jacoco`
  agent, etc. added to the build).

## Stop Conditions

- All listed behaviors have at least the relevant cases from the
  coverage checklist.
- `validation-runner` reports `passed` or `partial` for the targeted
  tests. A `failed` outcome stops the skill and creates a blocker.
- Report file exists at the canonical path.

## Outputs

- New or updated test files inside the repo.
- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/test-generation-report.md`
- An optional handoff packet via the `handoff-packet` skill.

## Handoff Contract

Receiving agents may rely on:

- `tests_added` — array of file paths
- `tests_modified` — array of file paths
- `behaviors_covered` — array of behavior strings
- `framework_used` — string
- `validation_outcome` — `passed | failed | partial | skipped`
- `next_skill` — default `validation-runner` for full validation

Receiving agents must not rely on:

- 100% behavior coverage — the report is honest about what was not
  covered and why.

## Validation

- `validation-runner` shows the new tests in the report's `commands` list
  with `passed` or `skipped` status (skipped only with a recorded
  reason).
- The generation report includes the `validation-runner` summary
  (commands run, pass/fail counts).
- No new files outside the discovered test directories (unless the
  report explicitly justifies a new directory).

## Completion Criteria

- Tests added, validation run, report written.
- Handoff packet prepared if any follow-up is needed.
