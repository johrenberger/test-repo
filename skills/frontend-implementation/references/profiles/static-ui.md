# Static UI profile

Per-framework guidance for the
[`frontend-implementation`](../../SKILL.md) skill when the target
module is a **non-framework** UI (vanilla HTML / CSS / JS,
static site, design system primitives, web components). Read on
demand; do not load wholesale.

## Detection cues

The target module matches this profile if any of the following
are present:

- `*.html` files at the project root or in a `public/` /
  `static/` directory
- `*.css` / `*.scss` / `*.sass` files without a framework build
  pipeline
- Vanilla JavaScript / TypeScript (`*.js`, `*.ts`) without a
  framework import
- Web Components (`customElements.define`, Shadow DOM)
- A static-site generator (11ty, Hugo, Jekyll, Astro for the
  static parts)
- `astro.config.mjs` with no `output: 'server'` (i.e. static
  output)

This profile also covers "framework-agnostic" libraries — design
system tokens, web component libraries, multi-framework UI
primitives — where the work is on the static / design / markup
layer.

## Conventions to preserve

- **HTML structure:** semantic HTML5. Do not introduce `div`
  soup where a `section` / `article` / `nav` / `main` is correct.
- **CSS approach:** whatever the repo uses — plain CSS, SCSS,
  PostCSS, Tailwind utilities, CSS custom properties, BEM,
  CSS Modules with a lightweight bundler. Match the repo.
- **JavaScript:** vanilla or a thin wrapper; do not introduce
  React / Vue / Angular.
- **Build pipeline:** whatever the repo uses — 11ty, Hugo,
  Astro static output, Vite + plain TS, none at all. Preserve.
- **Accessibility:** semantic HTML, ARIA only when no semantic
  element exists, keyboard navigation, focus management,
  sufficient color contrast, prefers-reduced-motion respect.

## Naming conventions

- HTML files: `kebab-case.html` (e.g. `user-profile.html`).
- CSS files: co-located (`user-profile.css`) or in
  `styles/components/`. Match the repo.
- JS files: co-located or in `scripts/`. Match the repo.

## Testing

- **Visual regression:** Percy, Chromatic, Playwright visual
  snapshots — preserve, do not introduce.
- **Accessibility:** `axe-core` (CLI or via Playwright) if the
  repo already uses it. Lighthouse a11y audits as a manual
  check, not a CI gate, unless the repo enforces it.
- **Unit / component:** Web Test Runner, Vitest + happy-dom /
  jsdom, or simple test harness — match the repo. Do not
  introduce a heavy framework.
- **E2E:** Playwright / Cypress only if the repo already uses
  them. Do not introduce E2E in a task that does not require
  it.

## Forbidden actions

- **Do not introduce a UI framework** (React, Vue, Angular) in
  a vanilla project. If the project is moving to a framework,
  that is a dedicated refactor, not a frontend task.
- **Do not change the build pipeline** (Hugo → 11ty, plain
  PostCSS → Tailwind) as part of an unrelated change.
- **Do not change the CSS approach** (BEM → Tailwind, SCSS →
  CSS Modules) as part of an unrelated change.
- **Do not add framework-specific tooling** (webpack, Vite +
  React plugin) without explicit approval.
- **Do not bypass the orchestrator** when the task also touches
  backend or integration code.

## Small example

Adding a "verified" badge to a static user-profile page:

```diff
 <!-- user-profile.html -->
 <article class="user-card">
   <h2 class="user-card__name">Ada Lovelace</h2>
+  <span class="user-card__verified" role="img" aria-label="Email verified">✓</span>
 </article>
```

```diff
 /* user-profile.css (BEM, matches repo) */
+.user-card__verified {
+  display: inline-block;
+  margin-left: 0.5rem;
+  color: var(--color-success, #2a7);
+}
```

No JS change required; no build pipeline change; no framework
introduction. The badge inherits the repo's color tokens and
naming convention.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profiles: [`react.md`](react.md),
  [`angular.md`](angular.md), [`vue.md`](vue.md),
  [`nextjs.md`](nextjs.md) — for framework-based UIs
- Tests: [`../../../test-generation/SKILL.md`](../../../test-generation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md)
- A11y: OWASP MASVS, axe-core rules — for security-relevant
  accessibility findings, route to
  [`security-review`](../../../security-review/SKILL.md)
