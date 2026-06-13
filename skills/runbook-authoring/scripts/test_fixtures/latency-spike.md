# Bad runbook

## Purpose

Triage.

## Scope

order-checkout.

## Symptoms

- Slow.

## Severity guidance

SEV-2.

## Prerequisites / access requirements

- kubectl

## Safe diagnostic commands

Check logs:

```bash
kubectl logs -l app=order-service
```

## Mitigation options

Rollback.

## Validation after mitigation

Verify:

```bash
kubectl logs -l app=order-service
```

## Known risks

- Risk.

## Owner / team / contact

- Owner: alice

## Cross-references

- ADR-0005
