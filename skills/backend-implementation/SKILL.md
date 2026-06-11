# backend-implementation

Implement backend behavior safely using repository evidence, tests, and
validation. The skill produces the smallest change that satisfies the
acceptance criteria and fits the existing codebase.

## Purpose

Translate an approved plan (typically from a product spec, an
architecture review, or a code-review fix-up) into working backend code
that matches the existing repo's style, framework, and test
conventions, and passes validation.

## Trigger

- An accepted task spec needs implementation.
- A `code-review-report.md` or `security-review-report.md` lists fix-ups
  that need to land.
- A handoff packet's "Required next action" calls for implementation.

## Do Not Use When

- The repository has not been discovered — run `repo-discovery` first.
- The change is documentation-only or pure config.
- The change requires new dependencies, a new framework, a new
  database, or a new service topology — those need an architecture
  review (route to `ARCHITECT_AGENT`) and explicit approval.
- The change involves a destructive migration — use
  `database-migration-safety` first.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `ACCEPTANCE_CRITERIA` — list of criteria the implementation must meet
- `SCOPE` (optional) — module or directory to focus on
- `REVIEW_REPORTS` (optional) — list of `code-review-report.md` /
  `security-review-report.md` / `dependency-change-report.md` /
  `migration-safety-report.md` paths that constrain the change

## Preflight

- Read the `repo-discovery` report. If absent, abort.
- Read all `REVIEW_REPORTS` listed in inputs. The implementation must
  resolve every Critical/High finding in those reports.
- Identify the smallest impacted module / subtree before editing.
  Use the discovery report's `smallest_impacted_module` if it exists.
- Pick the language / framework profile that matches the detected
  evidence (see `references/profiles/`). If no profile fits, stop
  and create a blocker.
- Confirm `validation-runner` has produced a command set, or run
  detection.

## Workflow

1. **Plan.** Produce a short implementation plan as comments in the
   report: which files will change, in what order, with what tests.
   The plan must be the smallest safe change that satisfies
   `ACCEPTANCE_CRITERIA` and resolves any review findings.
2. **Add or update tests first** when feasible. Use `test-generation`
   to write the tests in the existing framework. Tests-first is not
   dogma — for purely structural changes, tests can come after — but
   the default is tests-first.
3. **Implement.** Make the smallest change that:
   - preserves the existing architecture, layering, naming, and style;
   - does not introduce a new dependency, framework, or build tool
     without explicit justification recorded in the report;
   - does not refactor unrelated code;
   - does not touch code outside `SCOPE` unless the change is
     strictly required (record why in the report).
4. **Run validation.** Use `validation-runner` to run the targeted
   command set. Iterate until `outcome: passed` or `partial` (with
   recorded reasons).
5. **Resolve review findings.** For each Critical/High finding in any
   `REVIEW_REPORTS`, the report must record what was changed to resolve
   it. Unresolved findings are blockers — stop and create a blocker
   via `task-state-management`.
6. **Render the report** from `templates/backend-implementation-report.md`.
7. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/backend-implementation-report.md`.
8. **Default handoff.** To `code-change-review` (or
   `security-review` for security-sensitive changes) via
   `handoff-packet`.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Create or modify files inside `SCOPE` (and adjacent files only when
  strictly required, recorded in the report).
- Run the discovered validation commands via `validation-runner`.
- Create the report file under the task workspace.

## Forbidden Actions

- No redesigning architecture without approval.
- No broad abstractions without current need.
- No destructive migrations.
- No changing dependency manager, build tool, or test framework.
- No new dependencies without explicit justification in the report
  (route to `dependency-change-review` first).
- No infrastructure changes (Docker, CI, IaC) unless explicitly
  requested.
- No marking work complete without `validation-runner` showing
  `passed` / `partial`, or a clear "validation limited because X"
  note in the report.
- No formatter runs that mutate code outside the files you changed.

## Stop Conditions

- All `ACCEPTANCE_CRITERIA` are met.
- All Critical/High findings in `REVIEW_REPORTS` are resolved (or
  re-classified to a lower severity with justification).
- `validation-runner` outcome is `passed` or `partial` (or a clear
  validation limitation is recorded).
- Report file exists at the canonical path.

## Outputs

- Modified source files (and tests) inside `REPO_ROOT`.
- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/backend-implementation-report.md`
- A handoff packet via the `handoff-packet` skill.

## Handoff Contract

Receiving agents may rely on:

- `files_changed` — list of paths
- `acceptance_criteria_met` — array of criteria + status
- `review_findings_resolved` — array of finding IDs + status
- `validation_outcome` — string
- `deviations` — array of deviations from the plan / profile, with
  reason
- `next_skill` — default `code-change-review`

Receiving agents must not rely on:

- The implementation being minimal beyond the documented scope (the
  report's `deviations` is the only honest list).

## Validation

- The report file exists and parses as markdown.
- `validation_outcome` is one of `passed | partial | failed | not_run`.
- If `validation_outcome` is `failed`, the report contains a blocker
  explanation.
- Every entry in `review_findings_resolved` references a finding from
  a `REVIEW_REPORTS` file.

## Completion Criteria

- Implementation done, tests pass (or partial with reason), report
  written, handoff prepared.
- The agent that triggered the change emits a one-line confirmation
  listing changed files.
