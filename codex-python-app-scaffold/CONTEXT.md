# Workspace Routing

This file routes work across a Python application repository while keeping
context loading narrow and explicit.

## Default Read Order

For most non-trivial tasks, read:

1. `AGENTS.md` if present
2. `[PROJECT_OVERVIEW_DOC]`
3. `[PROJECT_MAP_OR_CURRENT_STATE_DOC]`
4. `references/python-routing.md`

Then read only the task-specific references needed for the request.

## Python Task Routing

- Runtime or business logic changes: main package or app entry points plus the smallest relevant tests
- CLI or operator script changes: `cli.py`, `scripts/`, root utilities, and operator docs
- Config or environment changes: `.env.example`, config modules, settings files, and setup docs
- Data model or schema changes: model definitions, serializers, migrations, and contract docs
- Test failures or regressions: failing tests first, then the smallest related source files
- Packaging or dependency changes: `pyproject.toml`, `requirements.txt`, lockfiles, and install docs

## Default Python Validation Examples

- Single-file syntax check: `python -m py_compile path\\to\\file.py`
- Narrow test file: `pytest tests\\path\\to\\test_file.py`
- Narrow test selection: `pytest -k "keyword"`
- Focused app script run: project-specific command that exercises only the changed surface

## Stage Routing

- `stages/01_discovery/`: understand the request, find the minimum relevant files, and capture assumptions.
- `stages/02_design/`: define the smallest safe change and note contract or path impacts.
- `stages/03_implementation/`: make scoped edits without breaking existing imports, scripts, or runtime paths.
- `stages/04_validation/`: run the narrowest Python checks that prove the change.
- `stages/05_handoff/`: summarize outcomes, residual risks, and source-level follow-ups.

## Shared Workspace Rules

- Preserve import paths and runtime entry points unless a migration is explicitly requested.
- Prefer additive scaffolding over structural churn.
- Update docs, scripts, and tests together when Python paths change.
- Treat background folders as reference material unless active routing points to them.
- If a recurring output edit keeps happening, improve the source instruction or
  reference file that caused it.
