# Workspace Routing

This file routes work across the repository while keeping context loading narrow
and explicit.

## Default Read Order

For most non-trivial tasks, read:

1. `[START_FILE_1]`
2. `[START_FILE_2]`
3. `[START_FILE_3]`

Then read only the task-specific references needed for the request.

## Task Routing

- `[TASK_TYPE_1]`: `[FILES_AND_DOCS_1]`
- `[TASK_TYPE_2]`: `[FILES_AND_DOCS_2]`
- `[TASK_TYPE_3]`: `[FILES_AND_DOCS_3]`
- `[TASK_TYPE_4]`: `[FILES_AND_DOCS_4]`

## Stage Routing

- `stages/01_discovery/`: understand the request, find the minimum relevant files, and capture assumptions.
- `stages/02_design/`: define the smallest safe change and note contract or path impacts.
- `stages/03_implementation/`: make scoped edits without breaking existing runtime paths.
- `stages/04_validation/`: run the narrowest checks that prove the change.
- `stages/05_handoff/`: summarize outcomes, residual risks, and source-level follow-ups.

## Shared Workspace Rules

- Preserve current runtime entry points unless a migration is explicitly requested.
- Prefer additive scaffolding over structural churn.
- Update active docs before creating parallel docs.
- Treat background folders as reference material unless active routing points to them.
- If a recurring output edit keeps happening, improve the source instruction or
  reference file that caused it.
