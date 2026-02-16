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
│   │   │   ├── capture.py          # Transcript/prompt extraction
│   │   │   ├── learnings.py        # Learning extraction (corrections, insights)
│   │   │   ├── prd.py              # PRD CRUD operations
│   │   │   ├── prd_capture.py      # PRD auto-capture from prompts
│   │   │   ├── pr_integration.py   # PR-PRD linking
│   │   │   └── summary.py          # Hierarchical summary generation (weekly/monthly/yearly)
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
│   ├── prompts/                    # Captured prompts with line references
│   ├── summaries/                  # Hierarchical summaries
│   │   ├── weekly/                 # Weekly summaries (YYYY-WXX.md)
│   │   ├── monthly/                # Monthly summaries (YYYY-MM.md)
│   │   └── yearly/                 # Yearly summaries (YYYY.md)
│   ├── prompt-index.json           # Deduplication index
│   └── summary-state.json          # Summary generation state
└── .claude/                        # Claude Code settings
```

## Ninho Commands

When working in this repo, these Ninho commands are available:

| Command | Description |
|---------|-------------|
| `/ninho:status` | View PRDs, learnings, and stale items |
| `/ninho:prd-list` | List all PRDs with detailed summaries |
| `/ninho:search <query>` | Search across PRDs and prompts |
| `/ninho:digest` | Generate weekly summary (legacy) |
| `/ninho:weekly` | Generate/view weekly summary with breadcrumbs |
| `/ninho:monthly` | Generate/view monthly summary (aggregates weekly) |
| `/ninho:yearly` | Generate/view yearly summary (aggregates monthly) |
| `/ninho:link-pr` | Manually link branch to PRD requirements |
| `/ninho:pr-context` | Manually generate PR context |

## How PRD Auto-Capture Works

Ninho automatically detects requirements, decisions, constraints, and questions from your prompts and saves them to PRDs.

### Signal Detection Patterns

**Requirements / Tasks** - triggers PRD requirement entries:
- "I need to build/create/add/fix/implement..."
- "fix this", "fix the"
- "we need", "we should", "we must"
- "add a", "create a", "build a", "implement"
- "can you", "please add/create/fix"
- "I want to", "I'd like to", "let's add/create/build"

**Bug Fixes / Issues** - triggers requirement entries:
- "fix this", "there's a bug", "bug in"
- "doesn't work", "not working", "broken"
- "error when", "failing", "crashes"

**Decisions** - triggers decision entries with rationale:
- "let's use", "we'll go with", "decided on"
- "I'll use", "we should use", "going with"
- "prefer", "better to", "makes sense to"

**Constraints** - triggers constraint entries:
- "must be", "cannot", "can't", "shouldn't"
- "limited to", "maximum", "minimum"
- "only if", "unless"

**Questions** - triggers open question entries:
- Any prompt ending with "?"
- "how do", "how can", "what if", "should we", "can we"

### Capture Triggers

PRD content is captured at two lifecycle events:
1. **PreCompact** - Before context compression (critical, prevents data loss)
2. **SessionEnd** - Final sweep when session ends

### Data Flow

```
User Prompt → PRDCapture.extract_prd_items() → PRD Module
                    │
                    ├─► Requirements → prd.add_requirement()
                    ├─► Decisions → prd.add_decision()
                    ├─► Constraints → prd.add_constraint()
                    └─► Questions → prd.add_question()
                    │
                    └─► Prompt saved to .ninho/prompts/YYYY-MM-DD.md
