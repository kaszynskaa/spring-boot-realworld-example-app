# Automation Leverage Analysis

## Scoring Framework

Each workflow step is scored across four dimensions:

- **Frequency** — how often the step occurs (daily / weekly / monthly)
- **Time/occurrence** — average minutes spent per occurrence
- **AI Capability** — how well AI can automate or accelerate this step (low / medium / high / very high)
- **ROI Score** — composite 1–10 score weighing frequency × time × AI capability

## Scores

| Step | Frequency | Time/occurrence | AI Capability | ROI Score |
|---|---|---|---|---|
| Explore Codebase | Daily | 45 min | Very High | **9** |
| Write Code | Daily | 90 min | Very High | **9** |
| Write Tests | Daily | 40 min | Very High | **9** |
| PR Description | Daily | 15 min | Very High | **9** |
| Understand Requirements | Daily | 30 min | High | 8 |
| Plan Implementation | Daily | 20 min | High | 8 |
| Address Feedback | Weekly | 30 min | High | 7 |
| Local QA | Daily | 20 min | Medium | 6 |
| Fix Pipeline | Weekly | 20 min | Medium | 6 |
| Ticket Pickup | Daily | 10 min | Medium | 5 |
| Await Review | Daily | 120 min | Low | 2 |

## Top 3 Automation Targets

### 1. Explore Codebase (ROI: 9)

Highest single time sink for any new ticket (~45 min/day). Claude Code's semantic search,
architecture explanation, and call-path tracing turns this from a manual treasure hunt into a
5-minute conversation. The combination of daily frequency and high per-occurrence cost makes
this the highest raw-minutes target.

**Automated by:** `/onboard` (first-time), then natural codebase exploration in every session.

### 2. Write Tests (ROI: 9)

Test scaffolding is formulaic — given a method's signature and behaviour, the structure of
unit and integration tests is nearly deterministic. AI capability is very high (repetitive
patterns, no creativity required) and the output is immediately runnable with minimal review.

**Automated by:** `/test-gen` — detects changed files, generates matching JUnit tests, runs
them, and reports results.

### 3. PR Description (ROI: 9)

Extremely high AI capability (reads the diff, writes the summary), near-zero human value in
the *writing* itself — the value is in *having* the description, not writing it. Takes 15 min
manually, ~30 seconds automated. Done daily, the compound saving across a 10-person team is
~25 hours/week.

**Automated by:** Stage 4 of `/ship` — generates PR body from review verdict + diff summary.
