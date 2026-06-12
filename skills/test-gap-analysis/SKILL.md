# test-gap-analysis

Analyze the existing test surface of a repository and produce a
risk-weighted list of test gaps — without writing tests or modifying code.

## Purpose

Give any agent a defensible answer to "what's not tested, and what should
be tested next?" before deciding where to invest test-writing effort. The
output is a report consumed by `test-generation` and reviewed by the
test owner or the requesting agent.

## Trigger

- A new task is opened against an unfamiliar repo and the test posture
  needs to be characterized.
- A code change touches critical paths and the existing test coverage for
  the changed area is unknown.
- A handoff packet's "Required next action" calls for a test gap analysis.
- A periodic audit of test health is requested by the project coordinator.

## Do Not Use When

- The repository has not been discovered — run `repo-discovery` first and
  consume the resulting `repo-discovery.md`.
- The task is to add a specific known test (use `test-generation` directly).
- A current test-gap report exists for the same scope and the working tree
  has not materially changed — re-use the existing one.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `SCOPE` (optional) — file, module, or directory to focus the analysis on
- `CHANGED_FILES` (optional) — list of files changed in the current task,
  used to elevate "recently changed" risk weighting

## Preflight

- Read the `repo-discovery` report for this task. If absent, abort with an
  error pointing to the `repo-discovery` skill — never invent repo facts.
- Verify `TASK_ID` is set and matches `[a-z0-9][a-z0-9-]{0,63}`.
- Verify the output directory
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/` exists or can be
  created (`mkdir -p` is local and reversible).

## Workflow

1. **Inventory.** From the discovery report and filesystem, list every
   test file under the discovered test directories. Detect the framework
   per the `Test framework detection` table in
   `references/risk-weighting.md`. Record the inventory.

   **Build-directory exclusion (mandatory).** Files under `target/`,
   `build/`, `dist/`, `out/`, `node_modules/`, `.venv/`, `__pycache__/`,
   or any other build / dependency directory MUST be excluded from
   the test inventory. Build tools (Maven, Gradle, npm, pytest)
   generate stub files in these directories (e.g.
   `target/generated-sources/.../...Test.java`) that look like
   test files but are not source-controlled and not actually
   executed. Including them causes an agent to mis-classify a
   class as "tested" when only its generated stub exists.

   The exclusion list above is the minimum; if the discovery
   report names additional build / cache directories, exclude
   those too. The agent must record the exclusion list in the
   report's `## Provenance` section so the choice is auditable.
2. **Source ↔ test mapping.** For each source directory, list the
   corresponding test directory contents. Note modules that have no
   adjacent test files. Do not assert coverage percentages unless a real
   coverage artifact is present.
3. **Risk weighting.** For each module / behavior area, assign a risk
   weight from the `Risk weighting` table in `references/risk-weighting.md`.
   "Recently changed" code (from `CHANGED_FILES`) gets a +1 risk bump.
4. **Gap classification.** Classify each gap as one or more of:
   - unit test gap
   - integration / API test gap
   - contract test gap
   - regression test gap
   - security / negative test gap
5. **Avoid E2E/load/chaos recommendations** unless E2E infrastructure
   is detected in the repo. E2E infrastructure detection:
   - `playwright.config.{js,ts,mjs}` or `@playwright/test` in
     `package.json` dependencies → **playwright** detected
   - `cypress.config.{js,ts,mjs}` or `cypress/` directory →
     **cypress** detected
   - `k6` or `k6 run` in CI workflow files or scripts → **k6**
     detected
   - `locustfile.py` at repo root or in `tests/` → **locust**
     detected
   - `tests/e2e/`, `e2e/`, or `integration/` with non-unit test
     patterns (heavy fixtures, browser drivers) → **e2e** detected
     (low confidence; manual review required)
   - 0 of the above → "no E2E infrastructure detected" is the
     default; E2E/load/chaos recommendations must be **omitted
     from the report**, not downgraded

   When E2E infrastructure is detected, the report's `## E2E
   infrastructure` section lists each detected tool with the
   evidence file path. When none is detected, that section says
   "none detected" and E2E recommendations are omitted.
6. **Render the report** from `templates/test-gap-report.md`, including
   every required field from the task spec.
7. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/test-gap-report.md`.
8. **Default handoff.** Suggest `test-generation` next, with the test
   owner (typically the Test Automation agent) as the consumer.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Read coverage artifacts if present (e.g. `coverage/lcov.info`,
  `target/site/jacoco/jacoco.xml`, `coverage.xml`, `cobertura.xml`,
  `lcov.dat`). Do not generate them. Note: `target/site/jacoco/`
  is a build output and is excluded from the test inventory
  per Workflow step 1, but reading it as a coverage artifact
  is allowed.
