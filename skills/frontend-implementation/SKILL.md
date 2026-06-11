# frontend-implementation

Implement **frontend / client-side** behavior safely using the
existing project conventions. The skill produces the smallest
frontend change that satisfies the acceptance criteria and fits
the existing codebase.

This skill is **narrowly scoped** to UI, client state, and
client-side behavior. It does not edit backend logic, server-side
APIs, or cross-system integration flows. If the task requires
those, stop and hand off to
[`implementation-orchestrator`](../implementation-orchestrator/SKILL.md).

## Purpose

Translate an approved frontend-scoped plan (typically from a
product spec, a UX/UI review, a code-review fix-up, or a handoff
from `backend-implementation` for a UI change that depends on a
new API) into working frontend code that matches the existing
repo's framework, styling, state-management, and test
conventions, and passes validation.

The skill is frontend-only. The orchestrator decides when this
skill is the right one to invoke; this skill does not decide that
on its own.

## Trigger

Use when the task involves any of:

- UI components (page, panel, modal, widget, layout, list, table)
- Client-side state (local store, form state, server cache,
  routing state)
- Forms (controlled / uncontrolled, validation, error display)
- Validation in the UI (client-side schema validation, error
  messages, accessibility messaging)
- Routing / navigation (route definitions, guards, lazy loading,
  page transitions)
- Frontend API calls (HTTP clients, fetch / axios / RTK Query,
  GraphQL clients, server-state caching)
- Accessibility (semantic HTML, ARIA roles, keyboard navigation,
  color contrast, focus management)
- Styling / layout (CSS, CSS modules, Tailwind, styled-components,
  CSS-in-JS, design tokens)
- Frontend tests (unit, component, integration, E2E if the repo
  already uses them)
- Browser behavior (storage, cookies, web workers, service
  workers, IndexedDB)
- Client-side error handling (error boundaries, fallback UI,
  telemetry)

## Do Not Use When

- A new **backend API or contract** must be created first — route
  to [`backend-implementation`](../backend-implementation/SKILL.md)
  first; this skill can do follow-up UI work only after the
  contract is stable.
- **Database changes** are required — route to
  [`database-migration-safety`](../database-migration-safety/SKILL.md)
  first.
- **Infrastructure / deployment** changes are the primary
  concern — out of scope.
- **Active security testing** is required — route to
  [`security-review`](../security-review/SKILL.md).
- The task is **integration-only** (external API call from the
  server, webhook handler, queue, file batch) — use
  [`integration-implementation`](../integration-implementation/SKILL.md).
- The task is **unclear about which layer** it touches — use
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
  first.

## Required Inputs

- **Task description** with concrete acceptance criteria.
- **Repo-discovery artifact** (current
  `discovery/repo-discovery.md`) for the task.
- **Routing report** (when invoked through the orchestrator) or
  equivalent target module list.
- **Frontend framework** — at least one of the supported
  profiles matches the actual code:
  [`react`](references/profiles/react.md),
  [`angular`](references/profiles/angular.md),
  [`vue`](references/profiles/vue.md),
  [`nextjs`](references/profiles/nextjs.md),
  [`static-ui`](references/profiles/static-ui.md). If none match,
  the skill stops and asks for guidance.
- **Existing API contract** for any backend the UI calls. If the
  API is changing as part of the task, the API change must be
  routed to `backend-implementation` first; this skill consumes
  the stable contract only.

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If not,
   run `repo-discovery` first; this skill does not invent repo
   facts.
2. Confirm acceptance criteria are concrete and testable.
3. Confirm the task is frontend-only. If the task also requires
   backend or integration changes, stop and route to the
   orchestrator.
4. Confirm the frontend framework profile matches reality. If
   the repo is a custom framework or one of the supported
   profiles does not cover it, the skill stops and asks for
   guidance.
5. Confirm the API contract is stable. If a backend change is
   part of the same task, route to
   [`backend-implementation`](../backend-implementation/SKILL.md)
   first; the orchestrator sequences the two skills.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact and
   confirm the target module is identified. The orchestrator's
   routing report or the explicit handoff names the target
   module; this skill must not change targets mid-flight.

2. **Identify frontend framework and module.** Match the actual
   code to one of the supported profiles:
   [`react`](references/profiles/react.md),
   [`angular`](references/profiles/angular.md),
   [`vue`](references/profiles/vue.md),
   [`nextjs`](references/profiles/nextjs.md), or
   [`static-ui`](references/profiles/static-ui.md). If the repo
   mixes frameworks in a single module, prefer
   [`static-ui`](references/profiles/static-ui.md) for the
   non-framework parts and call out the mix in the report.

3. **Inspect existing patterns.** Read the relevant profile. The
   profile documents detection cues, component conventions,
   routing style, state-management patterns, API client
   patterns, styling approach, and a small example specific to
   the framework.

4. **Preserve existing conventions.** Preserve the existing:

   - framework (do not introduce a new one)
   - package manager (do not change)
   - module system (CommonJS / ESM / Angular modules / Vue SFC)
   - styling approach (CSS modules, Tailwind, Sass, styled
     components, design tokens, etc.)
   - state management (Redux, Zustand, Pinia, NgRx, etc.)
   - test framework (Jest, Vitest, RTL, TestBed, Vue Test Utils,
     Cypress, Playwright)

5. **Add or update tests where feasible.** Prefer
   user-behavior / component tests over implementation-detail
   tests. Use the existing test framework only. Detect: Jest,
   Vitest, React Testing Library, Cypress, Playwright, Angular
   TestBed, Vue Test Utils. Add accessibility checks where
   relevant (e.g. `axe` with RTL, Angular CDK a11y). Do **not**
   add E2E tests unless the repo already uses them or the task
   specifically requires them.

