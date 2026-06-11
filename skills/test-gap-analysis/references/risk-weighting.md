# Risk weighting

Used by `test-gap-analysis` to assign risk to a behavior area, and by
`security-review` and `code-change-review` as a reference scale.

## Risk scale

| Level | Meaning |
| --- | --- |
| Critical | Failure causes data loss, auth bypass, or complete outage |
| High | Failure causes user-visible broken behavior on a primary path |
| Medium | Failure causes degraded behavior or a secondary path outage |
| Low | Failure causes a minor inconvenience or cosmetic regression |

## Risk dimensions

Apply each dimension independently. Sum or max-aggregate at your
discretion, but record the per-dimension result.

| Dimension | Critical if … | High if … |
| --- | --- | --- |
| Critical path behavior | The code is the primary user journey | The code is a common path |
| Auth / authz | The code is the only auth check | The code is one of multiple authz checks |
| Data persistence | The code writes a financial or identity record | The code writes a primary domain record |
| Error handling | The code swallows or misclassifies errors | The code has incomplete error handling |
| Boundary conditions | The code processes size or count limits | The code processes normal ranges |
| External integrations | The code is the only integration | The code is one of several |
| Concurrency / idempotency | The code is a distributed hot path | The code is single-process with shared state |
| Security-sensitive | The code handles secrets, sessions, or PII | The code is adjacent to a security boundary |
| Recently changed | The code changed in the current task | The code changed in the last 30 days |
| Low / missing coverage | The code has no test files adjacent | The code has only happy-path tests |

## Test framework detection

| Framework | Detector |
| --- | --- |
| JUnit 5 | `import org.junit.jupiter` or `junit-jupiter` in `pom.xml` / `build.gradle` |
| JUnit 4 | `import org.junit.Test` and not JUnit 5 |
| pytest | `pytest` in `pyproject.toml` / `requirements.txt` / `pytest.ini` |
| unittest | `import unittest` and no pytest |
| Jest | `jest` in `package.json` deps or `jest.config.*` |
| Vitest | `vitest` in `package.json` deps or `vitest.config.*` |
| Mocha | `mocha` in `package.json` deps |
| Go testing | `_test.go` files and `testing` import |
| xUnit | `xunit` in `.csproj` or `xunit.runner.visualstudio` |
| NUnit | `NUnit` in `.csproj` |
| MSTest | `MSTest.TestFramework` in `.csproj` |

If multiple are present, record all of them. Do not pick a "primary"
unless one is clearly dominant in the test directory listing.

## Gap classification

- **unit test gap** — isolated domain / service logic lacks direct tests
- **integration / API test gap** — endpoint or service boundary not
  exercised end-to-end against real collaborators
- **contract test gap** — external dependency has no pinned contract test
  (only relevant when contracts exist; do not invent)
- **regression test gap** — a previously-failing or recently-changed
  behavior has no test that would catch a regression
- **security / negative test gap** — auth/authz/injection/validation
  negative paths are untested

## When NOT to recommend E2E / load / chaos tests

Only recommend when:

- The repo already has E2E / load / chaos infrastructure (e.g.
  `playwright.config.*`, `k6/`, `locustfile.py`, `chaos-mesh`, etc.), AND
- The behavior area is in scope for that infrastructure.

If neither holds, the report must mark E2E/load/chaos as "not
recommended in this scope" with the reason.