- Create the report file under the task workspace.
- Run `scripts/lint-test-gap-report.py` (or any read-only linter)
  to validate the report before publishing.
- Print progress lines to stdout/stderr.

## Forbidden Actions

- No writing or modifying tests.
- No modifying application code.
- No adding coverage tooling or new test frameworks.
- No running tests (use `validation-runner` for that).
- No claiming a coverage percentage unless a real artifact or command
  output supports it. "Looks untested" is allowed; "73% covered" is not.
- No recommending E2E/load/chaos tests without evidence in the repo that
  such infrastructure is already in place.

## Stop Conditions

- The report file exists at the canonical path and includes every field
  from the task spec's report list.
- Every claimed gap is grounded in either an inventory observation (no
  test file adjacent to a source file) or a recent-change observation
  (file in `CHANGED_FILES` lacks a test).
- Confidence level is recorded for the report as a whole.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/test-gap-report.md`

## Handoff Contract

Receiving agents may rely on:

- `framework_detected` — array of detected test frameworks
- `existing_test_inventory` — list of test files with framework annotation
- `gaps` — array of `{area, risk, gap_type, recommended_test_type,
  evidence, files_likely_affected}`
- `confidence` — `low | medium | high`
- `validation_commands` — array of commands the `validation-runner` can use
- `follow_up_target` — agent name (default: `TEST_AUTOMATION_AGENT`)

Receiving agents must not rely on:

- A coverage % — this skill does not measure coverage.
- The specific files changed — only the `CHANGED_FILES` provided as input.

## Validation

- The report file parses as markdown and contains every required field.
- Every gap has a `risk` from the table in `references/risk-weighting.md`
  and a `recommended_test_type` from the gap classification list.
- `confidence` is one of `low | medium | high`. The confidence
  values are populated by the orchestrator based on:
  - `high` — multiple corroborating signals (e.g. a Maven plugin
    for the test framework + a `*Test.java` source file)
  - `medium` — a single strong signal (e.g. a `pytest.ini` alone)
  - `low` — inferred from convention (e.g. a `tests/` directory
    with no manifest, or a `*Spec.groovy` next to no Spock
    configuration)
- `scripts/lint-test-gap-report.py` is the canonical linter. It
  enforces the 10-rule contract (frontmatter, required sections,
  allowed risk / gap_type values, evidence, validation-command
  table, E2E recommendation, no fabricated coverage %, size
  sanity). Run it before publishing the report:
  `python3 scripts/lint-test-gap-report.py <report.md>`
  or `python3 scripts/lint-test-gap-report.py <reports-dir>`
  to lint a batch.
- The linter accepts a preflight-aborted marker (`# Test gap
  report (PREFLIGHT ABORTED)` plus an abort reason) as a valid
  alternative to a full report. Any other missing field is a
  failure.
- The linter also supports `--self-test` for the B6 exercise
  (5 fixtures under
  `/data/.openclaw/workspace/tasks/2026-06-12-test-gap-analysis-exercise/`).

## Helper scripts

- `scripts/lint-test-gap-report.py` — canonical linter. 10 rules
  (see docstring at the top of the file for the full list).
  Exit codes: 0 = pass, 1 = one or more reports failed,
  64 = bad usage. Read-only w.r.t. the repo and safe in any
  environment.

## Completion Criteria

- Report written, every required section populated.
- Follow-up handoff target is named explicitly, defaulting to
  `TEST_AUTOMATION_AGENT` unless the task scope dictates otherwise
  (e.g. a behavior gap might go to `SOFTWARE_ENGINEER_AGENT` instead).
