# Settings Hierarchy & Permission Configuration

## Claude Code Settings Hierarchy

Claude Code reads settings from four levels, applied in order from lowest to highest priority.
A rule at a higher level overrides the same rule at a lower level. Deny rules always take
precedence over allow rules at the same level.

```
┌─────────────────────────────────────────────────────────────┐
│  4. Enterprise / Managed Policy                             │  ← highest priority
│     /etc/claude-code/managed-settings.json                  │
│     Platform MDM / registry (Windows)                       │
│     Cannot be overridden by any lower level                 │
├─────────────────────────────────────────────────────────────┤
│  3. User Settings                                           │
│     ~/.claude/settings.json                                 │
│     Applies across ALL projects for this developer          │
│     Can be overridden by project or local settings          │
├─────────────────────────────────────────────────────────────┤
│  2. Project Settings  ← THIS FILE                           │
│     .claude/settings.json  (committed to git)               │
│     Applies to everyone who clones this repo                │
│     Can be overridden by local settings                     │
├─────────────────────────────────────────────────────────────┤
│  1. Local Settings                                          │
│     .claude/settings.local.json  (gitignored)              │
│     Developer-specific overrides, never committed           │
│     Highest non-enterprise priority                         │
└─────────────────────────────────────────────────────────────┘
```

**Key rule:** `deny` wins over `allow` at the same level. A deny in project settings
cannot be overridden by an allow in local settings — the deny at project level stands.

---

## This Project's Configuration

### Permission Mode: `default`

```json
"defaultMode": "default"
```

**What it means:** Claude Code prompts for confirmation before executing any tool call
that is not covered by an explicit `allow` or `deny` rule. Combined with our allowlist,
this means:

- Tools on the `allow` list → run automatically, no prompt
- Tools on the `deny` list → blocked immediately, no prompt
- Everything else → user is asked to approve or deny

**Why `default` and not `bypassPermissions`?**

`bypassPermissions` skips all permission prompts — useful for fully automated CI pipelines
where no human is present. For a team of developers working interactively, `default` is
the right choice: the allowlist handles the common cases automatically, but unusual or
unconfigured tool calls still surface for human review. This gives developers visibility
into what the AI is doing without constant interruption on routine operations.

`acceptEdits` would auto-approve all file edits without prompting — we deliberately do
NOT use this because our `scope-guard.sh` hook and the `Write/Edit` deny rules depend on
the permission layer as a second line of defence. Auto-accepting edits would bypass that.

---

## Allowlist — Why Each Rule Is Here

### Build & Test

```json
"Bash(./gradlew *)",
"Bash(JAVA_HOME=* ./gradlew *)"
```
Core build tool. The `JAVA_HOME=*` variant is needed because the system Java is 26 but
the project requires Java 11. Without this, every Gradle call would need manual approval.

### Git — Read Operations

```json
"Bash(git status)",
"Bash(git diff*)",
"Bash(git log*)",
"Bash(git branch*)"
```
Read-only git commands. Used by `/review` (to get the staged diff) and `/onboard`
(to read recent history). Zero destructive potential — always auto-approved.

### Git — Write Operations

```json
"Bash(git add *)",
"Bash(git commit*)",
"Bash(git push*)"
```
Required by `/commit` and `/ship`. These are write operations, but they're in the
allowlist because the slash commands can't function without them. The hooks provide
the second layer: `validate-bash.py` ensures `push` can't be combined with `--force`,
and the denylist provides a belt-and-suspenders block on force-push patterns.

### GitHub CLI

```json
"Bash(gh pr *)"
```
PR creation in `/ship` Stage 4. Scoped to `pr` subcommand — cannot accidentally
trigger `gh repo delete` or other destructive `gh` operations.

### Local HTTP

```json
"Bash(curl -s http://localhost:*)"
```
Smoke-testing the running Spring Boot server. Explicitly restricted to `localhost` —
prevents the AI from making external HTTP requests via curl during normal operation.

### Filesystem Read

```json
"Bash(find src *)", "Bash(find .claude *)", "Bash(grep -r * src/)",
"Bash(ls *)", "Bash(cat *)"
```
Codebase exploration used by `/onboard` and `/test-gen`. Read operations only.
`find` is scoped to `src/` and `.claude/` to avoid accidental filesystem traversal.

### Audit Infrastructure

```json
"Bash(mkdir -p .claude/audit)"
```
Allows the audit hook to create its target directory on first run. Scoped to a
single specific path.

### File Operations

```json
"Read(*)"
```
Unrestricted read access. Reading is safe — the risk is always in writing.

```json
"Write(src/*)", "Write(.claude/*)", "Write(docs/*)",
"Write(CLAUDE.md)", "Write(README.md)", "Write(REPORT.md)", "Write(workflow-analysis.md)"
```
Writes scoped to the project's work areas. `scope-guard.sh` enforces the same
constraint as a hook-level second check. Named root files are explicitly listed
rather than using a wildcard to prevent accidental writes to `build.gradle` etc.

---

## Denylist — Why Each Rule Is Here

```json
"Bash(rm *)"
```
Any deletion must be a conscious human action. No exceptions — even `rm -f build.log`
requires manual execution. The hook `validate-bash.py` provides the first block;
this denylist is the second.

```json
"Bash(curl * | *sh*)", "Bash(wget * | *sh*)"
```
Piping remote content to a shell is the classic supply-chain attack vector. Blocked
unconditionally regardless of the URL or shell.

```json
"Bash(chmod 777 *)"
```
World-writable permissions are never correct in this project. If a file needs
permissions changed, a developer should do it intentionally.

```json
"Bash(sudo *)"
```
The AI should never require root access for this project. Any prompt to `sudo`
indicates something has gone wrong and must be investigated.

```json
"Bash(git push --force*)", "Bash(git push *-f *)"
```
Force-push rewrites shared history and can destroy others' work permanently.
Always requires a conscious human decision — never automated.

```json
"Bash(git reset --hard*)"
```
Destroys all uncommitted changes without recovery. Too destructive for unattended
execution.

```json
"Write(/etc/*)", "Write(/usr/*)", "Write(/System/*)"
```
System directories. No legitimate project operation requires writing here. If the
AI ever attempts this, it indicates a serious prompt injection or model error.

```json
"Write(~/.ssh/*)", "Write(~/.aws/*)"
```
SSH keys and AWS credentials. Writing to either would be catastrophic — immediate
credential rotation required. Blocked at the permission layer before any hook even runs.

---

## Settings Hierarchy Decision: Why Project Level?

All rules in this project live at **Level 2 (project settings)** because:

1. They're **team-wide conventions** — every developer working on this repo should have
   the same safety controls, not just those who remember to configure them locally.

2. They're **auditable** — committed to git, so changes require a PR, a review, and
   leave a permanent history trail.

3. They're **not sensitive** — the rules describe what's allowed and denied but contain
   no credentials, tokens, or environment-specific paths that would vary per machine.

**What should move to user level (`~/.claude/settings.json`) in a real deployment:**

The `deny` rules for `rm`, `sudo`, `git push --force`, and writes to `/etc/`, `/usr/`,
`~/.ssh/`, `~/.aws/` are security rules that should apply across *all* repositories,
not just this one. Moving them to user-level settings means a developer is protected
even when working in a project that doesn't have its own `.claude/settings.json`.

**What should move to enterprise level in a 50-person organisation:**

The `disableAutoMode` and `allowManagedPermissionRulesOnly` flags, combined with the
deny rules, should be set in managed settings so that no individual project or developer
can disable them.
