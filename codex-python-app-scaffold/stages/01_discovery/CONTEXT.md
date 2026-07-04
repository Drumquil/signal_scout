# Stage 01: Discovery

## Goal

Understand the request and load only the minimum Python repo context needed to act.

## Inputs

- Layer 3: `AGENTS.md` if present
- Layer 3: default start files from `CONTEXT.md`
- Layer 3: `references/python-routing.md`
- Layer 3: `_config/workspace-principles.md`
- Layer 4: user-requested files, code, tests, docs, or scripts relevant to the task

## Process

- Identify the exact Python surface being changed: runtime, script, config, dependency, or test.
- Read only the task-specific references needed after the default docs.
- Search for path-sensitive files, imports, and entry points before proposing structural changes.
- Capture assumptions or hazards in `output/` if the task is complex.

## Outputs

- Optional discovery notes in `output/`
- A minimal set of files to carry into stage 02
