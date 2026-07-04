# Workspace Routing

This file routes work across the existing Signal Scout repository while keeping
context loading narrow and explicit.

## Default Read Order

For most non-trivial tasks, read:

1. `docs/CODEX_BRIEF.md`
2. `docs/PROJECT_MAP.md`
3. `docs/CURRENT_STATE.md`

Then read only the task-specific reference:

- `docs/schema.md` for Google Sheets, logging, config, onboarding, or data contracts.
- `docs/auctionsplus-selector-reference.md` for scraping, parsing, selectors, or AuctionsPlus behaviour.
- `docs/prelaunch-checklist.md` for beta behaviour, alerts, compliance, launch, onboarding, or production settings.
- `docs/strategy.md` for product scope, platform expansion, positioning, or roadmap.

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
- Treat `references/` as background unless an active doc points there.
- If a recurring output edit keeps happening, improve the source instruction or
  reference file that caused it.
