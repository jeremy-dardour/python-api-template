# CI/CD

Continuous integration runs the same quality gates enforced locally, on GitHub, for every
pull request and every push to `main`. CI is the last line of defense; the [prek pre-commit
hooks](adrs/009-pre_commit_hooks.md) are the first.

## Goals

- **Same gates as local.** Lint, format, type-check, and tests run in CI exactly as they run
  on a developer machine. No CI-only rules, no surprises at merge time.
- **Single source of truth.** CI calls the `just` recipes, not duplicated command strings, so
  there is nothing to keep in sync between the `Justfile` and the workflow.
- **Fast, granular signal.** Each gate is its own job, so a failure points directly at what
  broke instead of a single red blob.
- **Cheap.** Billed runner minutes are kept low by design (see Cost control below).

## What runs

Defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml). Four jobs run in parallel,
each calling one `just` recipe:

| Job      | Recipe              | Checks                                              |
|----------|---------------------|----------------------------------------------------|
| `lint`   | `just lint`         | `ruff check .`                                      |
| `format` | `just check-format` | `ruff format . --check --diff`                      |
| `types`  | `just check-types`  | `basedpyright`                                      |
| `test`   | `just test-coverage`| `pytest --cov=app --cov-report=term-missing --cov-fail-under=90` |

## Triggers

- `pull_request` — every PR, regardless of target branch.
- `push` to `main` — covers direct pushes and the merge commit after a PR lands.

Feature branches are validated through their PR, not on every push, so an open PR does not run
the suite twice per commit.

## Decisions

### Reuse `just` recipes instead of inlining commands

The workflow shells out to `just lint`, `just check-format`, `just check-types`, and
`just test-coverage`. The recipes already encode the exact commands and their flags, including
the `pytest` exit-code-5 handling ("no tests collected" is treated as success so the suite does
not fail on an empty test directory). Inlining `uv run ...` strings into the YAML would
duplicate that logic and let CI drift from local. The cost is one extra tool in CI
(`taiki-e/install-action@just`), which installs in seconds.

### Parallel jobs instead of one sequential job

Each gate is an independent job. A formatting failure and a type failure surface
simultaneously and independently, rather than the first failure masking the rest. The
trade-off is that setup (uv install, dependency sync) runs once per job rather than once total.
The uv cache keeps each setup to seconds, so the extra minutes are marginal. If cost ever
dominates correctness signal, collapsing the four jobs into one is the lever.

### Shared composite action for setup

The four jobs repeat the same environment setup. That is factored into a local composite
action, [`.github/actions/setup`](../.github/actions/setup/action.yml), which installs uv (with
caching), installs `just`, and runs `uv sync --locked`. Each job is then `checkout → setup →
recipe`. `--locked` installs exactly what `uv.lock` pins and fails if the lockfile is stale,
keeping CI reproducible.

### Coverage gate at 90% with a PR comment

`just test-coverage` runs `--cov-fail-under=90`, so the `test` job fails when coverage drops
below 90%. On pull requests the job then posts the coverage report as a comment via
[`py-cov-action/python-coverage-comment-action`](https://github.com/py-cov-action/python-coverage-comment-action).
The comment step is gated on `!cancelled()` so the number is posted even when the threshold
fails, giving the reviewer the figure alongside the red check. This requires
`pull-requests: write` on the `test` job only (the other jobs keep `contents: read`), and
`relative_files = true` under `[tool.coverage.run]` so the action resolves source paths.

## Cost control

CI minutes are billed, so the workflow is built to spend as few as possible:

- **Cancel superseded runs.** A `concurrency` group keyed on the ref with
  `cancel-in-progress` on pull requests: pushing a new commit to a PR cancels the in-flight run
  for the previous commit, so only the latest commit consumes minutes.
- **Cache dependencies.** `enable-cache: true` on `setup-uv` caches the uv install and resolved
  dependencies, cutting the largest cost in short jobs (environment setup).
- **Hard per-job timeout.** `timeout-minutes: 3` caps any hung run.
- **Scoped push trigger.** `push` is limited to `main`, so feature-branch pushes do not trigger
  duplicate runs alongside their PR.
- **Cheapest runner tier.** `ubuntu-latest` (1x billing multiplier).
- **Least privilege.** Workflow default is `permissions: contents: read`; only the `test` job
  widens to `pull-requests: write`, and only to post the coverage comment.

## Not included (yet)

- **Branch protection.** Requiring these checks before merge is a GitHub repository setting, not
  a file in this repo. Configure it under Settings → Branches → Branch protection rules.
- **Coverage upload / Codecov, deployment (CD).** Out of scope for the template's minimum CI.
