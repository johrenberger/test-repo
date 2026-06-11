# Incident timeline

Output of the
[`incident-triage`](../../../../skills/incident-triage/SKILL.md)
skill. Timestamped record of incident events, facts, and
hypothesis updates. Save to
`/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-timeline.md`.

The timeline is the load-bearing artifact for both the
active investigation and the post-incident review. It must
be **append-mostly** (entries are added in order; entries
are edited only to correct a fact, never to hide one).

## Template

```markdown
# Incident timeline for <TASK_ID>

- **Incident ID:** <INC-YYYYMMDD-NNN>
- **Generated at:** <ISO-8601>
- **Last updated:** <ISO-8601>
- **Severity:** <SEV-1 | SEV-2 | SEV-3 | SEV-4>
- **Status:** <investigating | mitigating | monitoring |
  resolved | post-incident>

## Conventions

- All timestamps are UTC in `YYYY-MM-DDTHH:MM:SSZ` form.
- Each entry has a `kind`: `fact` (sourced), `hypothesis`
  (labeled), `action` (taken, by whom), `decision`
  (recorded), or `communication` (sent).
- Sources are paths or log lines, not free-form
  recollections.

## Timeline

| UTC timestamp | Kind | Event | Source / owner |
| --- | --- | --- | --- |
| <UTC-ts> | fact | <one line> | `<path>` or `<log>` or `<metric>` |
| <UTC-ts> | fact | <one line> | `<...>` |
| <UTC-ts> | hypothesis | H1 raised: <one line> | <owner> |
| <UTC-ts> | action | <one line> | <owner> |
| <UTC-ts> | decision | <one line> | `decisions/<id>.md` |
| <UTC-ts> | communication | <one line> | <channel> |
| <UTC-ts> | fact | <one line> | `<...>` |
| <UTC-ts> | hypothesis | H1 confirmed: <one line> | <evidence> |
| <UTC-ts> | hypothesis | H2 ruled out: <one line> | <evidence> |
| <UTC-ts> | fact | <one line> | `<...>` |
```

## Field rules

- Entries are added in order; out-of-order entries are
  marked with a `(late entry)` note.
- `fact` entries must have a source path / log line /
  metric. A fact without a source is moved to
  `hypothesis`.
- `hypothesis` entries must have a confidence level and an
  evidence path. Updates to the hypothesis (confirmed,
  ruled out, refined) are new entries, not edits.
- `action` entries must have an owner; `decision` entries
  must link to `decisions/<id>.md`.
- `communication` entries must have a channel; sensitive
  details are redacted (`<REDACTED: kind>`).

## When to add entries

- Whenever a fact is observed.
- Whenever a hypothesis is raised, refined, confirmed, or
  ruled out.
- Whenever a mitigation option is taken or rejected by the
  operator.
- Whenever a decision is recorded.
- Whenever a status update is sent (internal or external).
- Whenever severity or status changes.

## When the incident is resolved

Append a final `fact` entry recording the resolution time,
the mitigation that worked, and the next state. The
post-incident review builds on the timeline; do not delete
or rewrite history.

## Provenance

- Produced by `incident-triage` (draft).
- Output path:
  `/data/.openclaw/workspace/tasks/<TASK_ID>/reports/incident-timeline.md`
  (recommended; not required).
- This is a **primary artifact** for the incident
  investigation. It is preserved through the post-incident
  review.
