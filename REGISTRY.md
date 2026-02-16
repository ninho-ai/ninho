# Claude Code Plugin Registry Submission

This document describes how to submit Ninho to the Claude Code community plugin registry.

## Plugin Information

| Field | Value |
|-------|-------|
| Name | ninho |
| Version | 1.0.0 |
| Repository | github:ninho-ai/ninho |
| Plugin Path | adapters/claude-code |
| License | MIT |

## Capabilities

### Hooks
- **SessionStart** - Injects PRD context at session start
- **SessionEnd** - Extracts learnings when session ends
- **PreCompact** - Captures context before compaction
- **Stop** - Monitors for PRD updates and PR commands

### Commands
- `/ninho:status` - View PRDs, learnings, stale items
- `/ninho:prd-list` - List all PRDs with details
- `/ninho:search` - Search across PRDs and prompts
- `/ninho:digest` - Generate weekly summary
- `/ninho:link-pr` - (Optional) Manual PR linking
- `/ninho:pr-context` - (Optional) Manual PR context

### Agents
- **prd-maintainer** - Background agent for PRD maintenance

## Submission Steps

### 1. Validate Plugin Structure

```bash
# Ensure required files exist
ls -la adapters/claude-code/.claude-plugin/plugin.json
ls -la adapters/claude-code/hooks/hooks.json

# Validate JSON
python3 -c "import json; json.load(open('adapters/claude-code/.claude-plugin/plugin.json'))"
python3 -c "import json; json.load(open('adapters/claude-code/hooks/hooks.json'))"
```

### 2. Test Plugin Locally

```bash
# Install plugin locally
claude plugin add ./adapters/claude-code

# Verify it loads
claude --debug
# Should show "ninho" in loaded plugins

# Test commands
# /ninho:status
```

### 3. Submit to Registry

**Option A: Community Registry (claude-plugins.dev)**

1. Fork the registry repository
2. Add entry to `plugins.json`:
   ```json
   {
     "name": "ninho",
     "description": "Automatic PRD and context capture for AI coding sessions",
     "repository": "github:ninho-ai/ninho",
     "path": "adapters/claude-code",
     "categories": ["productivity", "documentation", "memory"],
     "version": "1.0.0"
   }
   ```
3. Submit PR

**Option B: Direct GitHub Installation**

Users can install directly:
```bash
claude plugin add github:ninho-ai/ninho --path adapters/claude-code
```

### 4. Announce Release

- [ ] Post to Claude Code community Discord
- [ ] Tweet announcement with #ClaudeCode tag
- [ ] Add to Awesome Claude Code list

## Quality Checklist

- [x] Plugin manifest (plugin.json) is valid
- [x] Hooks configuration (hooks.json) is valid
- [x] All scripts are executable
- [x] README has installation instructions
- [x] MIT license included
- [x] No hardcoded paths (uses ${CLAUDE_PLUGIN_ROOT})
- [x] Error handling in all scripts
- [x] Async hooks don't block user workflow
- [x] Sync hooks (PreCompact) are fast

## Support

- Issues: https://github.com/ninho-ai/ninho/issues
- Documentation: https://ninho.ai/docs
- Email: hello@ninho.ai
