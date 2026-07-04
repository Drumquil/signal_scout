# Signal Scout Status

Last updated: 2026-05-30

This file is the compact detailed status reference for Signal Scout.

Use:

- `docs/CURRENT_STATE.md` for the smallest active snapshot
- `docs/status.md` for current detailed state and locked decisions
- `archive/status-history.md` for full validation chronology and older state detail

## Current Position

- Product: Signal Scout beta
- Runtime focus: AuctionsPlus-first monitoring and WhatsApp alerts
- Runtime version in play: `v2.4` validation path
- Delivery mode: Google Sheets-backed multi-user config plus Twilio WhatsApp alerts
- GitHub Actions runtime: current runtime code is on `master`
- `TEST_MODE`: still `True`

## What Is Working

- AuctionsPlus scraping and catalogue-state handling are implemented.
- Two-stage WATCHING -> ALERT flow is implemented.
- Google Sheets logging, listings writes, and config loading are working.
- Multi-user config architecture is implemented with per-user deduplication.
- Onboarding transform script writes row-block config entries.
- Stage 1 and Stage 2 behavior have both been validated locally.
- Controlled real WhatsApp send has been confirmed without switching the whole
  runtime out of `TEST_MODE`.

## Active Beta Blockers

1. `TEST_MODE` is still `True`.
2. Multi-user runtime has not yet been validated with 2+ active real users in
   the same run.
3. First real beta tester has not been onboarded end to end.
4. Beta user guide and feedback process still need to be finalised.
5. Incident response runbook still needs a short operational final pass.

## Current Repo / Runtime Notes

- Main runtime file: `cattle_scout.py`
- Onboarding transform: `transform_form_response.py`
- Workflow file: `.github/workflows/cattle_scout.yml`
- Runtime schedule: 21:00 UTC and 03:00 UTC daily
- Current production source remains AuctionsPlus only
- Active validated dev profile: `tom_steers`

## Locked Decisions

### Scope and sequencing

- Beta stabilisation comes before platform expansion.
- Signal Model remains deferred behind Scout beta stabilisation.
- Product rename work is deliberately deferred until beta is stable.

### Matching behavior

- Silent misses are worse than false positives for this buy-side tool.
- Unknown or missing soft-gate fields should not suppress otherwise relevant
  listings.
- `sale_types` is deprecated and should be removed in a dedicated cleanup pass.

### Multi-user architecture

- Config schema is row-block-per-user: `user_id | setting | value`.
- Deduplication is keyed by `(url, user_id)`.
- `twilio_to` lives in the config sheet per user, not in environment secrets.

### Multi-profile support

- Full multi-profile-per-user support is deferred post-beta.
- Interim beta workaround: duplicate form submissions creating separate user
  blocks that share the same destination number.

### Alert lifecycle

- For beta, alert deactivation is manual by setting `active = FALSE` in the
  config sheet for that user block.

### Legal / beta sequencing

- Unpaid beta may proceed before formal platform consent.
- Paid users remain blocked pending platform consent and later legal work.
- Terms of Use, Privacy Policy, and lawyer review are post-beta hard gates for
  paid rollout rather than pre-beta gates.

## Key Implemented Features Worth Remembering

### `target_sex`

- Implemented in `v2.4`
- Stored in config as a plain string: `steer`, `heifer`, or `either`
- Only enforced when the target is explicitly `steer` or `heifer`
- Skipped when target is `either`, blank, or the listing sex is unknown

### Onboarding pipeline

- Google Form is live
- Response sheet is active
- `transform_form_response.py` includes WhatsApp number normalisation
- Current active config set is still essentially the Tom validation profile

## Immediate Next Actions

1. Get the first real beta tester to submit the form.
2. Run `transform_form_response.py` to append the tester block.
3. Validate the runtime with 2+ active users in one run.
4. Switch `TEST_MODE` to `False` only when live beta sends are intentionally
   starting.
5. Finish the short beta guide and feedback path.

## Where To Read Next

- `docs/schema.md`: Sheets contracts, config structure, onboarding writes
- `docs/auctionsplus-selector-reference.md`: AuctionsPlus parsing behavior
- `docs/prelaunch-checklist.md`: beta and paid-rollout gates
- `docs/strategy.md`: product and roadmap questions
- `archive/status-history.md`: full historical validation log and prior state detail
