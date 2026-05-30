# AGENTS.md

## Project Identity

This repository contains Signal Scout, a Drumquil Signal product for monitoring Australian cattle sale listings, filtering lots against buyer criteria, and sending WhatsApp alerts for matching opportunities.

The current implementation focuses on online cattle listing platforms. AuctionsPlus is the first active source, but the product direction is broader: Signal Scout should eventually support cattle sale data from multiple online platforms and, where feasible, structured or semi-structured data from physical saleyard locations such as Grafton, Lismore, Casino, and other Australian saleyards.

The current priority is Signal Scout beta stabilisation. Work should focus on making the existing scraper, filtering logic, Google Sheets data layer, onboarding workflow, and alert pipeline reliable before expanding scope.

Signal Model, web interface work, platform expansion, product renaming, and paid-launch infrastructure are important but deferred unless the user explicitly asks to work on them.

## Read Order

Read the smallest set of files needed for the task, starting from the ordered list below.

Always read `README.md`, `HANDOVER.md`, and `docs/status.md` before non-trivial changes.

Also read:

- `docs/schema.md` before changing Google Sheets, logging, config, onboarding, or data contracts.
- `docs/auctionsplus-selector-reference.md` before changing scraping, parsing, selectors, listing classification, or AuctionsPlus-specific behaviour.
- `docs/prelaunch-checklist.md` before changing beta behaviour, alerts, compliance, launch, user onboarding, or production settings.
- `docs/strategy.md` before changing product scope, platform expansion, pricing, positioning, or roadmap.

Use `references/` only for background research or source material. Reference files are not authoritative unless an active doc points to them or the user explicitly asks to use them.

Treat older root-level project state, checkpoint, `.docx`, `files/`, and `files.zip` material as historical unless it has been migrated into `docs/` or `references/`.
