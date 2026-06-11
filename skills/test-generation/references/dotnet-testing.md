# .NET — xUnit / NUnit / MSTest profile

Used by `test-generation` when the repo is .NET. Pick the framework
based on the project evidence.

## Detection

- `<PackageReference Include="xunit" ... />` in `.csproj` → xUnit
- `<PackageReference Include="NUnit" ... />` → NUnit
- `<PackageReference Include="MSTest.TestFramework" ... />` → MSTest
- `*.sln` in repo root → solution; tests usually in a separate
  `<Solution>.Tests` or `<Solution>.UnitTests` project

## Test layout

- Separate test project(s) in the solution
- Test project naming: usually `<Component>.Tests` or
  `<Component>.UnitTests` — match the existing naming
- Test files: `XxxTests.cs` for xUnit/MSTest, `XxxTests.cs` for NUnit;
  class names match the production class with `Tests` suffix

## Style rules

- **xUnit:** `[Fact]` for parameterless, `[Theory]` with `InlineData` for
  parameterized. Use `Assert.Equal`, `Assert.Throws`. Do not mix in
  NUnit / MSTest attributes.
- **NUnit:** `[Test]` / `[TestCase]`. Use `Assert.That` / `ClassicAssert`.
- **MSTest:** `[TestMethod]` / `[DataTestMethod]` with
  `[DataRow]`. Use `Assert.AreEqual` / `Assert.ThrowsException`.
- **Moq / NSubstitute / FakeItEasy:** if already used, use it. Do not
  introduce a new mocking library.
- **FluentAssertions:** if already used, use it. Do not introduce it.

## Coverage checklist mapping

| Case | xUnit idiom |
| --- | --- |
| happy path | `Assert.Equal(expected, actual)` |
| validation failure | `Assert.Throws<ValidationException>(() => ...)` |
| auth failure | inject a fake `IUserContext`, expect 401/403 |
| not-found | `Assert.Throws<NotFoundException>` |
| conflict | `Assert.Throws<ConflictException>` |
| persistence | verify fake repository call (`mockRepo.Verify(...)`) |
| boundary | `[Theory] [InlineData(...)]` |
| regression | `// Regression: <link or issue>` comment |

## Forbidden

- New test framework, assertion library, or mocking library.
- New NuGet packages for test purposes.
- Solution / project file changes (`.sln`, `.csproj`) for test purposes
  unless explicitly approved.

## Example skeleton (xUnit)

```csharp
public class OrderServiceTests
{
    [Fact]
    public async Task GetOrder_returns_order_when_it_exists()
    {
        var service = new OrderService(fakeRepo);
        var order = await service.GetOrderAsync("123");
        Assert.Equal("123", order.Id);
    }

    [Theory]
    [InlineData("")]
    [InlineData("does-not-exist")]
    public async Task GetOrder_throws_when_id_invalid(string id)
    {
        var service = new OrderService(fakeRepo);
        await Assert.ThrowsAsync<NotFoundException>(
            () => service.GetOrderAsync(id));
    }
}
```
