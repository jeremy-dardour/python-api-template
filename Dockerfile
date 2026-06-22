# Pinned base image and uv for reproducible builds; bump deliberately.
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /usr/local/bin/uv

# PYTHONUNBUFFERED: stream logs straight to stdout (the structured logging relies on this).
# PYTHONDONTWRITEBYTECODE: no .pyc writes at runtime, so the image stays read-only friendly.
# UV_COMPILE_BYTECODE: precompile during the build for faster cold starts.
# UV_LINK_MODE=copy: avoid hardlink warnings when installing from the build cache mount.
# UV_PYTHON_DOWNLOADS=0: never fetch a managed Python; use the image interpreter.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app

# Install dependencies first so this layer is cached until the lockfile changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Then install the project itself against the cached dependency layer.
# README.md is required because pyproject sets it as the project `readme`.
COPY README.md ./
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

USER app

EXPOSE 8000

# No Docker HEALTHCHECK by design: orchestrators (Kubernetes, etc.) probe the /health and /ready
# endpoints directly and ignore it. Add one in docker-compose if you run plain Docker.

# Run the venv entrypoint directly: no uv resolution at boot, and it works cleanly as non-root.
CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
