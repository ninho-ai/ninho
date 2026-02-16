---
name: ninho:weekly
description: Generate or view weekly summary with breadcrumb references
---

# Weekly Summary

Generate a summary for a specific week with links to original prompts.

## Instructions

1. **Determine the week**:
   - Default: Current week
   - Optional: Specify `--week YYYY-WXX` for a specific week (e.g., `--week 2026-W07`)

2. **Check for existing summary**:
   - Look in `.ninho/summaries/weekly/YYYY-WXX.md`
   - If it exists, display it
   - If not, generate it

3. **Generate summary from raw data**:
   - Read prompts from `.ninho/prompts/YYYY-MM-DD.md` for each day in the week
   - Read decisions from `.ninho/prds/*.md` (filter by date)
   - Read learnings from `~/.ninho/daily/YYYY-MM-DD.md`
   - Aggregate and format with breadcrumb links

4. **Save summary**:
   - Write to `.ninho/summaries/weekly/YYYY-WXX.md`
   - Update `.ninho/summary-state.json`

## Output Format

```markdown
# Week 7 Summary (Feb 10-16, 2026)

## Overview
- **Prompts analyzed**: 47
- **Requirements completed**: 8
- **Decisions made**: 5
- **Learnings captured**: 12

## Decisions Made

### Auth System
- **Use JWT tokens** - Stateless, scales horizontally
  - [Source](../prompts/2026-02-12.md#L42)

## Requirements Completed

### Auth System
- [x] Login with email/password ([prompt](../prompts/2026-02-11.md#L23))

## Learnings

### Corrections
- Don't use `git add .` - add specific files
  - [Source](../../daily/2026-02-12.md#L8)

## Prompt References
- **2026-02-10**: 12 prompts ([view](../prompts/2026-02-10.md))
- **2026-02-11**: 8 prompts ([view](../prompts/2026-02-11.md))

---
_Generated: 2026-02-17 08:30:00_
_Days covered: 7/7 (complete)_
```

## Options

- `/ninho:weekly` - Current week
- `/ninho:weekly --week 2026-W07` - Specific week
- `/ninho:weekly --regenerate` - Force regenerate even if exists

## Implementation

Use the `SummaryManager` class from the core library:

```python
from summary import SummaryManager
from storage import Storage, ProjectStorage

project_storage = ProjectStorage(cwd)
storage = Storage()
summary_manager = SummaryManager(project_storage, storage)

# Generate for current week
week_str = summary_manager.get_current_week()
content = summary_manager.generate_weekly_summary(week_str)
print(content)
```

## Use Cases

1. **End of week review**: See what was accomplished
2. **Sprint retrospective**: Review decisions and learnings
3. **Handoff**: Share context with team members
4. **Audit trail**: Track what was discussed and decided
