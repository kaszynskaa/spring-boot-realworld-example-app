# CLAUDE.md — Team Workflow Rules & Conventions

## Project Overview

Spring Boot 2.6 + MyBatis + SQLite REST/GraphQL API following the RealWorld spec.
Java 11 required. Build tool: Gradle. Run with `JAVA_HOME=<java-11-path> ./gradlew bootRun`.

## Architecture

```
src/main/java/io/spring/
├── api/           # Controllers (REST) and GraphQL data fetchers — web layer only
├── application/   # Query/read services (CQRS read side) — return DTOs
├── core/          # Domain entities, repository interfaces, write services
└── infrastructure/ # MyBatis mappers, JWT, security config — tech details
```

**Layer rules:**
- `api` may call `application` and `core` services. Never the reverse.
- `application` reads only — no writes, no side effects.
- `core` has no Spring/HTTP/DB imports. Pure domain logic.
- `infrastructure` implements interfaces defined in `core`.

## Code Conventions

- No business logic in controllers — delegate to services immediately.
- Services in `core` must be covered by unit tests without Spring context.
- Use Lombok `@RequiredArgsConstructor` for injection; no `@Autowired` on fields.
- All public API methods need input validation (`@Valid`, `@NotBlank`, etc.).
- Exceptions: throw domain exceptions from `core`, translate to HTTP codes in `api`.
- No `System.out.println` — use SLF4J `log.info/warn/error`.
- Google Java Format enforced via Spotless (`./gradlew spotlessApply`).

## Testing Standards

- Unit tests: plain JUnit 5, no Spring context, mock with Mockito.
- Integration tests: `@SpringBootTest` with `MockMvc` or RestAssured.
- Test class naming: `<ClassName>Test` for unit, `<Feature>IntegrationTest` for integration.
- Every new public service method needs at least one happy-path + one error-path test.
- Run tests: `JAVA_HOME=<java-11> ./gradlew test`
- Coverage target: 70% line coverage on `core` and `application` packages.

## Git Workflow

- Branch naming: `feat/<short-description>`, `fix/<short-description>`, `chore/<topic>`.
- Commits: imperative mood, under 72 chars, no "WIP" on main.
- PR must pass CI (tests + Spotless) before merge.
- Squash merge to keep main history clean.
- Never force-push to `main`.

## Security Rules

- JWT secret lives in `application.properties` — never hardcode tokens in source.
- No credentials, API keys, or `.env` files committed.
- All endpoints require auth unless explicitly whitelisted in `SecurityConfig`.

## Slash Commands Available

| Command | Purpose |
|---|---|
| `/review` | AI code review of staged changes vs. these conventions |
| `/test-gen` | Generate + run tests for recently changed files |
| `/commit` | Smart commit message from diff |
| `/ship` | Full pipeline: review → test-gen → commit → PR |
| `/onboard` | Architecture briefing for new team members |
