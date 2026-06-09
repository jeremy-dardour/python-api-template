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
