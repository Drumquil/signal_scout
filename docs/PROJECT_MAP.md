# Project Map

## Start Here

- `docs/CODEX_BRIEF.md`: product and technical snapshot.
- `docs/CURRENT_STATE.md`: live status, blockers, next actions.
- `AGENTS.md`: repo operating rules and doc routing.
- `CLAUDE.md`: workspace identity for Codex/ICM-style routing.
- `CONTEXT.md`: workspace-level task routing and stage map.

## Root Files

- `cattle_scout.py`: main Signal Scout runtime.
- `transform_form_response.py`: Google Form response to config-row transform.
- `smoke_sheets.py`: live Google Sheets connectivity check.
- `smoke_twilio.py`: live Twilio connectivity check.
- `inspect_listing.py`: listing inspection helper.
- `validate_multi_user_config.py`: config validation utility.
- `README.md`: human-facing repo summary.
- `HANDOVER.md`: local workspace and secret-path notes.

## Docs

- `docs/CURRENT_STATE.md`: default status snapshot for active work.
- `docs/schema.md`: Sheets schema and data contracts.
- `docs/auctionsplus-selector-reference.md`: AuctionsPlus extraction reference.
- `docs/prelaunch-checklist.md`: beta and launch gates.
- `docs/strategy.md`: higher-level product strategy.
- `docs/status.md`: compact detailed state and locked decisions.

## Workspace Orchestration

- `_config/`: stable workspace operating references.
- `shared/`: reusable cross-stage assets for Codex work.
- `setup/questionnaire.md`: reusable questionnaire for adapting this scaffold to other projects.
- `stages/01_discovery/` through `stages/05_handoff/`: additive ICM-style workflow contracts for discovery, design, implementation, validation, and handoff.
- `codex-starter-scaffold/`: reusable starter version of this workspace layer for other Codex projects.
- `codex-python-app-scaffold/`: Python-app-focused starter scaffold with more concrete routing and validation defaults.

## Validation / Helper Scripts

- `activate_batch_validation_users.py`: batch validation user activation.
- `deactivate_batch_validation_users.py`: batch validation user deactivation.
- `deactivate_dummy_multi_users.py`: cleanup helper for dummy users.
- `inspect_multi_user_validation.py`: multi-user validation inspection.

## Reference / Historical Areas

- `references/`: research and source material, not default context.
- `archive/`: historical state docs, handovers, and superseded schema references.
- `files/`: imported historical material, not active source of truth.

## Task Routing

- Scraper or parser changes: `cattle_scout.py` + `docs/auctionsplus-selector-reference.md`
- Config / onboarding changes: `transform_form_response.py` + `docs/schema.md`
- Beta behaviour / live-send changes: `docs/CURRENT_STATE.md` + `docs/prelaunch-checklist.md`
- Product-scope questions: `docs/strategy.md`
