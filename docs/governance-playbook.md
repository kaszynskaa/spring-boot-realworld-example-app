# Governance Playbook — AI-Augmented Pipeline Rollout

**Team:** 10 developers
**Project:** spring-boot-realworld-example-app
**Timeline:** 6 weeks
**Owner:** Engineering Lead

---

## Overview

This playbook describes a phased rollout of Claude Code with governance controls across a
10-person engineering team. The goal is to reach full adoption with audit logging, safety
hooks, and measured ROI within six weeks — without disrupting ongoing delivery.

**Rollout philosophy:** safety first, productivity second. Week 1–2 establish controls before
anyone uses the AI for real work. You only get one chance to build the habit of "AI inside
guardrails" — don't let developers form habits on uncontrolled tooling first.

---

## Pre-Rollout Checklist (before Week 1)

- [ ] Engineering lead reviews and approves `settings.json` permissions
- [ ] Security team reviews hook scripts (`validate-bash.py`, `check-secrets.py`)
- [ ] `.claude/` directory committed to the main branch of each target repository
- [ ] All developers have Claude Code installed (`claude --version` returns cleanly)
- [ ] Java 11 path confirmed on all developer machines (`/usr/libexec/java_home -v 11`)
- [ ] `gh` CLI authenticated on all developer machines (`gh auth status`)
- [ ] Audit log destination decided: local `.claude/audit/` (Week 1–3) → centralised (Week 4+)
- [ ] Team briefed: "AI is a tool with guardrails, not a magic button"

---

## Week 1 — Foundation & Safety Controls

**Goal:** Every developer has Claude Code running with hooks active. No one uses it for real
work yet. This week is about making sure the safety net is in place before anyone jumps.

### Actions

**Day 1–2: Install and smoke-test**
- Each developer clones the repo and confirms `.claude/` is present
- Run the hook self-tests:
  ```bash
  echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
    | python3 .claude/hooks/validate-bash.py
  # Expected: {"decision": "block", "reason": "..."}

  echo '{"tool_name":"Write","tool_input":{"file_path":"src/Foo.java","content":"sk-abc123XYZabc123XYZabc123XYZabc123XYZabc123XYZ12"}}' \
    | python3 .claude/hooks/check-secrets.py
  # Expected: {"decision": "block", "reason": "..."}
  ```
- Confirm audit directory exists and is writable: `ls -la .claude/audit/`

**Day 3–4: Team walkthrough (60 min session)**
- Walk through `CLAUDE.md` — everyone reads it, questions answered
- Walk through `settings.json` — explain every allow and deny rule
- Demonstrate a hook blocking a dangerous command live
- Demonstrate audit log entry being written

**Day 5: Dry run**
- Each developer runs `/onboard` on the repo and reads the output
- No production code changes this week

### Success Criteria
- [ ] All 10 developers have hooks confirmed working
- [ ] All 10 developers have read CLAUDE.md
- [ ] Zero hook bypasses attempted
- [ ] At least one audit log entry per developer

---

## Week 2 — Slash Command Training

**Goal:** Developers are comfortable with all 5 slash commands. They use them on low-risk
tasks (documentation, tests for existing code, understanding unfamiliar files).

### Actions

**Day 1–2: /onboard and /review practice**
- Each developer runs `/onboard` on a module they didn't write
- Each developer runs `/review` on their last merged PR (post-hoc, no stakes)
- Discuss review output in team standup: did Claude catch real issues?

**Day 3: /test-gen practice**
- Identify 3 files in `core/` or `application/` with low test coverage
- Each developer runs `/test-gen` on one of those files
- Review generated tests together — focus on what the AI got right and wrong

**Day 4: /commit practice**
- Make a small non-production change (update a comment, add a test)
- Run `/commit` and review the generated message
- Compare to what you would have written manually

**Day 5: /ship dry run on a feature branch**
- Each developer creates a `practice/` branch
- Makes a trivial change (add a field to a DTO)
- Runs `/ship` end-to-end up to (but not including) the `git push` step
- Documents: what did each stage catch? what was the commit message quality?

### Known Issues to Discuss
- `/test-gen` may generate tests that don't compile if it misreads method signatures —
  always review before accepting
- `/review` is opinionated about Lombok style; adjust CLAUDE.md if team disagrees
- `/commit` asks for confirmation — do not skip this step

### Success Criteria
- [ ] Every developer has run all 5 commands at least once
- [ ] Team has agreed on any CLAUDE.md changes based on feedback
- [ ] Zero "I just bypassed the pipeline" incidents

