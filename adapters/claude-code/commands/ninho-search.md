---
name: ninho:search
description: Search across PRDs and prompts
---

# Search Ninho Context

Search across all PRDs, prompts, and learnings to find relevant context.

## Instructions

1. **Get the search query** from the user's input (everything after `/ninho:search`)

2. **Search locations** (in order of relevance):
   - `.ninho/prds/*.md` - PRD files
   - `.ninho/prompts/*.md` - Prompt history
   - `~/.ninho/daily/*.md` - Daily learnings

3. **Search strategy**:
   - Case-insensitive text matching
   - Search in: decisions, requirements, questions, constraints
   - Return file path, line number, and context

4. **Format results** showing:
   - Source (PRD name, prompt date, or learning date)
   - Section (Decisions, Requirements, etc.)
   - Matching text with context
   - Link to source file

## Usage

```
/ninho:search <query>
```

## Examples

### Search for a decision

```
> /ninho:search JWT

Found 3 results:

## auth-system.md (PRD)
**Decision** (2026-02-15):
> Use JWT tokens - Stateless, scales horizontally

## prompts/2026-02-15.md
**Prompt** (L12):
> "Can you implement the login endpoint using JWT? I want stateless auth..."

## daily/2026-02-15.md
**Learning**:
> Decided to use JWT for stateless authentication
```

### Search for a requirement

```
> /ninho:search password

Found 2 results:

## auth-system.md (PRD)
**Requirement** (incomplete):
> - [ ] Password reset flow

**Constraint**:
> Password minimum: 12 characters
```

### No results

```
> /ninho:search graphql

No results found for "graphql" in PRDs, prompts, or learnings.

Try:
- Different keywords
- Check available PRDs: /ninho:status
```

## Search Tips

- Use specific technical terms (e.g., "JWT", "bcrypt", "Redis")
- Search for decision keywords (e.g., "decided", "chose", "use")
- Search for constraint keywords (e.g., "must", "cannot", "limit")
- Search by date (e.g., "2026-02-15")

## Implementation Notes

For Claude Code implementation, use grep-based search:

```bash
# Search PRDs
grep -rni "$query" .ninho/prds/

# Search prompts
grep -rni "$query" .ninho/prompts/

# Search learnings
grep -rni "$query" ~/.ninho/daily/
```

Format results with file context and links.
