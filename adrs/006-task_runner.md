# 2026-06-09 Task Runner: just

- **Decision**: just (Justfile)
- **Date**: 2026-06-09

## Alternatives considered

- `make` / Makefile
- Plain shell scripts

## Rationale

- Simpler syntax than Makefile with no footgun tab-vs-space issues and no implicit POSIX shell behaviors.
- Cross-platform (macOS, Linux, Windows via WSL) without additional tooling.
- Commands are self-documenting via `just --list`.
- Works well alongside uv -- recipes are thin wrappers around `uv run` commands, keeping the task runner and package manager cleanly separated.

## Rejected alternatives

- **Makefile**: Ubiquitous but designed for build dependency graphs, not developer scripts. Tab-indentation requirement and implicit rules are frequent sources of confusion.
- **Shell scripts**: No discoverability; each developer must read the script or documentation to know what's available.

## Consequences

- `just dev` starts the development server with hot-reload.
- `just start` starts the production server.
- New developer tasks should be added as `just` recipes in the `Justfile`.
