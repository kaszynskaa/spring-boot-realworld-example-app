Generate tests for recently changed files, run them, and report results.

Steps:
1. Run `git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only --staged` to find changed Java files.
2. For each changed `.java` file in `src/main/java`:
   a. Read the file to understand its public methods and behaviour.
   b. Determine the appropriate test type:
      - Files in `core/` → plain JUnit 5 unit test (no Spring context).
      - Files in `application/` → JUnit 5 with Mockito mocks.
      - Files in `api/` → `@WebMvcTest` or RestAssured integration test.
   c. Check if a corresponding test file already exists in `src/test/java` at the matching path.
   d. If it exists, add missing test cases. If not, create a new test class.
   e. Cover at minimum: one happy-path test and one error/edge-case test per public method.
3. Write all generated/updated test files.
4. Run the tests: `JAVA_HOME=/Library/Java/JavaVirtualMachines/microsoft-11.jdk/Contents/Home ./gradlew test --tests "*" 2>&1 | tail -30`
5. Report:
   - Which test files were created or updated.
   - Test run results (passed / failed / skipped).
   - Any test failures with the relevant stack trace excerpt.
   - Estimated coverage improvement (files touched vs. test methods added).
