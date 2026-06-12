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
  `/data/.openclaw/workspace/tasks/<TASK_ID>/validation/validation-report.md`.
  Must match the regex `[a-z0-9][a-z0-9-]{0,63}` (max 64 chars,
  lowercase, hyphens allowed). Nested exercise patterns are
  supported: `<exercise-id>/<scenario-id>` is valid as long as
  each segment individually matches the regex and the joined
  string is at most 64 chars. Example:
  `2026-06-12-validation-runner-exercise/val-s1-broadleaf-pom`.
- `REPO_ROOT` — absolute path to the repository being validated.
- `SCOPE` (optional) — file path or module to focus targeted validation on.
- `MODE` (optional) — `targeted` (default) or `full`.

## Preflight

- Verify `TASK_ID` matches the regex above and `REPO_ROOT` is set
  and is an existing directory.
- Run `scripts/detect_validation_commands.sh "$REPO_ROOT"` to enumerate
  available commands. If no commands are detected, stop and write a report
  that says validation cannot be run, with likely manual next steps.
- Do not execute any command that is not in the detected set.
- Ensure the output directory
  `/data/.openclaw/workspace/tasks/<TASK_ID>/validation/` exists or can be
  created.

## Environment variables

The runner uses shell-inherited environment variables when
executing validation commands. In particular:

- `PATH` — must include the directories for the build tools
  (e.g. `mvn`, `gradle`, `pytest`, `node`). The runner does
  **not** inherit `/etc/profile.d` content via `subprocess.run`,
  so agents must set `PATH` explicitly when invoking the runner
  from a non-interactive shell.
- `JAVA_HOME` — must point to a valid JDK for Maven / Gradle
  validation. The runner does not set this; the calling agent
  must export it. Recommended: `JAVA_HOME=/data/jdk21/jdk-21.0.5+11`
  (or the JDK version the repo requires).
- `MAVEN_HOME` (optional) — set to the Maven root for the
  required version. The runner uses `mvn` from `PATH` if
  present, falling back to the wrapper (`./mvnw`).
- `GITHUB_TOKEN` and similar secrets — the runner does **not**
  read or pass through any environment variable matching
  `*TOKEN*`, `*SECRET*`, `*KEY*`, `*PASSWORD*`, or `*CRED*`.
  Validation commands that need credentials must read them
  themselves; the runner will refuse to inject them.

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
   If any command is `trivial_pass`, set the report outcome to
   `partial` and add a warning bullet to `## Next steps` explaining
   which command(s) were trivial.
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
  - `passed` — every command exited 0 and at least one command did
    meaningful work
  - `partial` — every command exited 0, but at least one command was
    `trivial_pass` (no real work was done). The agent should treat
    this as a warning, not a failure.
  - `failed` — at least one command exited non-zero
  - `not_run` — no commands were detected (the report's `## Manual
    steps` section explains what to do)
- `commands` — array of `{id, command, exit_code, duration_ms, status}`
  - `status` per command: `passed` | `failed` | `trivial_pass` |
    `refused` | `skipped`
  - `trivial_pass` means the command exited 0 but a "no work done"
    pattern was detected (see "Trivial pass detection" below). The
    consumer can rely on this to surface the warning.
- `top_failures` — array of the first error line per failed command
- `next_steps` — array of suggested follow-ups

Receiving agents must not rely on:

- Coverage % — the runner does not compute coverage by default.
- Build success — the runner does not build; it tests/lints/typechecks.
- A test command that exited 0 — the runner may have downgraded the
  status to `trivial_pass` if no tests were run.

## Validation

- `bash -n` on both scripts must pass. This is enforced as a CI
  gate: any change to `scripts/detect_validation_commands.sh` or
  `scripts/run_validation.sh` triggers a `bash -n` check in the
  test-repo CI workflow; a non-zero exit blocks the PR.
- `detect_validation_commands.sh` must emit at least one line for any repo
  with a known manifest, and zero lines for an empty repo.
- A self-test on this repo (`test-repo`) must produce zero detected
  commands and a `not_run` outcome with a clear manual-steps list.
- `run_validation.sh` must downgrade a `mvn test` command with no real
  tests (log contains both "No tests to run" and "BUILD SUCCESS") to
  status `trivial_pass`, and a `mvn test` with no real sources
  ("No sources to compile" + "BUILD SUCCESS") to the same status. The
  overall report outcome in these cases must be `partial`, not
  `passed`.

## Multi-manifest warning

When `detect_validation_commands.sh` finds **two or more distinct
build manifests** in the same repo (e.g. `pom.xml` + `build.gradle`,
or `package.json` + `requirements.txt`), the report's `## Next steps`
section MUST include a warning bullet:

> **Multi-manifest repo detected:** `<list of manifests found>`. The
> validation runner will run each command independently. This usually
> indicates a half-baked or in-migration repo. Consider running
> validation manually to confirm which manifest is authoritative.

This warning is informational; the runner does not refuse to run
or downgrade the outcome. The agent should treat it as a flag to
investigate the repo state.

## Trivial pass detection

A test command that exits 0 but did no meaningful work is a real
failure mode that masks underlying problems (orphaned build files,
missing test sources, broken test infrastructure). The runner
inspects the captured log after the command finishes and downgrades
the status from `passed` to `trivial_pass` if any of these patterns
match:

- **Maven:** log contains both `No tests to run` and `BUILD SUCCESS`,
  OR both `No sources to compile` and `BUILD SUCCESS`.
- **Gradle:** log contains `BUILD SUCCESSFUL` but no occurrence of
  `test` or `spec` (case-insensitive).
- **pytest:** log contains `0 tests collected`, `collected 0 items`,
  or a summary line of `0 passed` with no failures.
- **Generic:** the log is under 100 bytes and contains no
  recognizable success pattern (`test`, `spec`, `pass`, `fail`,
  `build`, `error`).

The detection logic lives at the bottom of
`scripts/run_validation.sh` in the `detect_trivial_pass` function.
Adding a new pattern is a one-line edit; the runner does not need
to be re-installed or re-tested beyond the new pattern.

## Completion Criteria

- Report file exists, is non-empty, and matches the template.
- Every detected command appears in the report, even if skipped.
- The report includes a `next_steps` section with concrete actions.
