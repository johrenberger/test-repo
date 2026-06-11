# Java / Spring profile

Used by `backend-implementation` when the repo is Java and Spring
Boot is detected. This is the strictest profile — Spring projects
have many ways to drift; this profile enforces the smallest safe
change.

## Detection

- `pom.xml` with `spring-boot-starter-parent`, or `build.gradle` /
  `build.gradle.kts` with `org.springframework.boot` plugin → Spring Boot
- `src/main/java/` and `src/test/java/` present
- JUnit 5 (Jupiter) — preferred. JUnit 4 is allowed if the repo
  already uses it; do not mix.
- Mockito — if present, follow the existing style.
- Testcontainers — if present, follow the existing style.
- Flyway / Liquibase — `db/migration` / `src/main/resources/db/migration`
  directories

## Architecture

Preserve the existing layering. The default in this profile:

- `controller/` — HTTP boundary, request/response DTOs
- `service/` — domain logic
- `repository/` — persistence
- `entity/` / `model/` — JPA entities or domain models
- `dto/` — request/response objects
- `config/` — Spring `@Configuration` classes
- `exception/` — domain exceptions and a `@ControllerAdvice` handler

If the existing repo uses a different layering, match it exactly.
Do not introduce a new package.

## Test rules

- JUnit 5 by default; JUnit 4 if the repo already uses it.
- `@SpringBootTest` only when integration behavior requires the full
  application context, or the existing tests use it. Prefer slice
  annotations (`@WebMvcTest`, `@DataJpaTest`).
- `MockMvc` for MVC, `WebTestClient` for WebFlux. Match the existing
  pattern.
- Do not introduce Lombok, MapStruct, Testcontainers, Flyway,
  Liquibase, or new Spring starters unless explicitly justified.
- Do not introduce Spring Security changes without explicit
  justification.

## Migration rules

- Flyway / Liquibase migrations: do not write destructive migrations.
  For schema changes, prefer additive migrations. For destructive
  changes, use `database-migration-safety` first.
- Backfills: never run destructive backfills in a single transaction
  against production data; propose a phased approach in
  `database-migration-safety`.

## Forbidden

- New Spring starters, Lombok, MapStruct, Testcontainers, Flyway,
  Liquibase, Spring Security changes.
- Destructive migrations.
- Cross-cutting concerns added without a clear current need
  (e.g. global exception handlers, request/response logging,
  tracing) — propose a separate task.
- Changing build files (`pom.xml`, `build.gradle`,
  `build.gradle.kts`) for implementation purposes unless explicitly
  approved.

## Example layering preservation

```text
src/main/java/com/example/order/
├── OrderApplication.java
├── controller/OrderController.java
├── service/OrderService.java
├── repository/OrderRepository.java
├── entity/Order.java
├── dto/OrderResponse.java
├── dto/CreateOrderRequest.java
└── exception/OrderNotFoundException.java

src/test/java/com/example/order/
├── controller/OrderControllerTest.java
├── service/OrderServiceTest.java
└── repository/OrderRepositoryTest.java  (only if the repo already has repository tests)
```

If the repo has only controller + service tests, do not introduce a
new `repository/` test directory.
