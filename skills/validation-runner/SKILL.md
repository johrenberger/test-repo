# validation-runner

Run safe, evidence-discovered local validation commands and produce a
structured report. Prefers targeted validation (lint, typecheck, focused
tests) over full suite execution.

## Purpose

Give any agent a single, well-defined way to validate a change before
handing it off — without installing dependencies, modifying files, or
accessing secrets.

## Trigger

- A code change is complete and the agent needs evidence it does not
  regress existing behavior.
- A handoff packet's "Required next action" calls for validation.
- A new module or language is being added to a repo and the available
  command set is unknown.

## Do Not Use When

- The task is documentation-only with no code change.
- The repo has not been discovered yet — run `repo-discovery` first.
- The required validation requires network access, credentials, or a
  staging environment (this skill is local-only and read-only-by-default).

## Required Inputs

- `TASK_ID` — used for the report path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/validation/validation-report.md`
- `REPO_ROOT` — absolute path to the repository being validated.
- `SCOPE` (optional) — file path or module to focus targeted validation on.
- `MODE` (optional) — `targeted` (default) or `full`.

## Preflight

- Verify `TASK_ID` and `REPO_ROOT` are set and valid.
- Run `scripts/detect_validation_commands.sh "$REPO_ROOT"` to enumerate
  available commands. If no commands are detected, stop and write a report
  that says validation cannot be run, with likely manual next steps.
- Do not execute any command that is not in the detected set.
- Ensure the output directory
  `/data/.openclaw/workspace/tasks/<TASK_ID>/validation/` exists or can be
  created.

## Workflow

1. **Detect.** Run `scripts/detect_validation_commands.sh` to produce the
   available command set with confidence levels.
2. **Select.** For `targeted` mode, prefer in this order: lint, typecheck,
   focused test (if `SCOPE` given), full test, coverage. For `full` mode,
   run the entire detected command set in the order below.
3. **Run.** Execute each selected command via `scripts/run_validation.sh`,
   which captures exit code, stdout, stderr, and elapsed time. Commands
   run in a working directory of `REPO_ROOT`. Network access is not
   required and is not made.
4. **Stop on hard failure in `targeted` mode** when a high-confidence
   command fails. Soft warnings (lint warnings with non-zero exit by
   config) are recorded but do not stop the run.
5. **Render** the report from `templates/validation-report.md`, including
   each command, its exit code, top-of-output excerpt, and a summary.
6. **Write** the report to the canonical path. Do not modify any file
   inside `REPO_ROOT`.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Execute the detected validation commands listed in the **Supported
  commands** table.
- Create the report file under the task workspace.
- Print progress lines to stdout/stderr.

## Forbidden Actions

- No package installation (`npm install`, `pip install`, `mvn dependency:*`,
  `go mod tidy`, `cargo update`, `dotnet restore` of new packages, etc.).
- No file modification in `REPO_ROOT` (no `git commit`, no `git push`, no
  file rewrites, no `sed -i`, no formatter runs that mutate code).
- No deployment, no network calls beyond reading local manifests.
- No access to environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*`.
- No execution of arbitrary commands — only the detected set.
- No backgrounding or daemonization.

## Supported commands

| Command | When detected |
| --- | --- |
| `npm test` | `package.json` present and `test` script declared |
| `npm run lint` | `lint` script declared |
| `npm run typecheck` | `typecheck` / `type-check` / `tsc` script declared |
| `yarn test` | `yarn.lock` present |
| `pnpm test` | `pnpm-lock.yaml` present |
| `mvn test` | `pom.xml` present and `mvnw` not present |
| `./mvnw test` | `mvnw` present |
| `gradle test` | `build.gradle` present and `gradlew` not present |
| `./gradlew test` | `gradlew` present |
| `pytest` | `pytest` config or `conftest.py` present |
| `go test ./...` | `go.mod` present |
| `cargo test` | `Cargo.toml` present |
| `dotnet test` | a `*.sln` file is present |

If a command is requested that is not in the detected set, the runner
reports "command not available in this repo" and skips it.

## Stop Conditions

- All selected commands have completed (success, failure, or skipped).
- A report exists at the canonical path even if zero commands ran.
- A hard failure in `targeted` mode produces a report with `outcome:
  failed` and stops further commands in the same run.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/validation/validation-report.md`
  — full per-command report
- A one-line summary printed to stdout:
  `<commands_run>/<commands_total> passed, <failed> failed, <skipped> skipped`

## Handoff Contract

Receiving agents may rely on:

- `outcome` — `passed` | `failed` | `partial` | `not_run`
- `commands` — array of `{id, command, exit_code, duration_ms, status}`
- `top_failures` — array of the first error line per failed command
- `next_steps` — array of suggested follow-ups

Receiving agents must not rely on:

- Coverage % — the runner does not compute coverage by default.
- Build success — the runner does not build; it tests/lints/typechecks.

## Validation

- `bash -n` on both scripts must pass.
- `detect_validation_commands.sh` must emit at least one line for any repo
  with a known manifest, and zero lines for an empty repo.
- A self-test on this repo (`test-repo`) must produce zero detected
  commands and a `not_run` outcome with a clear manual-steps list.

## Completion Criteria

- Report file exists, is non-empty, and matches the template.
- Every detected command appears in the report, even if skipped.
- The report includes a `next_steps` section with concrete actions.
