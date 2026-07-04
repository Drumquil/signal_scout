# Signal Scout Workspace Identity

This workspace uses an additive Interpretable Context Methodology (ICM) layer.
The existing application layout remains the source of truth for runtime code,
tests, and product documentation. The ICM files in this repository exist to
help Codex and other agents load the smallest useful context for a task.

## Workspace Purpose

Signal Scout monitors Australian cattle sale listings, filters lots against
buyer criteria, and sends WhatsApp alerts for matching opportunities.

Current priority is beta stabilisation of the AuctionsPlus-first runtime:

- scraping reliability
- filter correctness
- Google Sheets contracts
- onboarding flow
- alert delivery

Deferred unless explicitly requested:

- Signal Model
- web interface work
- platform expansion
- product renaming
- paid-launch infrastructure

## First Routing

1. Read [AGENTS.md](/C:/Users/Drumquil/Documents/Codex/Drumquil%20Signal/Signal%20Scout/AGENTS.md).
2. Read [CONTEXT.md](/C:/Users/Drumquil/Documents/Codex/Drumquil%20Signal/Signal%20Scout/CONTEXT.md).
3. Follow the stage contract under `stages/` that matches the current task.

## Source Of Truth

- Runtime code lives at the repository root.
- Active operational docs live under `docs/`.
- Historical and background material lives under `archive/` and `references/`.
- The ICM scaffolding must not require moving existing runtime files unless a
  future migration is explicitly planned and validated.