```

## Verifying Ninho is Active

### Quick Health Check

At session start, you should see `<ninho-context>` with PRD summaries. If not visible:

1. **Check plugin registration**:
   ```bash
   cat ~/.claude/settings.json
   ```
   Should contain `"enabledPlugins": [".../ninho/adapters/claude-code"]`

2. **Verify directories exist**:
   ```bash
   ls -la ~/.ninho/
   ls -la .ninho/
   ```

3. **Check for captured data**:
   ```bash
   ls -la .ninho/prds/
   ls -la .ninho/prompts/
   ls -la .ninho/summaries/
   ```

### Ensuring Latest Version

Before major sessions, ensure Ninho is current:
```bash
cd /path/to/ninho && git pull origin main
```

### When Prompts Are Captured

Prompts are captured at two lifecycle events:
1. **PreCompact** - Before context compression (prevents data loss)
2. **SessionEnd** - Final sweep when session ends

If prompts aren't appearing immediately, they will be captured when you:
- End the current session
- Hit memory pressure (triggers PreCompact)

### Auto-Summary Generation

Summaries are auto-generated at period boundaries when you start a new session:
- **Weekly**: Generated on Mondays for the previous week
- **Monthly**: Generated on the 1st for the previous month
- **Yearly**: Generated on January 1st for the previous year

### Triggering Auto-Capture

Ninho detects and captures prompts containing these patterns:

**Requirements** (saved to PRDs):
- "I need to build...", "add a...", "implement...", "create a..."
- "fix this...", "we need...", "please add..."

**Decisions** (saved with rationale):
- "let's use...", "we'll go with...", "decided on..."
- "prefer...", "better to...", "going with..."

**Constraints**:
- "must be...", "cannot...", "limited to..."
- "maximum...", "minimum...", "only if..."

**Questions** (tracked as open items):
- Any prompt ending with "?"
- "how do...", "should we...", "can we..."

Use these phrases naturally - Ninho captures them automatically.

## Development Guidelines

### Core Library (packages/core/src/)
- LLM-agnostic Python library
- All storage operations go through `Storage` and `ProjectStorage` classes
- Keep adapters separate from core logic
- Use try/except for imports to support both package and direct imports

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
- [prd_capture.py](ninho/packages/core/src/prd_capture.py) - Signal detection patterns for PRD auto-capture
- [summary.py](ninho/packages/core/src/summary.py) - Hierarchical summary generation
- [on-pre-compact.py](ninho/adapters/claude-code/scripts/on-pre-compact.py) - Captures ALL prompts and PRD content
- [on-session-end.py](ninho/adapters/claude-code/scripts/on-session-end.py) - Final prompt capture sweep
- [on-session-start.py](ninho/adapters/claude-code/scripts/on-session-start.py) - Injects context and triggers auto-summaries

## Storage Locations

- **Global**: `~/.ninho/` - User-level data (daily learnings, config, logs)
- **Project**: `.ninho/` - Project-specific data (PRDs, prompts, summaries, PR mappings)
  - `.ninho/prompts/` - Daily prompt logs (YYYY-MM-DD.md)
  - `.ninho/prds/` - Auto-generated PRDs
  - `.ninho/summaries/weekly/` - Weekly summaries (YYYY-WXX.md)
  - `.ninho/summaries/monthly/` - Monthly summaries (YYYY-MM.md)
  - `.ninho/summaries/yearly/` - Yearly summaries (YYYY.md)

## Quick Reference

### Quick Verification
- If you see `<ninho-context>` at session start, Ninho is injecting existing context
- After a session ends, check `.ninho/prds/` for auto-generated PRDs
- Check `.ninho/prompts/` for captured prompt history
- Check `.ninho/summaries/` for generated summaries

### Debug
```bash
# Check logs
cat ~/.ninho/ninho.log | tail -20

# Verify directories exist
ls -la ~/.ninho/
ls -la .ninho/

# Check for PRDs
ls -la .ninho/prds/

# Check for captured prompts
ls -la .ninho/prompts/
```

### Plugin Registration
The plugin should be registered at:
`~/.claude/settings.json` -> `enabledPlugins` array

---

*Ninho automatically captures requirements, decisions, and questions from your prompts. Just code normally - PRDs are generated when sessions end or compact. Weekly/monthly/yearly summaries are auto-generated at period boundaries with breadcrumb links to original prompts.*
