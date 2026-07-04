# Workspace Principles

## Why This ICM Layer Exists

The repo already has a working Python application structure. This ICM layer is
here to improve agent routing, observability, and repeatability without forcing
a risky reorganization of the runtime.

## Adaptation Rules

- Treat the project's existing source tree and docs as the live product workspace.
- Treat `stages/` as an orchestration layer for Codex work, not as a replacement
  for the app's package layout.
- Keep Python packages, entry points, and environment conventions in place
  unless a migration is planned, implemented, and validated end to end.
- Prefer stage outputs that document thinking, validation notes, or migration
  artifacts over moving core source files prematurely.

## Five-Layer Mapping In This Repo

- Layer 0: `CLAUDE.md`
- Layer 1: `CONTEXT.md`
- Layer 2: `stages/*/CONTEXT.md`
- Layer 3: `_config/`, `references/`, stable docs, and stage `references/`
- Layer 4: stage `output/` folders plus the task-specific Python code or docs being changed
