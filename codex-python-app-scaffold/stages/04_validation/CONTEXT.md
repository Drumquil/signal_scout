# Stage 04: Validation

## Goal

Prove the Python change with the narrowest effective checks.

## Inputs

- Layer 3: project routing and validation docs
- Layer 3: `references/python-routing.md`
- Layer 3: `_config/change-safety.md`
- Layer 4: changed files
- Layer 4: task-specific validation targets

## Process

- Start with the smallest command that can fail for the changed surface.
- Use `python -m py_compile` for touched Python files when syntax confidence is enough.
- Prefer narrow `pytest` targets such as one file or one keyword over full-suite runs.
- Use a focused script or app command only when it is the safest way to confirm runtime behavior.
- Record any unrun checks or environmental blockers clearly.

## Outputs

- Validation notes in `output/`
- A clear pass/fail status for the changed surface
