setup:
    uv sync
    uv run prek install

dev:
    uv run uvicorn app.main:app --reload

start:
    uv run uvicorn app.main:app

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check . --fix

check-format:
    uv run ruff format . --check  --diff

format:
    uv run ruff format .

check-all:
    @just lint
    @just check-format
    @just check-types

fix-all:
    @just lint-fix
    @just format

check-types:
    uv run basedpyright

# pytest exit 5 means "no tests collected" — treat it as success so recipes don't fail on empty test dirs.
# Each recipe uses a bash shebang so $? is captured in the same shell process that ran pytest.

test:
    #!/usr/bin/env bash
    uv run pytest tests/; ret=$?; [[ $ret -eq 0 || $ret -eq 5 ]]

test-unit:
    #!/usr/bin/env bash
    uv run pytest tests/unit/; ret=$?; [[ $ret -eq 0 || $ret -eq 5 ]]

test-api:
    #!/usr/bin/env bash
    uv run pytest tests/api/; ret=$?; [[ $ret -eq 0 || $ret -eq 5 ]]

test-coverage:
    #!/usr/bin/env bash
    uv run pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=90; ret=$?; [[ $ret -eq 0 || $ret -eq 5 ]]
