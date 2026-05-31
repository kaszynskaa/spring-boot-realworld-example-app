# Onboard

Generate a complete onboarding briefing for a new team member joining this project.

Steps:

1. Read CLAUDE.md for team conventions and architecture rules.
2. Read `build.gradle` for the dependency stack.
3. Read `src/main/resources/application.properties` for runtime config.
4. Explore `src/main/java/io/spring/` — list all packages and read one representative file per layer.
5. Read `src/main/resources/schema/` for the GraphQL schema.
6. Run `git log --oneline -10` for recent activity context.
7. Run `find src/test -name "*.java" | wc -l` to gauge test coverage breadth.

Then produce a structured briefing covering:

---

## 1. What This Project Is (2 sentences)

## 2. How to Run It Locally

- Prerequisites (Java version, env vars)
- Build + run command
- How to verify it's working (URL to hit)

## 3. Architecture Map

- Diagram of the 4 layers with their responsibilities
- Key classes in each layer (actual class names from the codebase)
- Data flow: HTTP request → controller → service → mapper → DB

## 4. Key Files to Read First

List 8–10 files with a one-line description of why each matters.

## 5. How to Make a Change (end-to-end example)

Walk through adding a new field to an existing endpoint: where to touch, in what order.

## 6. Team Conventions Cheat Sheet

- Naming, layer rules, test requirements, git workflow — condensed from CLAUDE.md.

## 7. Common Pitfalls

At least 3 things that trip up newcomers in this codebase.

## 8. Slash Commands Available

List the 5 commands with one-line descriptions of when to use each.
