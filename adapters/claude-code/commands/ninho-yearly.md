---
name: ninho:yearly
description: Generate or view yearly summary aggregated from monthly summaries
---

# Yearly Summary

Generate a yearly summary by aggregating monthly summaries.

## Instructions

1. **Determine the year**:
   - Default: Current year
   - Optional: Specify `--year YYYY` for a specific year (e.g., `--year 2026`)

2. **Check for existing summary**:
   - Look in `.ninho/summaries/yearly/YYYY.md`
   - If it exists, display it
   - If not, generate it

3. **Generate summary from monthly summaries**:
   - Read from `.ninho/summaries/monthly/YYYY-MM.md` for each month
   - Aggregate statistics
   - Note any missing months

4. **Save summary**:
   - Write to `.ninho/summaries/yearly/YYYY.md`
   - Update `.ninho/summary-state.json`

## Output Format

```markdown
# 2026 Annual Summary

## Overview
- **Months included**: 12
- **Months missing**: 0
- **Total prompts**: 2,340
- **Total decisions**: 215
- **Total requirements completed**: 380
- **Total learnings**: 520

## Monthly Breakdown

| Month | Prompts | Decisions | Requirements | Learnings |
|-------|---------|-----------|--------------|-----------|
| [2026-01](monthly/2026-01.md) | 180 | 16 | 28 | 40 |
| [2026-02](monthly/2026-02.md) | 189 | 18 | 32 | 45 |
| [2026-03](monthly/2026-03.md) | 210 | 20 | 35 | 48 |
| ... | ... | ... | ... | ... |
| [2026-12](monthly/2026-12.md) | 195 | 17 | 30 | 42 |

---
_Generated: 2027-01-01 00:30:00_
_Months covered: 12/12 (complete)_
```

## Options

- `/ninho:yearly` - Current year
- `/ninho:yearly --year 2026` - Specific year
- `/ninho:yearly --regenerate` - Force regenerate even if exists

## Implementation

Use the `SummaryManager` class from the core library:

```python
from summary import SummaryManager
from storage import Storage, ProjectStorage

project_storage = ProjectStorage(cwd)
storage = Storage()
summary_manager = SummaryManager(project_storage, storage)

# Generate for current year
year_str = summary_manager.get_current_year()
content = summary_manager.generate_yearly_summary(year_str)
print(content)
```

## Use Cases

1. **Annual review**: Comprehensive view of the year's work
2. **Documentation**: Archive project history
3. **Onboarding**: Help new team members understand project evolution
4. **Metrics**: Track productivity and decision-making patterns
