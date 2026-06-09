# python-api-template

Personal template for Python API projects.

## Tools

| Tool | Role | Config |
|------|------|--------|
| [uv](https://docs.astral.sh/uv/) | Package manager, virtualenv, Python version | `pyproject.toml` |
| [just](https://just.systems/) | Task runner | `Justfile` |
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework | — |
| [Ruff](https://docs.astral.sh/ruff/) | Linter and formatter | `pyproject.toml` `[tool.ruff]` |
| [basedpyright](https://docs.basedpyright.com/) | Type checker | `pyproject.toml` `[tool.basedpyright]` |
| [prek](https://github.com/j178/prek) | Pre-commit hooks (ruff + basedpyright) | `prek.toml` |

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [just](https://just.systems/man/en/installation.html).

## Setup

```bash
just setup
```

This installs dependencies and registers the pre-commit hooks.

## Running Commands

List available commands:

```bash
just --list
```

Activate the virtual environment before running project commands:

```bash
source .venv/bin/activate
```
