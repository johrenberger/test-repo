# runbook-authoring

Create or update operational runbooks and troubleshooting
guides from validated system evidence. The skill produces
operational docs that an on-call responder can follow under
pressure.

## Purpose

Make operational procedures **reproducible** so that:

- the on-call responder does not have to remember the
  procedure from a previous incident;
- the procedure is verified against actual repo / operator
  evidence, not invented;
- destructive steps are gated by approval;
- the procedure is linked to the artifacts that produced it
  (incident, ADR, observability review);
- the procedure lives where the on-call can find it.

The skill is the operational counterpart to
[`documentation-update`](../documentation-update/SKILL.md):
it produces docs that operators use, not docs that
end-users read.

## Trigger

Use when:

- A new service / process requires operational support.
- `release-readiness` identifies a missing runbook for a
  release.
- `observability-review` identifies an alert without a
  runbook.
- `incident-triage` requires a repeatable procedure.
- DevOps / Monitoring asks for operational documentation.
- A runbook is outdated (commands have changed, the system
  has changed, the failure mode is new).
- A post-incident review identifies a missing runbook as
  the contributing cause.

## Do Not Use When

- The behavior is not understood — stop and investigate
  first; the skill cannot document what is not known.
- Commands cannot be verified or sourced from repo /
  operator evidence — stop and request evidence.
- Public documentation is needed instead of internal
  operational docs — use
  [`documentation-update`](../documentation-update/SKILL.md)
  for public-facing docs; this skill is internal.
- The task is to add a specific log line, metric, or
  alert — small enough to be done directly.
- The task is to author an ADR — use
  [`architecture-decision`](../architecture-decision/SKILL.md).

## Required Inputs

