## Session handoff (resume here if the session crashes)

Goal: finish production-readiness of the template on branch `feat/finish-production-readiness`.

Done and committed:
- LICENSE (MIT), `/health` + `/ready`, CORS (default-closed), security headers (HSTS prod-only).
- Structured logging: committed as `d95bef1 feat(logging): ...` (10 files). structlog, request_id correlation, static service metadata, configurable log_level, uvicorn routing, ADR 016.

Uncommitted in the working tree (each its own next commit):
1. Test reorg: `tests/api/{test_errors,test_security_headers}.py` moved to `tests/api/cross_cutting_concerns/`. Working tree shows them as deleted-old + untracked-new (the rename was unstaged when scoping the logging commit). Re-stage with `git add -A tests/api` and commit as `test:` or `refactor:`.
2. `Dockerfile` + `.dockerignore` (untracked): python:3.13-slim, non-root, uv, uvicorn on 8000. Needs its own commit + a test/smoke check. Consider adding `--no-access-log` is NOT needed (uvicorn.access already silenced in setup_logging).
3. `CLAUDE.md`: cross-cutting test rule rewritten (prefer real app, standalone only when construction/route differs). Commit as `chore(memory):` or fold via /close-session.
4. `TODO.md`, `scratchpad.md`: housekeeping, handled at session close.

Still TODO (not started, see TODO.md): README "What's included / Not included" section; Dependabot `.github/dependabot.yml`; broader items (http client lib, CI security/dependency checks, DB, auth, rate limiting, observability/OTel, secret management).

Verify after any change: `uv run pytest -q` (currently 25 pass), `uv run ruff check src/app tests`, `uv run basedpyright src/app tests`. prek runs format/lint/types on commit.

## Decisions
- Assessing public-readiness of the template repo against TODO.md and enterprise expectations.
- LICENSE: MIT
- Health endpoints: `/health` and `/ready` at root (outside `/api/v1`). `/ready` is a placeholder for adopters to extend with dependency checks.
- CORS: `CORSMiddleware`, default-closed (`allow_origins=[]`), `CORS_ORIGINS` env var, credentials off, methods/headers `["*"]`.
- Security headers: custom middleware, all five (nosniff, X-Frame-Options, HSTS production-only, X-XSS-Protection: 0, CSP default-src none).
- Structured logging: `structlog`, request ID via `contextvars` (accept X-Request-ID or generate UUID4), JSON in prod, console in dev, access log (method/path/status/duration/request_id). ADR 016 written.
- Logging middleware (grilled): bind via `clear_contextvars()` at entry, NO end-of-request unbind, because the unhandled-exception handler runs in Starlette's ServerErrorMiddleware (outside user middleware) and any with/finally unbind fires before it, dropping request_id from the 500 log. Rejected `bound_contextvars` for this reason (measured).
- Logging middleware: emit access line from `finally` (not after call_next) so crashes also get exactly one access record. Mounted outermost in main.py so request_id covers the full request and duration_ms is end-to-end.
- Test capture: `capture_logs()` strips the processor chain; re-add `merge_contextvars` via `capture_logs(processors=[...])` to assert request_id. capture_logs mutates the processor list in place, so it works with cached loggers; a fresh `configure(processors=[...])` does not.
- Dockerfile: `python:3.x-slim`, single stage, non-root user, `uv` install, layer caching on deps, uvicorn entrypoint port 8000. Plus `.dockerignore`.
- README: "What's included / Not included (yet)" section right after opening description.
- Dependabot: `.github/dependabot.yml`, weekly updates for pip + github-actions, manual review.
- Close-session skill: updated to include README sync step scoped to session changes.

## Feedback (review round 2)
- Static service metadata (`service`, `version`) added via a processor (NOT startup contextvars, which clear_contextvars wipes). `environment` intentionally omitted: it is a deployment fact the log shipper tags, not self-reported by the app.
- Configurable `log_level` setting (default INFO). `JSONRenderer(default=str)` to avoid repr() noise on UUID/datetime; orjson recommended but deferred as an adopter dependency choice.
- Uvicorn loggers routed through root handler; `uvicorn.access` silenced (RequestLoggingMiddleware already emits a structured access line).
- OpenTelemetry trace correlation deferred to the observability decision.
- Testing: removed white-box unit tests of private helpers (violated "test at natural altitude" + reportPrivateUsage). Static fields tested at api altitude by swapping the root handler onto a buffer reusing the real formatter (capture_logs can't see static fields since it strips the processor chain).

## Feedback
- Recovered a mistakenly-closed session from scratchpad + git working tree. Mid-flight: structured logging.
- Fixed broken state: exception_handlers.py had `import logging` removed but still called `logging.getLogger`; migrated it to `structlog.stdlib.get_logger()` to match middleware.
- Cross-cutting tests live under `tests/api/cross_cutting_concerns/` (errors, security_headers, request_logging). Feature tests (hello_world, todos, health) stay at `tests/api/` root.
- FRICTION: MEMORY rule says cross-cutting tests should use standalone apps with fake routes, not depend on feature endpoints. But test_security_headers already hits `/health` via the shared `client` fixture for the non-production case, and only builds a standalone app when it needs a different app construction (production HSTS). User wants request-logging test to follow the same pattern: use `/health` + real app, reserve standalone apps for when app construction must differ. Need to reconcile the MEMORY rule with this practice.

## Open questions
- RESOLVED: MEMORY rule rewritten to "prefer real app via /health; standalone app only when construction must differ (production) or a route is missing (raises)". Error-path logging tests use a standalone /boom fixture for exactly this reason.
