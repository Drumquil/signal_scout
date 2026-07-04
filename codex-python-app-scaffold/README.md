# Codex Python App Scaffold

This folder is a reusable ICM-style scaffold optimized for Python application
repositories.

It assumes the target project usually has some combination of:

- application entry points such as `app.py`, `main.py`, `manage.py`, `cli.py`, or `src/<package>/`
- tests under `tests/` or targeted validation scripts at the repo root
- environment files such as `.env` and `.env.example`
- dependency files such as `requirements.txt`, `pyproject.toml`, or `uv.lock`

## What Makes This Version Different

Compared with the generic scaffold, this version includes:

- Python-oriented routing defaults
- safer guidance for entry points, imports, and package paths
- more concrete validation examples for `pytest`, `py_compile`, and focused script runs
- setup questions tailored to Python repos

## What To Copy

Copy these items into a target repository:

- `CLAUDE.md`
- `CONTEXT.md`
- `_config/`
- `shared/`
- `setup/`
- `stages/`
- `references/`

## Minimum Customization

Complete `setup/questionnaire.md`, then update:

1. `CLAUDE.md`
2. `CONTEXT.md`
3. `_config/change-safety.md`
4. `references/python-routing.md`
5. any stage `CONTEXT.md` files that need project-specific instructions

## Recommended Rollout

1. Add the scaffold without moving existing source files.
2. Point the routing files at the project's actual Python entry points and docs.
3. Confirm the preferred environment and validation commands.
4. Run the narrowest checks that prove the scaffold did not interfere with the app.
5. Only plan path migrations if repeated work justifies them.
