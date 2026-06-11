# Angular profile

Per-framework guidance for the
[`frontend-implementation`](../../SKILL.md) skill when the target
module is an Angular app or library. Read on demand; do not load
wholesale.

## Detection cues

The target module is Angular if any of the following are present:

- `@angular/core` and `@angular/common` in `package.json`
  `dependencies`
- `angular.json` workspace config
- `*.component.ts` with `@Component` decorator
- `@angular/cli` or `@angular-devkit/build-angular` in
  devDependencies
- TypeScript `tsconfig.json` with `experimentalDecorators`
  (Angular-specific usage)
- `ng` scripts in `package.json` (`ng serve`, `ng test`,
  `ng build`)

## Conventions to preserve

- **Component style:** standalone components (Angular 14+) or
  NgModule-based — match the repo. Do not migrate modules to
  standalone as part of an unrelated change.
- **Change detection:** `OnPush` (default in modern Angular) or
  `Default` — match the repo.
- **Reactive patterns:** RxJS observables, signals, or a mix —
  match the repo. Do not introduce signals as a wholesale
  replacement.
- **State management:** NgRx, Akita, NGXS, Component Store, or
  services with `BehaviorSubject` — match the repo. Do not
  introduce a new state library.
- **Routing:** `@angular/router` with route definitions,
  resolvers, guards, lazy-loaded modules — preserve.
- **Styling:** Angular component styles, SCSS, Tailwind, Material
  — match the repo.
- **Templates:** inline template, `templateUrl`, or
  `template:` — match the repo.
- **Forms:** Reactive Forms or Template-driven forms — match the
  repo.

## Naming conventions

- Component files: `feature.component.ts` (kebab-case)
- Module files: `feature.module.ts`
- Service files: `feature.service.ts`
- Test files: `feature.component.spec.ts`,
  `feature.service.spec.ts` (co-located)
- Selector prefix: `app-`, `lib-`, or repo-specific — match the
  repo.

## Testing

- **Test framework:** Karma + Jasmine (legacy) or Jest
  (`jest-preset-angular`) — match the repo.
- **Component testing:** Angular TestBed with `ComponentFixture`.
  Use the existing service / component test patterns. Do not
  switch the test framework.
- **Mocking:** `HttpClientTestingModule` for HTTP, class spies
  for services, `jasmine.createSpyObj` for dependencies — match
  the repo.
- **E2E:** Protractor (legacy, deprecated), Cypress, or
  Playwright — preserve, do not introduce E2E in a task that
  does not require it.

## HTTP / API client

- `HttpClient` from `@angular/common/http`. Interceptors for
  auth, logging, error handling — match the repo.
- Do not introduce `fetch` / `axios` in an Angular project that
  uses `HttpClient`.

## Forbidden actions

- **Do not migrate modules to standalone components** as part of
  an unrelated change.
- **Do not convert Observable-based code to signals** as part of
  an unrelated change.
- **Do not introduce NgRx** (or any other state library) unless
  explicitly approved.
- **Do not change the test framework** (Jasmine/Karma → Jest, or
  similar).
- **Do not change the package manager.**
- **Do not introduce a new UI library** (Material, PrimeNG,
  Clarity) unless the repo already uses it or it is explicitly
  approved.
- **Do not bypass the orchestrator** when the task also touches
  backend or integration code.

## Small example

Adding a "verified" badge to a `UserCardComponent`:

```diff
 // user-card.component.ts
 @Component({
   selector: 'app-user-card',
   templateUrl: './user-card.component.html',
+  imports: [CommonModule],
 })
 export class UserCardComponent {
   @Input({ required: true }) user!: User;
+  get verified(): boolean { return this.user.emailVerified; }
 }
```

```diff
 <!-- user-card.component.html -->
 <article>
   <h2>{{ user.name }}</h2>
+  <span *ngIf="verified" role="img" aria-label="Email verified">✓</span>
 </article>
```

```typescript
// user-card.component.spec.ts — TestBed, no new test framework
it('shows the verified badge when email is verified', () => {
  const fixture = TestBed.createComponent(UserCardComponent);
  fixture.componentRef.setInput('user', { name: 'A', emailVerified: true });
  fixture.detectChanges();
  expect(fixture.nativeElement.querySelector('[aria-label="Email verified"]'))
    .toBeTruthy();
});
```

No new dependency, no RxJS → signals migration, no
OnPush-vs-Default change — all consistent with the repo.

## Cross-references

- Skill: [`../../SKILL.md`](../../SKILL.md)
- Sibling profile: [`react.md`](react.md) for React-based UIs
- Sibling profile: [`static-ui.md`](static-ui.md) for non-Angular
  UI in mixed-codebase repos
- Tests: [`../../../test-generation/SKILL.md`](../../../test-generation/SKILL.md)
- Review: [`../../../code-change-review/SKILL.md`](../../../code-change-review/SKILL.md)
