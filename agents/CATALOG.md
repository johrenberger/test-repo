# Agent Catalog — Quick Decision Guide

Use this guide to pick the right agent for a task. Start with the
[Quick Decision Table](#quick-decision-table). If two agents seem
right, look at [Pairings](#pairings) for the common multi-agent
flows. The 20 agents are grouped by domain below the table.

If you don't know where to start: most engineering work begins
with the **Software Engineer** agent. Most product/business
work begins with the **Product Manager** agent. Most research
work begins with the **Research Analyst** agent.

---

## Quick Decision Table

| Situation | Agent | First step the agent will take |
| --- | --- | --- |
| You have a coding task (implement feature, fix bug, refactor) | [Software Engineer](SOFTWARE_ENGINEER_AGENT.md) | Break the task into a plan, identify the right skills, write the code |
| You need to choose a tech stack, framework, or architecture | [Architect / Tech Lead](ARCHITECT_AGENT.md) | Frame the trade-offs; produce options with explicit costs and risks |
| You have a PR ready and want it reviewed before merge | [Code Reviewer](CODE_REVIEW_AGENT.md) | Walk the diff; flag logic, security, and design issues automated tests miss |
| You need tests written for new or changed code | [Test Automation](TEST_AUTOMATION_AGENT.md) | Run test-gap-analysis; propose a test plan; generate the tests |
| You need to deploy to production or set up CI/CD | [DevOps](DEVOPS_AGENT.md) | Audit current pipeline; propose the deploy strategy and infrastructure changes |
| Something is broken in production right now | [Monitoring](MONITORING_AGENT.md) | Triage the alert; isolate the failure; coordinate with the on-call responder |
| You need to actively test a running system for vulnerabilities | [Pen Testing](PEN_TESTING_AGENT.md) | Run hands-on tests; produce evidence-backed findings with PoC steps |
| You need a structured code-vs-OWASP security review | [Security Analyst](SECURITY_ANALYST_AGENT.md) | Audit the code against OWASP; produce findings with severity and remediation |
| You need to secure a cloud environment (VPS, Docker, OS, packages) | [Cloud Security](CLOUD_SECURITY_AGENT.md) | Inspect the actual environment for CVEs, misconfigurations, and drift |
| You need a doc updated (API reference, runbook, onboarding guide) | [Documentation](DOCUMENTATION_AGENT.md) | Find the existing doc; identify the change; rewrite the affected section |
| You have a product idea or feature request that needs decomposition | [Product Manager](PRODUCT_MANAGER_AGENT.md) | Break it into small, independent user stories for the Software Engineer |
| You need to coordinate a multi-agent pipeline or sprint | [Project Coordinator](PROJECT_COORDINATOR_AGENT.md) | Track the handoffs; enforce the timeline; surface blockers |
| You need help managing schedule, commitments, or follow-ups | [Executive Assistant](EXECUTIVE_ASSISTANT_AGENT.md) | Triage the calendar and commitments; propose the day plan |
| You need to draft an email, report, or meeting summary | [Communications Manager](COMMUNICATIONS_MANAGER_AGENT.md) | Get the technical content; produce the audience-appropriate draft |
| You need financial analysis (expenses, invoices, revenue modeling) | [Financial Analyst](FINANCIAL_ANALYST_AGENT.md) | Pull the data; build the model; produce a one-page summary |
| You need a contract or compliance review (GDPR, CCPA, HIPAA, etc.) | [Legal & Compliance](LEGAL_COMPLIANCE_AGENT.md) | Identify the regulation in scope; flag risks; recommend counsel when needed |
| You need brainstorming, naming, positioning, or content strategy | [Creative Director](CREATIVE_DIRECTOR_AGENT.md) | Frame the brief; produce 3-5 distinct options with rationale |
| You need to record or retrieve a decision, lesson, or best practice | [Knowledge Manager](KNOWLEDGE_MANAGER_AGENT.md) | Search the existing knowledge base; append or update |
| You need structured research on a topic, tech, or competitor | [Research Analyst](RESEARCH_ANALYST_AGENT.md) | Define the question; gather sources; produce actionable intel |
| You need raw data turned into decisions, trends, or reports | [Data Analyst](DATA_ANALYST_AGENT.md) | Identify the data; analyze; produce visualizations and a non-obvious insight |

---

## Pairings

Common multi-agent flows. Pick the first agent from your task,
then follow the chain. Each arrow is a handoff with a written
packet (see the `handoff-packet` skill).

- **Feature delivery:**
  Product Manager → Software Engineer → Code Reviewer → Test Automation → DevOps
  *(The canonical engineering chain. Used for almost every product change.)*

- **Security audit (defense in depth):**
  Security Analyst → Pen Testing → Cloud Security
  *(Static review first, then active testing, then environment audit. All three run independently.)*

- **Production incident response:**
  Monitoring → Software Engineer → DevOps → Documentation
  *(Detect, fix, deploy the fix, then update the runbook so the next incident is easier.)*

- **Compliance change:**
  Legal & Compliance → Code Reviewer → Test Automation
  *(Identify the regulation, audit the code change, prove the test covers the new requirement.)*

- **Research → product:**
  Research Analyst → Product Manager → Communications Manager
  *(Research the space, frame the product change, announce it in plain language.)*

---

## Engineering (10 agents)

The agents that own code, run validation, and move work between
phases of the engineering lifecycle. Most product work touches
several of these.

- [Architect / Tech Lead](ARCHITECT_AGENT.md) — strategic sounding board for tech selection, architecture, and scaling
- [Software Engineer](SOFTWARE_ENGINEER_AGENT.md) — designs, implements, and ships code; sets code quality standards
- [Code Reviewer](CODE_REVIEW_AGENT.md) — peer review before merge; catches what tests miss
- [Test Automation](TEST_AUTOMATION_AGENT.md) — owns test strategy and quality gates
- [DevOps](DEVOPS_AGENT.md) — owns CI/CD, deployment, and infrastructure
- [Monitoring](MONITORING_AGENT.md) — production visibility and alert triage
- [Documentation](DOCUMENTATION_AGENT.md) — project memory; keeps docs accurate
- [Pen Testing](PEN_TESTING_AGENT.md) — active security testing against running systems
- [Security Analyst](SECURITY_ANALYST_AGENT.md) — static code review against OWASP
- [Cloud Security](CLOUD_SECURITY_AGENT.md) — environment-level security (CVE, drift, misconfiguration)

## Business Operations (8 agents)

The agents that turn product intent into shipped work, keep
the calendar running, and translate between technical and
non-technical stakeholders.

- [Product Manager](PRODUCT_MANAGER_AGENT.md) — decomposes product ideas into user stories
- [Project Coordinator](PROJECT_COORDINATOR_AGENT.md) — orchestrates the multi-agent pipeline
- [Executive Assistant](EXECUTIVE_ASSISTANT_AGENT.md) — time, schedule, and follow-up management
- [Communications Manager](COMMUNICATIONS_MANAGER_AGENT.md) — drafts emails, reports, summaries
- [Financial Analyst](FINANCIAL_ANALYST_AGENT.md) — financial and business intelligence
- [Legal & Compliance](LEGAL_COMPLIANCE_AGENT.md) — contract and compliance review
- [Creative Director](CREATIVE_DIRECTOR_AGENT.md) — brainstorming, naming, positioning
- [Knowledge Manager](KNOWLEDGE_MANAGER_AGENT.md) — institutional memory and lessons

## Data & Research (2 agents)

The agents that turn raw information into decisions.

- [Research Analyst](RESEARCH_ANALYST_AGENT.md) — structured research on topics, tech, competitors
- [Data Analyst](DATA_ANALYST_AGENT.md) — raw data → actionable decisions and reports

---

## How this guide is maintained

- **Source:** generated from the per-agent `uses_skills` and
  frontmatter fields. Run `python -m skill_governance.cli validate`
  to keep the source data clean.
- **Updates:** PRs that add a row to the table, a new pairing, or
  a new domain are welcome. Keep the situation phrasing
  user-centric ("You need to..."), not agent-centric.
- **Bypassing:** if none of these agents fit, you may need a new
  agent spec. See [README.md](./README.md) for how to add one.
