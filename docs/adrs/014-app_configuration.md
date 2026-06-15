# 006 — Configuration: pydantic-settings

- **Decision**: pydantic-settings with BaseSettings
- **Date**: 2026-06-13

## Problem

Application configuration must be sourced from environment variables to follow 12-factor app principles. Values must be typed, validated, and have sensible defaults — not read as raw strings via `os.environ` scattered across the codebase.

## Alternatives considered

- **pydantic-settings** (~2.9k ★, ~5M downloads/month)
- **pydantic BaseModel** (bundled with pydantic)
- **python-dotenv** (~4.5k ★, ~30M downloads/month)
- **dynaconf** (~3.6k ★, ~500k downloads/month)

## Rationale

- Environment variables are read, validated, and typed automatically from field declarations — no manual parsing
- `.env` file support built in for local development, with no code change needed for production (env vars take precedence)
- Single `settings` instance in `core/config.py` is the only entry point for configuration across the entire codebase
- Already part of the Pydantic ecosystem — no new mental model to learn

## Rejected alternatives

- **pydantic BaseModel**: Reads from Python dicts, not environment variables. Would require manual `os.environ` calls to populate it, defeating the purpose.
- **python-dotenv**: Only loads `.env` into `os.environ` — no typing, no validation, no defaults. Solving a subset of the problem.
- **dynaconf**: More powerful (multiple sources, environments, layered config) but significantly more complex. That complexity is not warranted for an API service with straightforward config needs.

## Consequences

- All configuration is accessed via `from app.core.config import settings` — direct `os.environ` calls are forbidden
- `.env` is gitignored; `.env.example` is committed with all keys and no values
- In production, environment variables are injected by the platform — no `.env` file is used or needed

---