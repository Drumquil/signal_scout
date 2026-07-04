# Stage 01: Discovery

## Goal

Understand the request and load only the minimum repo context needed to act.

## Inputs

- Layer 3: `../../AGENTS.md`
- Layer 3: `../../docs/CODEX_BRIEF.md`
- Layer 3: `../../docs/PROJECT_MAP.md`
- Layer 3: `../../docs/CURRENT_STATE.md`
- Layer 3: `../../_config/workspace-principles.md`
- Layer 4: user-requested files, code, docs, or artifacts relevant to the task

## Process

- Identify the exact work being asked for.
- Read only the task-specific references needed after the default docs.
- Search for path-sensitive files before proposing structural changes.
- Capture assumptions or hazards in `output/` if the task is complex.

## Outputs

- Optional discovery notes in `output/`
- A minimal set of files to carry into stage 02
