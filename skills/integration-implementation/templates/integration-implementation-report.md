# Integration implementation report

Output of the
[`integration-implementation`](../../../../skills/integration-implementation/SKILL.md)
skill. Records the target boundary, profile, contract reference,
failure modes addressed, files changed, tests added, and
validation outcome for an integration-only implementation task.

## Task

- **Task ID:** <TASK_ID>
- **Implementation skill:** `integration-implementation`
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
- **Contract reference:** <path / URL to OpenAPI / AsyncAPI /
  schema / doc, or `none — flagged as blocker`>

## Integration profile

Exactly one of:

- `rest-api` — see
  [`references/profiles/rest-api.md`](../../../../skills/integration-implementation/references/profiles/rest-api.md)
- `async-messaging` — see
  [`references/profiles/async-messaging.md`](../../../../skills/integration-implementation/references/profiles/async-messaging.md)
- `webhook` — see
  [`references/profiles/webhook.md`](../../../../skills/integration-implementation/references/profiles/webhook.md)
- `file-batch` — see
  [`references/profiles/file-batch.md`](../../../../skills/integration-implementation/references/profiles/file-batch.md)
- `contract-testing` — see
  [`references/profiles/contract-testing.md`](../../../../skills/integration-implementation/references/profiles/contract-testing.md)

If none match, the skill stops and the report records the
mismatch as a blocker.

If the integration spans multiple boundaries, list all profiles
in execution order.

## Detection evidence

Cite concrete files / lines that justify the profile choice:

- Client / adapter — <file>
- DTO / schema — <file>
- Retry / timeout wrapper — <file>
- Error handling — <file>
- Logging / correlation — <file>
- Test framework / test doubles — <file>
- Build / dev command — <command>

## Target boundary / files changed

| File | Action (added / modified / deleted) | Reason |
| --- | --- | --- |
| <file> | added | <one line> |
| <file> | modified | <one line> |

List integration files only. Pure backend, pure frontend, and
infrastructure changes are out of scope and must be routed to
the orchestrator.

## Out of scope (not touched)

- <file or area> — reason: <one line, e.g. "backend, routed to
  `backend-implementation`">
- Or `none`.

## Failure modes addressed

Tick each failure mode the change addresses, or document the
existing handling if not addressed:

- [ ] timeout
- [ ] retry exhaustion
- [ ] duplicate delivery
- [ ] partial failure
- [ ] invalid payload
- [ ] auth failure
- [ ] rate limit
- [ ] downstream unavailable
- [ ] schema / version mismatch
- [ ] DLQ / dead-letter (broker)
- [ ] ordering / partition rebalance (broker)
- [ ] replay / duplicate (webhook)
- [ ] parsing / malformed file (file-batch)
- [ ] contract drift (contract-testing)
- [ ] `<other — describe>`

For each addressed failure mode, cite the file / lines that
implement the handling. For each not-addressed failure mode,
justify why (e.g. "out of scope for this task; tracked in
`<issue>`").

## Design checks

- [ ] Timeout: explicit, not default
- [ ] Retry: bounded with backoff, or explicit no-retry rationale
- [ ] Idempotency: key, dedup window, or at-most-once rationale
- [ ] Error classification: retryable vs non-retryable explicit
- [ ] Logging without secrets: payload redaction documented
- [ ] Observability / correlation IDs: reused existing pattern
- [ ] Schema / contract compatibility: pinned, additive changes
  only
- [ ] Backpressure / rate limit: handled where relevant

If any check is not satisfied, the report must justify why.

## Compatibility impact

- **Contract change:** `none | additive | breaking`
- **Backwards compatibility impact:** <one paragraph>
- **Migration plan (if breaking):** <one paragraph, or `n/a`>

Breaking contract changes without a migration plan and an
approval gate are a blocker for this skill.

## Tests added or updated

| File | Test framework | Type (unit / contract / fault-injection) | Notes |
| --- | --- | --- | --- |
| <file> | <framework> | <type> | <one line> |

For each test:

- **Test double used:** <mock | recorded fixture | contract
  test | sandbox endpoint | none>
- **Real production endpoint called:** `no` (always `no`)
- **Recorded fixture path:** <path> (if applicable)

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
  `handoffs/<UTC-ts>-integration-implementation-to-<target>.md`>
- **Target skill:** <e.g. `code-change-review`>
- **Required next action:** <one line>

## Audit trail

- `decisions/<id>.md` — <one line> (or `none`)
- `blockers/<id>.md` — <one line> (or `none`)
- `approvals/<gate-id>.md` — <one line> (or `none`)

## Cross-references

- Discovery: `<path>` or `none`
- Routing report: `<path>` or `none`
- Contract reference: `<path / URL>` or `none`
- Validation report: `<path>` or `none`
- Handoff packet: `<path>`

## Provenance

- Produced by `integration-implementation` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/integration-implementation-report.md`
  (recommended; not required).
- This report is a **primary report** for the implementation
  step. It is not derived from another report; the receiving
  skill treats it as input.
