---
name: dependency-change-review
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- cloud-security-agent
- devops-agent
- security-analyst-agent
purpose: Read-only review of dependency, package manager, build file, and lockfile
  changes. Produces a ranked findings report with explicit recommendation on whether
  the change is acceptable.
---

# dependency-change-review

Read-only review of dependency, package manager, build file, and
lockfile changes. Produces a ranked findings report with explicit
recommendation on whether the change is acceptable.

## Purpose

Catch dependency drift, supply-chain risk, and unjustified dependency
additions before they land. The skill is the machine-readable first
pass; human review is required for any blocker finding.

## Trigger

- A change touches `package.json`, `package-lock.json`, `yarn.lock`,
  `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `requirements.txt`,
  `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `poetry.lock`,
  `uv.lock`, `pom.xml`, `build.gradle`, `build.gradle.kts`,
  `go.mod`, `go.sum`, `Cargo.toml`, `Cargo.lock`, `*.csproj`,
  `*.sln`, `Packages.json`, `Package.resolved`, `*.tf`,
  `Dockerfile`, `docker-compose*.yml`, or CI workflow files that pin
  action versions.
- A handoff packet's "Required next action" calls for dependency
  review.
- A `code-change-review` or `security-review` flags a dependency
  concern.

## Do Not Use When

- The change is pure code with no dependency / build / lockfile
  edits.
- The change targets runtime infrastructure not represented by the
  files above (route to `security-review` or DevOps review).
- The task is to perform the upgrade — this skill is read-only.

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `CHANGED_FILES` (optional) — explicit list of changed paths; if not
  provided, the skill derives the set from `git diff` for the working
  tree

## Preflight

- Resolve the changed-file set. If the set is empty, abort with "no
  dependency / build / lockfile changes to review."
- For each file, parse the diff and identify added, removed, and
  modified lines.
- Read the `repo-discovery` report to confirm the package manager
  and lockfile conventions.

## Workflow

1. **Inventory the change.** For each file in the set, list:
   - added dependencies (and their version)
   - removed dependencies
   - version changes (major / minor / patch)
   - lockfile regeneration
   - build-tool / plugin changes
   - workspace / monorepo manifest changes
2. **Classify each change** along the dimensions in
   `references/dependency-risk-checklist.md`.
3. **For added dependencies, check for:**
   - existing alternative in the project that satisfies the need
   - security / CVE history (record what was checked, but do not
     invent CVE numbers)
   - license compatibility (record the SPDX identifier if visible)
   - maintenance status (last release date, if visible)
4. **Check for:**
   - package manager drift (lockfile present for one manager, manifest
     for another)
   - lockfile consistency (lockfile matches manifest)
   - duplicate dependencies (two packages doing the same thing)
   - dev dependency placed in runtime, or vice versa
   - build-tool / plugin changes (record and require justification)
5. **Apply stop conditions** (see below). Any blocker stops the
   review and creates a blocker via `task-state-management`.
6. **Render the report** from
   `templates/dependency-change-report.md`.
7. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/dependency-change-report.md`.
8. **Default handoff.** If the change is approved, hand off to
   `code-change-review` for full review. If blocked, hand off to
   `ARCHITECT_AGENT` for the upgrade / migration decision.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Read the existing `repo-discovery` report and any
  `security-review-report.md` for the same task.
- Run `git diff` and `git log` to resolve the change set.
- Create the report file under the task workspace.

## Forbidden Actions

- No `npm install` / `yarn` / `pnpm install` / `pip install` /
  `poetry install` / `cargo add` / `dotnet add package` /
  `go get` / `bundle install`.
- No automatic upgrades.
- No package manager changes.
- No lockfile rewrites (other than recording what changed).
- No reading environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*`.

## Stop Conditions

- A major version upgrade is proposed for any runtime dependency →
  blocker, escalate to architecture.
- A package manager migration is proposed (e.g. `npm` → `pnpm`,
  `pip` → `poetry`, Maven → Gradle, etc.) → blocker, escalate.
- A dependency with known security risk is added → blocker, escalate.
- A production / runtime dependency is added without explicit
  rationale in the diff → blocker, escalate.
- For all other changes, the report is rendered and the review
  continues.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/dependency-change-report.md`
- An optional blocker file under the task workspace.
- An optional handoff packet via the `handoff-packet` skill.

## Handoff Contract

Receiving agents may rely on:

- `change_set` — list of changed files with summaries
- `findings` — array of `{change, category, severity, evidence,
  recommendation}`
- `outcome` — `approved | changes_requested | blocked`
- `blocker_filed` — boolean
- `escalation_target` — agent name if blocked

Receiving agents must not rely on:

- A clean review meaning the dependency is safe (the skill is a
  best-effort first pass; the project owner is responsible for
  license / CVE verification).

## Validation

- The report file exists and parses as markdown.
- Every changed file from the input set appears in the report.
- Every added dependency has a `license`, `latest_version_checked`,
  and `rationale` field (or `not_provided` with a one-line reason).
- `outcome` is one of `approved | changes_requested | blocked`.
- If any blocker was filed, `blocker_filed: true` and a blocker file
  exists.

## Completion Criteria

- Report written, outcome decided, blockers filed if needed.
- If `outcome` is `changes_requested` or `blocked`, the report names
  the follow-up target.
