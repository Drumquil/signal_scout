# Python Routing Reference

Use this file to adapt the scaffold to a Python application quickly.

## Common Source Layouts

- Root app files: `app.py`, `main.py`, `manage.py`, `cli.py`
- Package layout: `src/<package_name>/` or `<package_name>/`
- Tests: `tests/`
- Utility scripts: `scripts/` or root-level helper scripts
- Config and settings: `settings.py`, `config.py`, `.env.example`, `pyproject.toml`

## Common Routing Decisions

- If the repo uses `src/`, treat `src/` as the source root and avoid moving files out of it casually.
- If tests mirror package structure, use the matching test file as the first validation target.
- If the project uses CLI utilities instead of a web server, route operational tasks to those scripts first.
- If there are both integration and unit tests, prefer unit or file-scoped tests first unless the change crosses boundaries.

## Common Validation Order

1. `py_compile` for touched Python files when syntax confidence is enough
2. narrow `pytest` target for changed behavior
3. focused script or app command for runtime confirmation
4. broader suite only when shared logic changed
