# Agents

Index of agent specifications in this repository. Each file is a self-contained
agent spec — identity, purpose, core capabilities, and collaboration protocol.

> **Naming convention:** every agent spec lives at the root of this directory
> and follows the pattern `<ROLE>_AGENT.md`. (One historical file,
> `CLOUD_SECURITY_AGENT.md`, was renamed from `CLOUD_SECURITY_SPECIALIST.md` to
> match this convention.)

## Engineering

- [`ARCHITECT_AGENT.md`](ARCHITECT_AGENT.md) — Principal Engineer / Tech Lead; strategic sounding board for architecture, tech selection, and scaling decisions upstream of the Software Engineer.
- [`SOFTWARE_ENGINEER_AGENT.md`](SOFTWARE_ENGINEER_AGENT.md) — Designs, implements, and ships code; sets code quality standards and handles cross-session context for engineering work.
- [`CODE_REVIEW_AGENT.md`](CODE_REVIEW_AGENT.md) — Reviews pull requests before they reach testing; catches logic errors, design inconsistencies, readability issues, and security concerns automated tests miss.
- [`TEST_AUTOMATION_AGENT.md`](TEST_AUTOMATION_AGENT.md) — Validates code from the Software Engineer through unit, integration, E2E, scalability, and property-based testing; maintains quality gates before merge.
- [`DEVOPS_AGENT.md`](DEVOPS_AGENT.md) — Owns CI/CD, containerization, cloud infrastructure, deployment strategies, and environment management from code to production.
- [`MONITORING_AGENT.md`](MONITORING_AGENT.md) — Real-time production visibility; anomaly detection, log aggregation, degradation alerts before users notice.
- [`DOCUMENTATION_AGENT.md`](DOCUMENTATION_AGENT.md) — Project memory; keeps onboarding, API references, runbooks, and architecture docs accurate and current.
- [`PEN_TESTING_AGENT.md`](PEN_TESTING_AGENT.md) — Hands-on penetration testing against deployed apps; produces evidence-backed findings with PoC reproduction steps.
- [`SECURITY_ANALYST_AGENT.md`](SECURITY_ANALYST_AGENT.md) — Systematic security posture review of project code against OWASP; structured findings with severity and remediation guidance.
- [`CLOUD_SECURITY_AGENT.md`](CLOUD_SECURITY_AGENT.md) — Cloud-environment security (Hostinger VPS, Linux Docker); continuous CVE-aware inspection of actual OS, packages, services, and config.

## Business Operations

- [`PRODUCT_MANAGER_AGENT.md`](PRODUCT_MANAGER_AGENT.md) — Decomposes product ideas and feature requests into small, independent user stories for the Software Engineer.
- [`PROJECT_COORDINATOR_AGENT.md`](PROJECT_COORDINATOR_AGENT.md) — Orchestrates the multi-agent pipeline; tracks sprint progress, coordinates handoffs, enforces timeline.
- [`EXECUTIVE_ASSISTANT_AGENT.md`](EXECUTIVE_ASSISTANT_AGENT.md) — Time, schedule, and follow-up management; tracks commitments, flags deadlines, prepares meetings.
- [`COMMUNICATIONS_MANAGER_AGENT.md`](COMMUNICATIONS_MANAGER_AGENT.md) — Drafts emails, reports, meeting summaries; translates technical content for non-technical stakeholders.
- [`FINANCIAL_ANALYST_AGENT.md`](FINANCIAL_ANALYST_AGENT.md) — Financial and business intelligence: expenses, invoices, revenue modeling, financial clarity for monetizable projects.
- [`LEGAL_COMPLIANCE_AGENT.md`](LEGAL_COMPLIANCE_AGENT.md) — Contract and compliance review (GDPR, CCPA, HIPAA, etc.); flags risk before lawyer consultation. Not a substitute for counsel.
- [`CREATIVE_DIRECTOR_AGENT.md`](CREATIVE_DIRECTOR_AGENT.md) — Lateral-thinking sparring partner; brainstorming, naming, positioning, content strategy, visual concepts.
- [`KNOWLEDGE_MANAGER_AGENT.md`](KNOWLEDGE_MANAGER_AGENT.md) — Institutional memory: decisions, lessons, best practices; prevents repeated mistakes across projects and sessions.

