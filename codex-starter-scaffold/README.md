# Codex Starter Scaffold

This folder is a reusable ICM-style scaffold for existing Codex projects.

It is designed for projects that already have a working source layout and want:

- clearer context routing for Codex
- consistent stage contracts
- stable shared instructions
- better handoff and validation discipline

It is intentionally additive. The scaffold should sit alongside an existing repo
layout rather than forcing a full source-tree reorganization on day one.

## What To Copy

Copy these items into a target project:

- `CLAUDE.md`
- `CONTEXT.md`
- `_config/`
- `shared/`
- `setup/`
- `stages/`

## What To Customize

Complete `setup/questionnaire.md`, then edit:

1. `CLAUDE.md`
2. `CONTEXT.md`
3. `_config/workspace-principles.md`
4. `_config/change-safety.md`
5. any stage `CONTEXT.md` files that need domain-specific routing

## Recommended Rollout

1. Add the scaffold without moving existing source files.
2. Point the routing files at the project's real source of truth.
3. Validate that the current runtime and tooling still work.
4. Only plan structural file moves if repeated work shows they are worth the risk.

## Good Fit

Use this scaffold when the project work is mostly:

- sequential
- reviewable by a human between steps
- repeatable across many tasks or runs

## Less Suitable

This scaffold is less useful when a project depends on:

- real-time multi-agent collaboration
- heavy automated branching
- high-concurrency runtime orchestration

## Notes

- Keep prompts and rules in plain markdown.
- Keep stable references separate from task-specific working artifacts.
- Improve source instructions when the same output edits recur.
