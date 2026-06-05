# Commit Format

Conventional Commits.

## Structure

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

## Types

| Type       | Use for                                         |
|------------|-------------------------------------------------|
| `feat`     | New feature or capability                       |
| `fix`      | Bug fix                                         |
| `chore`    | Tooling, deps, config (no production code)      |
| `refactor` | Restructuring without behavior change           |
| `test`     | Adding or updating tests                        |
| `docs`     | Documentation only                              |
| `ci`       | CI/CD pipeline changes                          |

`build` is collapsed into `chore`.

## Scope

Optional. Component affected: `auth`, `logging`, `db`, `config`, etc. Omit for cross-cutting changes.

## Subject rules

- Imperative mood: "add rate limiting" not "added" or "adds"
- No period at the end
- 72 chars max

## Examples

```
chore: initialize project with uv
feat(logging): add structured JSON logging
fix(config): handle missing env vars at startup
ci: add GitHub Actions workflow
```
