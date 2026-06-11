# Dependency risk checklist

Used by `dependency-change-review`.

## Categories

Apply each category to the change set. A finding can map to multiple
categories.

### Necessity

- **unjustified new dependency** — a runtime dependency was added
  without a clear rationale in the diff (or the rationale is
  "convenience" / "cleaner code" / "best practice")
- **existing alternative** — a dependency was already in the project
  that could satisfy the new need; the new one was added
  unnecessarily
- **speculative dependency** — added for a feature not yet required
  by the current task

### Version risk

- **major version upgrade** — first major digit changed (e.g.
  `1.x` → `2.x`); treat as High by default; often requires
  architecture approval
- **breaking pre-release** — `0.x` or `-alpha` / `-beta` / `-rc`; treat
  as High
- **lockfile-bypassing version** — manifest allows a floating range
  (e.g. `^1.2.3` allowing `1.x.y`); the project's existing
  floating-pin policy applies

### Supply chain

- **unmaintained dependency** — no release in the last 12 months
  (record the date; do not invent)
- **single-maintainer dependency** — record the observation; flag
  for human judgment
- **typosquatting risk** — package name is a common misspelling of a
  popular package (e.g. `reqests` vs. `requests`); Critical if it
  appears to be a real install target
- **transitive explosion** — a single new dependency brings in a
  large transitive set; record the rough size
- **postinstall script** — a dependency with a `postinstall` (npm) /
  equivalent; record whether the script does anything beyond
  compile / codegen

### License

- **incompatible license** — license is not in the project's
  acceptable license list (record the SPDX identifier; do not
  decide compatibility for the project)
- **unknown license** — no LICENSE file or no recognizable SPDX
  identifier in the package; record for human review

### Placement

- **runtime dep in devDeps** — a package that ships in the production
  artifact is declared in `devDependencies` (Node) / `[project.optional-dependencies]`
  (Python) / similar
- **dev-only dep in deps** — a package used only for testing /
  building declared as a runtime dependency
- **test-only dep in production test setup** — record the case and
  recommend the right placement

### Lockfile / manifest consistency

- **lockfile missing** — manifest changed, lockfile did not (e.g.
  `package.json` updated without `package-lock.json`); High
- **lockfile drift** — lockfile and manifest disagree; High
- **lockfile committed in a repo that ignores it** — repo convention
  violated; record the violation, do not silently fix

### Build tool / plugin

- **build-tool upgrade** — Gradle plugin, Webpack, Vite, esbuild,
  Rollup, etc. upgraded; record the change and the version delta
- **CI action upgrade** — `actions/checkout@v3` → `v4`, etc.; record
  the change; major version upgrades are typically a blocker
- **tool added that duplicates an existing tool** — e.g. two
  linters; record and recommend dropping one

### Duplicate / overlapping

- **duplicate functionality** — two packages doing the same thing
  (e.g. `lodash` + `ramda`, `axios` + `node-fetch`); record the
  observation, recommend consolidating

## Severity scale

| Level | Use when |
| --- | --- |
| Critical | typosquat risk, hard-blocked license, known CVE, missing lockfile on a runtime dep |
| High | major version upgrade of a runtime dep, build-tool change, lockfile drift, runtime dep without rationale |
| Medium | minor version upgrade of a runtime dep, license unknown, single-maintainer risk, dev/runtime placement wrong |
| Low | patch version upgrade, transitive explosion small, version floating policy question |

## Required fields for a finding

```yaml
- change: "<package@old → package@new, or new package, or removed>"
  category: <category from the list above>
  severity: <critical|high|medium|low>
  evidence: <file:lines + excerpt>
  recommendation: <concrete recommendation, not "consider X">
  rationale_required: <yes | no>  # yes if the change requires explicit human rationale
  escalation_target: <agent or "none">
```

## When to escalate (blocker)

Stop the review and create a blocker via `task-state-management`:

- Major version upgrade of a runtime dependency
- Package manager migration
- Dependency with known security risk
- Production / runtime dependency addition without rationale

Escalation target: `ARCHITECT_AGENT` for major upgrades and migrations,
`SECURITY_ANALYST_AGENT` for security risk.
