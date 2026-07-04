# Stage 03: Implementation

## Goal

Make the scoped Python change while preserving existing runtime behaviour.

## Inputs

- Layer 3: `_config/change-safety.md`
- Layer 3: `references/python-routing.md`
- Layer 4: approved design scope from stage 02
- Layer 4: the exact Python files, configs, tests, or docs to edit

## Process

- Edit only the files required for the task.
- Keep changes readable and reversible.
- When adding structure, prefer scaffolding files and docs over moving Python packages or modules.
- If a path changes, update every known import, script reference, and doc reference before validation begins.

## Outputs

- Updated source, tests, configs, docs, or workspace scaffolding
- Optional implementation notes in `output/`
