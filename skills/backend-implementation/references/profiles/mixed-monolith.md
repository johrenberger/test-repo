# Mixed-stack / monolith profile

Used by `backend-implementation` when the repo spans multiple stacks
(monorepo) or is a single repo with multiple language modules
(legacy monolith with a new service added in another language, etc.).

## When this profile applies

- A `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, or `turbo.json`
  is present (monorepo).
- Multiple top-level `pom.xml` / `build.gradle` / `go.mod` /
  `Cargo.toml` are present (multi-module).
- Different language stacks coexist (e.g. Java backend + Node
  frontend).
- A single binary embeds multiple runtimes (e.g. a Python ML model
  served by a Go API).

## Rules

### 1. Identify the impacted module first

Use `repo-discovery`'s `smallest_impacted_module` (or recompute it).
All changes must stay inside that module's subtree unless the change
is strictly cross-module, in which case the cross-module change is
recorded in the report with justification.

### 2. Use module-local build / test commands

- For monorepos: prefer the workspace's per-package test command
  over the root `test` command. The root command may run unrelated
  tests and increase iteration time.
- For multi-module Java: use the affected module's
  `./mvnw -pl <module> test` or `./gradlew :<module>:test`.
- For multi-module Node: run the affected package's test command
  (e.g. `pnpm --filter <pkg> test`).
- For Go: `go test ./<package>/...` for the affected package.

### 3. Avoid root-level config changes

Do not edit:

- root `package.json` (workspaces, scripts, devDeps)
- root `tsconfig.json` / `tsconfig.base.json`
- root `pyproject.toml` workspace settings
- root `pom.xml` / `build.gradle` (parent)
- root `Cargo.toml` workspace
- `nx.json`, `turbo.json`, `lerna.json`, `pnpm-workspace.yaml`
- root `Dockerfile`, `docker-compose.yml`
- `.github/workflows/*` (CI)

…unless the cross-module impact is proven and recorded in the report.

### 4. Avoid cross-module refactors

Do not refactor across modules unless the task explicitly requires
it. The smallest safe change in a mixed stack is almost always
"change only the impacted module."

### 5. Be explicit about cross-stack boundaries

If a change requires a contract change between modules (e.g. a new
field in a shared API), record the contract change in the report and
propose it as a separate decision-log entry. Do not silently change
contracts.

### 6. Test integration only at the boundary

If the change crosses a stack boundary (e.g. Java backend exposes a
new endpoint consumed by a TypeScript frontend), test the boundary
on the side that changed, not the consumer. The consumer's tests
are the consumer's responsibility.

## Forbidden

- Root-level config changes (see list above) without explicit
  justification and an architecture / security approval.
- Cross-module refactors without explicit task scope.
- Adding dependencies at the workspace root for a single-module
  need.
- Changing the package manager, build tool, or workspace orchestrator.

## Suggested report fields

Add these to the standard `backend-implementation-report.md`:

- `impacted_module` — path or module identifier
- `module_local_test_command` — exact command used for validation
- `cross_module_changes` — list of paths outside the impacted
  module, each with justification, or `none`
- `contract_changes` — list of API / event / schema contract
  changes, or `none`
