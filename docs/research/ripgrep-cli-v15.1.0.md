# ripgrep CLI Research (v15.1.0)

Status: Current
Date: 2026-04-17
Version: ripgrep 15.1.0
Purpose: Set project-default search tooling for agent and workflow operations

## Environment Verification
- Binary path: `/opt/homebrew/bin/rg`
- Runtime check: `rg --version` -> `ripgrep 15.1.0`
- Install source: Homebrew core formula (`brew install ripgrep`)

## Official and Trusted References
- Official README: https://github.com/BurntSushi/ripgrep/blob/master/README.md
- Official Guide: https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md
- Official FAQ: https://github.com/BurntSushi/ripgrep/blob/master/FAQ.md
- Homebrew formula page: https://formulae.brew.sh/formula/ripgrep
- Homebrew core formula source: https://raw.githubusercontent.com/Homebrew/homebrew-core/HEAD/Formula/r/ripgrep.rb

## Why ripgrep Is Default
- Fast recursive search with sane defaults for code repositories.
- Honors ignore files by default (`.gitignore`, `.ignore`, `.rgignore`).
- Cleaner results than broad `grep -R`/`find` patterns in large trees.
- Single default command pattern reduces agent behavior drift.

## Project Policy
- File discovery default: `rg --files`
- Content search default: `rg -n`
- Keep ignores enabled by default.
- Use fallback only when rg is unavailable.

## Fallback Contract
If `rg` is unavailable:
1. Use `find . -type f` for file discovery.
2. Use `grep -RIn --exclude-dir=.git` for content search.
3. Emit one log line: `rg unavailable, using grep/find fallback`.

## Security and Supply Chain Notes
- Installed via official Homebrew core tap.
- Current version (`15.1.0`) is beyond historical vulnerable ranges such as pre-13.0.0 CVE-2021-3013 scope.
- Policy: avoid ad-hoc mirrors and unverified binaries.

## Files Updated for Enforcement
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/spec-driven.instructions.md`
- `.github/agents/*.agent.md`
- `.claude/agents/*.agent.md`
- `.agents/workflows/*.md`
