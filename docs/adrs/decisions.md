# Decisions

Architectural and tooling decisions are recorded as individual ADRs in [`adrs/`](.).

| # | Date | Decision | Summary |
|---|------|----------|---------|
| [001](001-package_management.md) | 2026-06-05 | Package Management | uv |
| [002](002-commit_format.md) | 2026-06-05 | Commit Format | Conventional Commits |
| [003](003-application_structure.md) | 2026-06-05 | Application Structure | Layer-based (`routers/`, `services/`, `repositories/`, `schemas/`, `models/`, `core/`) |
| [004](004-api_framework.md) | 2026-06-05 | API Framework | FastAPI |
| [005](005-package_layout.md) | 2026-06-09 | Package Layout | src/ layout |
| [006](006-task_runner.md) | 2026-06-09 | Task Runner | just |
| [007](007-linter_formatter.md) | 2026-06-09 | Linter and Formatter | Ruff |
| [008](008-type_checker.md) | 2026-06-09 | Type Checker | basedpyright |
| [009](009-pre_commit_hooks.md) | 2026-06-09 | Pre-commit Hooks | prek |
| [010](010-application_structure_feature_based.md) | 2026-06-13 | Application Structure | Feature-based (vertical slices), supersedes 003 |
| [011](011-testing_framework.md) | 2026-06-13 | Testing Stack | pytest + pytest-asyncio + httpx + pytest-mock |
| [012](012-continuous_integration.md) | 2026-06-13 | Continuous Integration | GitHub Actions (lint, format, types, tests) |
| [013](013-dependency_injection.md) | 2026-06-13 | Dependency Injection | Provider-function chain in `dependencies.py`; domain classes stay FastAPI-free |
