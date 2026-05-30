# Signal Scout Docs

This folder contains the active Codex-facing project documentation for Signal Scout.

## Files

- `status.md` - current project state, locked decisions, blockers, and next actions.
- `schema.md` - current Google Sheets schema and tab contracts.
- `auctionsplus-selector-reference.md` - current AuctionsPlus extraction reference.
- `prelaunch-checklist.md` - beta, launch, legal, technical, and operational gates.
- `strategy.md` - product strategy, market position, and architecture direction.
- `handover-chat14-to-chat15.md` - latest imported Claude handover; merge into `status.md` as work progresses.

## Rules

- Treat `status.md` and `schema.md` as the first files to read before changing behaviour.
- Keep secrets, live credentials, raw `.env` values, and private phone numbers out of docs.
- Move historical or third-party material to `references/` rather than keeping it in this active docs folder.
