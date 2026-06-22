# Memory

## Feedback

- **No Claude co-author in commits**: never include `Co-Authored-By: Claude ...` in commit messages. User preference.
- **Commit type for tooling in template**: use `feat` for tooling/config additions (ruff, just, linters). The template is the product; adding tooling is a feature, not chore. Use `chore` only for non-product changes like CI fixes or dependency bumps.
- **No prod code for tests**: don't introduce production code (factories, seams, indirection) whose only purpose is testability. Test logic at its natural altitude. Before proposing a test that needs new production surface, ask whether the logic can be tested directly at a lower layer.
- **Type ignore policy**: analyse the error first. Only suppress with `# pyright: ignore` or `# type: ignore` when there is no clean and pragmatic fix. When suppressing, always add a comment explaining the reason. Never scatter ignores without understanding the root cause.
- **Decouple infrastructure tests**: tests for cross-cutting concerns (error handling, middleware) should use standalone FastAPI apps with fake routes, not depend on feature endpoints. Keeps tests isolated and avoids coupling to feature implementation details.
