# Decision quality checklist

Self-check applied to an
[`architecture-decision`](../../SKILL.md) ADR before it is
handed off. The checklist is read on demand, not loaded
wholesale. Use it as a review-time lens, not as a substitute
for the ADR.

## 1. The decision is one sentence

- [ ] The `Decision` section is one or two sentences.
- [ ] The decision states what we will do, the scope, and the
  primary reason.
- [ ] The decision does not bury the choice in rationale.

## 2. Constraints are real and concrete

- [ ] Functional requirements are listed, not implied.
- [ ] Non-functional requirements (latency, throughput, scale)
  are stated as numbers or "unspecified", not as vibes.
- [ ] Reliability, security, compliance, cost, and team
  constraints are listed.
- [ ] When a constraint is unspecified, the ADR says so —
  silence is not an option.

## 3. At least two viable options are compared

- [ ] The options table has at least two rows.
- [ ] Each option has a description, strengths, weaknesses,
  cost, reversibility, and extension seams.
- [ ] A single-option ADR is justified by an explicit
  "no comparison meaningful" note in the analysis.

## 4. Rejected common patterns are explained

- [ ] Microservices — explicit verdict
- [ ] Event sourcing — explicit verdict
- [ ] CQRS — explicit verdict
- [ ] Service mesh — explicit verdict
- [ ] Queue / broker — explicit verdict
- [ ] Cache layer — explicit verdict
- [ ] Sharding — explicit verdict
- [ ] (Add others when relevant to the decision area)

Each verdict is either "considered, rejected because <reason>"
or "not applicable because <reason>".

## 5. Tradeoffs are honest

- [ ] What becomes easier is listed.
- [ ] What becomes harder is listed.
- [ ] What is locked in is listed.
- [ ] What is given up is listed.
- [ ] Opinion claims are labeled `opinion`.
- [ ] Estimated numbers are labeled `estimate` and sourced.

## 6. Reversibility is explicit

- [ ] `Reversibility` is exactly `cheap | expensive |
  irreversible`.
- [ ] For `cheap` or `expensive`, a reversal cost paragraph is
  present.
- [ ] For `irreversible`, mitigations are listed.

## 7. Validation plan is concrete

- [ ] The validation plan names a test, metric, load test, or
  SLO.
- [ ] Each validation step has an owner and a "done when"
  condition.
- [ ] A decision without a validation plan is not approved.

## 8. Implementation impact is named

- [ ] Affected files / modules are listed.
- [ ] The implementing skill
  (`backend-implementation` / `frontend-implementation` /
  `integration-implementation` / `implementation-orchestrator`)
  is named.
- [ ] Review gates required are listed.

## 9. Risks are owned

- [ ] Outstanding risks accepted by the decision are listed.
- [ ] Each risk has a mitigation.
- [ ] No risk is left ownerless.

## 10. The ADR is consistent with prior ADRs

- [ ] Existing ADRs in the same area were read.
- [ ] Contradictions with prior ADRs are called out in the
  `Cross-references` section.
- [ ] When the decision supersedes a prior ADR, the prior
  ADR's status is updated to `superseded` and the new ADR
  links to it.

## 11. Status is exact

- [ ] `Status` is exactly one of `proposed | accepted |
  superseded | rejected`.
- [ ] Status transitions are recorded in the same file.

## 12. No silent complexity

- [ ] If a complex design is selected, the simpler design is
  named and the reason it failed a stated requirement is
  recorded.
- [ ] "Future-proofing" is not a reason; if a future
  requirement is named, it is in the constraints.

## Red flags (block approval)

- Decision statement is missing.
- Reversibility is "irreversible" without explicit approval.
- Rejection reasons for common alternatives are absent.
- Validation plan is "we'll see" or absent.
- The decision introduces new infrastructure (cloud service,
  broker, datastore, queue) without a
  `dependency-change-review` gate.
- The decision claims no tradeoffs.
- The decision is presented as inevitable when at least one
  viable alternative exists.

## How to use

1. After writing the ADR, run through this checklist.
2. Mark any item that does not apply `n/a` with a one-line
   reason.
3. If a red flag fires, the ADR is not approved — the author
   must revise or escalate.
4. Attach the completed checklist to the handoff packet so
   the receiving skill and any approver can verify.
