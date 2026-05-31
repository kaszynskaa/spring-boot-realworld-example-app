Run the full shipping pipeline: review → test generation → commit → pull request.

This command orchestrates the complete workflow from staged changes to an open PR.
Stop immediately if any stage returns blockers — do not proceed to the next stage.

---

## Stage 1: Code Review

Run /review against the staged changes.
- If verdict is REQUEST CHANGES: list the blockers, stop, and ask the user to fix them first.
- If verdict is APPROVE or APPROVE WITH COMMENTS: note any warnings and continue.

## Stage 2: Test Generation & Verification

Run /test-gen for the changed files.
- If any tests fail: show the failures, stop, and ask the user to fix them.
- If tests pass: report coverage summary and continue.

## Stage 3: Commit

Run /commit to generate a smart commit message and create the commit.
- Wait for user confirmation of the commit message before proceeding.
- If the user edits the message, use their version.

## Stage 4: Pull Request

After the commit is created:
1. Run `git branch --show-current` to get the current branch name.
2. If the branch is `main` or `master`, stop and warn the user to create a feature branch first.
3. Push the branch: `git push -u origin <branch>` (ask for confirmation first).
4. Create a PR using `gh pr create` with:
   - Title: the commit subject line.
   - Body template:
     ```
     ## Summary
     <bullet points from the review stage — what changed and why>

     ## Test plan
     - [ ] Unit/integration tests added (see /test-gen output)
     - [ ] `./gradlew test` passes locally
     - [ ] Spotless formatting: `./gradlew spotlessCheck`

     ## Review checklist
     - [ ] Architecture layer boundaries respected
     - [ ] No hardcoded secrets
     - [ ] New endpoints require authentication
     ```
5. Output the PR URL.

---

## Summary report

After all stages complete, print a one-page summary:
- Review verdict
- Tests: N added, N passed
- Commit SHA and message
- PR URL
- Total time (approximate)
