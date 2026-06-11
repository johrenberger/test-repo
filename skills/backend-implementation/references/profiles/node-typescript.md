# Node / TypeScript profile

Used by `backend-implementation` when the repo is Node.js or
TypeScript.

## Detection

- `package.json` with a `dependencies` / `devDependencies` block
- Framework: `express`, `fastify`, `nestjs`, `next` (API routes),
  `@hapi/hapi`, `koa`, serverless handlers in `aws-lambda` /
  `aws-cdk` / `@azure/functions`
- TypeScript: `tsconfig.json` and `typescript` in devDependencies
- Module system: `package.json` `"type": "module"` → ESM; otherwise
  CommonJS (or "none" — TypeScript-only)
- Test framework: `jest`, `vitest`, `mocha`
- HTTP test: `supertest`

## Architecture

Preserve the existing layering. Common patterns:

- `src/controllers/` or `src/routes/` — HTTP boundary
- `src/services/` — domain logic
- `src/repositories/` or `src/data/` — persistence
- `src/models/` or `src/entities/` — domain objects
- `src/middleware/` — Express / Fastify middleware
- `src/utils/` — pure helpers

If the repo uses `src/<feature>/` (feature-folder) layout, match it.
Do not introduce a new package layout.

## Test rules

- Match the existing test framework. Do not switch from Jest to Vitest
  or vice versa.
- Co-located tests (`<file>.test.ts`) vs. `__tests__/` directory:
  match the existing convention.
- Supertest for HTTP — only if already present or clearly appropriate.
- Do not convert CommonJS ↔ ESM.
- Do not change package manager.
- Do not introduce a new test framework.

## Forbidden

- New runtime dependency without explicit justification in the report
  and a `dependency-change-review` pass.
- New test framework, assertion library, or mocking library.
- CommonJS ↔ ESM conversion.
- Package manager change.
- Running `npm install` / `yarn` / `pnpm install` unless strictly
  necessary and explicitly approved.

## Module system cues

- `package.json` has `"type": "module"` → ESM
- `import` statements in source files → ESM (or TS)
- `require(...)` in source files → CommonJS
- Mixed → preserve the mix; do not normalize

## TypeScript rules

- If `tsconfig.json` `strict: true`, do not introduce `any`.
- Match the existing pattern for `interface` vs `type`, optional
  properties, and nullability.
- Do not change the TypeScript version.
- Do not change `tsconfig.json` settings to make code compile. Fix
  the code.