## Data & Research

- [`RESEARCH_ANALYST_AGENT.md`](RESEARCH_ANALYST_AGENT.md) — Structured research on topics, tech, competitors, decisions; actionable intelligence without rabbit holes.
- [`DATA_ANALYST_AGENT.md`](DATA_ANALYST_AGENT.md) — Raw data → actionable decisions; trend analysis, reports, visualizations, non-obvious insights.

---

## Recommended Skill Mapping

The following skills in `../skills/` are recommended for each
engineering agent. Agents that own code, run validation, or move
work between agents should treat these as required companions to
their spec. Non-engineering agents may use them on demand.

Skills are grouped in `../skills/README.md` into Foundation, Software
Delivery, and Review and Risk. The mapping below picks from all
groups.

### [`SOFTWARE_ENGINEER_AGENT.md`](SOFTWARE_ENGINEER_AGENT.md)

- [`repo-discovery`](../skills/repo-discovery/SKILL.md)
- [`backend-implementation`](../skills/backend-implementation/SKILL.md)
- [`test-generation`](../skills/test-generation/SKILL.md)
- [`validation-runner`](../skills/validation-runner/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`TEST_AUTOMATION_AGENT.md`](TEST_AUTOMATION_AGENT.md)

- [`repo-discovery`](../skills/repo-discovery/SKILL.md)
- [`test-gap-analysis`](../skills/test-gap-analysis/SKILL.md)
- [`test-generation`](../skills/test-generation/SKILL.md)
- [`validation-runner`](../skills/validation-runner/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`CODE_REVIEW_AGENT.md`](CODE_REVIEW_AGENT.md)

- [`code-change-review`](../skills/code-change-review/SKILL.md)
- [`security-review`](../skills/security-review/SKILL.md)
- [`dependency-change-review`](../skills/dependency-change-review/SKILL.md)
- [`database-migration-safety`](../skills/database-migration-safety/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`SECURITY_ANALYST_AGENT.md`](SECURITY_ANALYST_AGENT.md)

- [`security-review`](../skills/security-review/SKILL.md)
- [`dependency-change-review`](../skills/dependency-change-review/SKILL.md)
- [`database-migration-safety`](../skills/database-migration-safety/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`ARCHITECT_AGENT.md`](ARCHITECT_AGENT.md)

- [`repo-discovery`](../skills/repo-discovery/SKILL.md)
- [`database-migration-safety`](../skills/database-migration-safety/SKILL.md)
- [`dependency-change-review`](../skills/dependency-change-review/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`DEVOPS_AGENT.md`](DEVOPS_AGENT.md)

- [`repo-discovery`](../skills/repo-discovery/SKILL.md)
- [`validation-runner`](../skills/validation-runner/SKILL.md)
- [`dependency-change-review`](../skills/dependency-change-review/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

### [`PROJECT_COORDINATOR_AGENT.md`](PROJECT_COORDINATOR_AGENT.md)

- [`task-state-management`](../skills/task-state-management/SKILL.md)
- [`handoff-packet`](../skills/handoff-packet/SKILL.md)

See `../skills/README.md` for the full skill index, required
`SKILL.md` sections, maturity levels, and the non-destructive-script
rule.

## Adding a new agent spec

1. Create `agents/<ROLE>_AGENT.md` using the existing files as a template.
2. Sections to include: **Identity**, **Purpose**, **Core Capabilities**,
   **Collaboration Protocol** (handoffs, context sharing), **Operating Model**.
3. Add a one-line summary to this README, grouped under the right domain.
4. Open a PR.

## Editing an existing spec

Specs are living documents. PRs that tighten wording, clarify capabilities, or
update collaboration protocols are welcome — keep the section structure intact
so agents parsing these files don't break.
