# documentation-update

Identify and update documentation impacted by code, API,
architecture, configuration, deployment, or workflow changes.
The skill is **evidence-driven** — it documents what the repo
actually does, not what someone wishes it did.

## Purpose

Keep documentation aligned with the repo so that:

- API docs match the actual API contract;
- README and onboarding docs match the actual setup / build /
  test / run commands;
- architecture docs (ADRs, design notes) match the implemented
  design;
- runbooks match the actual operational behavior;
- changelog / release notes summarize what actually changed.

The skill produces a documentation impact report even when no
docs are changed, so the next agent or human reviewer can see
what was considered.

## Trigger

Use when:

- APIs change
- Configuration changes
- Setup / build / test / run commands change
- Architecture decisions are made
- Deployment / release process changes
- User-facing behavior changes
- README / runbook / onboarding docs are stale
- Another agent or skill requests a documentation handoff
- Release-readiness identifies documentation as a blocker

## Do Not Use When

- The task is pure implementation with no external behavior,
  workflow, or operational change — out of scope.
- The source of truth for the relevant doc is unknown and no
  repo discovery is available — stop and request clarification.
- The task is purely formatting or typo fixing with no
  semantic change — small enough to skip the workflow and edit
  directly; record the change in a doc-impact report anyway.
- The task is a one-line change to a doc the skill did not
  introduce — use a regular code / doc PR instead.

## Required Inputs

- **Task description** — what changed (or is changing) and
  why.
- **Acceptance criteria** — what "doc is up to date" means for
  the task.
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`.
- **Change set** — diff, branch, PR, or list of files changed.
- **Prior review / decision artifacts** —
  `architecture-decision` ADRs, `architecture-review-report.md`,
  `code-change-review-report.md`, `release-readiness-report.md`
  if any of these document the change.
- **Doc source-of-truth** — known preferred sources (see
  [`references/doc-source-of-truth.md`](references/doc-source-of-truth.md)).

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; the skill must not invent repo
   facts.
2. Confirm the change set is attached. A documentation update
   without a concrete change is not useful.
3. Identify the source of truth for each doc area
   (`references/doc-source-of-truth.md` provides a default
   table; the repo's actual layout may differ).
4. Confirm the doc updates are in scope. If the doc is
   published externally and the task requires publication, stop
   and request operator / product approval; this skill does
   not publish.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the relevant modules, doc files, and config files
   are identified.

2. **Identify documentation sources.** For each impacted area
   (API, setup, architecture, deployment, runbook, etc.),
   list the candidate doc files. Use
   [`references/doc-source-of-truth.md`](references/doc-source-of-truth.md)
   as a starting point, but the repo's actual layout wins.

3. **Determine update vs flag-only.** For each candidate doc:

   - **Update** when the doc is the source of truth (or a
     source-controlled manual doc) and the change is concrete.
   - **Flag only** when the doc is auto-generated and the
     repo's convention is to commit generated files, but
     regeneration is not in scope; the flag goes in the
     documentation impact report.
   - **Out of scope** when the doc is published externally or
     is purely marketing / product copy; the flag goes in the
     report for the human owner.

4. **Update docs.** For each `update` doc:

   - Match the existing format and style.
   - Cite the change in the doc when the repo's convention is
     to link to ADRs / PRs / issues.
   - Validate code examples and commands when feasible through
     [`validation-runner`](../validation-runner/SKILL.md) or
     repo evidence. Do not invent commands.
   - Do not duplicate existing content; link to the source
     of truth instead.

5. **Flag-only items.** For each `flag-only` doc, write the
   flag in the documentation impact report; the next agent or
   human owner can decide.

6. **Validate the doc set.** Cross-check the doc set for
   contradictions:

   - README and `docs/` cover the same surface area.
   - API doc matches the OpenAPI / GraphQL / schema.
   - Setup commands match the actual scripts / Makefile /
     `package.json` / `pyproject.toml` / etc.
   - Runbook commands match the actual operational steps
     (cite `runbook-authoring` for runbook updates).

7. **Produce the documentation impact report.** Use
   [`templates/documentation-impact-report.md`](templates/documentation-impact-report.md).
   Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/documentation-impact-report.md`.

8. **Hand off.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to the next
   skill. The packet lists which docs were updated, which
   were flagged, and any blockers.

## Allowed Actions

