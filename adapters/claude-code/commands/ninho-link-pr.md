---
name: ninho:link-pr
description: (Optional) Manually link branch to PRD requirements
---

# Link PR to PRD Requirements (Manual Override)

**Note:** Ninho automatically links branches to PRDs when you run `gh pr create` or `git push -u`. This command is only needed if:
- Auto-detection linked to the wrong PRD
- You want to select specific requirements (auto-link selects all incomplete)
- Auto-detection failed to find a matching PRD

Links the current git branch to requirements in a PRD, enabling automatic tracking when the PR is merged.

## Instructions

1. **Get current branch name**
   ```bash
   git branch --show-current
   ```

2. **Detect related PRD** based on:
   - Branch name patterns (e.g., `feat/auth-*` → `auth-system`)
   - Recently modified files
   - Ask user if ambiguous

3. **Read the PRD** and extract requirements (lines starting with `- [ ]`)

4. **Present checklist to user** asking which requirements this PR addresses

5. **Store the mapping** in `.ninho/pr-mappings.json`:
   ```json
   {
     "branch-name": {
       "prd": "auth-system",
       "requirements": ["Login with email/password", "Password reset flow"],
       "created": "2026-02-16T14:30:00Z"
     }
   }
   ```

6. **Update the PRD** to add the PR to the Pull Requests table (if PR exists):
   - Check if PR exists: `gh pr view --json number,url`
   - Add row to Pull Requests table

## Example Interaction

```
> /ninho:link-pr

Current branch: feat/jwt-auth

Detected PRD: auth-system.md

Which requirements does this PR address?

  [x] Login with email/password
  [ ] User registration with email verification
  [ ] OAuth integration (Google, GitHub)
  [ ] Password reset flow

Select requirements (space to toggle, enter to confirm):
```

After selection:

```
✅ Linked feat/jwt-auth to auth-system PRD

Requirements tracked:
  - Login with email/password

When this PR merges, these requirements will be marked complete.

To generate PR context: /ninho:pr-context
```

## If No PRD Found

```
No PRD found for this branch.

Options:
1. Create new PRD for this feature
2. Link to existing PRD: [list PRDs]
3. Skip linking

Select option:
```

## Branch-to-PRD Detection

Map branch prefixes to PRDs:
- `feat/auth-*`, `fix/auth-*` → auth-system
- `feat/api-*`, `fix/api-*` → api-integration
- `feat/dashboard-*` → user-dashboard

Or infer from modified files in the branch:
```bash
git diff main --name-only | head -20
```
