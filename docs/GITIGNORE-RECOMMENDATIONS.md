# Recommended .gitignore entries for AI Package Framework

# Personal Claude configuration (machine-specific)
CLAUDE.local.md

# Auto-memory (optional — depends on team preference)
# .claude/memory/

# Session artifacts (temporary planning files)
.copilot/session-state/

# MCP server cache (if applicable)
.mcp-cache/

# Common development artifacts
*.pyc
__pycache__/
node_modules/
.env
.env.local
*.log

# IDE-specific
.vscode/
.idea/
*.swp
*.swo

# OS-specific
.DS_Store
Thumbs.db

# Build artifacts (customize for your project)
dist/
build/
*.egg-info/
.pytest_cache/
coverage/
.coverage
