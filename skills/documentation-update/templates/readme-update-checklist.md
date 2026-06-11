# README update checklist

Read on demand by
[`documentation-update`](../../SKILL.md) when a README is
being updated. The checklist is applied per-section and the
results are summarized in the documentation impact report.

## When this checklist applies

- The repo has a `README.md` at the root (or per-package
  READMEs).
- A change touches any of the README's responsibilities:
  description, setup, build, test, run, contribute, license,
  status, etc.

## Sections to check

### Title and one-liner

- [ ] Title still matches the repo / package purpose.
- [ ] One-liner describes the current state, not the planned
  state.
- [ ] Status badge (when present) reflects the current state.

### Description

- [ ] Description matches the actual scope.
- [ ] Out-of-scope areas are still described as out of scope
  (e.g. "this repo does not contain the runtime").
- [ ] No marketing claims that cannot be backed by code or
  evidence.

### Setup / prerequisites

- [ ] Required tool versions match the actual repo
  requirements (cite `package.json`, `pyproject.toml`,
  `go.mod`, `Cargo.toml`, `Dockerfile`, etc.).
- [ ] OS / platform assumptions are explicit.
- [ ] Required environment variables are listed with redacted
  values (`<REDACTED: kind>`), not real values.
- [ ] Required credentials / tokens are described as
  required, not committed.

### Install

- [ ] Install commands match the actual install path
  (validated by `validation-runner` when feasible).
- [ ] No installer references for tools the repo does not use.
- [ ] When the repo has a Makefile / npm scripts / task
  runner, the README points to it rather than duplicating.

### Build

- [ ] Build command matches the actual build path.
- [ ] Build artifacts and their locations are accurate.
- [ ] Build flags / options are documented when the build
  supports them.

### Test

- [ ] Test command matches the actual test path.
- [ ] Test framework matches the actual framework
  (Jest, Vitest, JUnit, pytest, go test, etc.).
- [ ] Coverage / lint / typecheck commands are documented
  when the repo enforces them.

### Run

- [ ] Run command matches the actual run path.
- [ ] Default port / URL is documented when applicable.
- [ ] Required config files are listed.
- [ ] Stop / shutdown command is documented.

### Project layout

- [ ] Layout diagram matches the actual directory structure.
- [ ] Each top-level directory is described with one line.
- [ ] Per-package READMEs are linked when applicable.

### Conventions

- [ ] Naming conventions still match.
- [ ] Branch / commit / PR conventions are described when
  the repo enforces them.
- [ ] The "do not modify" rules (e.g. "do not commit
  secrets") are present when applicable.

### Contributing

- [ ] Contribution process matches the actual repo workflow.
- [ ] Required checks (CI, lint, test) are listed.
- [ ] Code-of-conduct link is present when applicable.

### License

- [ ] License is named correctly.
- [ ] License file is referenced (not duplicated).

### Status / roadmap

- [ ] Status section reflects the current state (e.g.
  "Foundation skills exist").
- [ ] Roadmap items that are now done are moved out of the
  roadmap, or annotated as done.

## Validation

- [ ] Every command in the README is validated by
  [`validation-runner`](../validation-runner/SKILL.md) or
  flagged as not validated.
- [ ] Every example output is current.

## Handoff checklist

- [ ] Documentation impact report entry is written for the
  README change.
- [ ] The handoff packet lists the README file in
  `docs_updated`.
- [ ] If the README contradicts another doc area, the
  contradiction is recorded in
  `documentation-impact-report.md`.

## Red flags

- README contains commands that are not in the actual build /
  test / run paths.
- README contains example values that look like real
  credentials.
- README claims the repo is at a maturity or version that
  the code does not match.
- README duplicates information that is better sourced
  from a single source of truth.