6. **Implement smallest safe frontend change.** Follow the
   profile's conventions. Do not change the package manager,
   introduce a new UI framework, rewrite the component
   architecture, or convert the styling system. Do not introduce
   a state-management library unless explicitly approved.

7. **Run validation.** Use
   [`validation-runner`](../validation-runner/SKILL.md) to
   discover and run the repo's local validation commands. Do
   not install dependencies. If validation cannot be run, the
   report must explain why.

8. **Hand off for review and follow-up.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to
   `code-change-review` or `test-generation` as appropriate.

## Allowed Actions

- Read repo files.
- Add or update frontend source files (components, hooks,
  modules, routes, styles, tests) within the target module.
- Run repo-local validation commands detected by
  [`validation-runner`](../validation-runner/SKILL.md).
- Run the repo's test suite locally; never install dependencies
  to make it pass.
- Write the implementation report and handoff packet.

## Forbidden Actions

- **Do not change backend contracts.** A new endpoint, schema
  change, or auth flow must be routed to
  [`backend-implementation`](../backend-implementation/SKILL.md)
  first.
- **Do not change the package manager.** If a package-manager
  change is required, stop and route to
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
  first.
- **Do not introduce a new UI framework.**
- **Do not rewrite the component architecture** (e.g. convert
  class components to hooks across the codebase; that is a
  dedicated refactor task, not an implementation task).
- **Do not convert the styling system** (e.g. CSS modules to
  Tailwind) as part of an unrelated change.
- **Do not introduce a state-management library** (Redux, Zustand,
  Pinia, NgRx, etc.) unless explicitly approved.
- **Do not modify production deployment settings** (CDN config,
  cache headers, edge config).
- **Do not introduce new build / bundler / test tooling.**
- **Do not run installers** (`npm install`, `yarn add`,
  `pnpm add`, `pip install`).
- **Do not read or write credentials, secrets, tokens, or
  environment variables matching `*TOKEN*`, `*SECRET*`, `*KEY*`,
  `*PASSWORD*`.**
- **Do not deploy, run load tests, or call real production
  endpoints.**
- **Do not add E2E tests** unless the repo already has them or
  the task specifically requires them.
- **Do not bypass the orchestrator** when the task touches more
  than one layer.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- The target module is not actually frontend, or is genuinely
  mixed with no clean frontend boundary.
- The required frontend profile does not match the repo.
- Acceptance criteria are unclear.
- A new backend API or contract is required and no
  `backend-implementation` task has been scheduled.
- A package-manager change, new dependency, or build-tool change
  is required and no review has been scheduled.
- The task requires touching backend or integration code as part
  of the same change; the orchestrator must sequence the
  skills.
- The repo's validation commands fail in a way that is not
  related to the change.
- Production credentials or live external services are required.

## Outputs

- **Source changes** — frontend source files and tests within
  the target module, per the profile's conventions.
- **Implementation report** —
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/frontend-implementation-report.md`
  (see
  [`templates/frontend-implementation-report.md`](templates/frontend-implementation-report.md)).
- **Handoff packet** to
  [`code-change-review`](../code-change-review/SKILL.md) or
  [`test-generation`](../test-generation/SKILL.md) as
  appropriate.

## Handoff Contract

Fields the receiving skill may rely on:

- `target_modules` — list of `path:reason` for the modules changed
- `framework_profile_used` — exactly one of
  `react | angular | vue | nextjs | static-ui`
- `component_or_route_changes` — list of files added or updated
- `tests_added_or_updated` — list of test files touched
- `validation_result` — short summary of what
  [`validation-runner`](../validation-runner/SKILL.md) produced
- `out_of_scope` — list of files the skill refused to touch
  (backend, integration, infra)
- `acceptance_criteria` — the testable conditions
- `api_contract_version` — version / commit of the API the UI
  targets

Fields the receiving skill must not rely on:

- "production-safe" — local validation is not a deployment claim.
- "accessible" — accessibility is asserted only by a dedicated
  a11y review.
- "no regressions" — claims of no regression require
  `validation-runner` evidence in the implementation report.

## Validation

The skill is "validated" when:

1. The implementation report exists and references the target
   module, the framework profile used, and the tests added or
   updated.
2. `validation-runner` was run; its report is linked from the
   implementation report.
3. No forbidden action was performed (dependency install,
   package-manager swap, framework change, styling system
   change, backend or integration edit, secret read).
4. The handoff packet to the next skill has all 14 required
   fields.

## Completion Criteria

- The smallest frontend change that satisfies the acceptance
  criteria is in the working tree.
- The framework profile's conventions are followed.
- Frontend tests covering the change are present and pass
  locally.
- `validation-runner` ran without installer refusals.
- The implementation report is complete and the handoff packet
  is accepted by the next skill.

## Cross-references

- Routing:
  [`implementation-orchestrator`](../implementation-orchestrator/SKILL.md)
- Sibling implementation skills:
  [`backend-implementation`](../backend-implementation/SKILL.md),
  [`integration-implementation`](../integration-implementation/SKILL.md)
- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Review gates:
  [`code-change-review`](../code-change-review/SKILL.md),
  [`security-review`](../security-review/SKILL.md),
  [`dependency-change-review`](../dependency-change-review/SKILL.md)
- Tests:
  [`test-generation`](../test-generation/SKILL.md)

## Profiles

Per-framework guidance. Read on demand, not loaded wholesale.

- [`references/profiles/react.md`](references/profiles/react.md)
- [`references/profiles/angular.md`](references/profiles/angular.md)
- [`references/profiles/vue.md`](references/profiles/vue.md)
- [`references/profiles/nextjs.md`](references/profiles/nextjs.md)
- [`references/profiles/static-ui.md`](references/profiles/static-ui.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
