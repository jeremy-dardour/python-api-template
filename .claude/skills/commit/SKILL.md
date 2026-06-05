---
name: commit
description: Stage and commit changes to this repository following the project's commit format. Use when the user asks to commit, stage changes, or create a git commit.
---

# Commit

Follow the format defined in [standards/commit-format.md](../../../standards/commit-format.md).

## Workflow

1. Run `git status` and `git diff` to understand what changed.
2. Stage specific files by name -- never `git add -A` or `git add .`.
3. Draft a commit message from the format spec.
4. Commit using a HEREDOC to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
type(scope): subject

Optional body.
EOF
)"
```

5. Run `git status` to confirm success.

## Rules

- Never skip hooks (`--no-verify`).
- Never amend a published commit.
- Never commit `.env` or credential files -- warn the user if asked.
- If a pre-commit hook fails, fix the issue and create a new commit; do not amend.
