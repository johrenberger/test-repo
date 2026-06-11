# Contract testing profile

Per-boundary guidance for the
[`integration-implementation`](../../SKILL.md) skill when the
target boundary needs explicit contract tests — verifying that
the client and server (or producer and consumer, or this
service and a partner) agree on the request / response /
message / file shape.

> **Scope:** This profile covers the **contract test artifacts**
> and the **test-driven discovery** of incompatibilities. The
> implementation work that surfaces an incompatibility (e.g.
> a client that needs to handle a new field) is **integration
> implementation**; the contract test itself is the artifact
> that drives that work.

## Detection cues

The target boundary matches this profile if any of the following
are present:

- Pact files (`*.json`, `pacts/`, Pact Broker config)
- OpenAPI spec checked into the repo (`openapi.yaml`,
  `openapi.json`, `swagger.yaml`)
- AsyncAPI spec checked into the repo
- GraphQL schema file (`schema.graphql`, `*.gql`)
- JSON Schema files (`*.schema.json`)
- Existing contract test runner: `pact`, `pact-python`,
  `pact-go`, `pact-net`, `dredd`, `schemathesis`,
  Spectral, `graphql-inspector`

## Conventions to preserve

- **Contract tooling:** match the repo's existing tooling
  (Pact, schemathesis, Spectral, Spectral CLI, etc.). Do not
  introduce new tooling as part of an unrelated change.
- **Spec location:** match the repo (repo root, `spec/`,
  `contracts/`, `api/`).
- **Consumer-driven vs provider-driven:** match the repo's
  direction.
- **CI integration:** match the repo's existing CI hook for
  contract verification.

## Required design checks

| Check | Default expectation |
| --- | --- |
| Spec is current | spec reflects the version of the contract being implemented |
| Backwards compatibility | additive changes only; breaking changes have a migration plan |
| Coverage | at least the changed operation / message / endpoint is covered |
| Broker / shared spec | contract is published to broker / shared location when one exists |
| CI gate | contract check runs in CI |

## Required tests

At minimum, cover:

- happy path — request / response match the spec
- required fields — missing required field → 4xx
- additional fields — server tolerates extra fields
  (forward-compat)
- type mismatch — wrong type → 4xx (or graceful ignore, per
  repo policy)
- enum / format — invalid value → 4xx
- auth contract — missing / invalid auth → 4xx

For each, use the existing contract tooling
(`pact-jvm`, `pact-python`, `pact-go`,
`schemathesis`, Spectral rules, etc.). **Do not call real
production endpoints.**

## Forbidden actions

- **Do not introduce a new contract testing tool**
  (Pact → Spectral, schemathesis → Pact) without explicit
  approval.
- **Do not commit contract secrets** (e.g. a Pact Broker token
  used to publish contracts). Use env vars / CI secrets.
- **Do not skip CI integration** for new contract tests; a
  contract test that does not run is not a contract test.
- **Do not bypass the orchestrator** when the task also
  touches pure backend or frontend code.

## Small example

Adding a Pact contract test for a `getUser` client (consumer
side):

```typescript
// user-client.pact.test.ts
import { pactWith } from 'pact-ng';

pactWith({ consumer: 'frontend', provider: 'user-service' }, provider => {
  describe('getUser', () => {
    it('returns a user when id exists', async () => {
      await provider.given('user 1 exists')
        .uponReceiving('a request for user 1')
        .withRequest({ method: 'GET', path: '/users/1' })
        .willRespondWith({
          status: 200,
          headers: { 'Content-Type': 'application/json; charset=utf-8' },
          body: { id: '1', name: 'Ada', email: 'a@example.com' },
        });
      const user = await client.getUser('1');
      expect(user.name).toBe('Ada');
    });

    it('returns 404 when id is unknown', async () => {
      await provider.given('user 99 does not exist')
        .uponReceiving('a request for user 99')
        .withRequest({ method: 'GET', path: '/users/99' })
        .willRespondWith({ status: 404, body: { error: 'not_found' } });
      await expect(client.getUser('99')).rejects.toThrow(/404/);
    });
  });
});
```

The contract artifact (`pacts/frontend-user-service.json`) is
generated from these tests and can be published to a Pact
Broker (or a shared location) for the provider to verify
against. The provider side runs the same contract and rejects
incompatibilities.

## OpenAPI / schema-driven contract test

```yaml
# openapi.yaml — excerpt
paths:
  /users/{id}:
    get:
      parameters:
        - in: path
          name: id
          required: true
          schema: { type: string }
      responses:
        '200':
          content:
            application/json:
              schema: { $ref: '#/components/schemas/User' }
        '404':
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Error' }
```

```bash
# schemathesis — runs requests against the spec, surface
# non-conforming responses
schemathesis run openapi.yaml --base-url http://localhost:8080 \
  --checks all --hypothesis-max-examples=50
```

If the running server returns a 200 with a body that does not
match the `User` schema, schemathesis reports a contract drift
finding, which is then routed back to
[`backend-implementation`](../../../backend-implementation/SKILL.md)
or the relevant implementation skill for the fix.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`rest-api.md`](rest-api.md),
  [`async-messaging.md`](async-messaging.md),
  [`webhook.md`](webhook.md),
  [`file-batch.md`](file-batch.md)
- Pact docs and broker:
  - [Pact Docs](https://docs.pact.io)
  - [Pact Broker](https://pact-foundation.github.io/pact-broker/)
- Schemathesis: [schemathesis.io](https://schemathesis.io)
- Spectral (linting OpenAPI): [stoplight.io/spectral](https://stoplight.io/open-source/spectral)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md),
  [`../../../dependency-change-review/SKILL.md`](../../../dependency-change-review/SKILL.md)
  (for new tooling)
