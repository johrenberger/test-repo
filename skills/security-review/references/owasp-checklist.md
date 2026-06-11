# OWASP-style checklist

Used by `security-review`. Adapted from the OWASP Top 10 and the
OWASP Application Security Verification Standard (ASVS), with the
focus narrowed to code-reviewable evidence.

## Severity scale

| Level | Definition | Required evidence |
| --- | --- | --- |
| Critical | Remote unauthenticated exploit, hard-coded credential, auth bypass, or data loss in production. | file:line + code excerpt, secret redacted |
| High | Exploitable with low-privilege access, or authz bypass for a single resource, or stored XSS / SQLi on a common path. | file:line + code excerpt |
| Medium | Requires authentication AND a non-trivial precondition, or information disclosure limited to non-sensitive data. | file:line + code excerpt |
| Low | Defense-in-depth gap, minor information disclosure, or hardening recommendation. | file:line |

## Checklist

For each item, the result is one of:

- `not_in_scope` — out of the reviewed change
- `not_present` — code/config does not contain this surface
- `covered` — present, with the existing mitigation cited
- `finding` — present, with the evidence and severity recorded

### Authentication

- [ ] **A1 — broken authentication:** weak credential storage (plain
  text, MD5, SHA-1, base64), missing rate limiting on auth, missing
  lockout, predictable session IDs, missing MFA on sensitive actions
- [ ] **A2 — broken cryptographic checks:** using `==` to compare
  hashes / signatures, using ECB mode, using a static IV, using
  `Math.random` / `Random` for security purposes
- [ ] **Missing authentication:** endpoints that should require auth
  but do not

### Authorization and ownership

- [ ] **IDOR / missing ownership check:** a resource is accessed by
  ID without verifying the requester owns it
- [ ] **Role bypass:** role / scope checks are missing, optional, or
  client-controlled
- [ ] **Privilege escalation:** role change paths that don't require
  elevated permissions

### Input validation and output encoding

- [ ] **Injection:** SQL injection, NoSQL injection, command injection,
  LDAP injection — query construction by string concatenation
- [ ] **XSS:** unescaped user input rendered in HTML, JS, or CSS
  contexts
- [ ] **Path traversal:** user-controlled path segments without
  normalization or `..` rejection
- [ ] **SSRF:** server-side fetch of a user-supplied URL without
  allow-listing
- [ ] **Insecure deserialization:** untrusted input deserialized to
  objects with side effects (Java `ObjectInputStream`, Python `pickle`,
  Node `node-serialize`, etc.)

### Sensitive logging and error handling

- [ ] **Sensitive data in logs:** passwords, tokens, PII, session IDs,
  full request bodies
- [ ] **Stack traces in production responses:** raw exceptions
  surfaced to the caller
- [ ] **Verbose error messages:** leaking internal paths, schema
  details, or version info

### Secrets and configuration

- [ ] **Hard-coded secrets:** credentials, API keys, private keys,
  tokens committed to the repo (Critical)
- [ ] **Insecure defaults:** debug flags, default admin credentials,
  permissive CORS (`*` for credentialed requests)
- [ ] **TLS / cookie security:** missing `Secure`, `HttpOnly`,
  `SameSite` on auth cookies; mixed-content resources

### Dependencies and supply chain

- [ ] **Vulnerable dependency:** known CVE in a runtime dependency
  (route to `dependency-change-review` for full analysis)
- [ ] **Unpinned dependency:** a runtime dep without a version range
  or hash

### Rate limiting and abuse

- [ ] **Missing rate limiting:** on auth, on password reset, on
  expensive endpoints

### Data exposure

- [ ] **Excess data in responses:** returning full database rows when
  a subset is needed, exposing internal IDs, exposing PII that the
  API surface does not require
- [ ] **Missing access controls at the storage layer:** the
  application enforces authz but the database row is fetchable
  directly

## How to record a finding

```yaml
- category: <owasp-id or sub-category>
  severity: <critical|high|medium|low>
  file: <path>
  lines: "<start>-<end>"
  summary: <one line>
  evidence_redacted: <code excerpt, secrets redacted as <REDACTED: kind>>
  exploitability: <one paragraph: who can trigger, what is the pre-condition>
  impact: <one paragraph: what is the worst realistic outcome>
  recommended_fix: <concrete fix, not "add validation">
  approval_required: <yes | no>  # yes if fix changes architecture or removes a feature
```

## False-positive uncertainty

If a checklist item is technically present but the surrounding
mitigation makes the finding unexploitable, record it as `covered`
with the mitigation cited — not as a finding. Do not invent
uncertainty. If unsure, record the finding with `severity: low` and
note the uncertainty in the evidence.
