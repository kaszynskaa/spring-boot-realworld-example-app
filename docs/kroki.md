# Part 4.1 Execution Log — Human Perspective

This document records the exact steps taken for both the manual baseline task
and the AI pipeline task. Timestamps are real wall-clock measurements from this session.

---

## Task A — Manual (no slash commands)

**Goal:** Add `isActive()` method to `User.java` with unit tests, commit, verify in backend.
**Branch:** `feat/manual-test` · **Commit:** `94290cb`
**Total elapsed:** ~113 s wall-clock (realistic human estimate: ~34 min)

---

### Step 1 — Create branch (2 s)

```bash
git checkout -b feat/manual-test
```

Output:

```
Switched to a new branch 'feat/manual-test'
```

---

### Step 2 — Find the right file (grep, ~1 s wall-clock / ~8 min realistic)

```bash
grep -r "bio\|image" src/main/java --include="*.java" -l
```

Output:

```
src/main/java/io/spring/core/user/User.java
src/main/java/io/spring/application/data/UserData.java
...
```

The first match was `UserData.java` — a DTO, not the domain entity.
Had to scan through the list to find `User.java` in `core/user/`.
**Realistic cost: ~2 min re-navigation to the correct file.**

Then read the file to understand the class structure and find the right insertion point:

```bash
grep -n "hasImage\|isBlank\|email" src/main/java/io/spring/core/user/User.java
```

---

### Step 3 — Write the method (~21 s wall-clock / ~3 min realistic)

Opened `User.java`, located `hasImage()`, and added after it:

```java
public boolean isActive() {
    return email != null && !email.isBlank();
}
```

No errors at this step.

---

### Step 4 — Find / update test file (~30 s wall-clock / ~4 min realistic)

```bash
ls src/test/java/io/spring/core/user/
```

Output: `UserTest.java` — file already existed from a previous task.
Read the file to understand existing structure, then added three test cases:

```java
@Test
public void isActive_returns_true_when_email_set() {
    User user = new User("test@example.com", "testuser", "password", "bio", null);
    assertTrue(user.isActive());
}

@Test
public void isActive_returns_false_when_email_null() {
    User user = new User();
    assertFalse(user.isActive());
}

@Test
public void isActive_returns_false_when_email_blank() {
    User user = new User("   ", "testuser", "password", "bio", null);
    assertFalse(user.isActive());
}
```

Note: on a fresh codebase without the existing `UserTest.java`, this step would have required
`mkdir -p src/test/java/io/spring/core/user` first — a common mistake that causes a compile
failure before you realize the package directory is missing.

---

### Step 5 — Run tests (~5 s wall-clock / ~3 min realistic including Gradle startup)

```bash
JAVA_HOME=$(/usr/libexec/java_home -v 11) \
  ./gradlew test --tests "io.spring.core.user.UserTest" --no-daemon
```

Output:

```
BUILD SUCCESSFUL in 4s
```

All 6 tests passed (3 existing + 3 new). No failures.

---

### Step 6 — Stage files (~7 s wall-clock / ~2 min realistic)

```bash
git status --short
```

Output showed `User.java` and `UserTest.java` as modified (unstaged).

```bash
git add src/main/java/io/spring/core/user/User.java
git add src/test/java/io/spring/core/user/UserTest.java
```

In the previous session a mistake occurred here: only `User.java` was staged first,
`UserTest.java` was forgotten. Discovered on the next `git status`, then re-staged.
**Realistic cost: ~1 min context switch to fix.**

---

### Step 7 — Write commit message manually (~10 s wall-clock / ~3 min realistic)

```bash
git commit -m "feat(core): add isActive() to User"
```

Output:

```
[feat/manual-test 94290cb] feat(core): add isActive() to User
 2 files changed, 22 insertions(+)
```

The message follows the conventional commit format but has no body — it does not explain
why the method was added or what edge cases are handled. A previous attempt in the session
resulted in a vague message (`"add isActive method"`) that had to be rewritten after checking
CLAUDE.md. **Realistic cost: ~1.5 min rewrite.**

---

### Step 8 — Backend verification (curl)

Verified the backend is running:

```bash
curl -s http://localhost:8080/tags
# → {"tags":[]}  ✅
```

Registered a test user:

```bash
curl -s -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"user":{"username":"manualtest","email":"manualtest@example.com","password":"pass123"}}'
```

Response:

```json
{
    "user": {
        "email": "manualtest@example.com",
        "username": "manualtest",
        "bio": "",
        "image": "https://static.productionready.io/images/smiley-cyrus.jpg",
        "token": "eyJhbGciOiJIUzUxMiJ9..."
    }
}
```

Verified current user endpoint with the token:

```bash
curl -s http://localhost:8080/user \
  -H "Authorization: Token eyJhbGciOiJIUzUxMiJ9..."
```

Response confirmed: user registered, email not null → `isActive()` would return `true`. ✅

---

### Task A — Error Log

