# Java / JUnit / Spring profile

Used by `test-generation` when the repo is Java and the test framework
detected is JUnit (4 or 5). Spring guidance is layered on top.

## Detection

- `pom.xml` with `spring-boot-starter-parent`, or `build.gradle` with
  `org.springframework.boot` plugin → Spring Boot
- JUnit version: look for `org.junit.jupiter` (JUnit 5) or
  `org.junit.Test` only (JUnit 4)
- Mockito: `mockito-core` or `mockito-junit-jupiter` in deps
- AssertJ: `assertj-core` in deps
- Testcontainers: `org.testcontainers` in deps
- MockMvc: `spring-test` with `MockMvc` usage in existing tests
- WebTestClient: `spring-test` with `WebTestClient` usage in existing
  tests
- Flyway / Liquibase: detected by `db/migration` / `src/main/resources/db/migration`
  directories

## Test layout

- Unit tests: `src/test/java/<package>/<Class>Test.java` (same package
  as the class under test)
- Integration tests: same directory, often with `IT` suffix or under
  `src/test/java/**/integration/`
- Resources: `src/test/resources/`

## Style rules

- **JUnit 5** if present — use Jupiter API. Do not mix with JUnit 4
  unless the repo already does.
- **Assertion library:** if AssertJ is present, use it. If the repo uses
  bare JUnit assertions, preserve that. Do not introduce AssertJ.
- **Mockito:** if Mockito is present, use it. Otherwise use simple
  hand-written fakes. Do not introduce Mockito.
- **MockMvc / WebTestClient:** use whatever the existing tests use. Do
  not introduce the other one.
- **`@SpringBootTest`:** only when integration behavior genuinely
  requires the full application context, or the existing tests already
  use it. Prefer slice annotations (`@WebMvcTest`,
  `@DataJpaTest`, etc.) when possible.
- **Test naming:** match the existing style. Common patterns: `shouldX`,
  `givenX_whenY_thenZ`, or `MethodName_condition_expected`. Look at
  three existing tests in the same package and follow their convention.

## Coverage checklist mapping

For each behavior, ensure the relevant cases:

| Case | JUnit 5 idiom |
| --- | --- |
| happy path | `assertEquals(expected, actual)` |
| validation failure | assert thrown `ConstraintViolationException` or custom |
| auth failure | Spring Security test: `with(user("..."))` then expect 401/403 |
| not-found | expect `NotFoundException` or response status 404 |
| conflict | expect `ConflictException` or 409 |
| persistence | verify repository call with `ArgumentCaptor` or `verify` |
| boundary | parameterized test with `@ValueSource` / `@MethodSource` |
| regression | `// Regression: <link or issue>` comment at the top of the test |

## Forbidden

- New Spring starters, Lombok, MapStruct, Testcontainers, Flyway,
  Liquibase without explicit justification in the report.
- Destructive migrations in test setup.
- Modifying build files (`pom.xml`, `build.gradle`) for test purposes
  unless explicitly approved.

## Example skeleton (JUnit 5 + Spring Boot + MockMvc)

```java
package com.example.order;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired MockMvc mockMvc;

    @Test
    void getOrder_returns200_whenOrderExists() throws Exception {
        mockMvc.perform(get("/orders/123"))
               .andExpect(status().isOk());
    }

    @Test
    void getOrder_returns404_whenOrderDoesNotExist() throws Exception {
        mockMvc.perform(get("/orders/does-not-exist"))
               .andExpect(status().isNotFound());
    }
}
```
