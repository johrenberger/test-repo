# Node / TypeScript — Jest / Vitest profile

Used by `test-generation` when the repo is JavaScript or TypeScript and
the test framework detected is Jest or Vitest. Mocha is supported but
less common; the same general rules apply.

## Detection

- `package.json` `devDependencies` includes `jest` → Jest
- `package.json` `devDependencies` includes `vitest` → Vitest
- `jest.config.*` or `vitest.config.*` present
- `mocha` / `chai` in deps → Mocha
- `supertest` in deps → HTTP-level tests

## Test layout

- Co-located: `<file>.test.ts` next to source `<file>.ts`
- `__tests__/`: a directory of test files
- `tests/` or `test/`: separate test directory

Match whatever the existing tests do. If the repo co-locates, do not
move tests to a `__tests__/` directory.

## Style rules

- **CommonJS vs ESM:** match exactly. Do not convert. Check
  `package.json` `"type": "module"` and the import / `require` style in
  existing files.
- **Assertions:** if the repo uses `expect(x).toBe(y)` (Jest / Vitest),
  use that. If the repo uses `chai` (`expect(x).to.equal(y)`), preserve.
- **Mocks:** Jest / Vitest's `vi.mock` / `jest.mock`. Mock at the network
  boundary. Do not mock every internal function — test behavior through
  the public surface.
- **HTTP:** if `supertest` is present, use it. Otherwise use the
  framework's own test utilities.
- **Test naming:** match the existing convention (`describe` / `it` vs
  `test`, sentence-style vs terse).

## Coverage checklist mapping

| Case | Jest / Vitest idiom |
| --- | --- |
| happy path | `expect(result).toEqual(expected)` |
| validation failure | `expect(() => fn(bad)).toThrow(...)` |
| auth failure | mock the auth middleware, expect 401 / rejected promise |
| not-found | mock the data source to return null, expect thrown / rejected |
| conflict | similar to not-found with explicit conflict value |
| persistence | assert the mock was called with the right args |
| boundary | `it.each([...])` (Jest) or `test.each` (Vitest) |
| regression | `// Regression: <link or issue>` comment at the top of the test |

## Forbidden

- New test framework, assertion library, or mocking library.
- Converting CommonJS ↔ ESM.
- Changing package manager.
- Adding `ts-node`, `tsx`, or other runtime tooling unless explicitly
  approved.

## Example skeleton (Jest + TypeScript)

```ts
import { getOrder } from "./orderService";

describe("getOrder", () => {
  it("returns the order when it exists", async () => {
    const order = await getOrder("123");
    expect(order.id).toBe("123");
  });

  it.each([
    ["does-not-exist", "OrderNotFound"],
    ["", "InvalidId"],
  ])("throws %s for input %s", async (id, kind) => {
    await expect(getOrder(id)).rejects.toThrow(kind);
  });
});
```
