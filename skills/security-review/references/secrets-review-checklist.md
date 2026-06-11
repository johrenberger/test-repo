# Secrets review checklist

Used by `security-review`. Focused on secret handling, separate from
the broader OWASP checklist because secrets are the most common
Critical finding and the easiest to automate.

## What counts as a secret

Any of:

- API key, access token, refresh token, OAuth client secret
- Database connection string with credentials in-line
- Private key (PEM, SSH, GPG)
- Cloud provider credentials (AWS, GCP, Azure, etc.)
- Webhook signing secrets
- CI / CD tokens (GitHub, GitLab, CircleCI, Jenkins)
- Customer-supplied secrets captured in logs
- Passwords, even hashed (verify the hash algorithm is acceptable)

## Where to look

For each, record the path and a redacted excerpt.

- Source files (`*.py`, `*.js`, `*.ts`, `*.java`, `*.go`, `*.cs`, etc.)
- Config files (`*.yml`, `*.yaml`, `*.json`, `*.toml`, `*.ini`,
  `*.properties`, `*.env*`)
- Infrastructure as code (`*.tf`, `*pulumi*`, `cloudformation/*`,
  `ansible/*`)
- Container build (`Dockerfile`, `docker-compose*.yml`)
- CI / CD (`.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`,
  `.circleci/config.yml`)
- Documentation examples (a code sample with a real key is still a
  finding)
- Test fixtures (real keys in fixtures are still a finding; faked
  keys are not)
- Source-map or build artifacts (a `*.map` or `dist/` that contains
  keys is a finding)

## Detection patterns

These are heuristic, not exhaustive. Pair with a real secret scanner
in CI when available.

| Pattern | Regex (informal) |
| --- | --- |
| AWS access key | `AKIA[0-9A-Z]{16}` |
| AWS secret key | `(?i)aws.{0,20}(secret|sk).{0,5}['\"][0-9a-zA-Z/+=]{40}['\"]` |
| GitHub token | `gh[pousr]_[A-Za-z0-9_]{36,255}` |
| Generic API key | `(?i)(api[_-]?key\|apikey).{0,10}['\"][0-9a-zA-Z]{20,}['\"]` |
| Private key header | `-----BEGIN (RSA \|EC \|OPENSSH \|)PRIVATE KEY-----` |
| Generic password | `(?i)(password\|passwd\|pwd).{0,10}['\"][^'\"]{6,}['\"]` |
| JWT | `eyJ[A-Za-z0-9_-]{10,}\\.eyJ[A-Za-z0-9_-]{10,}\\.[A-Za-z0-9_-]{10,}` |

## How to record a finding

For every secret hit:

- `severity: critical` (a committed credential is always Critical
  regardless of scope)
- `file` and `lines`
- `evidence_redacted`: the line with the secret value replaced by
  `<REDACTED: <kind>>` — never include the actual secret
- `recommendation`:
  1. **Rotate the secret immediately** (call this out in
     `impact` — assume the secret is compromised as soon as it's in
     the repo, even if the repo is private)
  2. Move the secret to a secret store (Vault, AWS Secrets Manager,
     GitHub Actions secrets, etc.)
  3. Reference it at runtime via the secret store's API
  4. Add a pre-commit hook or CI gate (e.g. `gitleaks`,
     `trufflehog`, `detect-secrets`) to prevent recurrence

## Non-findings

These are NOT findings (record them as `covered`, not as findings):

- Public keys (`*.pub`)
- Placeholder strings that match the pattern but are clearly
  documentation (`"your-api-key-here"`, `example.com`, `xxxxx`)
- Test fixtures that use a clearly-fake key (`"test-key-do-not-use"`,
  `00000000-0000-0000-0000-000000000000`)
- Local-only `.env` files that are explicitly in `.gitignore` AND not
  present in the working tree (still flag if present in tree)

## When to stop and create a blocker

Stop the review and create a blocker via `task-state-management` if:

- A secret appears to be **active** (not just leftover from history)
  AND the secret has permissions beyond read-only.
- A secret is committed to a public-facing branch.
- A secret is committed and the repository is public.
