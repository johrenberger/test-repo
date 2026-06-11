# React profile

Per-framework guidance for the
[`frontend-implementation`](../../SKILL.md) skill when the target
module is a React app or component library. Read on demand; do
not load wholesale.

## Detection cues

The target module is React if any of the following are present:

- `react` and `react-dom` in `package.json` `dependencies`
- `vite.config.ts` with `@vitejs/plugin-react`
- `create-react-app` artifacts (`react-scripts` in
  `package.json`)
- `next` in `package.json` `dependencies` — also matches the
  [`nextjs`](nextjs.md) profile; prefer `nextjs` when the project
  uses the Next.js router, server components, or `getServerSideProps`
- JSX / TSX files
- `@testing-library/react` in devDependencies
- `vitest` + `@testing-library/react` (Vitest is the test runner;
  RTL is the renderer)

## Conventions to preserve

- **Component style:** hooks + functional components, unless the
  repo predominantly uses class components (preserve, do not
  rewrite)
- **State management:** whatever the repo uses (Redux Toolkit,
  Zustand, Jotai, Recoil, React Query / TanStack Query,
  SWR, MobX, Context). Do not introduce a new state library.
- **Routing:** `react-router`, `tanstack/router`, or app-level
  custom routing. Do not change the routing library.
- **Styling:** CSS Modules, Tailwind, styled-components, Emotion,
  Sass, vanilla-extract, plain CSS — match the repo.
- **Module system:** ESM (Vite/Next) or CommonJS (CRA) — match the
  repo.
- **Package manager:** npm, yarn, pnpm, or bun — match the repo.
  Do not switch.
- **TypeScript vs JavaScript:** match the repo. Do not migrate
  JS to TS as part of an unrelated change.

## Naming conventions

- Component files: `PascalCase.tsx` (e.g. `UserCard.tsx`) or
  `kebab-case.tsx` (e.g. `user-card.tsx`) — match the repo.
- Hook files: `useFoo.ts` / `use-foo.ts` — match the repo.
- Test files: co-located `*.test.tsx` or in `__tests__/` — match
  the repo.

## Testing

- **Test framework:** Jest (CRA / older projects) or Vitest
  (Vite-based projects). Preserve.
- **Component / behavior testing:** React Testing Library
  preferred. Prefer user-behavior tests (e.g. `getByRole`,
  `findByText`) over implementation-detail tests (e.g. snapshot
  of every component, internal state inspection).
- **Snapshot tests:** allowed only when the repo already relies
  on them. Do not add new snapshot-only tests.
- **A11y checks:** `jest-axe` or `@axe-core/react` if the repo
  already uses them.
- **E2E:** Cypress or Playwright only if the repo already uses
  them. Do not introduce E2E in a task that does not require it.

## API client

- `fetch` + custom hooks, `axios`, `@tanstack/react-query`,
  `swr`, `urql`, Apollo Client, RTK Query — match the repo.
- If the repo has a server-state library, use it; do not
  introduce a second one.

## Forbidden actions

- **Do not introduce a new UI framework** (e.g. switching to
  Material UI when the repo uses Chakra).
- **Do not rewrite the component architecture** (e.g. converting
  class components to hooks across the codebase as part of an
  unrelated change).
- **Do not convert the styling system** (e.g. CSS Modules to
  Tailwind) as part of an unrelated change.
- **Do not change the package manager.**
- **Do not introduce a state-management library.**
- **Do not change the build tool** (Vite → webpack, or similar)
  without explicit approval.
- **Do not bypass the orchestrator** when the task also touches
  backend or integration code.

## Small example

A user-facing change to add an "Email verified" badge to a
`UserCard` component:

```diff
 // UserCard.tsx (functional component, hooks-based, matches repo)
+const VerifiedBadge = ({ verified }: { verified: boolean }) => (
+  verified ? <span role="img" aria-label="Email verified">✓</span> : null
+);
+
 export const UserCard = ({ user }: { user: User }) => (
   <article>
     <h2>{user.name}</h2>
+    <VerifiedBadge verified={user.emailVerified} />
   </article>
 );
```

```tsx
// UserCard.test.tsx — RTL user-behavior test, no new snapshot
it('shows the verified badge when email is verified', () => {
  render(<UserCard user={{ name: 'A', emailVerified: true }} />);
  expect(screen.getByRole('img', { name: /verified/i })).toBeInTheDocument();
});
```

No new dependency, no styling change, no architecture change —
all consistent with the repo's existing conventions.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profile: [`nextjs.md`](nextjs.md) — preferred when the
  project uses the Next.js router or server components
- Sibling profile: [`static-ui.md`](static-ui.md) — for non-React
  UI in mixed-codebase repos
- Tests: [`../../../test-generation/SKILL.md`](../../../test-generation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md)
