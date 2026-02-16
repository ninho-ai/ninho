---
name: ninho:prd-list
description: List all PRDs with detailed summaries
---

# List PRDs

Display all PRDs in the current project with detailed information about each.

## Instructions

1. **Scan `.ninho/prds/`** for all markdown files

2. **For each PRD**, extract:
   - Title (from `# Title` line)
   - Overview (from Overview section)
   - Requirements status (open vs completed)
   - Number of decisions made
   - Open questions (with staleness)
   - Related files count
   - Last modification date

3. **Sort by** last modification (most recent first)

4. **Display** in a readable format

## Output Format

```
Ninho PRDs

Found 3 PRDs in this project:

## 1. Auth System
   File: .ninho/prds/auth-system.md

   Overview: User authentication and authorization system

   Requirements: 2 open / 3 completed (60% done)
   Decisions: 5 made
   Questions: 1 open (stale: 1)
   Files: 4 tracked

   Last updated: 2 days ago

---

## 2. API Integration
   File: .ninho/prds/api-integration.md

   Overview: REST API for frontend communication

   Requirements: 5 open / 0 completed (0% done)
   Decisions: 2 made
   Questions: 2 open
   Files: 2 tracked

   Last updated: today

---

## 3. User Dashboard
   File: .ninho/prds/user-dashboard.md

   Overview: Main dashboard with activity widgets

   Requirements: 0 open / 4 completed (100% done)
   Decisions: 3 made
   Questions: 0 open
   Files: 6 tracked

   Last updated: 1 week ago

---
Total: 7 open requirements | 7 completed | 10 decisions
```

## If No PRDs

```
Ninho PRDs

No PRDs found in this project.

PRDs are created automatically when you:
- Discuss features or requirements
- Make architectural decisions
- Set constraints or limitations

Just keep coding with Claude Code!

To manually create a PRD:
1. Create `.ninho/prds/feature-name.md`
2. Use the PRD template from the Ninho docs
```

## Quick Actions

After listing PRDs, offer quick actions:

```
Quick actions:
1. View a PRD: Just ask "show me the auth-system PRD"
2. Add requirement: "add requirement to auth-system: OAuth support"
3. Mark complete: "mark 'Login flow' as complete in auth-system"
```
