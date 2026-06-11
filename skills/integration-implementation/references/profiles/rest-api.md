# REST / API profile

Per-boundary guidance for the
[`integration-implementation`](../../SKILL.md) skill when the
target boundary is an external or cross-service REST / GraphQL
HTTP API call. Read on demand; do not load wholesale.

> **Scope:** This profile covers the **client side** of an
> HTTP API call from this service to another system. The
> **server side** (the controller / route that accepts the
> call) is covered by
> [`backend-implementation`](../../../backend-implementation/SKILL.md).

## Detection cues

The target boundary matches this profile if any of the following
are present:

- HTTP client usage: `fetch`, `axios`, `undici`, `got`, `requests`
  (Python), `RestTemplate` / `WebClient` (Spring), `HttpClient`
  (Angular), `requests` / `httpx` (Python), `net/http` (Go),
  `HttpClient` / `IHttpClientFactory` (.NET)
- GraphQL client: `apollo-client`, `urql`, `@tanstack/react-query`
  with GraphQL endpoint, `graphql-request`
- OpenAPI / Swagger generated client
- Contract file: `openapi.yaml`, `openapi.json`,
  `swagger.yaml`, `*.graphql`, `schema.graphql`
- Base URL / host config in env vars, config, or
  `application.{yml,properties}`

## Conventions to preserve

- **HTTP client:** match the repo's existing client
  (`fetch` wrapper, `axios` instance, Spring `RestTemplate`,
  Angular `HttpClient`, etc.). Do not introduce a new client
  library.
- **Base URL config:** match the repo's config pattern
  (env var, `application.yml`, config file, vault).
- **Auth:** match the repo's auth pattern (header-based bearer
  token, mTLS, signed request, OAuth client credentials).
  Reuse the existing auth helper, do not introduce a new one.
- **Serialization:** match the repo (JSON via Jackson, Gson,
  kotlinx.serialization, encoding/json, System.Text.Json).
- **Error mapping:** match the repo's existing error model
  (typed exception, problem-detail, custom error class).
- **Logging:** match the repo's logging pattern. **Do not log
  auth headers, tokens, or sensitive payload fields.** Redact
  as `<REDACTED: kind>`.
- **Correlation / tracing:** match the repo's correlation
  pattern (request id header, OpenTelemetry, custom
  correlation id).
- **Retries:** match the repo's retry strategy. Default
  expectation: bounded retries with backoff for idempotent
  verbs (`GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`) only;
  `POST` retries require an idempotency key.

## Required design checks

| Check | Default expectation |
| --- | --- |
| Timeout | explicit, not default |
| Retry | bounded with backoff, or explicit no-retry rationale |
| Idempotency | idempotency key for `POST` retries, or at-most-once rationale |
| Error classification | retryable (`5xx`, `429`, network) vs non-retryable (`4xx` other than `429`) |
| Logging without secrets | payload field redaction list documented |
| Observability | correlation id propagated to downstream |
| Contract compatibility | version pinned, additive changes only |
| Backpressure / rate limit | `429` handling + `Retry-After` honored where relevant |

## Required tests

At minimum, cover:

- success (2xx)
- 4xx (validation / auth / not-found)
- 5xx (server error)
- timeout
- auth failure
- malformed response (invalid JSON, missing required field)

For each, the test must use a test double
(mock, recorded fixture, MSW / WireMock / Nock / VCR, contract
test) — **never a real production endpoint**.

## Forbidden actions

- **Do not call real production endpoints** from tests.
- **Do not commit credentials or tokens.** Use placeholders.
- **Do not introduce a new HTTP client library** (`axios` →
  `ky`, `requests` → `httpx`, etc.) as part of an unrelated
  change.
- **Do not change the contract** without documenting
  compatibility impact in the implementation report.
- **Do not introduce a new auth pattern** (e.g. switching from
  bearer to mTLS) without explicit approval.
- **Do not log secrets.** If the existing client logs the full
  request, scope the change to the affected call only and
  document the redaction list.
- **Do not bypass the orchestrator** when the task also
  touches pure backend or frontend code.

## Small example

Adding a `getUser` call to an external API, with explicit
timeout, retry, error classification, and redaction:

```typescript
// user-client.ts — typed client, matches repo's fetch wrapper
const USER_FIELDS_TO_REDACT = ['email', 'phone'] as const;

export class UserClient {
  constructor(
    private readonly baseUrl: string,
    private readonly auth: Auth,
    private readonly logger: Logger,
    private readonly correlation: Correlation,
  ) {}

  async getUser(id: string, signal?: AbortSignal): Promise<User> {
    const url = new URL(`/users/${encodeURIComponent(id)}`, this.baseUrl);
    const headers: Record<string, string> = {
      'Authorization': this.auth.bearer(),            // <-- auth helper, not raw
      'X-Correlation-Id': this.correlation.id(),
      'Accept': 'application/json',
    };
    const res = await fetch(url, { method: 'GET', headers, signal });
    if (!res.ok) {
      // classify, do not retry 4xx; do retry 5xx / 429 / network
      throw new UserClientError(res.status, await res.text());
    }
    const data = await res.json();
    this.logger.info('user.fetched', {
      id,
      status: res.status,
      correlation: headers['X-Correlation-Id'],
    });
    return redactFields(data, USER_FIELDS_TO_REDACT);
  }
}
```

```typescript
// user-client.test.ts — Nock recorded fixture, no real endpoint
import nock from 'nock';

it('retries on 5xx and succeeds', async () => {
  nock('https://api.example.com').get('/users/1').reply(503);
  nock('https://api.example.com').get('/users/1').reply(200, { id: '1', name: 'Ada' });
  const user = await client.getUser('1');
  expect(user.name).toBe('Ada');
});

it('does not retry on 4xx', async () => {
  nock('https://api.example.com').get('/users/1').reply(404);
  await expect(client.getUser('1')).rejects.toThrow(/404/);
});

it('redacts sensitive fields in logs', async () => {
  nock('https://api.example.com').get('/users/1').reply(200, { id: '1', email: 'a@x' });
  await client.getUser('1');
  expect(logger.lastInfo()).not.toMatchObject({ email: expect.anything() });
});
```

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`async-messaging.md`](async-messaging.md),
  [`webhook.md`](webhook.md),
  [`file-batch.md`](file-batch.md),
  [`contract-testing.md`](contract-testing.md)
- Server side: [`../../../backend-implementation/SKILL.md`](../../../backend-implementation/SKILL.md)
- Contract: [`contract-testing.md`](contract-testing.md) for
  Pact / OpenAPI tooling
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md),
  [`../../../security-review/SKILL.md`](../../../security-review/SKILL.md)
