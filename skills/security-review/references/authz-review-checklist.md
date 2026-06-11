# Authz review checklist

Used by `security-review`. Focused on authorization and ownership
checks. Authentication is in the OWASP checklist; this file is the
detailed drill-down for the access-control surface.

## What to inventory

For each API endpoint, RPC handler, or data-access method:

- **Endpoint / method** — exact path or signature
- **Authentication required?** — yes / no / N/A (public)
- **Authorization required?** — yes / no / N/A (public)
- **Ownership check?** — does the handler verify the requester owns
  the resource? On what field? (user_id, tenant_id, org_id, etc.)
- **Role / scope check?** — does the handler verify the requester has
  the right role? On what role model?
- **Failure response** — 401, 403, 404 (for existence-hiding), or
  something else

## Common failure patterns

These are the patterns that the checklist is looking for.

### IDOR (Insecure Direct Object Reference)

- A handler accepts a resource ID from the path or query.
- It loads the resource.
- It returns the resource without checking that the requester owns it.

**Severity:** typically High (or Critical if the resource is
sensitive).

### Missing role check

- A handler accepts a request from an authenticated user.
- The action requires a specific role (admin, owner, etc.).
- The handler does not check the role, or the check is on a field the
  client controls.

**Severity:** High (Critical if the role grants write to all
resources).

### Tenant boundary leak

- A multi-tenant system.
- A handler loads a resource by ID without filtering by tenant.
- The resource may belong to another tenant.

**Severity:** Critical (data leak between tenants is a Critical
finding).

### BOLA / BFLA (API-specific)

- The API exposes an object ID.
- A user with low privilege can read or modify an object owned by a
  user with higher privilege.

**Severity:** Critical.

### Broken access control on a state transition

- A handler allows a state transition (e.g. `cancel`, `refund`,
  `delete`).
- The handler checks the source state but not the requester's
  authority to perform the transition.

**Severity:** typically High.

## How to record a finding

```yaml
- category: <idor | missing-role | tenant-leak | bola | bfla |
  broken-state-transition | other>
  severity: <critical|high|medium|low>
  file: <path>
  lines: "<start>-<end>"
  endpoint_or_method: <signature>
  summary: <one line>
  evidence_redacted: <code excerpt, IDs redacted as <REDACTED: id>>
  exploitability: <one paragraph>
  impact: <one paragraph>
  recommended_fix: <concrete fix — e.g. "load resource with filter on
  tenant_id == requester.tenant_id; return 404 if not found">
  approval_required: <yes | no>
```

## Defensive patterns (record as `covered`)

- **Resource load + check pattern** — load the resource with the
  requester ID as a filter; if not found, return 404 (also hides
  existence).
- **Policy / capability checks** — a single `authorize(action, resource)`
  call at the top of the handler. Note which library or pattern
  (`pundit`, `casbin`, `casl`, custom `IAuthorizationService`, etc.).
- **Existence-hiding 404s** — when a resource does not exist OR the
  requester does not own it, return 404 (not 403). Note this only when
  the pattern is consistent.
- **Centralized middleware** — authn / authz is enforced in middleware,
  not in each handler. Note any gaps (handlers that bypass the
  middleware for "internal" reasons).
