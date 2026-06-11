# Go profile

Used by `backend-implementation` when the repo is Go.

## Detection

- `go.mod` present
- `cmd/`, `internal/`, `pkg/` directories are common
- Framework: `gin`, `echo`, `chi`, `fiber`, `net/http` standard
  library, `grpc-go`
- Test helpers: `testify`, `gomock` (only if present)
- Migrations: `golang-migrate`, `goose`, `atlas` (only if present)

## Architecture

Preserve the existing package structure. Common patterns:

- `cmd/<binary>/main.go` — entry points
- `internal/<feature>/` — non-exported packages
- `pkg/<feature>/` — exported libraries
- `<feature>/<file>.go` — flat structure
- `api/`, `proto/` — API definitions
- `migrations/` — SQL migrations

Match the existing convention. Do not introduce a new layout.

## Test rules

- Standard `testing` package. Table-driven tests if the package
  already uses them.
- `testify/assert` / `testify/require` only if already present.
- `gomock` / `mockery` only if already present. Otherwise prefer
  hand-written fakes.
- `go test ./...` for full suite; `go test ./<pkg>` for targeted.
- Do not introduce `testify` if not present.

## Migration rules

- `golang-migrate`, `goose`, `atlas`: do not write destructive
  migrations. Use `database-migration-safety` first.

## Forbidden

- New module dependency without explicit justification and a
  `dependency-change-review` pass.
- New test framework, assertion library, or mocking library.
- Module path changes (`module` line in `go.mod`).
- `go get` for new dependencies unless strictly necessary and
  explicitly approved.
- `go mod tidy` sweeping changes.

## Concurrency

- Preserve the existing concurrency model. If the package uses
  channels, use channels. If it uses sync primitives, use those.
- Do not introduce goroutines where none existed unless the task
  specifically requires it.
