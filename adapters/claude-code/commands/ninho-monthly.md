---
name: ninho:monthly
description: Generate or view monthly summary aggregated from weekly summaries
---

# Monthly Summary

Generate a monthly summary by aggregating weekly summaries.

## Instructions

1. **Determine the month**:
   - Default: Current month
   - Optional: Specify `--month YYYY-MM` for a specific month (e.g., `--month 2026-02`)

2. **Check for existing summary**:
   - Look in `.ninho/summaries/monthly/YYYY-MM.md`
   - If it exists, display it
   - If not, generate it

3. **Generate summary from weekly summaries**:
   - Find all weeks that overlap with the month
   - Read from `.ninho/summaries/weekly/YYYY-WXX.md`
   - Aggregate statistics and key items
   - Note any missing weeks

4. **Save summary**:
   - Write to `.ninho/summaries/monthly/YYYY-MM.md`
   - Update `.ninho/summary-state.json`

## Output Format

```markdown
# February 2026 Summary

## Overview
- **Weeks included**: W05, W06, W07, W08
- **Weeks missing**: None
- **Total prompts**: 189
- **Total decisions**: 18
- **Total requirements completed**: 32
- **Total learnings**: 45

## Weekly Breakdown

| Week | Prompts | Decisions | Requirements | Learnings |
|------|---------|-----------|--------------|-----------|
| [W05](weekly/2026-W05.md) | 42 | 4 | 7 | 10 |
| [W06](weekly/2026-W06.md) | 51 | 5 | 9 | 12 |
| [W07](weekly/2026-W07.md) | 47 | 5 | 8 | 11 |
| [W08](weekly/2026-W08.md) | 49 | 4 | 8 | 12 |

---
_Generated: 2026-03-01 00:15:00_
_Weeks covered: 4/4 (complete)_
```

## Options

- `/ninho:monthly` - Current month
- `/ninho:monthly --month 2026-02` - Specific month
- `/ninho:monthly --regenerate` - Force regenerate even if exists

## Implementation

Use the `SummaryManager` class from the core library:

```python
from summary import SummaryManager
from storage import Storage, ProjectStorage

project_storage = ProjectStorage(cwd)
storage = Storage()
summary_manager = SummaryManager(project_storage, storage)

# Generate for current month
month_str = summary_manager.get_current_month()
content = summary_manager.generate_monthly_summary(month_str)
print(content)
```

## Use Cases

1. **Month-end review**: High-level view of accomplishments
2. **Reporting**: Share progress with stakeholders
3. **Trend analysis**: Compare months over time
4. **Planning**: Inform next month's priorities
