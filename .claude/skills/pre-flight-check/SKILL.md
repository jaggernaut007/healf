---
name: pre-flight-check
description: >
  Industrial Meta-Tool for Antigravity/Gemini compliance.
  Consolidates codebase discovery, impact analysis, and persistent memory updates.
  Use before any architectural change or multi-file implementation wave.
---

# Skill: Pre-Flight Check (Industrial Meta-Tool)

This skill implements **Pattern C: Meta-Tools** from the v7.2 Industrial Guide. It provides a unified workflow to reduce token consumption and improve decision quality.

## Prerequisites
- nexus-mcp (for search, caller/callee, impact)
- memstate-ai (for persistent memory)
- sequential-thinking (for planning)

## Protocol

### 1. Unified Discovery
Instead of running individual `grep` and `find` commands, use **nexus-mcp** to perform a hybrid search for the target feature or module.
- `search(query="[module name]")`: Identify core files and existing patterns.

### 2. Impact Assessment
Analyze the blast radius of the proposed change.
- `find_callers(uid="[symbol uid]")`: Identify internal dependencies.
- `impact(uid="[symbol uid]")`: Assess transitive dependencies.

### 3. Persistent Memory Update
Checkpoint the architectural intent in **memstate-ai**.
- `remember(key="current_task", value="[High-level intent + impact findings]")`

### 4. Planning Loop
Use **sequential-thinking** to synthesize the findings into a task DAG.
- Map each task to `SPEC.md` phases.
- Identify tasks achievable within the 50-minute horizon.

## Verdict
Produce a "GO/NO-GO" verdict based on:
- Blast radius (High-risk if > 5 callers)
- Pattern consistency (Does this follow existing repository patterns?)
- Context window capacity (Clear history if impact spans > 10 files)
