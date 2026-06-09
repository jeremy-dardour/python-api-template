dev:
    uv run uvicorn app.main:app --reload

start:
    uv run uvicorn app.main:app

lint:
    uv run ruff check .

lint-fix:
    uv run ruff check . --fix

format-check:
    uv run ruff format . --check  --diff

format:
    uv run ruff format .

check-all:
    @just lint
    @just format-check

fix-all:
    @just lint-fix
    @just format
