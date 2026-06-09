# 2026-06-09 Type Checker: basedpyright

- **Decision**: basedpyright
- **Date**: 2026-06-09

## Alternatives considered

- mypy (~20.5k ★)
- pyright (~15.5k ★)
- basedpyright (~3.4k ★) -- chosen
- ty, by Astral (~18.8k ★) -- deferred

## Rationale

- FastAPI and Pydantic v2 are designed and tested against pyright's type system -- their generics, stubs, and inference patterns are tuned for it. basedpyright inherits this compatibility directly.
- pip-installable (`uv add --dev basedpyright`) with no Node.js dependency, unlike upstream pyright -- cleaner Docker builds and CI pipelines.
- Stricter defaults than pyright out of the box: catches more issues without manual `strict` flag configuration.
- Tracks pyright releases closely (last release was 4 days behind pyright 1.1.410), so it is not a stale fork.
- Configuration lives in `pyproject.toml` under `[tool.basedpyright]`, consistent with the rest of the toolchain.

## Rejected alternatives

- **mypy** (~20.5k ★): Still the most widely adopted type checker and has the broadest plugin ecosystem, but its Pydantic v2 support lags behind pyright, it is significantly slower, and the "use mypy for SQLAlchemy" argument is largely legacy -- SQLAlchemy 2.0 ships with native pyright stubs.
- **pyright** (~15.5k ★): The upstream tool basedpyright is forked from. Functionally equivalent but requires Node.js as a runtime dependency, which is an unnecessary footgun in a pure Python project. basedpyright is a strict superset in terms of checks.
- **ty** (~18.8k ★): Written in Rust by Astral (the creators of uv and ruff), 10-100x faster than mypy/pyright, and architecturally aligned with the rest of this toolchain. However, it is currently versioned at `0.0.x` and explicitly does not guarantee stability between releases -- breaking diagnostic changes can occur on any update. Type system coverage also has known gaps. Revisit when it reaches `1.0`.

## Consequences

- `just check-types` runs `basedpyright` against `src/`.
- Type checking mode is set to `"all"` from project initialization. Exceptions for third-party libraries with incomplete stubs are handled per-package via `[tool.basedpyright.overrides]` rather than by downgrading the global mode.
- If a library is added with significantly better mypy support and no pyright stubs (rare, but possible), this decision should be revisited. Switching is low-cost -- it is a dev-only tool with no runtime impact.
