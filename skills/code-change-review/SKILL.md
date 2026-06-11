# code-change-review

Read-only review of local code changes — staged, unstaged, branch
diffs, or a specified set of files. Produces a ranked findings report
without modifying code.

## Purpose

Catch correctness, design, security, and maintainability issues in a
change before it reaches a human reviewer or merges. The skill is the
machine-readable first pass; a human reviewer is still required for
final sign-off.

## Trigger

- A `git diff` exists and a review is requested before merge.
- A handoff packet's "Required next action" calls for review.
- An agent wants a second opinion on a slice of code it just produced.

## Do Not Use When

- The change is documentation-only with no code impact (use the
  `documentation-agent` directly, no review needed).
- The change has not been finalized (still in draft / WIP). Review
  pre-final changes is allowed but the report must be flagged as
  `preliminary`.
- The change targets production infrastructure / secrets / runtime
  config — use `security-review` and `dependency-change-review` in
  addition to this one.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `MODE` — one of `diff-only | full-context | test-focused |
  security-focused | architecture-focused` (default: `diff-only`)
- `TARGET` — one of `staged | unstaged | branch:<name> | files:<list> |
  commit:<sha>` (default: `unstaged`)
- `CHANGED_FILES` (optional) — explicit list, overrides `TARGET` for
  file selection

## Preflight

- Verify `TASK_ID` and `REPO_ROOT` are set.
- Resolve the file set from `TARGET` / `CHANGED_FILES`. If the set is
  empty, abort with "no changes to review."
- Read the `repo-discovery` report if present — it tells you the
  test framework and language profile to use for style judgments.
- Read any existing `validation-runner` report for the same task;
  reference its outcome in the review.

## Workflow

1. **Resolve the diff.** From `TARGET` / `CHANGED_FILES`, build the
   list of changed files and the unified diff.
2. **Read the changed files end-to-end first.** This catches obvious
   issues without context drift.
3. **Inspect surrounding context** as needed. For each finding, capture
   the line range and a one-line "why" that points to the surrounding
   code.
4. **Apply the review categories** in
   `references/review-severity.md`. For each category, decide:
   - No finding.
   - Finding at the matching severity, with evidence.
5. **Rank findings** by severity (Critical → Nit). For every Critical
   and High finding, attach `evidence` (file:line, the actual code, and
   a one-line justification).
6. **Respect scope.** `diff-only` mode does not flag pre-existing
   issues. `full-context` mode may flag pre-existing issues but they
   must be tagged `pre-existing`.
7. **Cross-reference** any `validation-runner` report. If validation
   failed, the report must include a `validation_blocker` finding.
8. **Render the report** from `templates/code-review-report.md`.
9. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/code-review-report.md`.
10. **Default handoff.** If findings require code changes, hand off to
    `backend-implementation` (or the appropriate language profile) via
    the `handoff-packet` skill. Otherwise to the project coordinator for
    scheduling.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Run `git diff` and `git log` to resolve the file set and history.
- Read existing reports under the task workspace.
- Create the report file under the task workspace.

## Forbidden Actions

- No file modifications. The skill is read-only by default.
- No approval of changes that were not inspected (do not blanket-approve
  files outside the resolved set).
- No claiming validation passed without command output backing it.
- No blocking on subjective preferences alone — every finding must map
  to a documented category and severity.
- No style-only comments unless they materially affect maintainability
  or violate an explicit repo convention. A naming nit is acceptable; a
  formatting nit is not.
- No running tests, linters, or build tools (use `validation-runner`).

## Stop Conditions

- Every changed file has been read.
- Every finding has a category, a severity, and (for Critical/High)
  evidence with file and line range.
- The report file exists at the canonical path.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/code-review-report.md`
- An optional handoff packet via the `handoff-packet` skill.

## Handoff Contract

Receiving agents may rely on:

- `files_reviewed` — list of paths actually read
- `findings` — array of `{category, severity, file, lines, summary,
  evidence, recommended_action}`
- `outcome` — `approved | changes_requested | blocked`
- `preliminary` — boolean
- `validation_outcome` — string from the validation report (or `not_run`)

Receiving agents must not rely on:

- Findings outside the documented categories being absent (silence is
  not a guarantee; the review is best-effort).

## Validation

- The report file exists and parses as markdown.
- Every Critical/High finding has an `evidence` field with file:line.
- The `outcome` field is one of `approved | changes_requested | blocked`.
- The `files_reviewed` list is non-empty.

## Completion Criteria

- Report written, outcome decided, handoff prepared if needed.
- If `outcome` is `changes_requested` or `blocked`, the report names the
  follow-up target.
