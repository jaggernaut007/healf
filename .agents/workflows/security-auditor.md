# Security Auditor Workflow

Use this workflow for dependency changes and high-risk features.

1. Validate new package names in public registries.
2. Check dependency vulnerabilities and transitive risk.
3. Review changes for injection, path traversal, and secret exposure.
4. Confirm security scans executed where configured.
5. Return SHIP, ITERATE, or BLOCK with remediation steps.
