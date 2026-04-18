# Security Auditor Workflow

Use this workflow for dependency changes and high-risk features.

0. Read `SPEC.md` and confirm security/dependency scope matches active phase.
0.1 If change is outside spec, return BLOCK pending spec and ADR updates.
1. Validate new package names in public registries.
2. Check dependency vulnerabilities and transitive risk.
3. Review changes for injection, path traversal, and secret exposure.
4. Confirm security scans executed where configured.
5. Return SHIP, ITERATE, or BLOCK with remediation steps.
6. Use `rg --files` and `rg -n` for security-impact search; fallback to `find`/`grep` only if `rg` is unavailable.
