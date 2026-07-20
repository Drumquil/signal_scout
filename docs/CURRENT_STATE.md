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
- First self-serve authorised-source subscriptions were registered on
  19 July 2026 for Nutrien livestock/sales pages, Donovan mailing list,
  Ramsey & Bulmer livestock sales, and APL Casino livestock updates. The
  working register is now
  `references/operations/authorized_subscription_register.csv`; all four are
  waiting on first real source emails before parser or runtime work.
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
- A supervised live sandbox run on 6 July 2026 completed successfully with six
  dummy profiles: AuctionsPlus-only, 164 listings scraped, 15 `WATCHING` rows
  written, 0 `ALERTED`, and no observed Twilio send failures.
- Those six dummy/self-test profiles (`tom_steers`, `tomcows`, `steers`,
  `breeding_heifers`, `breeding_cows`, `caf`) were deactivated in
  `cattle_scout_config` on 19 July 2026 before first real tester onboarding.
- First real tester onboarding started on 19 July 2026 with Tom as a supervised
  sandbox tester for a Brangus breeding-cow / cow-calf-unit buying brief:
  Northern Rivers NSW focus, 1-30 head, age range 36-72 months, polled
  required, Brangus / Ultrablack and primary crosses. Live form row 6 was
  previewed with `transform_form_response.py --dry-run` and written to
  `cattle_scout_config` as `tom_brangus_cows_and_calves`.
- Tom's first tester profile is intentionally strict: cows and cow-calf units
  only, not PTIC/joined heifers. Location filtering is moving to the
  AuctionsPlus-style town-plus-radius model (`target_location_town` +
  `target_radius_km`) rather than selecting individual saleyards directly.
- Twilio sandbox delivery was confirmed on 19 July 2026 after the first tester
  rejoined the sandbox and received a retry smoke message. Sandbox remains
  acceptable for this one supervised tester, but a registered WhatsApp sender
  is still recommended before expanding to a 3-5 tester cohort.
- A supervised first-tester `TEST_MODE=TRUE` run completed on 19 July 2026 with
  only `tom_brangus_cows_and_calves` active and `auctionsplus` as the only
  enabled source: 164 listings discovered and scraped, 0 `TEST_WATCHING`, 0
  `TEST_ALERTED`, and no runtime errors. The run showed the current brief is
  narrow enough that no current AuctionsPlus listing matched.
- Runtime performance and cadence work was implemented on 20 July 2026:
  AuctionsPlus detail scraping now has opt-in local caching, env-configurable
  worker concurrency, staggered request starts, 15-minute pending-catalogue
  cache TTLs, and 3-hour released-listing cache TTLs; GitHub Actions now
  supports manual post-form runs with runtime inputs (`TARGET_USER_ID`,
  `FORCE_REFRESH`, pages, workers, and delay), overlap prevention, timeout
  control, and heavier Thu/Fri/Sat daylight cadence. This still needs one supervised
  `TEST_MODE=TRUE` validation run before relying on it for beta operations.
- Stud/genetics parsing was tightened on 20 July 2026 so female-sale listings
  are no longer flattened into bulls. `listing_type="stud"` can now flow
  through `breeding_female`, `cow_calf_unit`, or `bull` category gates, with
  known breeds still checked against buyer breed preferences.
- A website/form UX plan now exists in `docs/website-form-ux-plan.md`, but
  implementation is intentionally behind runtime validation.
- The valuation model remains intentionally deferred; runtime operation is
  currently acceptable with `No valuation`, but this decision should be
  revisited fortnightly during beta until model work is deliberately scheduled.

## Active Beta Blockers

- `TEST_MODE` defaults to `True`; production/live beta sends require explicitly
  setting `TEST_MODE=FALSE` in the runtime environment.
- First trusted tester has been chosen, live form submission has been written
  to config, WhatsApp sandbox delivery is confirmed, and a supervised
  `TEST_MODE=TRUE` run completed cleanly; the first intentional live
  `TEST_MODE=FALSE` alert run still has not been supervised end to end.
- No external beta tester has yet been supervised through the full first live
  WhatsApp flow end to end.
- Beta guide and feedback process drafts now exist, but they still need to be
  exercised with a real tester.
- New scrape cache/concurrency and stud-female classification changes need a
  supervised `TEST_MODE=TRUE` run before the first intentional live send.

## Immediate Next Actions

1. Use `docs/beta-sequence.md` as the operating order:
   test with real users before source outreach, then tighten for demo
   readiness, then start source-permission conversations.
2. Run one supervised `TEST_MODE=TRUE` validation pass with the new
   cache/concurrency path enabled (`SCRAPE_WORKERS=4`, `REQUEST_DELAY=1`) and
   confirm the stud/female classification output looks sane.
3. Use `docs/first-beta-launch-pack.md` to send the outreach, onboarding, and
   launch-day messages in a controlled order.
4. Set `TEST_MODE=FALSE` only when that first live beta send is being started
   intentionally.
5. Capture feedback through the process in `docs/beta-feedback-process.md`.
6. Keep the authorised-source mailbox organised by source label/folder and
   capture the first real Nutrien, Donovan, Ramsey & Bulmer, and APL Casino
   emails into `authorized_notice_raw/` for normalisation; do not treat source
   outreach as the main priority before beta evidence exists.
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
