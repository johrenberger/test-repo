---
name: security-review
artifact_type: skill
version: 1.0.0
owner: johrenberger
category: operations
quality_level: usable
last_reviewed: '2026-06-14'
used_by_agents:
- cloud-security-agent
- legal-compliance-agent
- pen-testing-agent
- security-analyst-agent
purpose: Application / code / config security review. Produces a ranked findings report
  grounded in code evidence. Read-only by default — does not exploit, fuzz, or scan.
---

# security-review

Application / code / config security review. Produces a ranked findings
report grounded in code evidence. Read-only by default — does not
exploit, fuzz, or scan.

## Purpose

Catch security-sensitive issues in a change before merge, with findings
ranked by severity, evidence, and exploitability. The skill is the
machine-readable first pass; a human security reviewer is still
required for final sign-off.

## Trigger

- A change touches authentication, authorization, data persistence,
  external integrations, secrets, or any security boundary.
- A handoff packet's "Required next action" calls for security review.
- A dependency, schema, or config change requires a security check
  (often paired with `dependency-change-review` or
  `database-migration-safety`).

## Do Not Use When

- The change is pure documentation or formatting.
- The task is active penetration testing (use a separate, authorized
  pen-testing workflow — never this skill).
- The change targets third-party systems (out of scope).

## Required Inputs

- `TASK_ID`
- `REPO_ROOT`
- `SCOPE` — file, module, or change-set to review
- `MODE` (optional) — one of `code | config | both` (default: `both`)

## Preflight

- Read the `repo-discovery` report. If absent, abort.
- Read any `code-change-report.md` and `dependency-change-report.md`
  for the same task; they provide context.
- Read the three references in `references/` for the categories
  covered.
- Confirm `REPO_ROOT` does not include the agent's own secrets in
  scope (e.g. an `.env` file). If a secret appears to be present in
  scope, create a blocker and stop.

## Workflow

1. **Inventory the security boundary.** Identify the auth entry points,
   the data-persistence entry points, the external integration entry
   points, and the config files. From the discovery report, note the
   detected framework and any security libraries already in use.
2. **Walk the OWASP checklist** in `references/owasp-checklist.md`.
   For each item: not in scope, not present, or finding (with
   evidence).
3. **Walk the secrets checklist** in
   `references/secrets-review-checklist.md`. Any hard-coded credential
   is a Critical finding.
4. **Walk the authz checklist** in
   `references/authz-review-checklist.md`. For each endpoint or
   resource access, verify the authz check exists and is not
   bypassable.
5. **Rank findings** using the severity scale in
   `references/owasp-checklist.md` (Critical / High / Medium / Low).
6. **For each finding**, capture: scope, evidence (file:line + code),
   exploitability notes, impact, recommended fix, and whether the fix
   needs architecture / security approval.
7. **Stop conditions** (see below) take precedence: if a finding
   implies immediate secret exposure or data-loss risk, stop the
   review and create a blocker.
8. **Render the report** from `templates/security-review-report.md`.
9. **Write the report** to
   `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/security-review-report.md`.
10. **Default handoff.** If findings require code changes, hand off to
    `backend-implementation` via the `handoff-packet` skill. If the
    findings need architecture / security approval, name the
    `ARCHITECT_AGENT` as a follow-up.

## Allowed Actions

- Read files anywhere under `REPO_ROOT`.
- Read existing reports under the task workspace.
- Create the report file under the task workspace.
- Print progress lines to stdout/stderr.

## Forbidden Actions

- No active exploitation, fuzzing, brute force, DDoS, credential
  attacks, or network scanning.
- No testing third-party systems.
- No exposing secrets in the report. If a secret is found, write
  `<REDACTED: <kind>>` and reference the file:line.
- No modifying code unless separately instructed (this skill is
  read-only by default).
- No running tests, linters, or build tools (use `validation-runner`).
- No reading environment variables matching `*TOKEN*`, `*SECRET*`,
  `*KEY*`, or `*PASSWORD*` from the agent's own environment.

## Stop Conditions

- A finding implies immediate secret exposure or data-loss risk →
  create a blocker via `task-state-management` and stop.
- A finding requires production data, production endpoints, or real
  credentials to verify → stop and request human authorization.
- The report is complete; no further findings are required by the
  current scope.

## Outputs

- `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/security-review-report.md`
- An optional handoff packet via the `handoff-packet` skill.
- An optional blocker file under the task workspace.

## Handoff Contract

Receiving agents may rely on:

- `scope` — what was reviewed
- `evidence_reviewed` — list of paths actually read
- `findings` — array of `{category, severity, file, lines, summary,
  evidence_redacted, exploitability, impact, recommended_fix,
  approval_required}`
- `outcome` — `approved | changes_requested | blocked`
- `blocker_filed` — boolean

Receiving agents must not rely on:

- A clean review meaning the system is secure (the skill is a
  best-effort first pass; human review is required for sign-off).

## Validation

- The report file exists and parses as markdown.
- Every Critical/High finding has a `file:lines` evidence pointer
  (with the secret value redacted if applicable).
- `outcome` is one of `approved | changes_requested | blocked`.
- If any finding triggered a stop, `blocker_filed: true` and a
  blocker file exists.

## Completion Criteria

- Report written, outcome decided, blockers filed if needed.
- If `outcome` is `changes_requested` or `blocked`, the report names
  the follow-up target and the approval gate required.