- Read repo files, including all candidate doc files.
- Run `repo-discovery` scripts (read-only).
- Run `validation-runner` to validate code examples in docs
  (when feasible).
- Edit markdown / doc files within the repo.
- Update examples and command references in docs.
- Add links to ADRs, reports, and other source-of-truth
  artifacts.
- Update API docs only when the repo stores them as
  source-controlled files.
- Update changelog / release notes when the repo has a
  changelog convention.
- Write the documentation impact report and handoff packet.

## Forbidden Actions

- **Do not modify application code.** Doc updates only.
- **Do not invent behavior not supported by code or accepted
  requirements.** Documentation must reflect the actual system.
- **Do not duplicate docs when a source of truth exists.**
  Link to the source instead.
- **Do not update generated files** unless the repo convention
  is to commit them. When the convention is to commit
  generated files, regenerate from the source rather than
  editing by hand.
- **Do not publish externally.** The skill updates
  source-controlled docs; it does not push to a public
  website or external doc host.
- **Do not change code to make a doc easier to write.** Update
  the doc to match the code, not the other way around.
- **Do not introduce new doc tooling** (a new static-site
  generator, a new doc linter) as part of a doc update.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- The documentation source of truth is unclear and the
  doc-area owner cannot be identified.
- The doc updates require product, legal, or security approval
  (e.g. public-facing docs that include sensitive internal
  details).
- The change is a doc-only change that contradicts a
  documented decision; the decision must be updated first via
  `architecture-decision` or the appropriate review skill.
- The change requires code changes to make the doc accurate;
  the implementation skill must run first, then the doc
  update.

## Outputs

- **Doc edits** — markdown / doc files within the repo.
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/documentation-impact-report.md`**
  — see
  [`templates/documentation-impact-report.md`](templates/documentation-impact-report.md).
- **Handoff packet** to the next skill (often a reviewer or
  release-readiness).

## Handoff Contract

Fields the receiving skill may rely on:

- `impact_report_path` — absolute path to the impact report
- `docs_updated` — list of `path:reason` for docs that were
  edited
- `docs_flagged` — list of `path:reason` for docs that were
  flagged as needing owner action
- `docs_out_of_scope` — list of `path:reason` for docs that
  this skill refused to touch (external, generated, etc.)
- `contradictions_found` — list of contradictions between doc
  areas, or `none`
- `validation_evidence` — list of validated commands /
  examples, or `none`
- `outstanding_questions` — list of items needing owner
  input, or `none`

Fields the receiving skill must not rely on:

- "docs are up to date" — the report records what was
  considered; it does not claim completeness.
- "approved" — the doc update is a change, not an approval.
- "no public-facing impact" — public-facing impact is
  asserted by the human owner, not by this skill.

## Validation

The documentation update is "validated" when:

1. The impact report covers all candidate doc areas
   (update / flag-only / out-of-scope for each).
2. Every updated doc cites the change it documents.
3. Code examples and commands are validated by
   [`validation-runner`](../validation-runner/SKILL.md) when
   feasible, or explicitly flagged as not validated.
4. No content was invented that is not supported by code or
   accepted requirements.
5. The handoff packet has all 14 required fields.

The skill itself runs no shell commands; it may invoke
`validation-runner` to validate example commands.

## Completion Criteria

- All impacted doc areas are classified (update / flag-only /
  out-of-scope).
- Updates are written in the same style and format as the
  existing docs.
- Code examples and commands are validated when feasible.
- The documentation impact report is complete.
- A handoff packet is produced and the next skill accepts
  it.
- The task's `state.json` reflects the doc-update outcome.

## Cross-references

- Decisions: [`architecture-decision`](../architecture-decision/SKILL.md)
- Architecture audits: [`architecture-review`](../architecture-review/SKILL.md)
- Release: [`release-readiness`](../release-readiness/SKILL.md)
- Runbook updates: [`runbook-authoring`](../runbook-authoring/SKILL.md)
- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Reference:
  [`references/doc-source-of-truth.md`](references/doc-source-of-truth.md)
- Templates:
  [`templates/documentation-impact-report.md`](templates/documentation-impact-report.md),
  [`templates/readme-update-checklist.md`](templates/readme-update-checklist.md),
  [`templates/api-doc-update-checklist.md`](templates/api-doc-update-checklist.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
