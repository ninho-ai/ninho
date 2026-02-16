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

Prompts and PRD content are captured at multiple lifecycle events:
1. **UserPromptSubmit** - Every prompt is captured immediately when submitted
2. **PreCompact** - Backup capture before context compression (prevents data loss)
3. **SessionEnd** - Final sweep when session ends

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

## Installing and Loading the Plugin

### For Development (Local Testing)

Use the `--plugin-dir` flag to load Ninho directly from its source directory:

```bash
claude --plugin-dir /path/to/ninho/adapters/claude-code
```

This is the fastest way to test changes. You can load multiple plugins:
```bash
claude --plugin-dir ./ninho/adapters/claude-code --plugin-dir ./other-plugin
```

### For Permanent Installation

Use the Claude Code CLI to install the plugin:

```bash
# Install for the current project
claude plugin install /path/to/ninho/adapters/claude-code --scope project

# Install for all projects (user-wide)
claude plugin install /path/to/ninho/adapters/claude-code --scope user
```

Other plugin management commands:
```bash
claude plugin uninstall ninho
claude plugin enable ninho
claude plugin disable ninho
claude plugin update ninho
```

### For External Distribution (Marketplace)

When Ninho is published to a marketplace, users install it with:
```bash
claude plugin install ninho@marketplace-name
```

Or via the interactive `/plugin` command in Claude Code, under the **Discover** tab.

## Verifying Ninho is Active

### Quick Health Check

At session start, you should see `<ninho-context>` with PRD summaries. If not visible:

1. **Check plugin is loaded** (CRITICAL - most common failure point):
   ```bash
   # Verify via debug log (definitive check)
   ls -t ~/.claude/debug/*.txt | head -1 | xargs grep -i "plugin"
   ```
   Look for:
   - `Found N plugins (N enabled, N disabled)` - should show >= 1 enabled
   - `Registered N hooks from N plugins` - should show >= 1

   If it shows `Found 0 plugins`, the plugin is not loaded. Restart with `--plugin-dir`:
   ```bash
   claude --plugin-dir /path/to/ninho/adapters/claude-code
   ```

2. **Check plugin.json capabilities match hooks.json**:
   ```bash
   cat ninho/adapters/claude-code/.claude-plugin/plugin.json
   ```
   The `capabilities.hooks` array MUST list every hook event defined in `hooks/hooks.json`.
   If a hook (e.g., `UserPromptSubmit`) is in `hooks.json` but missing from `plugin.json`,
   it will be silently ignored even if the plugin is loaded.

3. **Verify directories exist**:
   ```bash
   ls -la ~/.ninho/
   ls -la .ninho/
   ```

4. **Check for captured data**:
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

Prompts are captured immediately and at backup lifecycle events:
1. **UserPromptSubmit** - Every prompt is saved the moment you submit it
2. **PreCompact** - Backup capture before context compression
3. **SessionEnd** - Final sweep when session ends

Prompts appear in `.ninho/prompts/YYYY-MM-DD.md` immediately after submission.

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
# 1. Check if plugin is loaded in current session
ls -t ~/.claude/debug/*.txt | head -1 | xargs grep "Found.*plugin"

# 2. Check if hooks fired in current session
ls -t ~/.claude/debug/*.txt | head -1 | xargs grep "hook"

# 3. Check Ninho logs
cat ~/.ninho/ninho.log | tail -20

# 4. Verify plugin.json capabilities match hooks.json
cat ninho/adapters/claude-code/.claude-plugin/plugin.json
cat ninho/adapters/claude-code/hooks/hooks.json

# 5. Verify data directories exist
ls -la ~/.ninho/
ls -la .ninho/
ls -la .ninho/prds/
ls -la .ninho/prompts/
```

### Plugin Loading Methods

**Development (recommended for local work):**
```bash
claude --plugin-dir /path/to/ninho/adapters/claude-code
```

**Permanent installation via CLI:**
```bash
claude plugin install /path/to/ninho/adapters/claude-code --scope project
```

**Marketplace installation (for end users):**
```bash
claude plugin install ninho@marketplace-name
```

### Keeping plugin.json and hooks.json in Sync

Every hook event in `hooks/hooks.json` MUST also appear in `.claude-plugin/plugin.json` under `capabilities.hooks`. If they diverge, hooks will silently fail to fire.

**Current required hooks**: `SessionStart`, `UserPromptSubmit`, `SessionEnd`, `PreCompact`, `Stop`

After adding a new hook to `hooks.json`, always update `plugin.json` capabilities to match.

### Troubleshooting Plugin Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Prompts not saved | Plugin not loaded | Start with `--plugin-dir` or run `claude plugin install` |
| `Found 0 plugins` in debug log | Plugin not loaded | Use `claude --plugin-dir /path/to/adapter` |
| Plugin loaded but hooks don't fire | Hook missing from `plugin.json` capabilities | Add missing hook to `capabilities.hooks` in `plugin.json` |
| Commands not showing | Plugin not loaded or wrong scope | Reinstall with correct `--scope` flag |

**Note:** `~/.claude/plugins/installed_plugins.json` is an internal tracking file managed by the CLI.
Do NOT edit it manually — use `claude plugin install/uninstall` commands instead.
Similarly, `~/.claude/settings.json` `enabledPlugins` is a legacy field and should not be relied on.

## Session End Procedure

**Standard procedure when finishing a coding session:**

1. **Commit changes** - Stage and commit all work with a descriptive message
2. **Push to remote** - Push commits to origin
3. **Monitor CI** - Watch the CI pipeline until it passes:
   ```bash
   gh run watch <run-id> --exit-status
   ```
4. **Fix any failures** - If CI fails, fix the issue and repeat steps 1-3

This ensures all work is safely persisted and verified before ending the session.

---

*Ninho automatically captures requirements, decisions, and questions from your prompts. Just code normally - PRDs are generated when sessions end or compact. Weekly/monthly/yearly summaries are auto-generated at period boundaries with breadcrumb links to original prompts.*
