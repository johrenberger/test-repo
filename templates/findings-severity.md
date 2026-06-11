# Findings severity (shared)

Generic finding-severity record used by review and risk skills
(`code-change-review`, `security-review`, `dependency-change-review`,
`database-migration-safety`). The skill-specific references expand
on this with skill-specific categories and evidence rules.

## Severity levels

| Level | Definition | Required evidence | Default action |
| --- | --- | --- | --- |
| Critical | Causes data loss, security breach, production outage, or auth bypass in a realistic scenario. Architecture violation that must be addressed before merge. | file:line + code excerpt, secrets redacted as `<REDACTED: kind>` | Blocks merge; must be fixed or formally accepted with a decision-log entry |
| High | Clear bug or significant design problem that affects most users or causes maintainability pain. Missing test for a critical path. | file:line + code excerpt | Blocks merge; addressed before merge unless formally accepted |
| Medium | Real concern that should be addressed before merge if scope allows, but not strictly blocking. | file:line + excerpt | Address before merge when feasible; record in follow-up otherwise |
| Low | Real concern that can be addressed in a follow-up. | file:line | Track; do not block |
| Nit | Subjective preference; only record when it materially affects maintainability or violates an explicit repo convention. | file:line, link to convention | Track; do not block |

## Required fields for a finding

Every finding (regardless of severity) must include:

```yaml
- id: <stable id, e.g. SEC-001, CR-002, MIG-003>
  category: <skill-specific category>
  severity: <critical|high|medium|low|nit>
  file: <path or scope>
  lines: "<start>-<end>"  # or "n/a" if file-less
  summary: <one line>
  evidence: <code excerpt or statement, secrets redacted>
  recommendation: <concrete fix, not "consider X">
  approval_required: <yes | no>  # yes for blockers
  source_skill: <which skill produced this finding>
  created_at: <ISO-8601>
```

## Severity → action matrix

| Severity | Blocks merge? | Required for approval gate? | Routes to |
| --- | --- | --- | --- |
| Critical | yes | yes | `ARCHITECT_AGENT` if architecture-related, otherwise `SECURITY_ANALYST_AGENT` for security, or `SOFTWARE_ENGINEER_AGENT` for code |
| High | yes | yes | Same routing as Critical |
| Medium | recommended | no (track) | `SOFTWARE_ENGINEER_AGENT` for follow-up |
| Low | no | no | `task-state-management` follow-up task |
| Nit | no | no | Inline or follow-up; not a blocker |

## Cross-skill consistency

When the same finding shows up in multiple skills (e.g. a hard-coded
secret appears in both `code-change-review` and `security-review`):

- The `security-review` finding is the canonical record.
- `code-change-review` cross-references the security finding by ID
  rather than duplicating evidence.
- The `dependency-change-review` finding is canonical for dependency
  risks; `security-review` cross-references.
- The `database-migration-safety` finding is canonical for
  destructive migrations; `code-change-review` cross-references.

## How to reference a finding from another report

```markdown
- See `security-review-report.md#SEC-001` (Critical, hard-coded
  AWS access key) — already recorded; do not duplicate.
```
