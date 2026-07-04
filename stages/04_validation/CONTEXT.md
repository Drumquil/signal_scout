# Stage 04: Validation

## Goal

Prove the change with the narrowest effective checks.

## Inputs

- Layer 3: `../../docs/PROJECT_MAP.md`
- Layer 3: `../../_config/change-safety.md`
- Layer 4: changed files
- Layer 4: task-specific validation targets

## Process

- Choose the smallest checks that exercise the changed surface.
- Prefer targeted script runs or static checks over broad validation.
- Record any unrun checks or environmental blockers clearly.

## Outputs

- Validation notes in `output/`
- A clear pass/fail status for the changed surface
