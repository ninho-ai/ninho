---
name: ninho:status
description: View current PRDs and recent learnings
---

# Ninho Status

Show the current state of Ninho memory for this project.

## Instructions

1. Check if `.ninho/` directory exists in the current project
2. List all PRDs in `.ninho/prds/`
3. Show summary for each PRD:
   - Open requirements count
   - Completed requirements count
   - Open questions count
   - Latest decision
4. Show recent learnings from `~/.ninho/daily/` (last 3 days)
5. Format output in a readable table

## Output Format

```
Ninho Status

## Project PRDs

| PRD | Open | Done | Questions | Latest Decision |
|-----|------|------|-----------|-----------------|
| auth-system | 3 | 2 | 1 | Use JWT (2026-02-16) |
| api-integration | 5 | 0 | 2 | REST over GraphQL (2026-02-15) |

## Recent Learnings (Last 3 Days)

### 2026-02-16
- [Correction] Don't use `git add .` in commits
- [Decision] Use repository pattern for database access

### 2026-02-15
- [Learning] Always validate input at API boundaries

---
Storage: ~/.ninho/
Project: .ninho/
```

## If No Data

If no `.ninho/` directory or no data:

```
Ninho Status

No Ninho data found for this project.

Ninho will automatically start capturing:
- PRDs when you discuss requirements and decisions
- Learnings when you make corrections or note things

Just keep coding with Claude Code!
```