- **System / behavior** — what the runbook is about.
- **Acceptance criteria** — what "the runbook is ready"
  means (e.g. "all commands verified, all destructive
  steps gated").
- **Repo-discovery artifact** — current
  `discovery/repo-discovery.md`, or permission to run
  `repo-discovery`.
- **Source evidence** — incident triage report, observability
  review, ADR, prior runbook, or operator-provided procedure.
- **Existing runbooks** — if the repo stores them
  (`docs/runbooks/`, `runbooks/`, `RUNBOOK.md`); the new
  runbook matches the existing format.
- **Operator contact** — owner / team for the runbook, when
  known.
- **Severity guidance** — what severity triggers the
  runbook (cross-reference
  [`incident-triage`](../incident-triage/SKILL.md)).

## Preflight

1. Confirm a current `repo-discovery` artifact exists. If
   not, run `repo-discovery` first; the runbook must not
   invent repo facts.
2. Confirm the source evidence is attached. A runbook
   without source evidence is a guess.
3. Confirm the existing runbook format / location. If the
   repo has runbooks, match the format.
4. Confirm the procedure is understood. If commands cannot
   be verified or sourced, stop and request evidence.
5. Confirm destructive steps are gated. Destructive
   remediation requires operator approval and a labeled
   approval gate.

## Workflow

1. **Discovery gate.** Read the `repo-discovery` artifact
   and confirm the relevant services, config, and operational
   entry points are identified.

2. **Identify the runbook scope.** The runbook is for one
   specific service / process / failure mode. If the scope
   is broader, split into multiple runbooks.

3. **Match existing format / location.** When the repo
   already has runbooks, match the format and location. When
   the repo has no runbooks, use the default location
   (`docs/runbooks/`) and a default format (see
   [`templates/runbook.md`](templates/runbook.md)).

4. **Compose the runbook.** Use
   [`templates/runbook.md`](templates/runbook.md). The
   runbook includes:

   - **Purpose** — what is this runbook for?
   - **Scope** — what service / process / failure mode?
   - **Symptoms** — how the on-call knows to use this
     runbook
   - **Severity guidance** — link to
     [`incident-triage`](../incident-triage/SKILL.md)
   - **Prerequisites / access requirements** — what
     credentials / access are needed
   - **Safe diagnostic commands** — read-only commands to
     gather evidence
   - **Expected outputs** — what the operator should see
     at each step
   - **Mitigation options** — options, each labeled with
     the trigger, action, expected effect, rollback, and
     risk
   - **Rollback / escalation steps** — how to back out or
     escalate
   - **Validation after mitigation** — how to confirm the
     mitigation worked
   - **Known risks** — risks the procedure accepts
   - **Owner / team / contact** — placeholder when not
     known, real contact when known
   - **Cross-references** — ADRs, release reports,
     observability reports, incident reports, SLO / SLI

5. **Mark unverified commands clearly.** Every command that
   is not validated by `validation-runner` or by operator
   evidence is marked `unverified — confirm before
   running`. The operator's first act is to verify the
   command against the current system state.

6. **Gate destructive commands.** Destructive remediation
   steps (data deletion, mass update, force push, drop
   table, restart production) require:

   - An explicit `DESTRUCTIVE — requires operator approval`
     label.
   - An approval gate record in `approvals/<gate-id>.md`.
   - A rollback step in the same runbook.
   - An expected effect and a "verify after" step.

7. **Keep secrets out of examples.** Use placeholders
   (`<REDACTED: kind>`) for tokens, keys, and hostnames. The
   on-call uses their own credentials; the runbook is not
   a credentials store.

8. **Produce the runbook authoring report.** Use
   [`templates/runbook-authoring-report.md`](templates/runbook-authoring-report.md)
   if the task is to author or update a runbook as part of
   a larger change. Save to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/runbook-authoring-report.md`.

9. **Save the runbook** to the repo at the canonical
   location (e.g. `docs/runbooks/<service>-<scenario>.md`).
   If the repo has no `docs/runbooks/` location and the
   task does not require in-repo storage, save the runbook
   to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/<runbook-file>.md`
   and flag the storage decision in the authoring report.

10. **Hand off.** Produce a
    [`handoff-packet`](../handoff-packet/SKILL.md) to
    `DEVOPS_AGENT` or `MONITORING_AGENT` (depending on who
    owns the runbook) for review and adoption.

## Allowed Actions

- Read repo files, existing runbooks, ADRs, and operational
  artifacts.
- Run `repo-discovery` scripts (read-only).
- Run `validation-runner` to verify commands (when
  feasible).
- Write the runbook, the authoring report, and the handoff
  packet.
- Update the runbook in-repo (when the repo convention
  supports it).
- Update `task.md` / `state.json` to reflect the authoring
  outcome.

## Forbidden Actions

- **Do not invent production access details.** Credentials,
  hostnames, internal URLs, queue / topic names, and similar
  operational facts must be sourced from repo evidence or
  operator-provided evidence. Placeholders are used when
  the detail is sensitive.
- **Do not include real secrets, tokens, hostnames, or
  credentials** unless already public / non-sensitive and
  required. The default is `<REDACTED: kind>`.
- **Do not provide destructive remediation commands without
  approval gates.** Destructive steps are labeled and
  gated; the runbook is not a license to mutate production.
- **Do not publish externally.** The runbook is internal
  operational documentation; publishing it externally
  requires operator / product approval.
- **Do not bypass the existing runbook format.** When the
  repo has runbooks, match the format; the new runbook is
  not a reason to introduce a new format.
- **Do not present unverified commands as verified.** Every
  command that has not been validated is labeled
  `unverified`.
- **Do not skip the rollback step.** Every destructive step
  has a rollback; every mitigation has a "verify after"
  step.

## Stop Conditions

Halt the workflow and surface a blocker (via
`task-state-management`) when:

- Required operational facts are missing.
- A procedure includes production-impacting actions and
  the approval gate is not in place.
- Security / compliance review is required (e.g. the
  runbook handles credentials, PII, or regulated data).
- Commands cannot be verified or sourced; the runbook
  cannot be written with verified commands.
- The runbook scope is unclear and the operator cannot
  scope it.

## Outputs

- **Runbook** — at the canonical repo location
  (`docs/runbooks/<service>-<scenario>.md` or equivalent)
  or in
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/<runbook-file>.md`
  when in-repo storage is not appropriate.
- **`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/runbook-authoring-report.md`**
  — see
  [`templates/runbook-authoring-report.md`](templates/runbook-authoring-report.md).
- **Handoff packet** to `DEVOPS_AGENT` or `MONITORING_AGENT`
  for review and adoption.

## Handoff Contract

Fields the receiving role may rely on:

- `runbook_path` — absolute path to the runbook
- `authoring_report_path` — absolute path to the authoring
  report
- `scope` — service / process / failure mode covered
- `severity` — the severity that triggers the runbook
- `prerequisites` — access / credentials required
- `destructive_steps` — list of `step_id: label`
- `unverified_commands` — list of `step_id: command`
- `owner` — placeholder or named owner
- `cross_references` — list of related ADRs, reports, and
  runbooks

Fields the receiving role must not rely on:

- "approved" — the runbook is a draft until the
  `DEVOPS_AGENT` or `MONITORING_AGENT` reviews it.
- "tested" — the runbook is verified only for the commands
  the skill ran; unverified commands are marked.
- "complete" — the runbook is complete for the scope; the
  skill does not claim cross-scope completeness.

## Validation

The runbook is "validated" when:

1. Every command is sourced (validated by
   `validation-runner`, operator evidence, or repo
   evidence) and labeled with its source.
2. Unverified commands are explicitly labeled.
3. Destructive commands have an approval gate and a
   rollback step.
4. The runbook has a cross-reference section linking to
   ADRs, release reports, observability reports, and
   incident reports.
5. The handoff packet has all 14 required fields.
6. The authoring report covers source evidence, decisions
   made, and any unresolved questions.

The skill itself runs no shell commands; it may invoke
`validation-runner` to verify commands.

## Completion Criteria

- The runbook scope is clear and documented.
- All commands are sourced or explicitly labeled unverified.
- Destructive steps are gated and have rollbacks.
- The runbook cross-references related artifacts.
- The authoring report is complete.
- The handoff packet is produced and the next role accepts
  it.
- The task's `state.json` reflects the authoring outcome.

## Cross-references

- Foundation:
  [`repo-discovery`](../repo-discovery/SKILL.md),
  [`task-state-management`](../task-state-management/SKILL.md),
  [`handoff-packet`](../handoff-packet/SKILL.md),
  [`validation-runner`](../validation-runner/SKILL.md)
- Operational:
  [`incident-triage`](../incident-triage/SKILL.md),
  [`observability-review`](../observability-review/SKILL.md),
  [`release-readiness`](../release-readiness/SKILL.md)
- Documentation: [`documentation-update`](../documentation-update/SKILL.md)
- Decisions: [`architecture-decision`](../architecture-decision/SKILL.md)
- Reference:
  [`references/runbook-quality-checklist.md`](references/runbook-quality-checklist.md)
- Templates:
  [`templates/runbook.md`](templates/runbook.md),
  [`templates/troubleshooting-guide.md`](templates/troubleshooting-guide.md),
  [`templates/runbook-authoring-report.md`](templates/runbook-authoring-report.md)
- Shared: [`operational-risk-register`](../../templates/operational-risk-register.md),
  [`incident-summary`](../../templates/incident-summary.md)

## Maturity

`draft` — initial spec, not yet run end-to-end.
