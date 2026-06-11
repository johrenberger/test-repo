# Frontend implementation report

Output of the
[`frontend-implementation`](../../../../skills/frontend-implementation/SKILL.md)
skill. Records the target module, framework profile, files
changed, tests added, and validation outcome for a frontend-only
implementation task.

## Task

- **Task ID:** <TASK_ID>
- **Implementation skill:** `frontend-implementation`
- **Generated at:** <ISO-8601>

## Acceptance criteria

<bullet list of testable conditions. If acceptance criteria are
unclear, the implementation skill must stop and file a blocker;
do not invent criteria here.>

## Inputs received

- **Task description:** <path or text>
- **Routing report (if via orchestrator):** <absolute path or
  `none — direct invocation`>
- **Discovery artifact:** <absolute path to
  `discovery/repo-discovery.md` or `none`>
- **API contract version targeted:** <version / commit / `n/a`>

## Framework profile

Exactly one of:

- `react` — see [`references/profiles/react.md`](../../../../skills/frontend-implementation/references/profiles/react.md)
- `angular` — see [`references/profiles/angular.md`](../../../../skills/frontend-implementation/references/profiles/angular.md)
- `vue` — see [`references/profiles/vue.md`](../../../../skills/frontend-implementation/references/profiles/vue.md)
- `nextjs` — see [`references/profiles/nextjs.md`](../../../../skills/frontend-implementation/references/profiles/nextjs.md)
- `static-ui` — see [`references/profiles/static-ui.md`](../../../../skills/frontend-implementation/references/profiles/static-ui.md)

If none match, the skill stops and the report records the
mismatch as a blocker.

## Detection evidence

Cite concrete files / lines that justify the profile choice:

- `package.json` or equivalent — <package lines>
- Entry point — <file>
- Routing setup — <file>
- Styling approach — <file>
- State management — <file>
- Test framework — <file>
- Build / dev command — <command>

## Target module(s) and changes

| File | Action (added / modified / deleted) | Reason |
| --- | --- | --- |
| <file> | added | <one line> |
| <file> | modified | <one line> |

List frontend files only. Backend, integration, and infra
changes are out of scope and must be routed to the orchestrator.

## Out of scope (not touched)

- <file or area> — reason: <one line, e.g. "backend, routed to
  `backend-implementation`">
- Or `none`.

## Tests added or updated

| File | Test framework | Type (unit / component / a11y / E2E) | Notes |
| --- | --- | --- | --- |
| <file> | Jest / Vitest / TestBed / etc. | <type> | <one line> |

If no tests added, the report must justify why (e.g. trivial
styling-only change).

## Accessibility checks

- [ ] Semantic HTML / ARIA roles preserved or added
- [ ] Keyboard navigation preserved or added
- [ ] Color contrast / focus management considered
- [ ] A11y test (axe / a11y API) added if repo already has one
- Or `n/a — task is not a UI change`

## Validation

- **Tool used:** [`validation-runner`](../../../../skills/validation-runner/SKILL.md)
- **Command(s) discovered:** <commands>
- **Result:** <pass / fail / skipped> with one-line reason
- **Installer refusals:** <number, or `none`>
- **Validation report path:** <absolute path>

If validation was skipped, the report must explain why.

## Risks

Bullets covering non-obvious risks. Each risk should map to
either an existing `decisions/<id>.md` or an `approval-gate`
record. Plain text risks without ownership are not accepted.

- <risk> — owner: <agent or human> — mitigation: <one line>
- Or `none identified`.

## Handoff

- **Handoff packet:** <path to
  `handoffs/<UTC-ts>-frontend-implementation-to-<target>.md`>
- **Target skill:** <e.g. `code-change-review`>
- **Required next action:** <one line>

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Discovery: `<path>` or `none`
- Routing report: `<path>` or `none`
- Validation report: `<path>` or `none`
- Handoff packet: `<path>`

## Provenance

- Produced by `frontend-implementation` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/frontend-implementation-report.md`
  (recommended; not required).
- This report is a **primary report** for the implementation
  step. It is not derived from another report; the receiving
  skill treats it as input.
