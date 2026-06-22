# 015 — Response Structure: RFC 9457 errors, bare domain models for success

- **Decision**: Errors use RFC 9457 (Problem Details). Success responses return bare domain models. Metadata lives in HTTP headers.
- **Date**: 2026-06-16

## Problem

The API has no standardized response structure. Without one, clients must guess the shape of responses, each endpoint invents its own error format, and metadata (request IDs, pagination) has no consistent home. A template targeting enterprise consumers needs a single, documented contract.

## Alternatives considered

- **RFC 9457 errors + bare domain models** (chosen)
- **RFC 9457 errors + custom `ApiResponse[T]` success envelope** (`{"data": ..., "meta": {...}}`)
- **JSON:API** (~73k  ) — full standard covering both success and error shapes

- **FastAPI defaults only** — `{"detail": "..."}` for errors, raw models for success

## Rationale

- **Errors need a standard, success bodies don't.** Error shapes must be consistent across endpoints for clients to build generic error handling. Success bodies are domain-specific by nature and vary per endpoint — standardizing them adds a wrapper with no information gain.
- **HTTP headers are the correct home for metadata.** `X-Request-Id`, `Link` (RFC 8288 pagination), `Deprecation` (RFC 8594), `Date`, and `RateLimit-*` headers exist precisely for this purpose. Duplicating them in a JSON envelope ignores HTTP semantics.
- **No envelope means no fight with FastAPI.** `response_model` works natively, OpenAPI schemas reflect the actual domain types, and clients deserialize directly into typed objects without unwrapping.
- **RFC 9457 is the industry standard for HTTP error responses.** Adopted by Stripe, Azure, Spring Boot (default), and Zalando's API guidelines. Content-Type `application/problem+json` is IANA-registered.

## Rejected alternatives

- **`ApiResponse[T]` success envelope**: Creates a disparity — standard for errors, bespoke for success. The metadata it carries belongs in HTTP headers. Forces every client to unwrap `data` and makes OpenAPI schemas indirect.
- **JSON:API**: Heavyweight. Imposes a resource/relationship model, specific query parameter conventions, and compound document structure. Solves problems (hypermedia, content negotiation) this API doesn't have. Adopting it for the envelope alone is disproportionate.
- **OData**: Even heavier than JSON:API. Designed for queryable enterprise data services, not general-purpose APIs.
- **FastAPI defaults only**: `{"detail": "..."}` is not a recognized standard. Validation errors and application errors have different shapes. Clients cannot build a single error parser.

## Consequences

- All error responses conform to RFC 9457 with `application/problem+json` content type and `type` defaulting to `"about:blank"`
- Success responses return domain Pydantic models directly — no wrapper
- Domain exceptions in `app.core.errors` carry no HTTP knowledge; `app.core.exception_handlers` maps them to Problem Details
- `ProblemDetail` base model covers standard errors; `ValidationProblemDetail` subclass adds structured `errors` field for validation
- FastAPI's `RequestValidationError` is overridden to emit `ValidationProblemDetail` with per-field error details
- Catch-all handler returns generic 500 and logs the traceback
- Paginated list endpoints use a typed response model (e.g., `PaginatedResponse[T]`) with cursor/total fields — this is domain data, not metadata

---
