# Go — testing profile

Used by `test-generation` when the repo is Go. There is exactly one
testing framework — the standard `testing` package — but several
conventions are common.

## Detection

- `go.mod` present
- `*_test.go` files anywhere
- `testify` in `go.mod` for assertion / mock helpers (optional)

## Test layout

- `<file>_test.go` in the same package as `<file>.go`
- `internal/<pkg>/<file>_test.go` for internal packages
- Integration tests sometimes live in a separate `tests/` package or
  use build tags (`//go:build integration`)

## Style rules

- **`testing.T` for tests, `testing.B` for benchmarks, `testing.M` for
  TestMain.** Do not introduce a different framework.
- **Table-driven tests** are the Go idiom. If the package's existing
  tests use a table, follow it. If they don't, you can introduce one
  for the new tests, but match the surrounding style.
- **Assertions:** if `testify/assert` or `testify/require` is already
  used, use it. Otherwise use plain `if got != want { t.Errorf(...) }`.
  Do not introduce testify.
- **Mocks:** if `testify/mock` or `gomock` is already used, follow it.
  Otherwise use simple hand-written fakes — Go interfaces make this
  natural.
- **Test naming:** `TestFunctionName` or `TestFunctionName_scenario`.
  Match the existing style.

## Coverage checklist mapping

| Case | Go idiom |
| --- | --- |
| happy path | `if got != want { t.Errorf(...) }` |
| validation failure | expect a specific error with `errors.Is` / `errors.As` |
| auth failure | inject a fake auth interface that returns the failure |
| not-found | expect `ErrNotFound` (or repo-specific sentinel) |
| conflict | expect `ErrConflict` |
| persistence | assert the fake store was called with the right args |
| boundary | table-driven with edge values |
| regression | `// Regression: <link or issue>` comment |

## Forbidden

- `testify` introduction if not present.
- `gomock` / `mockery` introduction if not present.
- Changing `go.mod` for test purposes.
- Module path changes.

## Example skeleton (table-driven)

```go
package orders

import (
    "errors"
    "testing"
)

func TestGetOrder(t *testing.T) {
    tests := []struct {
        name    string
        id      string
        want    *Order
        wantErr error
    }{
        {"exists", "123", &Order{ID: "123"}, nil},
        {"not found", "missing", nil, ErrNotFound},
        {"empty id", "", nil, ErrInvalidID},
    }
    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got, err := GetOrder(tc.id)
            if !errors.Is(err, tc.wantErr) {
                t.Fatalf("err: got %v want %v", err, tc.wantErr)
            }
            if !equalOrder(got, tc.want) {
                t.Errorf("got %+v want %+v", got, tc.want)
            }
        })
    }
}
```
