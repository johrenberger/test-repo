# repo-discovery

Identify the language, framework, build system, test setup, and risk zones of
a repository from filesystem evidence alone. Produces a deterministic
discovery report that downstream skills and agents can act on without
re-scanning.

## Purpose

Give any agent a fast, evidence-backed answer to "what is this repo, what
runs it, and where would my change land?" before committing to a plan.

## Trigger

- A task is opened and the requesting agent does not already know the repo's
  primary stack or test entry points.
- An agent is handed a path that has not been discovered yet.
- A scope is provided (a file, symbol, or subtree) and the smallest impacted
  module needs to be identified.

## Do Not Use When

- The repo has not been cloned locally (the skill reads the filesystem).
- The task is a pure documentation or non-code change with no impact on
  build/test paths.
- A current `repo-discovery.md` already exists for the task and the working
  tree has not materially changed — re-run only when the report is stale or
  missing.

## Required Inputs

- `TASK_ID` — the task identifier; used to write the report to
  `/data/.openclaw/workspace/tasks/<TASK_ID>/discovery/repo-discovery.md`.
- `REPO_ROOT` — absolute path to the repository being discovered.
- `SCOPE` (optional) — file path, symbol, or directory used to identify the
  smallest impacted module/subtree.

## Preflight

- Verify `REPO_ROOT` exists and is a directory.
- Verify the parent of the output directory exists or can be created
  (`mkdir -p` is allowed because it is local and reversible).
- If `TASK_ID` is unset, abort with an explicit error — never write to a
  generic location.

## Workflow

1. Run `scripts/detect_project_stack.sh "$REPO_ROOT"` to enumerate languages,
   frameworks, package managers, build files, source dirs, test dirs, CI
   files, Docker/IaC files, and migration tools.
2. Run `scripts/detect_test_commands.sh "$REPO_ROOT"` to derive the test,
   lint, typecheck, and coverage commands available, with detected
   confidence.
3. Determine repository shape: single-app, multi-module, monorepo, or
   mixed stack. The detection logic in `detect_project_stack.sh`
   walks 1 level into top-level subdirs and counts modules with
   their own build manifests. The orchestrator does not need to
   replicate this walk.
   - presence of `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`
     → monorepo
   - 2+ top-level subdirs with their own `pom.xml` / `build.gradle` /
     `go.mod` / `Cargo.toml` → multi-module
   - single project file and no workspace manifest → single-app
   - mixed (e.g. Node frontend + Go backend) → mixed stack
   - 0 manifests at all but the repo has files → single-app
     (this includes the markdown-only case for this repo itself;
     the script's `.md` fall-back emits `primary_stack::markdown`)
4. If `SCOPE` is provided, walk up from the scoped path to the nearest module
   root and record it as the smallest impacted module.
5. Render the report from `templates/repo-discovery-report.md`, filling in
   detected values and listing anything that was not found as
   `not_detected`.
6. Write the report to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/discovery/repo-discovery.md`.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Create the discovery output directory tree under
  `/data/.openclaw/workspace/tasks/<TASK_ID>/discovery/`.
- Print evidence lines to stdout/stderr from scripts.

## Forbidden Actions

- No `npm install`, `yarn install`, `pnpm install`, `pip install`, `mvn`,
  `gradle`, `go build`, `cargo build`, or any dependency installation.
- No `git push`, no network calls beyond reading the local filesystem.
- No modification of files inside `REPO_ROOT`.
- No execution of project tests, linters, or build tools.
- No access to environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*`.
- No deletion of any file.

## Stop Conditions

- All required sections of the report are populated or marked `not_detected`.
- If `REPO_ROOT` is missing or unreadable, stop and report the failure
  instead of writing a partial report.
- If both scripts return no signals, stop and report the repo appears empty
  or unreadable; do not invent values.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/discovery/repo-discovery.md` —
  the full discovery report (see template).
- A short summary line printed to stdout: detected stack, repo shape,
  smallest impacted module (if `SCOPE` given).

## Handoff Contract

Receiving agents may rely on:

- `repo_layout` — single-app | multi-module | monorepo | mixed
- `primary_stack` — array of detected language/framework pairs
- `test_commands` — array of `{command, confidence, source}` entries
- `risk_zones` — array of detected risky areas (auth, secrets, migrations)
- `smallest_impacted_module` — path string or `null`

Receiving agents must not rely on:

- Build success — this skill never builds.
- Test pass/fail — this skill never runs tests.
- Code correctness — this skill reads manifests and filenames only.

## Validation

- `bash -n` on both detection scripts must pass.
- `python3 scripts/lint-repo-discovery-report.py --self-test` must pass.
  The linter checks the report's frontmatter, required sections, and
  forbids fabricated values (Evidence column must be a real file path).
- The report file must exist after the skill runs and must contain all
  template sections.
- A self-test on a known repo (e.g. this repo itself) must produce
  `primary_stack: markdown` and `repo_layout: single-app` (this repo has no
  build files).

## Helper scripts

- `scripts/detect_project_stack.sh` — read-only stack detection. Emits
  `kind::value::source` lines. Covers JVM (Maven/Gradle), Node, Python,
  Go, Rust, .NET, Docker, IaC, CI, migrations, and risk zones.
  Multi-module detection walks 1 level into top-level subdirs and
  emits `layout::multi-module` when 2+ sub-modules have manifests.
  Markdown fall-back: emits `primary_stack::markdown` when no manifests
  are present but `*.md` files exist (Finding 4, A1 exercise).
  Node test-dir gate: suppresses false-positive `test_dir::node` when
  no `package.json` and no JS/TS files are present (Finding 2, A1
  exercise).
- `scripts/detect_test_commands.sh` — read-only test-command detection.
  Emits `command_id::command_string::source::confidence` lines.
  `pytest.ini` is treated as a high-confidence source (Finding 5,
  A1 exercise).
- `scripts/lint-repo-discovery-report.py` — 10-rule linter for the
  report. Three invocation modes: single file, directory, `--self-test`.
  Exit codes: 0 (pass), 1 (failure), 64 (bad usage). Read-only
  with respect to the repo.

## Completion Criteria

- Report written to the canonical path.
- All detected values cite the file path they came from (evidence).
- `not_detected` fields are honest — no fabrication when a signal is missing.
