# 012 — Continuous Integration: GitHub Actions

- **Decision**: GitHub Actions running lint, format, type-check, and tests on pull requests and pushes to `main`
- **Date**: 2026-06-13

## Problem

The [prek pre-commit hooks](009-pre_commit_hooks.md) enforce quality locally, but they can be bypassed (`git commit --no-verify`) and never run on the server. Without CI, code can land on `main` with failing lint, types, or tests, and there is no shared, authoritative pass/fail signal on a pull request.

## Alternatives considered

- **GitHub Actions** — native to GitHub, where the template is hosted; no third-party integration.
- **CircleCI / GitLab CI / others** — established CI services requiring an external account and integration.

## Rationale

- Native to the repository host: no extra service to authorize or pay for separately.
- Reuses the existing `just` recipes (`lint`, `check-format`, `check-types`, `test-coverage`), so CI and local checks stay in sync with a single source of truth.
- One job per gate runs in parallel, giving granular pass/fail instead of one combined signal.

## Rejected alternatives

- **External CI services (CircleCI, GitLab CI, etc.)**: Added integration and a separate platform for no benefit on a GitHub-hosted template.

## Consequences

- [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) runs lint, format, type-check, and test+coverage on `pull_request` and on pushes to `main`.
- Per-job setup is factored into the composite action [`.github/actions/setup`](../../.github/actions/setup/action.yml).
- Cost is controlled via run cancellation on superseded commits, dependency caching, and per-job timeouts.
- Full goals, decisions, and cost-control measures are documented in [docs/ci-cd.md](../ci-cd.md).

---
