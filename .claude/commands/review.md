Review the staged changes in this repository against the team conventions defined in CLAUDE.md.

Steps:
1. Run `git diff --staged` to get all staged changes. If nothing is staged, run `git diff HEAD` instead and note that.
2. Read CLAUDE.md to load the current conventions (architecture layers, code style, testing standards, security rules).
3. For each changed file, check:
   - **Architecture violations** — does the change respect layer boundaries (api → application → core → infrastructure)?
   - **Code style** — Lombok usage, no field injection, no System.out, proper exception handling.
   - **Test coverage** — are new public methods accompanied by tests?
   - **Security** — no hardcoded secrets, all new endpoints properly secured.
   - **Correctness** — obvious bugs, null pointer risks, missing input validation.
4. Output a structured review with sections:
   - ✅ What looks good
   - ⚠️ Minor issues (style, naming, missing tests)
   - ❌ Blockers (architecture violations, security issues, bugs)
5. End with a clear verdict: **APPROVE**, **APPROVE WITH COMMENTS**, or **REQUEST CHANGES**.

Be specific — cite file names and line numbers. Do not flag style issues that Spotless will auto-fix.