---

## Week 3 — Controlled Production Use

**Goal:** `/review` and `/test-gen` used on all new PRs. `/commit` and `/ship` optional.
Audit logs reviewed weekly.

### Actions

**Process change (announce in team standup):**
> "Starting this week, every PR must include a `/review` output in the PR description.
> Paste the verdict line (`APPROVE`, `APPROVE WITH COMMENTS`, or `REQUEST CHANGES`) and
> the bulleted list of findings."

**Day 1: First real PRs with /review**
- Each developer includes `/review` output in their next PR
- Reviewers check: did Claude miss anything? did it flag false positives?

**Day 3: First audit log review**
- Engineering lead runs:
  ```bash
  jq -r '.tool_name' .claude/audit/audit.jsonl | sort | uniq -c | sort -rn
  ```
- Check for unexpected tool usage patterns
- Confirm no blocked events were manually bypassed

**Day 5: Retrospective (30 min)**
Questions to answer:
1. Which slash command saved the most time this week?
2. Which hook fired? Was it a true positive or false positive?
3. Does CLAUDE.md need any updates based on real-world use?

### Metrics to Track from Week 3 Onwards
| Metric | Target | How to measure |
|---|---|---|
| `/review` coverage | 100% of PRs | PR description contains verdict line |
| Hook block rate | >0 (hooks are firing) | `grep "decision.*block" .claude/audit/audit.jsonl` |
| False positive rate | <10% of blocks | Count developer-overridden blocks |
| Test coverage trend | Increasing | `./gradlew test jacocoTestReport` |

### Success Criteria
- [ ] `/review` used on 100% of PRs this week
- [ ] At least one genuine issue caught by `/review` before merge
- [ ] First weekly audit log review completed

---

## Week 4 — Full Pipeline Adoption

**Goal:** `/ship` is the default path for all non-trivial changes. Manual git commit/push
still allowed but tracked. Audit logs centralised.

### Actions

**Process change:**
> "From this week, use `/ship` for any change that touches `src/`. Manual commit is still
> fine for documentation-only changes."

**Day 1–2: Centralise audit logs**
- Update `audit-log.sh` to ship to a central store in addition to local file:
  ```bash
  # Append to local file (existing)
  echo "$LOG_ENTRY" >> "$AUDIT_DIR/audit.jsonl"

  # Also ship to central store — adapt for your stack:
  # curl -s -X POST "$LOG_ENDPOINT" -d "$LOG_ENTRY" -H "Content-Type: application/json"
  # aws s3 cp - "s3://team-audit-logs/$(date +%Y/%m/%d)/$(uuidgen).jsonl" <<< "$LOG_ENTRY"
  ```
- Decision: who has read access to central audit store?

**Day 3: Expand secret scanning**
- Review `check-secrets.py` patterns against your actual codebase
- Add any project-specific patterns (internal API key formats, DB connection string patterns)
- Test new patterns before deploying:
  ```bash
  echo '{"tool_name":"Write","tool_input":{"file_path":"src/Config.java",
    "content":"jdbc:sqlite:file:prod.db?password=hunter2"}}' \
    | python3 .claude/hooks/check-secrets.py
  ```

**Day 5: Measure Week 3–4 baseline**
- Pull time-to-PR data from git log:
  ```bash
  git log --format="%H %ai %s" --since="2 weeks ago" | head -20
  ```
- Compare PR description quality (before vs after `/ship`)
- Survey team: "How many minutes did /ship save you this week?"

### Success Criteria
- [ ] `/ship` used for >80% of `src/` changes
- [ ] Audit logs shipping to central store
- [ ] Secret scanner updated with project-specific patterns

---

## Week 5 — Governance Hardening

**Goal:** Settings hierarchy enforced. Hook maintenance process defined. Incident response
procedure documented.

### Actions

**Day 1: Settings hierarchy audit**
- Check each developer machine for local `settings.json` overrides:
  ```bash
  cat ~/.claude/settings.json 2>/dev/null || echo "No user-level settings"
  ```
- Identify any rules that should be at user level (apply across all repos) vs project level
- Recommended: move deny rules to user-level settings so they apply even in other projects

