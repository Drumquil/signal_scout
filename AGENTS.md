# AGENTS.md

## Project Identity

Signal Scout monitors Australian cattle sale listings, filters lots against buyer
criteria, and sends WhatsApp alerts for matching opportunities.

Current priority: beta stabilisation of the AuctionsPlus-first runtime. Focus on
scraping reliability, filtering, Google Sheets contracts, onboarding, and alert
delivery before expanding scope.

Deferred unless the user asks: Signal Model, web interface work, platform
expansion, product renaming, and paid-launch infrastructure.

## Default Read Order

Read the smallest relevant set of files first.

For most non-trivial tasks, start with:

1. `docs/CODEX_BRIEF.md`
2. `docs/PROJECT_MAP.md`
3. `docs/CURRENT_STATE.md`

Then read only the task-specific reference:

- `docs/schema.md` for Google Sheets, logging, config, onboarding, or data contracts.
- `docs/auctionsplus-selector-reference.md` for scraping, parsing, selectors, or AuctionsPlus-specific behaviour.
- `docs/prelaunch-checklist.md` for beta behaviour, alerts, compliance, launch, onboarding, or production settings.
- `docs/strategy.md` for product scope, platform expansion, positioning, or roadmap.

Read `README.md` or `HANDOVER.md` only when onboarding, reconciling workspace
setup, or investigating environment-specific issues.

Read `docs/status.md` only when detailed history, validation chronology, or
older decision context is required. It is not the default starting point.

## Working Rules

- Prefer small, scoped changes over broad refactors.
- Update existing active docs before creating parallel docs.
- Put frequently changing facts in `docs/CURRENT_STATE.md`, not here.
- Treat `references/` as background material, not active source of truth, unless
  an active doc points to it.
- Treat older root-level checkpoint files, `.docx`, `files/`, and `files.zip`
  material as historical unless migrated into `docs/` or `references/`.
