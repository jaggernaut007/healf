---
name: ship-it
description: >
  Orchestrate the full release workflow: pre-flight verification, documentation
  updates, commit with lint/test gates, and optional push/deploy. Use when user
  says 'ship it', 'deploy the feature', 'prepare for release', or 'commit and push'.
  Enforces Definition of Done before any deployment.
---

# Ship-It Release Pipeline Skill

The ship-it skill orchestrates a rigid release workflow to ensure quality before deployment.

## Spec Conformance Gate

- Read `SPEC.md` before release actions.
- Verify completed work satisfies active phase/wave acceptance criteria.
- If scope deviates from `SPEC.md`, block release until spec and docs are updated.

## Core Principle
**Never mark a feature complete in PROGRESS.md without having seen a test pass via tool call.**

## Workflow Steps

### 1. Pre-Flight Verification (BLOCKING)
Run `./scripts/init.sh` to confirm current project state.
- If init.sh fails → STOP. Fix broken state before proceeding.
- This ensures we never build on a broken foundation.

### 2. Definition of Done Check (BLOCKING)
Verify all criteria met:
- [ ] Tests pass (verified via tool call, output read)
- [ ] Linter passes
- [ ] Docs updated if behavior changed
- [ ] PROGRESS.md updated with what was done
- [ ] E2E smoke test passes (from init.sh)

### 3. Documentation Updates
Update if behavior changed:
- [ ] `docs/` — API changes, architectural decisions (ADRs)
- [ ] `llms.txt` — If public API changed
- [ ] `PROGRESS.md` — Current status and what was done
- [ ] `feature_list.json` — Feature status from test results only

### 4. Security Check (if applicable)
For new dependencies or security-sensitive code:
- [ ] No secrets in code
- [ ] Dependencies verified in registry
- [ ] Security scan passed (if configured)

### 5. Commit (with Gates)
Perform final commit with structured message:
```
<type>: <subject>

<body explaining what and why>

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**Note**: `hooks.json` Stop hook automatically runs linter/tests before commit.

### 6. Push (Optional, Confirm First)
**ALWAYS confirm with user before pushing.**
- Never force push
- Check for upstream changes first

### 7. Deploy (Optional, Confirm First)
**ALWAYS confirm with user before deploying.**
- Run post-deploy health checks if applicable
- Monitor for errors

## Selective Execution

Support different scopes based on user request:
- "Just commit" → Steps 1-5 only
- "Commit and push" → Steps 1-6
- "Ship it" / "Deploy" → All steps 1-7

## Failure Handling

### Step Fails → Pipeline Stops
- Pre-flight fails → Fix init.sh issues first
- Tests fail → Fix tests before proceeding
- Linter fails → Fix lint errors
- Commit fails → Check hooks.json configuration
- Push fails → Check remote status, conflicts
- Deploy fails → Rollback and investigate

## Key Rules

- Derive feature status from test results only (never self-report)
- Never commit secrets
- Never force push without explicit user approval
- Always confirm before deploying
- Read actual test output (don't assume pass)
- Update PROGRESS.md BEFORE marking feature complete

## Usage Examples

**User says**: "ship it"
→ Run all 7 steps (confirm before push/deploy)

**User says**: "commit this"
→ Run steps 1-5 only

**User says**: "prepare for release"
→ Run steps 1-4, summarize readiness

## Success Criteria

Pipeline succeeds when:
1. All blocking steps pass
2. Changes committed with proper message
3. PROGRESS.md reflects current state
4. (If pushed) Remote updated successfully
5. (If deployed) Health checks pass
