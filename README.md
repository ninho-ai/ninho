# Ninho

> Where your codebase decisions live

Automatically capture decisions, requirements, and learnings from AI coding sessions.

## Quick Install

```bash
npx claude-plugins install @ninho/ninho
```

Or via GitHub:

```bash
claude plugin add github:ninho-ai/ninho
```

## What It Does

- **PRDs** - Auto-generated from your conversations
- **Daily Learnings** - Corrections and insights captured automatically
- **PR Context** - Rich context for code reviewers

## How It Works

Ninho runs in the background during your Claude Code sessions:

1. **During your session**: PRDs are updated as you discuss requirements
2. **When context compacts**: Learnings are captured before they're lost
3. **When you exit**: Final learnings extraction runs

## Directory Structure

After using Ninho, you'll see:

```
~/.ninho/
├── daily/
│   └── 2026-02-16.md    # Today's learnings

your-project/.ninho/
├── prds/
│   └── auth-system.md   # Auto-generated PRD
└── prompts/
    └── 2026-02-16.md    # Captured prompts
```

## Commands

| Command | Description |
|---------|-------------|
| `/ninho:status` | View current PRDs and recent learnings |
| `/ninho:link-pr` | Link current branch to PRD requirements |
| `/ninho:pr-context` | Generate context for PR description |
| `/ninho:search` | Search across PRDs and prompts |

## Documentation

Visit [ninho.ai](https://ninho.ai) for full documentation.

## License

MIT
