# Installing Ninho

## Prerequisites
- Claude Code CLI installed
- Python 3.8+
- Git

## Quick Install

1. Clone the repository:
   ```bash
   git clone https://github.com/ninho-ai/ninho.git
   cd ninho
   ```

2. Register the plugin with Claude Code:
   ```bash
   # Add to ~/.claude/settings.json
   {
     "enabledPlugins": {
       "/absolute/path/to/ninho/adapters/claude-code": true
     }
   }
   ```

3. Start a new Claude Code session - Ninho is now active.

## Verify Installation

After starting a session, check:
```bash
ls -la .ninho/          # Project storage created
ls -la ~/.ninho/        # Global storage created
```

## Updating

```bash
cd /path/to/ninho && git pull origin main
```
