# Vue profile

Per-framework guidance for the
[`frontend-implementation`](../../SKILL.md) skill when the target
module is a Vue 2 or Vue 3 app or component library. Read on
demand; do not load wholesale.

## Detection cues

The target module is Vue if any of the following are present:

- `vue` in `package.json` `dependencies`
- `*.vue` Single-File Components (SFCs)
- `@vue/cli` (legacy Vue CLI) or `create-vue` artifacts
- Vite + `@vitejs/plugin-vue`
- Nuxt 2/3 — also matches the [`nextjs`](nextjs.md) pattern
  in spirit (meta-framework); treat as Vue with Nuxt-specific
  rules

## Conventions to preserve

- **API style:** Composition API (`<script setup>`, `setup()`,
  `defineProps`, `defineEmits`) or Options API (`data`,
  `methods`, `computed`) — match the repo. Do not migrate
  Options → Composition as part of an unrelated change.
- **State management:** Pinia, Vuex, or services with
  `reactive` / `ref` — match the repo. Do not introduce a new
  state library.
- **Routing:** `vue-router` (Vue 2 or Vue 3) — preserve.
- **Styling:** `<style scoped>`, Tailwind, Sass, CSS Modules
  (Vue 3 SFC `module` attribute), styled-vue — match the repo.
- **Build tool:** Vite (modern), Vue CLI (legacy) — match the
  repo.
- **TypeScript vs JavaScript:** Vue 3 SFCs may be `.vue` with
  `<script setup lang="ts">`; preserve the existing choice.

## Naming conventions

- Component files: `PascalCase.vue` (e.g. `UserCard.vue`) or
  `kebab-case.vue` (e.g. `user-card.vue`) — match the repo.
- Composables: `useFoo.ts` (Composition API) or in `composables/`
  dir.
- Test files: `*.spec.ts` co-located, or in `tests/unit/` —
  match the repo.

## Testing

- **Test framework:** Vitest (Vite-based) or Jest (Vue CLI) —
  match the repo.
- **Component testing:** Vue Test Utils (`@vue/test-utils`) —
  prefer user-behavior tests (`getByRole`, `findByText`,
  `trigger`) over implementation-detail tests.
- **A11y checks:** `vitest-axe` / `jest-axe` if the repo already
  uses them.
- **E2E:** Cypress or Playwright only if the repo already uses
  them. Do not introduce E2E in a task that does not require it.

## API client

- `fetch` + composables, `axios`, `@tanstack/vue-query`, `swr`,
  Apollo Client (for GraphQL) — match the repo.
- Do not introduce a second server-state library if one is
  already in use.

## Forbidden actions

- **Do not migrate Vue 2 → Vue 3** as part of an unrelated
  change. If a Vue 2 EOL task is in scope, route it as a
  dedicated refactor.
- **Do not migrate Options API → Composition API** as part of
  an unrelated change.
- **Do not introduce Pinia** (or any other state library) unless
  the repo already uses it or it is explicitly approved.
- **Do not change the package manager.**
- **Do not change the build tool** (Vue CLI → Vite) without
  explicit approval.
- **Do not bypass the orchestrator** when the task also touches
  backend or integration code.

## Small example

Adding a "verified" badge to a `UserCard.vue` (Composition API,
`<script setup lang="ts">`, matches repo):

```diff
 <!-- UserCard.vue -->
 <script setup lang="ts">
+const props = defineProps<{ user: User }>();
 </script>

 <template>
   <article>
     <h2>{{ user.name }}</h2>
+    <span v-if="user.emailVerified" role="img" aria-label="Email verified">✓</span>
   </article>
 </template>
```

```typescript
// UserCard.spec.ts — Vitest + Vue Test Utils, user-behavior test
import { mount } from '@vue/test-utils';
import UserCard from './UserCard.vue';

it('shows the verified badge when email is verified', () => {
  const wrapper = mount(UserCard, { props: { user: { name: 'A', emailVerified: true } } });
  expect(wrapper.find('[aria-label="Email verified"]').exists()).toBe(true);
});
```

No new dependency, no Options ↔ Composition migration, no
state-library change — all consistent with the repo.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profile: [`react.md`](react.md) for React-based UIs
- Sibling profile: [`nextjs.md`](nextjs.md) for meta-frameworks
  (Nuxt; Next.js itself is also routed here when the consumer
  is the Next.js router)
- Sibling profile: [`static-ui.md`](static-ui.md) for non-Vue UI
  in mixed-codebase repos
- Tests: [`../../../test-generation/SKILL.md`](../../../test-generation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md)