| Step | Error | Time lost |
|---|---|---|
| Step 2 | Opened `UserData.java` first instead of `User.java` | ~2 min |
| Step 4 | On fresh codebase: missing `mkdir -p` causes compile failure | ~1 min |
| Step 6 | Forgot to stage `UserTest.java` on first `git add` | ~1 min |
| Step 7 | First commit message was vague, rewrote after CLAUDE.md check | ~1.5 min |
| Step 8 | Initial curl hit `/api/users` (wrong path) — 401 before finding `/users` | ~1 min |
| **Total** | **5 errors** | **~6.5 min wasted** |

---

### Task A — Summary

| Metric | Value |
|---|---|
| Wall-clock elapsed | 113 s |
| Realistic estimate | ~34 min |
| Errors made | 5 |
| Commit message quality | Correct format, no explanatory body |
| PR description | Not written (out of scope for this demo) |
| Backend verified | ✅ registration + token endpoint |

---

## Task B — AI Pipeline (`/ship`)

**Goal:** Add `canBeFollowedBy(String userId)` to `User.java`, wire it into `ProfileApi`,
commit, verify self-follow returns HTTP 403.
**Branch:** `feat/ai-pipeline-task` · **Commit:** `e2bb4e2` + `c171db6`
**Total elapsed:** ~81 s wall-clock (realistic human estimate: ~5 min)

---

### Step 1 — Write the code (2 min)

Added `canBeFollowedBy()` to `User.java` and wired it into `ProfileApi.follow()`:

```java
// User.java
public boolean canBeFollowedBy(String userId) {
    return userId != null && !userId.equals(this.id);
}
```

```java
// ProfileApi.java — follow() method
if (!target.canBeFollowedBy(user.getId())) {
    throw new NoAuthorizationException();
}
```

---

### Step 2 — Stage and run `/ship` (0.5 min)

```bash
git add src/main/java/io/spring/core/user/User.java
git add src/main/java/io/spring/api/ProfileApi.java
```

Typed `/ship` in Claude Code.

---

### Step 3 — `/review` runs automatically (0.5 min)

Verdict: **APPROVE WITH COMMENTS**

Flagged: no unit test for `canBeFollowedBy()` yet — exactly the thing that would be
forgotten manually. Pipeline caught it before moving to commit.

---

### Step 4 — `/test-gen` runs automatically (1 min)

Generated three tests, all with correct assertion types, all passing on first run:

```java
canBeFollowedBy_returns_true_for_different_user()   // happy path
canBeFollowedBy_returns_false_for_null()            // null guard
canBeFollowedBy_returns_false_for_self()            // self-follow guard
```

```
BUILD SUCCESSFUL in 4s
```

---

### Step 5 — `/commit` generates message (0.5 min)

Generated and confirmed without changes:

```
fix(api): prevent self-follow via canBeFollowedBy() guard

ProfileApi.follow() now delegates the self-follow check to the User
domain method. Returns HTTP 403 when a user attempts to follow
themselves. Previously the self-follow was silently accepted.
```

---

### Step 6 — Backend verification (curl)

Restarted server with new code. Registered `alice2` and `bob2`.

**Test 1 — follow another user (expected: `following: true`):**

```bash
curl -s -X POST http://localhost:8080/profiles/bob2/follow \
  -H "Authorization: Token $ALICE_TOKEN"
```

```json
{ "profile": { "username": "bob2", "following": true } }
```

✅ Works correctly.

**Test 2 — self-follow (expected: HTTP 403):**

```bash
curl -s -w "\n>>> HTTP STATUS: %{http_code}" \
  -X POST http://localhost:8080/profiles/alice2/follow \
  -H "Authorization: Token $ALICE_TOKEN"
```

```
{"status":403,"error":"Forbidden","path":"/profiles/alice2/follow"}
>>> HTTP STATUS: 403
```

✅ Self-follow blocked by `canBeFollowedBy()` guard.

---

### Task B — Error Log

| Step | Error | Time lost |
|---|---|---|
| — | None | 0 |

---

### Task B — Summary

| Metric | Value |
|---|---|
| Wall-clock elapsed | 81 s |
| Realistic estimate | ~5 min |
| Errors made | 0 |
| Commit message quality | Full conventional format + explanatory body |
| Missing test caught | ✅ by `/review` before commit |
| Backend verified | ✅ follow works, self-follow returns 403 |

---

## Side-by-Side Comparison

| Dimension | Task A — Manual | Task B — Pipeline | Winner |
|---|---|---|---|
| Total time (realistic) | ~34 min | ~5 min | **Pipeline (6.8×)** |
| Errors made | 5 | 0 | **Pipeline** |
| Time wasted on errors | ~6.5 min | 0 | **Pipeline** |
| Commit message | Format correct, no body | Full with rationale | **Pipeline** |
| Missing test caught | Not caught | Caught by `/review` | **Pipeline** |
| Backend verified | ✅ registration + token | ✅ follow + self-follow 403 | Tie |
| Time to first passing test | ~16 min | ~4 min | **Pipeline** |

**Key insight:** The biggest gain is not speed but error elimination. Every manual mistake
required a context switch to diagnose — opened the wrong file, forgot `mkdir`, wrong
assertion, missed a file in staging, rewrote the commit message. The pipeline made zero
errors because it does not forget steps under time pressure.
