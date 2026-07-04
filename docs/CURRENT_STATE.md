# Current State

## Mission Right Now

Stabilise the Signal Scout beta runtime for the AuctionsPlus-first workflow.

## Current Runtime Position

- Main runtime is on `v2.4` validation path.
- Google Sheets-backed multi-user config is implemented.
- Onboarding transform script is live and writes config row blocks.
- Google Form responses now land in the `drumquil_scout` workbook on
  `Form responses 1` rather than a separate response spreadsheet.
- Stage 1 WATCHING flow has been validated on live catalogue data.
- Stage 2 ALERT flow has been validated in controlled local/test runs.
- GitHub Actions is running the current runtime from `master`.
- Runtime source abstraction is now in place:
  source discovery/scrape runs once per source per run, then shared listings
  are matched across all active users.
- Form `v2.1` wording and transform behavior have been validated for:
  commercial-only, breeding-heifer-only, breeding-cow-only, and CAF-only
  profiles.
- A local onboarding contract test now exists in
  `test_transform_form_response_contract.py`, plus a transform
  `--dry-run` preview path for checking a live submission before any config
  rows are written.
- Beta operations docs now cover a supervised 3-5 tester cohort, including
  explicit Twilio path choice, delivery-risk handling, tester tracking, and
  follow-up workflow.
- A real six-profile `TEST_MODE` runtime pass has now completed successfully
  against live catalogue data, with new `WATCHING` rows written for the
  `steers` and `breeding_heifers` test-derived profiles.
- A post-refactor six-profile `TEST_MODE` run completed successfully on
  14 June 2026 with `auctionsplus` as the only enabled live source:
  165 listings discovered, shared source collection working, no unexpected
  writes, and no regression in profile-matching behaviour.
- An opt-in `authorised_notice_proto` source scaffold now exists for future
  authorised email/PDF-style ingestion. It is disabled by default and expects
  local JSON sample records only when explicitly enabled.
- Local authorised-source intake tooling now exists:
  `authorized_notice_raw/` for mailbox/PDF exports,
  `transform_authorized_notices.py` for normalisation, and
  `validate_authorized_notice_samples.py` for intake checks before runtime use.
- Concrete beta rollout materials now exist:
  `docs/beta-sequence.md`,
  `docs/beta-user-guide.md`, and
  `docs/beta-feedback-process.md`.
- A first-tester operator runbook now exists in
  `docs/first-beta-launch-pack.md`.
- Test profiles `steers`, `breeding_heifers`, `breeding_cows`, and `caf`
  should remain live in `cattle_scout_config` for ongoing validation.
- The `Stockplace` prototype path is now wired into the shared source runtime
  behind `ENABLE_STOCKPLACE_SOURCE`, with parser hardening and contract tests
  in place.
- A controlled local `TEST_MODE` pass on 28 June 2026 kept AuctionsPlus stable
  and produced zero accepted `Stockplace` rows from the current live index,
  which means the source is safer but not yet strong enough to count on for
  beta-user value.
- The `RMA` prototype path is now wired into the shared source runtime behind
  `ENABLE_RMA_SOURCE`, with the live parser updated to the current June 2026
  page structure.
- A controlled local `TEST_MODE` pass on 28 June 2026 kept AuctionsPlus stable
  with `RMA` enabled and produced 32 parsed RMA records from the current live
  page, but many remain sparse `WATCHING`-grade sale notices with missing
  location/state unless the card itself exposes those fields.
- Alert/dedup safety was hardened on 4 July 2026: dedup log read failures now
  abort the run, successful alert rows are flushed per user, failed Twilio sends
  are not marked alerted, and `TEST_MODE` writes `TEST_ALERTED` /
  `TEST_WATCHING` rows so validation history does not suppress live sends.
- CI now runs offline unit discovery (`python -m unittest discover -p
  "test_*.py"`) before the scheduled scraper. Live Google Sheets and Twilio
  checks have been renamed to `smoke_sheets.py` and `smoke_twilio.py` so they
  are run deliberately, not by unit discovery.

## Active Beta Blockers

- `TEST_MODE` defaults to `True`; production/live beta sends require explicitly
  setting `TEST_MODE=FALSE` in the runtime environment.
- No first trusted tester has been chosen and onboarded yet.
- The first live WhatsApp beta send has not been supervised end to end yet.
- Beta guide and feedback process drafts now exist, but they still need to be
  exercised with a real tester.

## Immediate Next Actions

1. Use `docs/beta-sequence.md` as the operating order:
   test with real users before source outreach, then tighten for demo
   readiness, then start source-permission conversations.
2. Choose the first trusted beta tester and onboard them end to end via the
   live form and current config pipeline.
3. Use `docs/first-beta-launch-pack.md` to send the outreach, onboarding, and
   launch-day messages in a controlled order.
4. Set `TEST_MODE=FALSE` only when that first live beta send is being started
   intentionally.
5. Capture feedback through the process in `docs/beta-feedback-process.md`.
6. Create the dedicated Google Workspace alert mailbox and collect the first
   real authorised-source samples in parallel, but do not treat source outreach
   as the main priority before beta evidence exists.
7. Keep `Stockplace` behind its feature gate until live sampling produces
   useful `WATCHING` rows at acceptable noise levels.
8. Treat `RMA`, authorised email intake, and platform outreach candidates such
   as `StockLive` as the next practical expansion lane for a two-week beta
   value push.
9. Keep `RMA` gated until we decide whether its current sparse sale-notice
   coverage is good enough for beta `WATCHING` rows or needs another
   enrichment/filtering pass first.

## Locked Working Decisions

- AuctionsPlus is the first active source.
- Additional sources must enter through the shared source boundary and stay
  permission-first.
- Silent misses are worse than false positives for buy-side alerts, so unknown
  fields should not suppress matches unnecessarily.
- Multi-profile-per-user architecture is deferred post-beta; duplicate form
  submissions are the temporary workaround.
- Female breeding stock semantics are now explicit:
  heifers = females that have not calved, cows = females that have calved,
  CAF = cows with calves at foot only.
- Blank commercial sex/stage answers plus female-breeding selections are
  treated as a non-commercial-only profile.
- Paid-user legal/compliance work is deferred until beta evidence is collected,
  but unpaid beta still needs controlled rollout discipline.

## Read These When Needed

- `docs/schema.md`: Sheets/config/onboarding changes.
- `docs/auctionsplus-selector-reference.md`: scraper/parser changes.
- `docs/prelaunch-checklist.md`: beta launch, alerts, legal, and compliance.
- `docs/status.md`: full historical validation and decision chronology.
