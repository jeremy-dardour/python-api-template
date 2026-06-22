# 016 — Structured Logging with structlog and request correlation

- **Decision**: Use `structlog` over stdlib logging. Bind a `request_id` per request via contextvars (accept inbound `X-Request-ID` or generate a UUID4). Render JSON in production, console in development. The request-logging middleware binds at entry with `clear_contextvars()` (no end-of-request unbind) and emits one access line per request from a `finally` block. Inject static service metadata (`service`, `version`) via a processor, expose a configurable `log_level`, render JSON with `default=str`, and route uvicorn's loggers through the same renderer.
- **Date**: 2026-06-22

## Problem

The template had no structured logging. Enterprise consumers need machine-parseable logs, per-request correlation across log lines, and a single access record per request including failures. Plain stdlib logging with f-strings gives none of these without bespoke wiring.

## Alternatives considered

- **structlog with stdlib integration** (chosen)
- **stdlib logging with a JSON formatter** (`python-json-logger`)
- **loguru**

## Rationale

- **structlog is the de facto standard for structured logging in Python.** First-class key/value events, contextvars integration for request-scoped binding, and a processor pipeline that renders JSON in prod and human-readable console in dev from one configuration.
- **contextvars give correlation for free.** Binding `request_id` once makes it appear on every downstream log line (including the exception handler's) without threading it through call signatures.
- **stdlib integration keeps third-party logs in the same stream.** `ProcessorFormatter` routes uvicorn and library logs through the same renderer, so output is uniform.

## Request-logging middleware: two non-obvious decisions

- **Bind via `clear_contextvars()` at entry, do not unbind at exit.** An unhandled exception unwinds *past* the user middleware out to Starlette's `ServerErrorMiddleware`, which runs outside all user middleware and renders the 500. Any `with`/`finally` that unbinds `request_id` inside the middleware fires *before* that handler runs, so the 500 log loses correlation. Clearing at entry keeps each request isolated (and is safe since requests are contextvar-isolated per task) while leaving the binding intact on the error path.
- **Emit the access line from `finally`, not after `await call_next`.** On a crash, `call_next` raises and any post-call logging is skipped, so failures (the lines you most want) would have no access record. A `finally` block logs exactly one line per request, including crashes, with `status` defaulting to 500.
- **Mounted outermost.** Added last in `main.py` so `request_id` is bound before any other layer runs and `duration_ms` measures the full request, not just the inner application slice.

## Service metadata, log level, serialization, and uvicorn

- **Static service fields via a processor, not startup contextvars.** Every log carries `service` and `version` so a shared sink can attribute lines. These are injected by a processor (`_add_static_fields`) added to both the structlog chain and the `ProcessorFormatter` `foreign_pre_chain` (so third-party/uvicorn logs carry them too). They are *not* bound at startup via `bind_contextvars`, because the request middleware's `clear_contextvars()` at entry would wipe them (verified).
- **`environment` is omitted from app-emitted logs.** It is a deployment fact the log shipper/collector should tag, kept consistent across services rather than self-reported by the app.
- **Configurable `log_level`** (default `INFO`) via settings, so DEBUG can be enabled per environment without code changes.
- **`JSONRenderer(default=str)`.** The default serializer renders UUID/datetime as `repr()` noise (e.g. `"UUID('...')"`); `default=str` emits clean values. orjson is the recommended upgrade (RFC 3339 datetimes, faster) but is left as an adopter dependency choice.
- **Uvicorn loggers routed through the root handler**, and `uvicorn.access` silenced because `RequestLoggingMiddleware` already emits a structured access line (avoids double logging and format drift).

## Rejected alternatives

- **`structlog.contextvars.bound_contextvars` (context manager):** Cleaner-looking and exception-safe for cleanup, but it unbinds as the exception unwinds through the `with` block, which runs before `ServerErrorMiddleware`'s 500 handler. Measured result: the 500 log line drops `request_id`. Eager cleanup directly defeats correlation here, so it was rejected in favor of clear-at-entry.
- **Startup `bind_contextvars` for service metadata:** wiped by the per-request `clear_contextvars()`; replaced by a processor.
- **orjson serializer:** recommended but deferred; it is a dependency decision left to adopters. `default=str` covers correctness in the meantime.
- **OpenTelemetry trace/span correlation:** high value but deferred to the observability decision (no tracing in the template yet); it becomes an additional processor when OTel lands.
- **stdlib + JSON formatter:** Works, but request-scoped context and dev/prod rendering must be hand-rolled; reimplements what structlog provides.
- **loguru:** Ergonomic, but opinionated, harder to integrate with stdlib/uvicorn handlers, and less standard for structured key/value events in enterprise stacks.

## Consequences

- `app.core.logging.setup_logging(json_output=...)` configures structlog and routes stdlib logs through `ProcessorFormatter`; called once at startup with `json_output = environment == "production"`
- `RequestLoggingMiddleware` binds `request_id`, echoes it on the response `X-Request-ID` header (happy path), and logs one `request` event per request with method, path, status, and `duration_ms`
- `request_id` is present on handled and unhandled error logs because the binding survives exception propagation
- The `X-Request-ID` response header is set only on non-crash responses; the access log line is universal
- Cross-cutting tests assert correlation by re-adding `merge_contextvars` to `capture_logs(processors=...)`, since `capture_logs` strips the processor chain

---
