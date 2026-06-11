# Next.js profile

Per-framework guidance for the
[`frontend-implementation`](../../SKILL.md) skill when the target
module is a Next.js app. Read on demand; do not load wholesale.

> **Routing caveat:** A Next.js project's API routes
> (`pages/api/*` or `app/api/*`) are **backend code**, not
> frontend. Any task that primarily touches API routes must be
> routed to
> [`backend-implementation`](../../../backend-implementation/SKILL.md)
> via
> [`implementation-orchestrator`](../../../implementation-orchestrator/SKILL.md).
> This profile covers only the pages, components, and
> client-side behavior of a Next.js app.

## Detection cues

The target module is Next.js if any of the following are present:

- `next` in `package.json` `dependencies`
- `next.config.js` / `next.config.mjs` / `next.config.ts`
- `pages/` directory (Pages Router) or `app/` directory (App
  Router)
- `next/image`, `next/link`, `next/router` imports

## Router detection

Next.js has two routers with very different rules. Identify
which one is in use before doing anything:

- **Pages Router** — `pages/` directory exists; pages are
  `pages/*.tsx` exporting a default React component. Data
  fetching uses `getServerSideProps`, `getStaticProps`,
  `getStaticPaths`.
- **App Router** — `app/` directory exists; layouts and pages
  use `app/**/layout.tsx`, `app/**/page.tsx`. Server and client
  components are mixed; data fetching uses React Server
  Components, `fetch` (with caching directives), and Server
  Actions.

Some repos have **both** (incremental migration in progress). In
that case, the orchestrator's routing report must specify which
router the change targets; this skill must not change the
router mix.

## Conventions to preserve

- **Component boundary:** Server Components vs Client Components
  (`'use client'` directive in App Router). Preserve the
  existing mix. Do not flip a server component to a client
  component (or vice versa) without explicit approval — it
  changes the data flow, bundle size, and SEO behavior.
- **Rendering mode:** static (SSG), server (SSR), ISR, CSR —
  match the repo per route. Do not change the rendering mode
  without explicit approval.
- **Routing:** preserve Pages Router or App Router. Do not migrate
  one to the other as part of an unrelated change.
- **Styling:** whatever the repo uses (CSS Modules, Tailwind,
  styled-components, Emotion, Sass) — match the repo.
- **State management:** whatever the repo uses (React Query,
  SWR, Zustand, Redux, Context) — match the repo. Do not
  introduce a new state library.
- **API routes:** `pages/api/*` or `app/api/*` — **out of scope
  for this skill**. Route API-route work to
  [`backend-implementation`](../../../backend-implementation/SKILL.md).
- **Server Actions:** App Router feature. Treated as
  **frontend-handler, backend-execution** code. They live in
  Server Components; the orchestrator decides whether the
  change is frontend or backend based on whether the change
  touches the action's UI affordance or its server logic.
- **Middleware:** `middleware.ts` at project root. Out of scope
  for this skill; route to
  [`backend-implementation`](../../../backend-implementation/SKILL.md)
  or `integration-implementation` based on what the middleware
  does.

## Naming conventions

- Pages (Pages Router): `pages/about.tsx` (kebab-case) or
  `pages/About.tsx` (PascalCase) — match the repo.
- Routes (App Router): `app/about/page.tsx` (kebab-case dirs).
- Layouts: `app/layout.tsx`, `app/<segment>/layout.tsx`.
- Components: co-located with the route, or in
  `components/<Name>.tsx` — match the repo.

## Testing

- **Test framework:** Jest (older) or Vitest (newer) — match
  the repo.
- **Component testing:** React Testing Library for Client
  Components. Server Components have a more limited testing
  story; integration / E2E is preferred.
- **Route testing:** Next.js' built-in test utilities (`next/jest`)
  when present, or Playwright / Cypress if the repo already
  uses them.
- **A11y checks:** `jest-axe` if the repo already uses it.
- **E2E:** Playwright / Cypress only if the repo already has
  them. Do not introduce E2E in a task that does not require
  it.

## API client

- `fetch` (App Router, RSC), SWR, React Query, `useSWR`,
  `useFetch` — match the repo.
- API-route calls in Client Components use the same patterns
  as a regular React app (see [`react.md`](react.md)).

## Forbidden actions

- **Do not migrate Pages Router → App Router** (or vice versa)
  as part of an unrelated change.
- **Do not flip server ↔ client components** without explicit
  approval.
- **Do not change the rendering mode** (SSG ↔ SSR ↔ ISR ↔ CSR)
  without explicit approval.
- **Do not edit API routes** (`pages/api/*`, `app/api/*`) or
  middleware. Route to
  [`backend-implementation`](../../../backend-implementation/SKILL.md)
  or `integration-implementation` based on what they do.
- **Do not introduce a new state library.**
- **Do not change the package manager.**
- **Do not introduce a new UI library** (e.g. adding Material UI
  on top of Tailwind).
- **Do not bypass the orchestrator** when the task also touches
  backend, integration, or middleware code.

## Small example

Adding a "verified" badge to a user card in an App Router page:

```diff
 // app/users/[id]/page.tsx (Server Component)
 import { UserCard } from '@/components/UserCard';

 export default async function UserPage({ params }: { params: { id: string } }) {
   const user = await fetchUser(params.id); // RSC data fetch
   return <UserCard user={user} />;
 }
```

```diff
 // components/UserCard.tsx (Server Component, no 'use client')
 export function UserCard({ user }: { user: User }) {
   return (
     <article>
       <h2>{user.name}</h2>
+      {user.emailVerified && (
+        <span role="img" aria-label="Email verified">✓</span>
+      )}
     </article>
   );
 }
```

If the badge needs client-side interactivity (e.g. a click
handler), mark only that part as a Client Component and leave
the rest as a Server Component. Do not flip the entire
`UserCard` to a Client Component without explicit approval.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profile: [`react.md`](react.md) for plain React
  patterns; Next.js inherits most React patterns
- Backend: [`../../../backend-implementation/SKILL.md`](../../../backend-implementation/SKILL.md)
  for API routes and middleware
- Orchestrator: [`../../../implementation-orchestrator/SKILL.md`](../../../implementation-orchestrator/SKILL.md)
  for mixed UI + API-route tasks
- Tests: [`../../../test-generation/SKILL.md`](../../../test-generation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md)
