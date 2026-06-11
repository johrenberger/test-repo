# Webhook profile

Per-boundary guidance for the
[`integration-implementation`](../../SKILL.md) skill when the
target boundary is a webhook — outbound (this service emits
webhooks to other systems) or inbound (this service receives
webhooks from other systems). Read on demand; do not load
wholesale.

> **Scope:** This profile covers the webhook **delivery layer**
> for outbound webhooks and the webhook **reception / handler**
> layer for inbound webhooks. The handler's business logic
> inside an inbound webhook is **backend code** and is covered
> by [`backend-implementation`](../../../backend-implementation/SKILL.md).

## Detection cues

The target boundary matches this profile if any of the following
are present:

- HTTP route registered for `POST` with a path like
  `/webhook`, `/webhooks/<provider>`, `/hooks/<provider>`
- Outbound HTTP `POST` to a configured callback URL with
  signature header (`X-Signature`, `X-Hub-Signature-256`,
  `X-Stripe-Signature`, etc.)
- Provider SDK usage: Stripe, GitHub, Shopify, Twilio, Slack,
  PagerDuty, etc.
- Replay protection header (`X-Idempotency-Key`,
  `X-GitHub-Delivery`, `X-Request-Id`)

## Conventions to preserve

- **Signature scheme:** match the repo's existing signature
  scheme (HMAC-SHA256, HMAC-SHA1, RSA, provider-specific). Reuse
  the existing helper; do not introduce a new one.
- **Timestamp / replay protection:** match the repo's existing
  approach (timestamp window check, nonce store).
- **Idempotency:** match the repo's existing dedup approach
  (idempotency key, request id, provider delivery id).
- **Retry / queue:** match the repo's existing retry behavior
  (synchronous 200 + async retry, queued with backoff).
- **Logging:** match the repo. **Do not log the full payload**
  when it may contain PII or secrets; log the provider, event
  type, delivery id, and redacted relevant fields.
- **Error response:** match the repo's existing pattern
  (`2xx` to accept, `4xx` to signal client error, `5xx` to
  trigger provider retry).

## Required design checks (inbound)

| Check | Default expectation |
| --- | --- |
| Signature verification | before any other processing; failed → 4xx, no further work |
| Timestamp / replay protection | window check; expired → 4xx |
| Idempotency | dedup on provider delivery id; second delivery → 2xx, no work |
| Fast 2xx | respond 2xx quickly; defer heavy work to a queue |
| Logging without secrets | payload redaction list documented |
| Observability | correlation id propagated; event type logged |

## Required design checks (outbound)

| Check | Default expectation |
| --- | --- |
| Signature | signed with the consumer's shared secret / private key |
| Timeout | explicit, not default |
| Retry | bounded with backoff, or explicit no-retry rationale |
| Idempotency | delivery id; consumer can dedup |
| Logging | delivery id, target URL (redacted if it contains secrets), response status |
| Backpressure | queue depth bounded; drop or reject with explicit policy |

## Required tests

At minimum, cover:

- valid signature → accepted
- invalid signature → 4xx, no business logic run
- missing signature → 4xx
- expired timestamp (replay attack) → 4xx
- duplicate delivery → 2xx, no duplicate effect
- payload parse error → 4xx (or 5xx if the parser itself
  failed; depends on repo policy)
- response timing — 2xx returned within an acceptable budget
  even when the work is queued

For each, use a test double
(mocked HTTP server, recorded fixture, MSW, Nock, WireMock).
**Do not call real provider webhooks from tests.**

## Forbidden actions

- **Do not call real provider endpoints** from tests.
- **Do not commit webhook secrets** (signing keys, shared
  secrets). Use placeholders and env vars.
- **Do not introduce a new signature scheme** without explicit
  approval.
- **Do not log raw payload contents** for events that may
  contain PII (e.g. user data, payment data).
- **Do not bypass the orchestrator** when the task also
  touches pure backend or frontend code.

## Small example (inbound)

```typescript
// github-webhook-handler.ts
export class GitHubWebhookHandler {
  constructor(
    private readonly verifier: SignatureVerifier, // matches repo's helper
    private readonly dedup: Dedup,                // matches repo's dedup
    private readonly queue: Queue,                // matches repo's queue
    private readonly logger: Logger,
  ) {}

  async handle(req: Request): Promise<Response> {
    const sig = req.headers.get('X-Hub-Signature-256');
    const deliveryId = req.headers.get('X-GitHub-Delivery') ?? '';
    const event = req.headers.get('X-GitHub-Event') ?? '';
    if (!sig || !(await this.verifier.verify(req, sig))) {
      return new Response('invalid signature', { status: 401 });
    }
    if (await this.dedup.seen(deliveryId, '24h')) {
      return new Response('ok (duplicate)', { status: 200 });
    }
    const body = await req.json();
    this.queue.enqueue('github-webhook', { deliveryId, event, body });
    this.logger.info('webhook.received', { deliveryId, event });
    return new Response('ok', { status: 200 });
  }
}
```

```typescript
// github-webhook-handler.test.ts
it('rejects requests with invalid signature', async () => {
  const res = await handler.handle(makeReq({ sig: 'bogus' }));
  expect(res.status).toBe(401);
  expect(queue.enqueued).toHaveLength(0);
});

it('does not enqueue duplicate deliveries', async () => {
  dedup.seen.mockResolvedValueOnce(true);
  const res = await handler.handle(makeReq({ sig: 'good', deliveryId: 'abc' }));
  expect(res.status).toBe(200);
  expect(queue.enqueued).toHaveLength(0);
});

it('does not log the full payload', async () => {
  await handler.handle(makeReq({ sig: 'good', body: { secret: 'x' } }));
  expect(logger.lastInfo()).not.toMatchObject({ secret: expect.anything() });
});
```

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`rest-api.md`](rest-api.md),
  [`async-messaging.md`](async-messaging.md),
  [`file-batch.md`](file-batch.md),
  [`contract-testing.md`](contract-testing.md)
- Backend (handler logic): [`../../../backend-implementation/SKILL.md`](../../../backend-implementation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md),
  [`../../../security-review/SKILL.md`](../../../security-review/SKILL.md)
  (webhook security is a common source of CVEs)
