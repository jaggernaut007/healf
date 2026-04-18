---
name: session-handoff
description: >
  Summarize progress and prepare state for the next session. Use when the user
  says 'wrap up', 'end of session', 'save progress', 'what's the current state',
  or 'orient yourself'. Updates PROGRESS.md and feature_list.json for cross-session continuity.
---

# Session Handoff Skill

This skill ensures continuity between agent sessions by managing cross-session state.

## Spec Conformance Gate

- Read `SPEC.md` during both start-session and end-session modes.
- Ensure next steps map to active phase acceptance criteria in `SPEC.md`.
- If current work diverges from `SPEC.md`, record a blocked item and require spec update.

## Two Modes: End Session & Start Session

### End Session Mode
**Triggers**: "wrap up", "end of session", "save progress"

**Tasks**:
1. Update `PROGRESS.md` with structured state:
   ```markdown
   # PROGRESS.md
   
   ## Current Status
   [One-line summary of where we are]
   
   ## Done
   - [Completed item 1 — with test evidence]
   - [Completed item 2 — with test evidence]
   
   ## In Progress
   - [Item currently being worked on]
   - [Next steps for this item]
   
   ## Blocked
   - [Item blocked] — Reason: [why]
   
   ## Next Steps
   1. [Immediate next task]
   2. [Following task]
   
   ## Recent Decisions
   - [Decision 1] — Date: YYYY-MM-DD
   - [Decision 2] — Date: YYYY-MM-DD
   ```

2. Update `feature_list.json` with:
   - Feature status (from test results only, never self-report)
   - Task completion status
   - Timestamps

3. If there are uncommitted changes:
   - Summarize what's uncommitted
   - Ask user if they want to commit before ending session

4. Create summary for auto-memory (strategic knowledge):
   - What was learned
   - Key numbers/metrics
   - Architectural decisions made
   - User preferences discovered

### Start Session Mode
**Triggers**: "what's the current state", "orient yourself", session start

**Tasks**:
1. Read `PROGRESS.md` for tactical state:
   - What's in progress
   - What's blocked
   - Next steps

2. Read auto-memory for strategic knowledge:
   - Past decisions
   - User preferences
   - Lessons learned

3. Read recent git log for implementation history:
   - `git log --oneline -10`
   - What changed recently and why

4. Run `./scripts/init.sh` to verify state:
   - Does current state match documentation?
   - Are there any broken tests/linters?
   - If broken → Fix BEFORE starting new work

5. Provide orientation summary:
   ```
   ## Session Orientation
   
   **Current State**: [Summary from PROGRESS.md]
   
   **Init Status**: [✓ PASS / ✗ FAIL with issues]
   
   **Recent Changes**: [From git log]
   
   **Next Recommended Action**: [Based on PROGRESS.md]
   
   **Relevant Decisions**: [From ADRs or auto-memory]
   ```

## Loop Intelligence Pattern

Each session should start with strictly more knowledge than the previous one:
- **PROGRESS.md** → tactical state (what is in progress now)
- **Auto-memory** → strategic knowledge (what you learned)
- **Git log** → implementation history (what changed, when, why)

Read all three at session start. Write back at session end. This creates a ratchet — knowledge accumulates, mistakes are not repeated.

## Key Rules

### End Session
- Never mark feature complete without test evidence
- Update PROGRESS.md BEFORE clearing context
- Convert relative dates to absolute (not "tomorrow", use YYYY-MM-DD)
- Be specific about what's "in progress" vs "blocked"

### Start Session
- Fix broken state BEFORE starting new work
- Read PROGRESS.md + auto-memory + git log
- Run init.sh to verify state matches documentation
- Orient user on current state before proceeding

## Success Criteria

### End Session Success
- PROGRESS.md accurately reflects current state
- feature_list.json updated with test-verified status
- Strategic knowledge captured for auto-memory
- User understands what to expect in next session

### Start Session Success
- Current state understood
- init.sh passes (or issues identified and fixed)
- User oriented on next steps
- No time wasted rediscovering known information
