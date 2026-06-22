# 017 — Containerization: single-stage uv image, non-root, no in-image healthcheck

- **Decision**: Ship a `Dockerfile` based on `python:3.13-slim` with a pinned `uv`, single stage, layer-cached dependency install, non-root runtime user, and the venv entrypoint run directly. No Docker `HEALTHCHECK`. Paired with a `.dockerignore`.
- **Date**: 2026-06-22

## Problem

The template had no container build. Enterprise consumers deploy via containers and expect a reproducible, secure, cache-efficient image as the starting point.

## Rationale

- **`python:3.13-slim` + pinned `uv` (`0.6.13`).** Slim keeps the image small (~215MB) while pinning the interpreter minor and the uv version makes builds reproducible; bump deliberately.
- **Single stage.** uv is copied in as a static binary and the slim base carries no build toolchain we need to discard, so a multi-stage split would add complexity for negligible size gain. Revisit if native build deps are introduced.
- **Layer caching.** Copy `pyproject.toml` + `uv.lock` and `uv sync --no-install-project` first, so the dependency layer is reused until the lockfile changes; the project itself installs in a later layer. Build-cache mounts (`--mount=type=cache`) speed repeat builds.
- **Non-root runtime.** A system `app` user runs the process. The venv is built as root (read-only to `app`) and executed directly via `.venv/bin/uvicorn`, so no boot-time uv resolution and no write access to the venv is needed.
- **Log-friendly environment.** `PYTHONUNBUFFERED=1` streams structured logs straight to stdout; `PYTHONDONTWRITEBYTECODE=1` keeps the runtime read-only friendly; `UV_COMPILE_BYTECODE=1` precompiles for faster cold starts; `UV_LINK_MODE=copy` and `UV_PYTHON_DOWNLOADS=0` keep installs clean and offline-safe.

## Rejected alternatives

- **Docker `HEALTHCHECK`.** Kubernetes and most orchestrators ignore it and probe `/health` and `/ready` directly, which the app already exposes. Baking in intervals and a probe method the orchestrator overrides adds noise; compose users can add one themselves.
- **`uv run` as the entrypoint.** Adds resolver work at boot and can attempt to write to the venv; running `.venv/bin/uvicorn` directly is faster and non-root clean.
- **Multi-stage build.** Deferred; no native build dependencies to strip today.

## Consequences

- `.dockerignore` excludes the venv, caches, VCS, tests, docs, and `.env`, but keeps `README.md` (hatchling requires it to build the wheel, per pyproject `readme`).
- The image runs as non-root `app` on port 8000; verified `/health` returns 200 with security headers and production JSON logs carry `service`/`version`/`request_id`, with uvicorn logs routed through the same renderer.
- Adopters bump the base image and uv pins deliberately, and add an orchestrator probe against `/health` (liveness) and `/ready` (readiness).

---
