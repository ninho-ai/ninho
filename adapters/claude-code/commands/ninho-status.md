---
name: ninho:status
description: View current PRDs, recent learnings, and stale items
---

# Ninho Status

Show the current state of Ninho memory for this project.

## Instructions

1. **Check directories**:
   - Project: `.ninho/` (PRDs, prompts)
   - Global: `~/.ninho/` (daily learnings)

2. **List all PRDs** from `.ninho/prds/`:
   - Read each PRD file
   - Count open/completed requirements
   - Count open questions and identify stale ones (>7 days)
   - Get latest decision

3. **Show recent learnings** from `~/.ninho/daily/` (last 3 days)

4. **Highlight stale questions** that need attention

5. **Show PR mappings** from `.ninho/pr-mappings.json`

## Output Format

```
Ninho Status

## Attention Needed

### Stale Questions (>7 days old)
- **auth-system**: Should we support magic link login? (14 days)
- **api-integration**: Rate limiting strategy? (9 days)

## Project PRDs

| PRD | Open | Done | Questions | Latest Decision |
|-----|------|------|-----------|-----------------|
| auth-system | 3 | 2 | 1 | Use JWT (2026-02-16) |
| api-integration | 5 | 0 | 2 | REST over GraphQL (2026-02-15) |

## Active Branches

| Branch | Linked PRD | Requirements |
|--------|------------|--------------|
| feat/jwt-auth | auth-system | Login with email/password |
| feat/api-v2 | api-integration | REST endpoints |

## Recent Learnings (Last 3 Days)

### 2026-02-16
- [Correction] Don't use `git add .` in commits
- [Decision] Use repository pattern for database access

### 2026-02-15
- [Learning] Always validate input at API boundaries

---
Storage: ~/.ninho/
Project: .ninho/
PRDs: 2 | Learnings: 3 | Branches tracked: 2
```

## If No Data

```
Ninho Status

No Ninho data found for this project.

Ninho works automatically in the background:
- PRDs created when you discuss requirements and decisions
- Learnings captured when you make corrections
- PRs linked when you run `gh pr create`

Just keep coding with Claude Code!
```

## Implementation

Use the core library to gather data:

```python
from ninho.core import Storage, ProjectStorage, PRD, PRIntegration

storage = Storage()
project = ProjectStorage(cwd)
prd_manager = PRD(project)
pr_integration = PRIntegration(project)

# Get PRD summaries
for prd_name in prd_manager.list_prds():
    summary = prd_manager.get_summary(prd_name)
    stale = prd_manager.get_stale_questions(prd_name)

# Get PR mappings
mappings = pr_integration._load_mappings()

# Get recent learnings
learnings = storage.get_recent_learnings(days=3)
```
