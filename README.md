# Ninho

> **ninho** (Portuguese): "nest" - where knowledge grows and is nurtured

Automatically capture decisions, requirements, and learnings from AI coding sessions. Never lose context again.

## The Problem

Every AI coding session generates valuable context:
- Why you chose JWT over sessions
- What constraints shaped the architecture
- Which approaches you tried and rejected

**But when the session ends, that context disappears.**

## The Solution

Ninho runs in the background, automatically building:
- **PRDs** - Living documents that track requirements and decisions
- **Daily Learnings** - Corrections and insights captured automatically
- **PR Context** - Rich context for code reviewers

## Quick Install

```bash
# One-liner install
git clone https://github.com/ninho-ai/ninho ~/.ninho-plugin && ~/.ninho-plugin/install.sh
```

Or via Claude Code plugin system:

```bash
claude plugin add github:ninho-ai/ninho
```

## How It Works

Ninho works **completely automatically** in the background:

| When | What Happens |
|------|--------------|
| **Session starts** | PRD summaries and stale questions are surfaced |
| **You discuss features** | Requirements, decisions, constraints are captured to PRDs |
| **You edit files** | Related PRD context is shown |
| **You run `gh pr create`** | Branch auto-linked to PRD, context generated |
| **PR merges** | Requirements auto-marked as complete |
| **Session ends** | Learnings extracted and saved |

### Zero Configuration Required

Just code with Claude Code. Ninho handles the rest.

## Directory Structure

```
~/.ninho/                        # Global (user-level)
├── daily/
│   ├── 2026-02-16.md           # Today's learnings
│   └── 2026-02-15.md           # Yesterday's learnings
└── ninho.log                    # Debug log

your-project/.ninho/             # Project-level (git-trackable)
├── prds/
│   ├── auth-system.md          # Auto-generated PRD
│   └── api-integration.md      # Another PRD
├── prompts/
│   └── 2026-02-16.md           # Captured prompts with references
└── pr-mappings.json            # Branch-to-PRD links
```

## Automatic Features

### PRD Auto-Generation

When you discuss features, Ninho creates and maintains PRDs:

```markdown
# Auth System

## Requirements
- [x] Login with email/password
- [ ] OAuth integration (Google, GitHub)
- [ ] Password reset flow

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-15 | Use JWT | Stateless, scales horizontally |

## Open Questions
- Should we support magic link login? *(asked 2026-02-10)*
```

### Context Injection

At session start, you'll see:

```
<ninho-context>
## Active PRDs for this project

### Stale Questions (need attention)
- **auth-system**: Magic link login? (14 days old)

### Auth System
- Status: 3 open, 2 done
- Latest decision: Use JWT (2026-02-15)
</ninho-context>
```

### PR Integration

When you create a PR, Ninho automatically:
1. Detects the related PRD from your branch/files
2. Links the branch to open requirements
3. Adds the PR to the PRD's tracking table
4. Marks requirements complete when PR merges

## Commands (Optional)

These commands are **optional** - Ninho works automatically. Use them for manual overrides:

| Command | Description |
|---------|-------------|
| `/ninho:status` | View PRDs, learnings, and stale items |
| `/ninho:prd-list` | List all PRDs with detailed summaries |
| `/ninho:search <query>` | Search across PRDs and prompts |
| `/ninho:digest` | Generate weekly summary |
| `/ninho:link-pr` | (Manual) Link branch to PRD requirements |
| `/ninho:pr-context` | (Manual) Generate PR context |

## PRD Format

PRDs follow a consistent structure:

```markdown
# Feature Name

## Overview
Brief description of the feature.

## Requirements
- [ ] Incomplete requirement
- [x] Completed requirement

## Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | What was decided | Why |

## Constraints
- Technical or business constraints

## Open Questions
- Unanswered questions *(asked YYYY-MM-DD)*

## Related Files
- `src/feature/file.ts`

## Pull Requests
| PR | Branch | Status | Requirements Addressed |
|----|--------|--------|------------------------|

## Session Log
### YYYY-MM-DD
- What happened ([prompt](prompts/YYYY-MM-DD.md#LXX))
```

## Learnings Format

Daily learnings are captured in `~/.ninho/daily/YYYY-MM-DD.md`:

```markdown
# Daily Learnings - 2026-02-16

## [Correction] 14:32:15

> No, don't use `git add .` in commits. Always add specific files.

**Signal:** `don't do`

---

## [Decision] 15:45:22

> We decided to use the repository pattern for database access.

**Signal:** `we decided`
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 CORE LIBRARY (Python)                   │
│  packages/core/src/                                     │
│  ├── storage.py     # File storage abstraction         │
│  ├── capture.py     # Prompt extraction                │
│  ├── learnings.py   # Learning extraction              │
│  ├── prd.py         # PRD operations                   │
│  └── pr_integration.py  # PR-PRD linking               │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              CLAUDE CODE ADAPTER                        │
│  adapters/claude-code/                                  │
│  ├── hooks/hooks.json    # Hook definitions            │
│  ├── scripts/            # Hook implementations        │
│  ├── commands/           # Slash commands              │
│  └── agents/             # Background agents           │
└─────────────────────────────────────────────────────────┘
```

## Configuration

Ninho works out of the box with zero configuration. Optional settings in `~/.ninho/config.json`:

```json
{
  "stale_question_days": 7,
  "learning_signals": ["note:", "remember:", "TIL:"],
  "auto_prd": true
}
```

## Troubleshooting

### Check if Ninho is loaded

```bash
claude --debug
# Look for "ninho" in loaded plugins
```

### View logs

```bash
cat ~/.ninho/ninho.log | tail -20
```

### Verify hook execution

```bash
ls -la ~/.ninho/daily/
ls -la .ninho/prds/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test`
5. Submit a PR

## License

MIT

---

Built with love for developers who want to remember why they made decisions.

Visit [ninho.ai](https://ninho.ai) for documentation and articles.
