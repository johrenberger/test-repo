# Workflow — long form

> This file holds the long-form implementation of the
> `implementation-orchestrator` Workflow section. The main
> `SKILL.md` keeps a quick-reference table; consult this file
> when the routing decision is non-obvious or when the caller
> needs the rationale for a particular gate.

## Workflow (long form)

1. **Discovery gate.** Use `repo-discovery` unless a current
   artifact is already attached to the task. Record the artifact
   path in the routing report.

2. **Identify impacted layer(s).** Map the task to one or more of:

   - `backend` — server-side logic, API, persistence, auth
   - `frontend` — UI, client state, forms, routing
   - `integration` — cross-system calls, messaging, webhooks, file
     import/export
   - `database/migration` — schema change, data backfill, migration
   - `infrastructure/deployment` — provisioning, build, deploy
   - `documentation-only` — docs / comments / spec changes
   - `mixed` — two or more of the above

   The mapping must cite at least one concrete file or module per
   layer from the discovery artifact. **Known limitation
   (Finding 1, B1 exercise):** a reference implementation that
   uses keyword matching on the task description is brittle and
   may mis-classify tasks that don't contain the expected
   keywords (e.g. "fix the dashboard rendering bug"). A real
   orchestrator should parse the task description to extract
   concrete file paths and module names, then look them up in
   the discovery artifact.

3. **Identify smallest impacted module / subtree.** For each
   impacted layer, name the module(s) the change should land in.
   If multiple layers are touched, name the owning module for each.
   **Known limitation (Finding 2, B1 exercise):** a reference
   implementation that walks the filesystem for the first
   module with `src/main/java` is brittle. A real orchestrator
   should parse the task description for class / component
   names and look them up in the discovery artifact's module
   list.

4. **Decide whether to route to a review skill first.** Apply these
   gates:

   - Task requires a **destructive or irreversible migration** →
     route to `database-migration-safety` first.
   - Task requires a **new dependency, new package manager, or
     build-tool change** → route to `dependency-change-review`
     first.
   - Task is **architecturally novel** (new pattern, new module
     boundary, new persistence model) → route to architecture
     review first (`ARCHITECT_AGENT`).
   - Task is **security-sensitive** (auth, secrets handling,
     cryptographic change, PII handling) → route to
     `security-review` first.

   The output of the review skill is a findings report and a
   decision; only then does the orchestrator dispatch the
   implementation work.

5. **Produce the routing decision.** Pick exactly one of:

   - `backend-implementation` (with the module(s) to change)
   - `frontend-implementation` (with the module(s) to change)
   - `integration-implementation` (with the integration boundary)
   - `database-migration-safety` (gate, then usually
     `backend-implementation`)
   - `dependency-change-review` (gate, then re-route)
   - `security-review` (gate; the implementation skill is decided
     after the security review is satisfied)
   - `architecture-review` (gate; same — see note below)

   **Note on `architecture-review`:** the registry currently does
   not contain an `architecture-review` skill. The orchestrator
   should fall back to `backend-implementation` for now and flag
   the architectural novelty in the routing report's Risks
   section. This is a known gap (Finding 4, B1 exercise) and will
   be resolved when the `architecture-review` skill lands.
   **Note on infrastructure/deployment and documentation-only
   layers:** these layers are detected but have no dedicated
   implementation skill in the registry. The orchestrator
   should fall back to `backend-implementation` (the closest
   match) and flag the routing in the report (Finding 3, B1
   exercise; Finding 6, B1 exercise).

   If the task is `mixed` and the layers are roughly equal, the
   default is to **sequence** them: one orchestrator → one
   implementation skill → handoff packet → next orchestrator call
   for the next layer. This is intentional. A single
   implementation skill that tries to do two layers at once is
   the failure mode this skill is meant to prevent.

6. **Document risks and approval gates.** Use the shared
   [`approval-gate.md`](../../../templates/approval-gate.md) template
   for any blocker-level finding. Cross-link to the
   [`risk-register.md`](../../../templates/risk-register.md) for
   cross-skill risk aggregation.

7. **Hand off.** Produce a
   [`handoff-packet`](../handoff-packet/SKILL.md) to the selected
   skill. The packet's `Required next action` is "implement per
   routing report" and links to the routing report and discovery
   artifact.
