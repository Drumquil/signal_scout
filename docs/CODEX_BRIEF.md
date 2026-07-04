# Codex Brief

## Product Summary

Signal Scout is a Drumquil Signal beta product for monitoring Australian cattle
sale listings, filtering lots against buyer criteria, and sending WhatsApp alerts
 for matching opportunities.

## Current Product Direction

- Stabilise the AuctionsPlus-first beta runtime before expanding scope.
- Keep the scraper, filter logic, Google Sheets data layer, onboarding flow, and
  alert pipeline reliable.
- Defer Signal Model, platform expansion, and paid-launch work unless explicitly
  requested.

## Main Technical Areas

- `cattle_scout.py`: main runtime for scrape, filter, dedup, and alert flow.
- `transform_form_response.py`: onboarding transform from form responses to
  config rows.
- Google Sheets-backed config, listings, and run log contracts.
- AuctionsPlus-specific parsing and selector logic.
- Validation helpers for Sheets, Twilio, and multi-user configuration.

## Important Entry Points

- `docs/CURRENT_STATE.md`: active status, blockers, next actions.
- `docs/PROJECT_MAP.md`: where to start by task type.
- `cattle_scout.py`: runtime behavior.
- `transform_form_response.py`: onboarding/config writes.

## Testing / Validation

- Use the narrowest useful check first.
- Common offline checks use `python -m unittest discover -p "test_*.py"`.
- Live connectivity checks are `smoke_sheets.py` and `smoke_twilio.py`; run
  them deliberately because they touch Google Sheets/Twilio.
- Avoid broad validation unless the change touches shared runtime logic.

## Token Efficiency Notes

- Do not start with `docs/status.md` unless detailed history is needed.
- Use task-specific docs only when the change touches that area.
- Prefer updating `docs/CURRENT_STATE.md` over expanding root instructions.

## Do Not Inspect Unless Relevant

- `references/`
- old checkpoint and state markdown in the repo root
- `files/`
- generated exports, archives, and superseded docs

## Open Questions

- Multi-user validation with 2+ active users remains open.
- Beta-start timing still depends on first real tester onboarding and
  `TEST_MODE` being switched off deliberately.
