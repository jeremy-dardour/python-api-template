# 002 — Commit Format: Conventional Commits

- **Decision**: Conventional Commits
- **Date**: 2026-06-05

## Problem

Without a convention, git history fills with "fix stuff", "update", and "wip" messages. What changed, why, and when becomes impossible to answer from the log. Changelogs cannot be generated automatically and PRs are harder to review.

## Rationale

Standardized commit messages enable automated changelog generation, make the history scannable by type, and are enforced consistently by the `/commit` project skill.

See [standards/commit-format.md](../standards/commit-format.md) for the full spec.
