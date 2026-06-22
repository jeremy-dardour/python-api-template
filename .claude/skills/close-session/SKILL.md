---
name: close-session
description: End-of-session cleanup that commits pending work, extracts learnings to MEMORY.md, and clears the scratchpad. Use when the user says "close session", "wrap up", "end session", or invokes /close-session.
---

# Close Session

Run these steps in order. Present each step's result to the user before proceeding.

## 1. Assess pending changes

Run `git status` and `git diff --stat`. Show the user a summary of modified, staged, and untracked files.

## 2. Group and commit

Propose logical commit groups to the user. Typical groupings:

- **docs**: ADRs, standards, decision index updates
- **feat/fix**: production code and its tests
- **chore**: config, tooling, gitignore, CI

For each group: stage the specific files, draft a commit message following [commit format](../../../docs/standards/commit-format.md), and commit. Never use `git add -A` or `git add .`. Never skip hooks.

## 3. Extract learnings from scratchpad

Read `scratchpad.md`. For each item, classify it:

- **Already captured**: if the item is recorded in an ADR (`docs/adrs/`) or a standards doc (`docs/standards/`), skip it.
- **Feedback/preference**: interaction preferences, corrections, or confirmed approaches that should persist across sessions. Add to `MEMORY.md` under the Feedback section.
- **Project context**: ongoing work context, deadlines, stakeholder decisions not captured elsewhere. Add to `MEMORY.md` under a Project section (create if needed).
- **Ephemeral**: session-specific reasoning, progress notes, implementation details. Discard.

Present the proposed additions to the user before writing to MEMORY.md.

## 4. Update README

Review what changed during this session (commits made in steps above, scratchpad decisions). If the session introduced, removed, or changed any user-facing feature, tool, setup step, or `just` recipe, update `README.md` to reflect those changes. Only touch sections affected by this session's work; do not audit the entire README against the codebase unless the user asks.

## 5. Clear scratchpad

Empty `scratchpad.md` (write an empty file).

## 6. Final commit

Stage `MEMORY.md`, `scratchpad.md`, `README.md` (if changed), and any config files changed during the session (`.claude/settings.json`, `.gitignore`, `CLAUDE.md`, `TODO.md`). Commit as:

```
chore(kaizen): {main thing that was learned}
```

## 7. Summary

Show the user: number of commits made, what was added to memory, and any files left uncommitted.
