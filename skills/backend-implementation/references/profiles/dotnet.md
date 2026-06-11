# .NET profile

Used by `backend-implementation` when the repo is .NET.

## Detection

- `*.sln` in repo root
- `*.csproj` for project files
- `global.json` for SDK pinning
- Framework: `Microsoft.AspNetCore.*` for web APIs, `Microsoft.EntityFrameworkCore`
  for EF, `MediatR`, `AutoMapper`, `Serilog`, `FluentValidation`
- Test: `xunit`, `nunit`, `MSTest.TestFramework`
- Mocking: `Moq`, `NSubstitute`, `FakeItEasy`
- Assertions: `FluentAssertions` (only if present)

## Architecture

Preserve the existing project structure. Common patterns:

- `<Solution>.Api` — web API project
- `<Solution>.Application` or `<Solution>.Core` — domain logic
- `<Solution>.Infrastructure` or `<Solution>.Persistence` — data access
- `<Solution>.Domain` — entities, value objects
- `<Solution>.Tests` or `<Solution>.<Feature>.Tests` — test projects

Match the existing layout. Do not introduce a new project.

## Test rules

- Match the existing test framework (xUnit / NUnit / MSTest).
- Match the existing mocking library.
- `FluentAssertions` only if already present.
- For ASP.NET Core controllers, use the existing test pattern
  (often `WebApplicationFactory<>` with `HttpClient`).
- Do not introduce a new test framework, mocking library, or
  assertion library.

## Migration rules

- EF Core migrations: do not write destructive migrations. Use
  `database-migration-safety` first.

## Forbidden

- New NuGet package without explicit justification and a
  `dependency-change-review` pass.
- New test framework, mocking library, or assertion library.
- Solution / project file changes (`.sln`, `.csproj`,
  `Directory.Build.props`) for implementation purposes unless
  explicitly approved.
- `dotnet add package` / `dotnet restore` of new packages unless
  strictly necessary and explicitly approved.
- Changes to dependency injection / configuration patterns
  (`Program.cs`, `Startup.cs`, `appsettings.json`) without explicit
  approval.

## Dependency injection

- Match the existing DI registration style (extension methods,
  module classes, etc.).
- Do not introduce a new DI container.
- Do not change service lifetimes (`Singleton` / `Scoped` /
  `Transient`) without explicit justification.
