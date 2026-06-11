# API doc update checklist

Read on demand by
[`documentation-update`](../../SKILL.md) when an API doc
(OpenAPI / Swagger, GraphQL schema, gRPC / Protobuf, REST
handbook, GraphQL handbook) is being updated. The checklist
is applied per-endpoint and the results are summarized in the
documentation impact report.

## When this checklist applies

- The repo has a source-controlled API doc (OpenAPI / Swagger
  / GraphQL / Protobuf / REST handbook).
- A change touches any endpoint, schema, error model,
  auth model, or pagination / filtering convention.

## Sections to check

### Endpoint / operation

- [ ] Method and path still match the implementation.
- [ ] Description matches the actual behavior, not the
  planned behavior.
- [ ] Deprecation is marked when the endpoint is being
  retired.
- [ ] Sunset / removal date is documented when known.

### Request

- [ ] Path parameters are listed with type and constraints.
- [ ] Query parameters are listed with type, required /
  optional, and default.
- [ ] Request body schema is accurate; required fields are
  marked.
- [ ] Headers are listed (auth, content-type, custom).
- [ ] Content negotiation (e.g. JSON vs protobuf) is
  documented when applicable.

### Response

- [ ] Status codes are accurate; the happy path is documented
  first, then errors.
- [ ] Response body schema is accurate; required fields are
  marked.
- [ ] Headers are listed (rate limit, request id, etc.).
- [ ] Pagination is documented (cursor, offset, page-based)
  with example.
- [ ] Example response matches the actual schema.

### Errors

- [ ] Error model (HTTP status, error code, error message,
  problem-detail) is documented.
- [ ] Each documented error is reachable from the
  implementation; the doc does not list errors that cannot
  occur.
- [ ] Auth / authorization errors are documented
  (`401`, `403`).
- [ ] Rate-limit errors (`429`) are documented when
  applicable.

### Auth

- [ ] Auth model matches the implementation (bearer, mTLS,
  OAuth, API key).
- [ ] Required scopes / roles are documented.
- [ ] Token acquisition / refresh is documented or linked to
  the relevant doc.

### Versioning

- [ ] API version is documented in the path or header.
- [ ] Compatibility policy is documented (additive only,
  deprecation window).
- [ ] Breaking changes are flagged with a migration plan.

### Examples

- [ ] At least one example per major operation.
- [ ] Examples are runnable against the implementation
  (validated by `validation-runner` or recorded fixture
  when feasible).
- [ ] Examples do not contain real credentials; use
  placeholders (`<REDACTED: kind>`).

### Cross-references

- [ ] The doc links to the relevant ADR(s) for non-obvious
  design decisions.
- [ ] The doc links to the runbook for incident response,
  when applicable.
- [ ] The doc links to the changelog / release notes, when
  the repo has them.

## Validation

- [ ] The doc is validated against the implementation
  (schemathesis, contract test, recorded fixture).
- [ ] Every example is reproducible.
- [ ] No example uses a real production endpoint.

## Handoff checklist

- [ ] Documentation impact report entry is written for the
  API doc change.
- [ ] The handoff packet lists the API doc in `docs_updated`.
- [ ] If the API doc contradicts the implementation, the
  contradiction is recorded as a finding in
  `documentation-impact-report.md` and routed to the
  implementation skill or to `code-change-review`.

## Red flags

- Doc lists an endpoint or field that does not exist in the
  implementation.
- Doc omits an endpoint or field that the implementation
  exposes.
- Doc lists an error code that the implementation cannot
  produce.
- Doc uses real-looking credentials in examples.
- Doc is not updated when the contract changes; the change
  set includes API code but not the doc.
