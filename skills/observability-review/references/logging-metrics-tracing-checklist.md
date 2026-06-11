# Logging / metrics / tracing checklist

Read on demand by
[`observability-review`](../../SKILL.md). The checklist is
applied to a service or change when the review runs. It is
not a substitute for the report template; it is a lens.

## 1. Logging

- [ ] Key events are logged (request received, request
  completed, error, retry, circuit-breaker open / close,
  rate-limit hit, auth failure, dependency failure).
- [ ] Logs are structured (JSON or equivalent) and parseable
  by the log platform.
- [ ] Logs include a correlation / request id.
- [ ] Log levels are used appropriately (ERROR for failures,
  WARN for recoverable issues, INFO for routine events,
  DEBUG for development).
- [ ] Logs avoid secrets (tokens, keys, passwords) and PII
  (emails, phone numbers, payment data) — or the redaction
  list is explicit.
- [ ] Logs do not include full request / response bodies
  when the body may contain PII or secrets.
- [ ] Log volume is bounded (no per-request megabytes; no
  per-loop spam).
- [ ] Log retention is appropriate for the use case (audit
  logs longer, debug logs shorter).

## 2. Metrics

- [ ] Critical paths have metrics (latency, error rate,
  throughput).
- [ ] RED metrics (Rate, Errors, Duration) are emitted for
  request-serving paths.
- [ ] USE metrics (Utilization, Saturation, Errors) are
  emitted for resources (CPU, memory, disk, network, queue
  depth).
- [ ] Queue / lag metrics exist for asynchronous paths.
- [ ] Saturation metrics exist (in-flight requests, pool
  usage, connection pool).
- [ ] Metrics are labeled with the dimensions needed for
  triage (route, status, dependency).
- [ ] High-cardinality labels are avoided (no request ids
  in labels; no unbounded user identifiers).
- [ ] Metrics are emitted from the same code path that
  produces the work (no off-by-one in instrumentation).

## 3. Tracing

- [ ] Traces propagate correlation IDs across service
  boundaries (W3C trace context, OpenTelemetry, or
  equivalent).
- [ ] Spans are named usefully (operation, dependency,
  resource).
- [ ] Spans include relevant attributes (route, status,
  retry count, dependency name).
- [ ] Sampling is appropriate (head-based for uniform
  coverage; tail-based for error / latency-biased).
- [ ] Trace storage retention is appropriate.
- [ ] Trace-to-log correlation works (the trace id is in
  the log line; the log line is in the trace).

## 4. Health checks

- [ ] Liveness check exists and is shallow (the process is
  alive, not the dependencies).
- [ ] Readiness check exists and reflects dependencies
  (DB, queue, downstream services) when dependencies are
  required for serving traffic.
- [ ] Health check endpoint does not require auth (so the
  orchestrator can probe it).
- [ ] Health check does not log noise.
- [ ] Health check failure does not cascade (a failed
  dependency should not make the readiness check spin).

## 5. SLOs / SLIs

- [ ] User-facing capabilities have an SLI.
- [ ] The SLI is measurable from existing instrumentation
  (or a small change adds the measurement).
- [ ] The SLO target is a number with a window.
- [ ] The error budget is defined.
- [ ] The error budget policy (what happens when budget is
  exhausted) is documented.

## 6. Alerts

- [ ] Alerts are actionable (the responder can do
  something).
- [ ] Alerts have a runbook (see
  [`runbook-authoring`](../runbook-authoring/SKILL.md)).
- [ ] Alert thresholds are sane (not noisy, not silent).
- [ ] Multi-window / multi-burn-rate alerts are used for
  SLOs when feasible.
- [ ] Alerts do not page on known noise (e.g. deployment
  restarts).
- [ ] Alert routing reaches the right team (or has an
  escalation path).
- [ ] Alerts on critical paths (auth, payments, data loss)
  are higher severity.

## 7. Dashboards

- [ ] At least one dashboard per service.
- [ ] The dashboard is usable for triage (overview +
  per-dependency + per-error).
- [ ] The dashboard links to runbooks for common alerts.
- [ ] The dashboard is owned (a team is responsible).
- [ ] The dashboard is reviewed periodically (stale
  panels removed, new panels added).

## Red flags (block approval)

- Secrets in logs (tokens, keys, passwords, full credit
  card numbers).
- PII in logs without explicit redaction.
- No metrics on a critical path.
- No trace correlation across a service boundary.
- Liveness check that depends on a downstream service.
- Alert without a runbook.
- Alert that pages every deploy.
- SLO target without a number or window.
- Error budget "policy" that is "we'll figure it out."

## How to use

1. After mapping the change to observable signals, run
   through this checklist.
2. Each row becomes a `pass | concern | finding` verdict in
   the report's observability-dimensions table.
3. `concern` rows are recorded as `Low` or `Medium`
   findings; `finding` rows are recorded with a severity
   tied to impact.
4. Any red flag fires a blocker; the change is not approved
   until the red flag is resolved.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Report template:
  [`../templates/observability-review-report.md`](../templates/observability-review-report.md)
- SLO template:
  [`../templates/slo-review.md`](../templates/slo-review.md)
- Runbook authoring:
  [`../../runbook-authoring/SKILL.md`](../../runbook-authoring/SKILL.md)
  (for alert-without-runbook findings)
- Incident triage:
  [`../../incident-triage/SKILL.md`](../../incident-triage/SKILL.md)
  (for post-incident observability reviews)
- Security review:
  [`../../security-review/SKILL.md`](../../security-review/SKILL.md)
  (for secrets-in-logs findings)
