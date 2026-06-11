# Release gate checklist

Read on demand by
[`release-readiness`](../../SKILL.md). The gate is the
canonical list of items a release must satisfy before it is
Ready. The skill applies this checklist per release; the
per-release verdicts live in
[`templates/go-no-go-checklist.md`](../templates/go-no-go-checklist.md).

## 1. Tests pass

- [ ] Unit tests pass locally (validated by
  `validation-runner`).
- [ ] Integration tests pass locally when the repo has them.
- [ ] CI status (when available) is green.
- [ ] No tests are skipped or pending without a documented
  reason.

## 2. Build success

- [ ] The build artifact is produced locally (or in CI).
- [ ] The build artifact matches the expected version /
  tag.
- [ ] The build artifact is reproducible when the repo
  supports it.

## 3. Lint / typecheck

- [ ] Lint passes.
- [ ] Typecheck (when the language has it) passes.
- [ ] No new warnings introduced that the repo treats as
  errors.

## 4. Unresolved Critical findings

- [ ] Zero unresolved Critical findings from any review
  report.
- [ ] Any accepted Critical findings are recorded in
  `decisions/<id>.md` with a named approver and a mitigation
  plan.

## 5. Unresolved High findings

- [ ] Zero unresolved High findings, or each is recorded in
  `decisions/<id>.md` with a named approver and a mitigation
  plan.

## 6. Migration safety

- [ ] When the change includes a migration, the
  `migration-safety-report.md` is `pass` or `concern with
  acceptance`.
- [ ] The migration is expand-and-contract when destructive.
- [ ] The migration is rehearsed in a staging environment
  when feasible.

## 7. Dependency changes

- [ ] When the change includes a dependency change, the
  `dependency-change-report.md` is `pass` or `concern with
  acceptance`.
- [ ] No new runtime dependency without a
  `dependency-change-review` gate.
- [ ] No package-manager migration without an ADR.

## 8. Security risks

- [ ] When the change is security-sensitive, the
  `security-review-report.md` is `pass` or `concern with
  acceptance`.
- [ ] No new high-severity CVE introduced.
- [ ] Auth / secrets handling changes are reviewed.

## 9. Architecture review

- [ ] When the change is architecture-novel, the
  `architecture-review-report.md` is `pass` or `concern with
  acceptance`.
- [ ] Material changes have an ADR.

## 10. Rollback plan

- [ ] The rollback plan is documented and concrete.
- [ ] The rollback time is estimated (or rehearsed).
- [ ] The rollback's data implications are explicit
  (destructive / additive / n/a).
- [ ] The operator who runs the rollback is identified.

## 11. Feature flags / config

- [ ] Feature flags (when applicable) are configured to
  allow staged rollout.
- [ ] Config changes are documented and reversible.
- [ ] New env vars / secrets are documented; production
  values are not in the repo.

## 12. Monitoring / alerts / runbooks

- [ ] `observability-review-report.md` is `pass` or
  `concern with acceptance`.
- [ ] Dashboards for the new behavior exist or are planned
  for first-day.
- [ ] Alerts for the new failure modes exist or are planned
  for first-day.
- [ ] Runbooks for the new alerts exist; see
  [`runbook-authoring`](../runbook-authoring/SKILL.md).
- [ ] On-call coverage for the rollout window is confirmed.

## 13. Documentation updates

- [ ] `documentation-impact-report.md` is `pass` or
  `concern with acceptance`.
- [ ] README, API doc, runbook, and changelog are aligned
  with the change.
- [ ] Public-facing docs are reviewed (when applicable).

## 14. Known limitations

- [ ] Known limitations are documented in
  `decisions/<id>.md` or in the readiness report.
- [ ] Each limitation has an owner and a remediation plan
  (or an explicit "won't fix" with rationale).

## 15. Manual approvals

- [ ] Required manual approvals are recorded in
  `decisions/<id>.md` (e.g. security sign-off, product
  sign-off, on-call sign-off).
- [ ] The approver and the decision timestamp are recorded.
- [ ] When the release is in a regulated domain
  (financial, health, etc.), the regulatory approval is
  recorded.

## Red flags (block release)

- Any gate item is `finding` without an acceptance decision.
- The release is marked `Ready` while a Critical finding
  is open.
- Validation is missing for a high-risk change.
- The rollback plan is "we'll figure it out."
- Production credentials are required but not identified
  for the operator.
- The on-call coverage is missing for the rollout window.

## How to use

1. For each release, walk through the gate items in order.
2. Cite evidence for each item (path to the report or
   artifact).
3. Aggregate verdicts into the
   [`go-no-go-checklist.md`](../templates/go-no-go-checklist.md)
   per-release record.
4. Apply the status mapping from the
   [`release-readiness-report.md`](../templates/release-readiness-report.md)
   template.
5. The release is not `Ready` until every gate item has a
   passing verdict or an explicit acceptance decision.