**Day 2: Hook maintenance process**
- Assign hook ownership: who reviews PRs that modify `.claude/hooks/`?
- Add hook tests to CI:
  ```bash
  # In .github/workflows/gradle.yml, add:
  - name: Test governance hooks
    run: |
      echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
        | python3 .claude/hooks/validate-bash.py && exit 1 || true
      echo '{"tool_name":"Bash","tool_input":{"command":"./gradlew test"}}' \
        | python3 .claude/hooks/validate-bash.py
  ```
- Rule: hook changes require 2 approvals (same as security config changes)

**Day 3: Incident response procedure**
Document and share:

```
IF a hook fires unexpectedly:
  1. Do NOT edit the hook to make it pass.
  2. Escalate to hook owner with the blocked command.
  3. If it's a false positive, file a PR to update the pattern with a test case.
  4. If it's a true positive, thank the hook and fix the underlying issue.

IF audit logs show an unexpected action:
  1. Identify the session_id and cross-reference with git log.
  2. If the change was committed, review the diff.
  3. If the change was harmful, revert the commit and rotate any exposed secrets.
```

**Day 5: Security review**
- Engineering lead + one security-minded developer review all hook patterns
- Check: are there dangerous patterns NOT in `validate-bash.py`?
- Check: are there false-positive risks in `check-secrets.py` that block legitimate work?

### Success Criteria
- [ ] Hook tests added to CI pipeline
- [ ] Hook ownership assigned and documented
- [ ] Incident response procedure shared with team
- [ ] User-level settings deployed on all machines

---

## Week 6 — Measurement & Continuous Improvement

**Goal:** ROI report generated, team retrospective held, process declared stable.
Ongoing cadence established.

### Actions

**Day 1–2: Generate ROI report**
- Run the full before/after measurement (or use Week 3–5 data):
  ```bash
  # Time from first commit to PR open (proxy for task cycle time)
  git log --format="%H %ai" --since="5 weeks ago" | wc -l
  ```
- Fill in `docs/roi-report.md` with real numbers from this team
- Calculate: hours saved × $150/hr × team size × 48 weeks

**Day 3: Full team retrospective (60 min)**

Questions:
1. **What worked?** Which slash command had the highest real-world impact?
2. **What didn't?** Which command generated more friction than value?
3. **What surprised us?** Any hook fires that revealed a real risk we hadn't considered?
4. **What's missing?** Is there a workflow step that still has no automation?
5. **CLAUDE.md accuracy?** Does it reflect how the team actually works, or has it drifted?

**Day 4: Backlog of improvements**
Common findings and how to address them:

| Finding | Action |
|---|---|
| `/test-gen` generates non-compiling tests | Add example test to CLAUDE.md; refine the prompt |
| `/review` flags too many false positives | Tighten the conventions in CLAUDE.md |
| `/ship` too slow for small changes | Add a `/quick-commit` variant without review stage |
| Audit logs too noisy | Add a `tool_name` filter to `audit-log.sh` |
| CLAUDE.md conventions not followed | Add Spotless or a linter check to CI |

**Day 5: Declare stable + establish cadence**

Ongoing governance cadence:
- **Weekly:** Engineering lead reviews `audit.jsonl` for anomalies (15 min)
- **Monthly:** Team reviews CLAUDE.md for accuracy; update if conventions changed
- **Quarterly:** Rerun before/after measurement; update ROI report with real data
- **On every hook change:** Requires PR with 2 approvals + CI test passing

### Success Criteria
- [ ] ROI report completed with real team data
- [ ] Retrospective held, action items filed
- [ ] Ongoing cadence calendar events created
- [ ] Governance declared stable by engineering lead

---

## Rollout Summary

| Week | Focus | Key Deliverable |
|---|---|---|
| 1 | Foundation & safety | All hooks confirmed working on all machines |
| 2 | Slash command training | Every developer has used all 5 commands |
| 3 | Controlled production use | `/review` on 100% of PRs |
| 4 | Full pipeline adoption | `/ship` for 80%+ of `src/` changes |
| 5 | Governance hardening | Hook tests in CI, incident response documented |
| 6 | Measurement & improvement | ROI report, retrospective, ongoing cadence |

---

## Appendix: Escalation Matrix

| Situation | First contact | Escalate to |
|---|---|---|
| Hook blocks legitimate work | Hook owner | Engineering lead |
| Suspected secret exposure | Engineering lead | Security team + rotate immediately |
| Audit log shows unexpected action | Engineering lead | Engineering lead + affected developer |
| AI generates incorrect/harmful code | Developer (revert) | Engineering lead for pattern review |
| CLAUDE.md conflict with actual practice | Any developer (file PR) | Engineering lead for approval |
