# Async messaging profile

Per-boundary guidance for the
[`integration-implementation`](../../SKILL.md) skill when the
target boundary is a message queue, pub/sub, or event-streaming
system (Kafka, RabbitMQ, SQS/SNS, EventBridge, Pub/Sub, Service
Bus, NATS, Redis Streams, etc.). Read on demand; do not load
wholesale.

> **Scope:** This profile covers **producers and consumers** of
> messages at the boundary. The message-handling business
> logic inside the consumer is **backend code** and is covered
> by [`backend-implementation`](../../../backend-implementation/SKILL.md).
> This skill owns the producer / consumer wiring, the schema,
> the retry / DLQ / ordering behavior, and the related tests.

## Detection cues

The target boundary matches this profile if any of the following
are present:

- Kafka client (`kafkajs`, `node-rdkafka`, `confluent-kafka`,
  `kafka-python`, `aiokafka`, Spring Kafka)
- RabbitMQ client (`amqplib`, `pika`, Spring AMQP,
  `RabbitMQ.Client` (.NET))
- AWS SQS / SNS / EventBridge SDK usage
- GCP Pub/Sub client
- Azure Service Bus / Event Grid
- NATS client
- Redis Streams
- Schema registry reference (Confluent, Apicurio, etc.)
- AsyncAPI spec (`asyncapi.yaml`, `asyncapi.json`)

## Conventions to preserve

- **Client / SDK:** match the repo's existing client. Do not
  introduce a new client library as part of an unrelated
  change.
- **Topic / queue naming:** match the repo's naming convention.
- **Serialization:** match the repo (Avro, Protobuf, JSON,
  CloudEvents). Reuse the existing schema registry reference
  if present.
- **Producer patterns:** match the repo (transactional outbox,
  fire-and-forget with retry, idempotent producer).
- **Consumer patterns:** match the repo (manual ack, listener
  container, batch consumer).
- **Error handling:** match the repo's existing classification
  (retryable vs poison message, DLQ behavior).
- **Logging:** match the repo. **Do not log payload contents**
  when they may contain PII or secrets; log message id, key,
  topic, partition, offset, correlation id.
- **Correlation / tracing:** match the repo's correlation
  pattern (message header, OpenTelemetry context propagation).

## Required design checks

| Check | Default expectation |
| --- | --- |
| Timeout | consumer poll / processing timeout, explicit |
| Retry | bounded with backoff for retryable errors; non-retryable → DLQ |
| Idempotency | dedup key, dedup window, or at-least-once + idempotent processor rationale |
| Error classification | retryable (transient) vs non-retryable (poison) |
| Ordering | preserved within partition / key, or explicit relaxation |
| DLQ | DLQ topic / queue named; non-retryable messages routed there |
| Schema compatibility | backward / forward / full, pinned, additive changes only |
| Backpressure | consumer prefetch / max-in-flight bounded; producer idempotent |

## Required tests

At minimum, cover:

- success (consumer processes message, ack)
- retryable error (transient failure, retry, eventually
  success)
- non-retryable error (poison message, routed to DLQ)
- duplicate delivery (idempotency: same message id twice, only
  one effect)
- ordering (within partition, messages processed in order)
- timeout (consumer takes too long, message is redelivered or
  routed per repo policy)
- schema mismatch (new field added, old consumer still works
  under backward-compat policy)

For each, use a test double
(embedded broker, Testcontainers if the repo already uses
them, in-memory queue, or recorded fixtures). **Do not use a
real production broker.**

## Forbidden actions

- **Do not introduce a new broker / queue technology** (Kafka →
  RabbitMQ, SQS → Pub/Sub, etc.) without explicit approval and
  a [`dependency-change-review`](../../../dependency-change-review/SKILL.md)
  gate.
- **Do not change the schema compatibility mode** (e.g.
  backward → full) without an explicit migration plan.
- **Do not commit credentials or broker config** that
  references production.
- **Do not run load tests** against a real broker unless
  explicitly requested.
- **Do not introduce a new serialization format** (Avro →
  Protobuf) without explicit approval.
- **Do not log message payloads** that may contain PII or
  secrets; log the message id / key / topic / offset only.
- **Do not bypass the orchestrator** when the task also
  touches pure backend or frontend code.

## Small example

A consumer that processes `UserCreated` events with explicit
retry, DLQ for poison messages, idempotency, and redacted
logging:

```typescript
// user-created-consumer.ts
const REDACTED_FIELDS = ['email', 'phone'] as const;

export class UserCreatedConsumer {
  async handle(msg: KafkaMessage, ctx: ConsumerContext): Promise<void> {
    const event = parseUserCreated(msg.value); // schema-validated
    if (!event) {
      ctx.logger.warn('user-created.parse_failed', { offset: msg.offset });
      ctx.dlq.publish(msg, 'parse_failed');   // <-- poison → DLQ, do not retry
      ctx.commit();
      return;
    }
    const dedupKey = `user-created:${event.id}`;
    if (await ctx.dedup.seen(dedupKey, /* window: */ '24h')) {
      ctx.commit();                            // <-- duplicate, drop
      return;
    }
    try {
      await processUserCreated(event);
      ctx.dedup.remember(dedupKey, '24h');
      ctx.commit();
    } catch (e) {
      if (isTransient(e)) {
        ctx.nack(/* requeue */ true);          // <-- retryable, requeue
        return;
      }
      ctx.logger.error('user-created.poison', { id: event.id, error: String(e) });
      ctx.dlq.publish(msg, 'processing_failed');
      ctx.commit();
    }
  }
}
```

```typescript
// user-created-consumer.test.ts — embedded broker, no real Kafka
it('routes poison messages to DLQ', async () => {
  const msg = makeKafkaMessage({ invalid: 'shape' });
  await consumer.handle(msg, ctx);
  expect(ctx.dlq.published).toContainEqual(expect.objectContaining({ reason: 'parse_failed' }));
  expect(ctx.committed).toBe(true);
});

it('deduplicates redelivered messages', async () => {
  ctx.dedup.seen.mockResolvedValueOnce(true);
  await consumer.handle(makeKafkaMessage({ id: '1' }), ctx);
  expect(ctx.committed).toBe(true);
  expect(processUserCreated).not.toHaveBeenCalled();
});

it('does not log payload PII fields', async () => {
  await consumer.handle(makeKafkaMessage({ id: '1', email: 'a@x' }), ctx);
  expect(logger.lastInfo()).not.toMatchObject({ email: expect.anything() });
});
```

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`rest-api.md`](rest-api.md),
  [`webhook.md`](webhook.md),
  [`file-batch.md`](file-batch.md),
  [`contract-testing.md`](contract-testing.md)
- Backend (consumer logic): [`../../../backend-implementation/SKILL.md`](../../../backend-implementation/SKILL.md)
- Dependency review: [`../../../dependency-change-review/SKILL.md`](../../../dependency-change-review/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md),
  [`../../../security-review/SKILL.md`](../../../security-review/SKILL.md)
