# 2026-06-09 Package Layout: src/ layout

- **Decision**: src/ layout (`src/app/`)
- **Date**: 2026-06-09

## Alternatives considered

- Flat layout (`app/` at project root)

## Rationale

- Without `src/`, Python adds `.` to `sys.path` when running pytest, making `import app` work even if the package is not installed. This masks broken `pyproject.toml` install config -- tests pass locally but fail in CI or production where the package must be installed.
- With `src/`, `app` is only importable after `uv sync` installs the project in editable mode (`-e .`), which is exactly what CI and production do. Local dev matches deployment.
- The wrapper is not overhead -- it is a correctness guarantee.

## Rejected alternatives

- **Flat layout**: Common in simple scripts and tutorials, but unreliable for installable packages. The `sys.path` leakage silently hides misconfigured packaging.

## Consequences

- `uv sync` must be run before the project is importable (handled automatically; it installs in editable mode).
- All source code lives under `src/app/`. Imports remain `from app.x import y` -- the `src/` wrapper is transparent at runtime.
- Hatchling is configured with `packages = ["src/app"]` to locate the package during build.
