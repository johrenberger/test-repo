# Documentation source-of-truth table

Read on demand by
[`documentation-update`](../../SKILL.md) when identifying
which doc file to update for a given area. The table is a
**starting point**; the actual repo's layout and conventions
always win, and the discovery artifact is the source of
truth.

## When this reference applies

- The skill needs to decide which file is the
  source-of-truth for a doc area (README, API, setup,
  architecture, runbook, changelog).
- The repo's doc layout is unknown and the skill is
  searching for candidates.

## Default source-of-truth table

| Doc area | Default source-of-truth file | Convention |
| --- | --- | --- |
| Repo description, status | `README.md` at repo root | source-controlled |
| Setup / install / build / test | `README.md`, `CONTRIBUTING.md`, `Makefile`, `package.json` scripts | source-controlled |
| Per-package README | `<package>/README.md` | source-controlled |
| API — REST | `openapi.yaml`, `openapi.json`, `swagger.yaml`, or `docs/api/` | source-controlled; may be generated |
| API — GraphQL | `schema.graphql`, `*.gql` | source-controlled; may be generated |
| API — gRPC | `*.proto` | source-controlled; may be generated |
| Architecture decisions | `docs/adr/NNNN-*.md` or `docs/decisions/` | source-controlled |
| Architecture overview | `docs/architecture.md` or `ARCHITECTURE.md` | source-controlled; may be stale |
| Runbook / ops | `docs/runbooks/`, `runbooks/`, or `RUNBOOK.md` | source-controlled |
| Contributing | `CONTRIBUTING.md` | source-controlled |
| Code of conduct | `CODE_OF_CONDUCT.md` | source-controlled |
| License | `LICENSE` | source-controlled |
| Changelog | `CHANGELOG.md` | source-controlled; may be auto-generated |
| Release notes | `docs/releases/`, `releases/`, or per-tag notes | source-controlled |
| Onboarding | `docs/onboarding/`, `ONBOARDING.md`, or `README.md` "Getting started" | source-controlled |
| Setup / install scripts | `scripts/setup.sh`, `Makefile`, `package.json` scripts | source-controlled |
| Configuration reference | `docs/configuration.md`, `config.example.yaml`, `.env.example` | source-controlled |
| CLI reference | `docs/cli.md` or per-command help output | source-controlled; help output is canonical |
| Troubleshooting | `docs/troubleshooting.md`, `TROUBLESHOOTING.md`, or runbook | source-controlled |
| Security policy | `SECURITY.md` | source-controlled |
| Code comments | inline | only when the repo uses them as the source of truth |

## How to use

1. For each impacted doc area, find the row above.
2. Confirm the candidate file actually exists in the repo
   (cite the discovery artifact). If the file does not exist,
   the skill creates it in the expected location, or flags
   the gap in the documentation impact report.
3. If multiple candidates exist, the skill picks the one
   that is most authoritative by convention
   (e.g. `openapi.yaml` is the source of truth for the
   REST contract, not the README).
4. If no candidate exists in the default location, search
   the repo (e.g. `docs/`, `documentation/`, `wiki/`,
   `architecture/`).

## Common pitfalls

- **README is not a substitute for an API doc.** When the
  repo has `openapi.yaml`, the README's API examples are
  secondary; the source of truth is the spec.
- **Auto-generated docs are a special case.** When the repo
  has a code generator (e.g. `swagger-codegen`,
  `protoc-gen-doc`), the generated file is the source of
  truth; manual edits are lost on regeneration. Update the
  generator input, not the generated file.
- **Inline comments are not the source of truth** unless the
  repo has a documented convention that says otherwise (e.g.
  the code uses `///` doc-comments as the public API
  contract). When in doubt, the source of truth is the
  external doc file, not the inline comment.
- **Wiki / external docs are out of scope** for this skill.
  When the source of truth is an external system (Notion,
  Confluence, GitHub Wiki), the skill flags the doc as
  `out-of-scope` in the documentation impact report and
  routes the update to the human owner.
- **Architecture docs go stale faster than code.** Treat
  `docs/architecture.md` with suspicion; if a decision is
  recorded in an ADR, the ADR is the source of truth and the
  overview doc should link to it.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Report template:
  [`../templates/documentation-impact-report.md`](../templates/documentation-impact-report.md)
- README checklist:
  [`../templates/readme-update-checklist.md`](../templates/readme-update-checklist.md)
- API doc checklist:
  [`../templates/api-doc-update-checklist.md`](../templates/api-doc-update-checklist.md)
- ADRs: [`../../../architecture-decision/SKILL.md`](../../../architecture-decision/SKILL.md)
- Runbooks: [`../../../runbook-authoring/SKILL.md`](../../../runbook-authoring/SKILL.md)
