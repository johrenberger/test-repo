# Incident summary (shared)

One-page executive summary of an incident. Produced by
[`incident-triage`](../incident-triage/SKILL.md) and intended
for stakeholders, leadership, and post-incident review. The
detailed triage report lives in
[`incident-triage-report.md`](../incident-triage/templates/incident-triage-report.md);
this template is the **summary**.

The summary is a **derived view**; the primary artifacts are
the triage report, the timeline, and the action items.

## Template

```markdown
# Incident summary for <INC-YYYYMMDD-NNN>

- **Incident ID:** <INC-YYYYMMDD-NNN>
- **Task:** <TASK_ID>
- **Severity:** <SEV-1 | SEV-2 | SEV-3 | SEV-4>
- **Status:** <investigating | mitigating | monitoring |
  resolved | post-incident>
- **Date opened:** <YYYY-MM-DD>
- **Date resolved (if applicable):** <YYYY-MM-DD>

## One-line summary

<one sentence: what happened, who was impacted, what the
state is.>

## Impact

- **Service(s) impacted:** <list>
- **User group(s) impacted:** <list>
- **Likely scope:** <contained | partial | widespread>
- **Customer-facing:** <yes | no | partial>

## Timeline highlights

- `<UTC-ts>` — <one-line event>
- `<UTC-ts>` — <one-line event>
- `<UTC-ts>` — <one line>
- `<UTC-ts>` — resolution (if applicable)

Full timeline:
[`incident-timeline.md`](../incident-triage/templates/timeline.md).

## Root cause (when known)

<one paragraph or `under investigation` or `unknown at
time of summary`.>

## Mitigation

<one paragraph: what was done to mitigate; whether it was
sufficient; what follow-up is needed.>

## Action items

- <action id> — <one line> — owner: <role>
- <action id> — <one line> — owner: <role>

Full action items: <list of paths>.

## Lessons learned (when known)

- <one line>
- Or `pending post-incident review`.

## Post-incident review

- **Scheduled:** <YYYY-MM-DD, or `pending`>
- **Owner:** <role>
- **Inputs:** <list of artifacts — timeline, triage
  report, runbook diff>

## Cross-references

- Triage report:
  [`incident-triage-report.md`](../incident-triage/templates/incident-triage-report.md)
- Timeline:
  [`incident-timeline.md`](../incident-triage/templates/timeline.md)
- Action items: <list of paths>
- Handoff packet: <path>

## Provenance

- Produced as a **derived view** by
  [`incident-triage`](../incident-triage/SKILL.md).
- Output path: `<task path>/reports/incident-summary.md`
  (recommended; not required).
- The summary is intended for stakeholders and post-incident
  review; the per-event timeline and per-action-item records
  are the primary artifacts.
```

## Field rules

- `One-line summary` is one sentence.
- `Severity` is exactly one of the four values from the
  incident-triage skill.
- `Timeline highlights` lists the load-bearing events; the
  full timeline is the primary artifact.
- `Lessons learned` is `pending post-incident review` when
  the review has not run; it is not a placeholder for
  speculation.
- `Post-incident review` is required for SEV-1 and SEV-2;
  recommended for SEV-3; optional for SEV-4.

## When to update the summary

- When the incident's status changes
  (`investigating → mitigating → monitoring → resolved`).
- When the root cause is identified.
- When mitigation succeeds or fails.
- When the post-incident review is scheduled.
- When the post-incident review is complete (lessons
  learned finalized).

The summary is **append-mostly**; events are added, not
rewritten.

## Cross-references

- Triage report:
  [`../incident-triage/templates/incident-triage-report.md`](../incident-triage/templates/incident-triage-report.md)
- Timeline:
  [`../incident-triage/templates/timeline.md`](../incident-triage/templates/timeline.md)
- Severity guide:
  [`../incident-triage/references/incident-severity-guide.md`](../incident-triage/references/incident-severity-guide.md)
- Release readiness:
  [`../release-readiness/SKILL.md`](../release-readiness/SKILL.md)
  (for post-incident fixes that produce a release)
