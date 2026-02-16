# ClaudeMemory - Ninho Development Repository

This repository contains **Ninho**, an automatic context management system for AI coding sessions.

## What is Ninho?

Ninho (Portuguese for "nest") captures decisions, requirements, and learnings from AI coding sessions automatically. It prevents context loss between sessions by:

- Auto-generating and maintaining PRDs from discussions
- Capturing daily learnings from corrections and decisions
- Linking PRs to PRD requirements
- Surfacing stale questions and context at session start

## Repository Structure

```
ClaudeMemory/
├── ninho/                          # Main Ninho project (git repo)
│   ├── packages/
│   │   ├── core/src/               # Core Python library
│   │   │   ├── storage.py          # File storage abstraction
│   │   │   ├── capture.py          # Prompt extraction
│   │   │   ├── learnings.py        # Learning extraction
│   │   │   ├── prd.py              # PRD operations
│   │   │   └── pr_integration.py   # PR-PRD linking
│   │   └── cli/                    # Standalone CLI tool
│   ├── adapters/
│   │   └── claude-code/            # Claude Code plugin adapter
│   │       ├── hooks/hooks.json    # Hook definitions
│   │       ├── scripts/            # Hook implementations
│   │       ├── commands/           # Slash command definitions
│   │       └── agents/             # Background agents
│   └── website/                    # ninho.ai website (Next.js)
├── .ninho/                         # Project-level Ninho data
│   ├── prds/                       # Auto-generated PRDs
│   └── prompts/                    # Captured prompts
└── .claude/                        # Claude Code settings
```

## Ninho Commands

When working in this repo, these Ninho commands are available:

| Command | Description |
|---------|-------------|
| `/ninho:status` | View PRDs, learnings, and stale items |
| `/ninho:prd-list` | List all PRDs with detailed summaries |
| `/ninho:search <query>` | Search across PRDs and prompts |
| `/ninho:digest` | Generate weekly summary |
| `/ninho:link-pr` | Manually link branch to PRD requirements |
| `/ninho:pr-context` | Manually generate PR context |

## Development Guidelines

### Core Library (packages/core/src/)
- LLM-agnostic Python library
- All storage operations go through `Storage` and `ProjectStorage` classes
- Keep adapters separate from core logic

### Claude Code Adapter (adapters/claude-code/)
- Hooks run at session lifecycle events (start, end, compact, stop)
- Commands are markdown files that define slash commands
- Scripts use the core library for actual operations

### Testing Changes
- Validate Python syntax: `python3 -m py_compile <file>`
- Test hooks by starting a new Claude Code session
- Check logs at `~/.ninho/ninho.log`

### Key Files to Know
- [hooks.json](ninho/adapters/claude-code/hooks/hooks.json) - Defines when hooks run
- [plugin.json](ninho/adapters/claude-code/.claude-plugin/plugin.json) - Plugin manifest
- [__init__.py](ninho/packages/core/src/__init__.py) - Core library exports

## Storage Locations

- **Global**: `~/.ninho/` - User-level data (daily learnings, config, logs)
- **Project**: `.ninho/` - Project-specific data (PRDs, prompts, PR mappings)

## Quick Reference

### Verify Ninho is Active
If you see `<ninho-context>` at session start, Ninho is working.

### Debug
```bash
# Check logs
cat ~/.ninho/ninho.log | tail -20

# Verify directories exist
ls -la ~/.ninho/
ls -la .ninho/
```

### Plugin Registration
The plugin should be registered at:
`~/.claude/settings.json` -> `enabledPlugins` array

---

*Ninho automatically captures context from this session. Just code normally.*
