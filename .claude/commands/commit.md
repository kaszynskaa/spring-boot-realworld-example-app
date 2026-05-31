Generate a smart commit message from the current diff and create the commit.

Steps:
1. Run `git status` to check what is staged and unstaged.
2. Run `git diff --staged` to read the full staged diff. If nothing is staged, tell the user to stage files first and stop.
3. Analyse the diff:
   - What is the primary intent? (new feature, bug fix, refactor, test, chore, docs)
   - Which layer(s) are affected? (api / application / core / infrastructure)
   - What is the user-visible or developer-visible effect?
4. Draft a commit message following these rules (from CLAUDE.md):
   - Subject line: imperative mood, ≤72 characters, no period at end.
   - Format: `<type>(<scope>): <description>` — e.g. `feat(articles): add slug uniqueness validation`
   - Valid types: feat, fix, refactor, test, chore, docs.
   - Optional body: what changed and why (not how), wrapped at 72 chars.
5. Show the proposed commit message and ask for confirmation before committing.
6. On confirmation, run:
   ```
   git commit -m "<subject>" -m "<body if any>"
   ```
7. Show the resulting `git log --oneline -1` to confirm success.
