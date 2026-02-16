# Ninho Roadmap

## Phase 1: Stabilize (Current)

The plugin loads but was broken until the manifest was fixed. Validate core functionality before distributing.

- [x] Fix `plugin.json` manifest (remove invalid fields: `capabilities`, `categories`, `requirements`; fix `repository` type)
- [x] Update CLAUDE.md with correct plugin loading instructions (`--plugin-dir`, `claude plugin install`)
- [x] Verify all hooks fire correctly: `SessionStart`, `UserPromptSubmit`, `PreCompact`, `SessionEnd`, `Stop`
- [ ] Verify prompts are captured for every user message (not just pattern-matched ones)
- [ ] Verify PRD auto-capture works (requirements, decisions, constraints, questions)
- [ ] Verify deduplication works correctly (prompt-index.json)
- [ ] Verify `claude plugin install ./ninho/adapters/claude-code --scope project` works as a permanent install (no `--plugin-dir` needed)
- [ ] Test on a fresh project (not the Ninho repo itself) to confirm it works outside the development context
- [ ] Fix or remove the symlink at `~/.claude/plugins/ninho` created during debugging

## Phase 2: Harden

Make sure the plugin is reliable for daily use before sharing with others.

- [ ] Add error handling to hook scripts (graceful failure if Python dependencies missing)
- [ ] Verify the plugin doesn't slow down Claude Code startup or prompt submission
- [ ] Test with long prompts, multi-line prompts, and edge cases (empty prompts, special characters)
- [ ] Ensure `.ninho/` directory is created automatically on first use
- [ ] Test summary generation (weekly/monthly/yearly) end-to-end
- [ ] Test all slash commands (`/ninho:status`, `/ninho:search`, etc.)
- [ ] Add a `--version` or status check so users can verify Ninho is working

## Phase 3: Prepare for Distribution

Get ready for external users.

- [ ] Decide distribution method: GitHub marketplace vs. official Anthropic marketplace
- [ ] Write a user-facing README (installation, what it does, what to expect)
- [ ] Create a minimal example showing captured PRDs and prompts
- [ ] Test `claude plugin install` from a clean machine with no prior Ninho setup
- [ ] Ensure Python 3.9+ dependency is clearly documented
- [ ] Consider packaging core library (`pip install ninho`) for cleaner dependency management

## Phase 4: Publish to Official Marketplace

Goal: `claude plugin install ninho`

- [ ] Research Anthropic marketplace submission requirements
- [ ] Structure the repo to meet marketplace format
- [ ] Submit for review
- [ ] Set up automated updates (so `claude plugin update ninho` works)

## Phase 5: Future Enhancements

Ideas for after the core is solid.

- [ ] Web dashboard for browsing PRDs and summaries
- [ ] Multi-project summary views
- [ ] Team sharing (shared PRDs across collaborators)
- [ ] Integration with GitHub Issues/PRs (auto-link requirements to PRs)
- [ ] VS Code extension for browsing `.ninho/` data
