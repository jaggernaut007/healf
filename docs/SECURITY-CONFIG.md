# Security Configuration

This project follows lightweight, practical guardrails for agentic development.

## Permission Tiers

- Always allow: read/search, lint/test, formatting.
- Ask first: dependency additions, schema changes, CI changes, push/deploy.
- Never allow: secrets commits, force-push to protected branches, production credential edits.

## Supply Chain Policy

1. Verify package exists in the public registry.
2. Prefer maintained packages with active releases.
3. Pin exact versions in lockfiles.
4. Check transitive dependency risk before merge.

## Slopsquatting Prevention

- Never install unverified package names.
- Cross-check package homepage, owner, and release history.
- Record dependency decisions in docs/research.

## Dependency and Code Scanning

- Run security scanning for new or modified first-party code when supported tooling is available.
- Run dependency vulnerability checks when adding or changing dependencies.
- Treat critical/high findings as merge blockers.

## Workspace and Secrets

- Keep writes inside workspace boundaries.
- Keep local-only secrets in untracked files.
- Do not log credentials in terminal output or docs.
