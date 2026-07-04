# Stage 02: Design

## Goal

Translate discovery into the smallest safe implementation plan.

## Inputs

- Layer 3: `../../_config/change-safety.md`
- Layer 3: task-specific docs from `docs/`
- Layer 4: stage 01 notes, if any
- Layer 4: the code or docs that will be changed

## Process

- Define the change boundary.
- Note any file-path, runtime, or operator impact.
- Prefer additive structure over relocation when both would solve the problem.
- If a migration is necessary, list every file that must change with it.

## Outputs

- Optional design note in `output/`
- An implementation target small enough to validate confidently
