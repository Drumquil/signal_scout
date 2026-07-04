# Signal Scout — Independent Code Review

**Date:** 2026-07-04
**Scope:** Full read of `cattle_scout.py`, `transform_form_response.py`, `transform_authorized_notices.py`, `source_parser_spikes.py`, `validate_multi_user_config.py`, the activate/deactivate ops scripts, all five `test_*.py` files, `.github/workflows/cattle_scout.yml`, `requirements.txt`, `.gitignore`, `.env.example`, and the active docs (`docs/CURRENT_STATE.md`, `docs/status.md`, `docs/schema.md`, `HANDOVER.md`, `README.md`). The three offline unit suites were executed (all 12 tests pass). The two live-API scripts (`test_sheets.py`, `test_twilio.py`) were read but deliberately not run. Suspected logic bugs were verified by importing the real functions and exercising them in memory — nothing in the repo was modified.

---

## Executive summary

Signal Scout is in better shape than most solo-built beta products: secrets hygiene is genuinely clean, the multi-user config design is sensible, the source-abstraction refactor is real and working, comments explain *why* (including documented parser archaeology), and the newer test files are well-constructed. The offline test suite passes.

The serious problems cluster in one place: **the alert/dedup pipeline is not failure-safe, in either direction.** A failed WhatsApp send is swallowed and the listing is still marked ALERTED (the user silently never hears about it, forever); dedup rows are only flushed to Sheets at the very end of a run, so a crash or write failure after sends means every alert repeats next run; and a failed log *read* silently returns an empty dedup map, which would re-alert the entire history in one burst. For a product whose entire promise is "trustworthy alerts," this is the part to fix before onboarding real testers.

Two more findings deserve attention before building further: **TEST_MODE runs are poisoning the production dedup log** (test runs write real ALERTED rows, so the first live run after flipping `TEST_MODE = False` will silently send nothing for anything already seen), and **class detection uses raw substring matching** — verified concretely: a listing titled "45 Weaner Steers Braidwood" is classified as a *breeding female* because "aid" appears inside "Braidwood."

Structurally, the codebase fits its stage — one big well-commented script plus operator tools is fine for a supervised 3–5 person beta — but three debts will bite as it grows: the 650-line `scrape_commercial_listing` function has zero test coverage while being the highest-risk code in the repo; eight scripts copy-paste the same Google Sheets auth boilerplate with no shared module; and the git working tree is far ahead of `master` while production (GitHub Actions) runs `master`, so what has been validated locally is not what is deployed.

Findings below are ranked. Every Critical/High item was verified against the actual code (line references given), not inferred.

---

## CRITICAL

### C1. Alert delivery and dedup state can desync in both directions

**What.** Three related failure modes in the core pipeline, all confirmed in code:

1. **Failed send is still marked ALERTED.** `send_alert` and `send_watching_alert` wrap the Twilio call in `except Exception` and only print a warning (`cattle_scout.py:2339-2340`, `2420-2421`). They return `None` unconditionally, so the caller cannot know the send failed. The main loop marks the listing ALERTED regardless (`cattle_scout.py:2561-2568`). Result: one transient Twilio error (rate limit, invalid number, expired WhatsApp session) permanently suppresses that alert for that user. The user never learns a matching lot existed. This is the exact "silent miss" the codebase's own philosophy (docstring at `cattle_scout.py:1944-1946`) says is the worst outcome.

2. **Dedup rows are buffered until the very end of the run.** Sends happen immediately inside the user loop, but `pending_log_rows` are only flushed after all users are processed (`cattle_scout.py:2575-2577`). If the process crashes mid-run — or the batch write fails after its 4 retries (`append_rows_with_retry`, `cattle_scout.py:2257-2279`, which prints a warning and returns `False`) — every alert already sent this run has no durable record. The next scheduled run re-sends all of them. With two cron runs per day, a Sheets quota problem turns into a duplicate-alert storm for every user.

3. **A failed dedup-log *read* silently resets history.** `get_log_status` catches any exception and returns `{}` (`cattle_scout.py:2120-2122`). The run then continues as if no listing has ever been alerted: every currently-live matching listing re-alerts every user in one run, and duplicate ALERTED rows are appended to the log.

**Why it matters.** The product's single job is "send exactly one trustworthy alert per matching lot." All three modes corrupt that: (1) silently loses alerts forever; (2) and (3) spam users with duplicates, which is how a beta tester decides the tool is broken. These aren't theoretical — Sheets API quota errors are the very thing `append_rows_with_retry` was built to handle, and Twilio WhatsApp sends fail routinely (24-hour session window rules, sandbox re-joins).

**What to do.**
- Make `send_alert`/`send_watching_alert` return `True`/`False`. Only mark ALERTED and append log rows when the send succeeded. On failure, either skip (it retries naturally next run) or write a distinct `SEND_FAILED` status so it's visible and retried.
- Flush log rows incrementally — per user, or per N alerts — instead of once at run end. Alternatively (and more simply): append the log row *before* sending, with a status that a successful send upgrades; failing that, at minimum flush after each user.
- Make `get_log_status` failure fatal (raise, abort the run). Running with an empty dedup map is strictly worse than not running. This is a one-line change with a large safety payoff.

---

## HIGH

### H1. TEST_MODE runs write real ALERTED rows — flipping to production will silently suppress the first live alerts

**What.** `TEST_MODE = True` is hardcoded (`cattle_scout.py:97`) and only gates the Twilio call itself (`cattle_scout.py:2332-2334`, `2413-2415`). Everything else — status map updates, `pending_log_rows`, ALERTED/WATCHING rows written to Sheets — happens identically in test mode (`cattle_scout.py:2547-2569`, no `TEST_MODE` check anywhere in `main()`). The GitHub Actions cron has been running twice daily in this mode, appending real ALERTED rows for every active user.

**Why it matters.** `docs/CURRENT_STATE.md:69` lists "`TEST_MODE` remains True" as a known blocker, so the flag itself is intentional. What is *not* documented is the interaction: on the day you flip `TEST_MODE = False` for the first supervised live send, every listing currently in the log is already marked ALERTED for every user. The first production run will very likely send **nothing**, and it won't be obvious why. Worse, if the plan is to clear the log to fix that, the analytical `cattle_scout_listings` history built during validation is entangled with the same rows. Secondary issue: going live requires a code edit + commit rather than a config change, and the constant can't be overridden per-environment.

**What to do.**
- Read the flag from the environment: `TEST_MODE = os.getenv("TEST_MODE", "TRUE").upper() == "TRUE"`. The GitHub workflow then controls production explicitly, and local runs stay safe by default.
- Write a distinct status (`TEST_ALERTED` / `TEST_WATCHING`) when in test mode, and have the dedup check treat it as "not yet alerted" for production. This preserves validation history *and* makes the flip clean.
- If you keep the current design, add an explicit step to the launch checklist: purge (or re-status) test-mode rows from `cattle_scout_log` before the first live run.

### H2. Substring class detection misclassifies listings — verified false positives

**What.** `detect_class` (`cattle_scout.py:714-759`) matches qualifiers as raw substrings. Verified by executing the real function:

- `detect_class("45 Weaner Steers Braidwood", "")` → `('aid', 'breeding_female')` — "aid" (`BREEDING_FEMALE_QUALIFIERS`, `cattle_scout.py:411-414`) matches inside "Br**aid**wood". Braidwood is a real NSW cattle town; any town/property/sire name containing "aid", "caf", or "mated" misroutes the lot.
- Pass 1's compound-lot test accepts the word fragment "and" anywhere in the title (`has_ampersand = "&" in title or "and" in title_lower`, `cattle_scout.py:738`) — so "Highl**and**", "Gr**and**", "S**and**y" all count as the "&" in "cows & calves". Combined with a calf mention, a non-cow-calf lot becomes `cow_calf_unit`.

**Why it matters.** `listing_category` drives the hard include/exclude gates in `listing_match` (`cattle_scout.py:1956-1970`). A commercial steer lot misclassified as `breeding_female` is silently invisible to every user who left `include_breeding_females` off — the majority commercial-buyer profile. This is a silent miss on real inventory, in the code path that feeds real buying decisions, and it will never show up in any log as an error.

**What to do.** Match with word boundaries: precompile the qualifier list into regexes (`r"\b" + re.escape(q) + r"\b"` — for `ai'd`/`ai'` handle the apostrophe explicitly), and require a literal `&` or the standalone word `and` (`r"\band\b"`) in Pass 1. Then add a table-driven unit test for `detect_class` covering: each qualifier, the Braidwood-style town-name traps, and cow-and-calf titles with and without "&". This is a two-hour fix with test coverage to keep it fixed.

### H3. Production runs `master`, but the validated code only exists in the working tree

**What.** GitHub Actions executes `python cattle_scout.py` from a checkout of `master` (`.github/workflows/cattle_scout.yml:35`). Meanwhile the local working tree has heavily modified, uncommitted versions of `cattle_scout.py`, `transform_form_response.py`, all docs, and ~25 entirely untracked files including every new test and the parser-spike module (`git status`: 12 modified, 30+ untracked). Recent validation runs described in `docs/CURRENT_STATE.md` (the June 28 Stockplace/RMA passes) were done against code that is not deployed.

**Why it matters.** Two code realities exist: the one you test locally and the one that runs twice a day in production. Any fix you make locally does nothing until committed — and when you eventually do commit a month of accumulated changes in one lump, you deploy a large untested delta to production in a single step. This also means a laptop failure loses the only copy of the current runtime.

**What to do.** Commit the working tree now (in reviewed chunks if needed: runtime, tests, docs, tooling), and adopt "validated = committed = deployed" as a habit. Consider having the workflow run the offline unit tests as a job step before the scrape step, so a bad commit fails loudly instead of running.

### H4. The highest-risk code has zero test coverage, and CI never runs any tests

**What.** Coverage is inverted relative to risk:

- `scrape_commercial_listing` — ~650 lines (`cattle_scout.py:906-1546`), a stack of ~20 order-dependent regex/line-scanning extractions against un-versioned third-party HTML — has **no tests at all**. Nor do `detect_class`, `detect_listing_type`, state extraction, `get_log_status`, `score_listing`, or the main-loop dedup logic.
- What *is* tested (parser spikes, notice transform, form→config contract — `test_source_parser_spikes.py`, `test_transform_authorized_notices.py`, `test_transform_form_response_contract.py`) is good quality, including a genuine end-to-end contract test through `load_config` and `listing_match`. But the contract test exercises only breeding/CAF profiles; commercial filtering gates (state, class, weight, breed, accreditations) are untested.
- The CI workflow installs deps and runs the scraper; it never runs a test (`.github/workflows/cattle_scout.yml:22-35`). There is no pytest/unittest config; suites are run by hand.

**Why it matters.** AuctionsPlus will change their markup — that's a *when*, not an *if* — and when they do, extraction degrades silently: fields come back `None`/"Unknown", soft gates stop filtering, and users get noise or nothing. Without fixture-based tests you can't tell a parser regression from a market lull. The comments in the parser show this has already happened repeatedly ("Previous parser used field-id=... — this attribute does not exist", `cattle_scout.py:1234-1235`).

**What to do.**
1. Save two or three real AuctionsPlus listing HTML pages as fixtures (the repo's `.tmp_*` capture files show this workflow already exists informally) and write golden-output tests for `scrape_commercial_listing` — assert the full returned dict.
2. Add unit tests for `detect_class` (see H2) and a table-driven test for `listing_match` covering each gate, both match and reject, for the commercial profile.
3. Add `python -m unittest discover -p "test_*.py" -k "not sheets and not twilio"` (or rename the two live scripts to not match `test_*`) as a CI step before the run.
4. Rename `test_sheets.py`/`test_twilio.py` to `smoke_sheets.py`/`smoke_twilio.py` — they are live side-effect scripts (a real Sheets write, a real WhatsApp send) and any future `unittest discover`/pytest run would execute them by accident.

---

## MEDIUM

### M1. Mandatory gates hard-reject listings the parser failed to parse — contradicting the stated soft-gate philosophy

**What.** The docstring commits to "never suppress a match because the parser missed a field" (`cattle_scout.py:1942-1946`), and weight/breed/fat/age honour that. But three mandatory gates do not:

- State: `state == "Unknown"` fails any user with `target_states` set (`cattle_scout.py:1973-1975`).
- Class: `class == "unknown"` fails any user with `target_classes` set (`cattle_scout.py:1979-1982`).
- Sale type: `sale_name == "Unknown Sale"` fails any user with `sale_types` set (`cattle_scout.py:2005-2008`).

**Why it matters.** A location-element markup change at AuctionsPlus would zero out alerts for every user with a state filter — silently, indefinitely, with each rejection logged only as a console line in a CI run nobody reads. Since state/class extraction is exactly the fragile HTML-dependent code (H4), this couples "parser drift" directly to "product goes quiet."

**What to do.** Decide per gate. If state really must be mandatory (defensible — interstate freight is real money), add a counter: if >N% of a run's listings have `state == "Unknown"`, treat it as a parser failure and alert *yourself* (a Twilio message to the operator is two lines here). Alternatively, pass unknown-state listings through with a "state unverified" marker in the alert text.

### M2. Invalid numeric config values silently disable the user's filter

**What.** `load_config` parses numeric settings with `float(value)`, and on `ValueError` stores `None` with no warning (`cattle_scout.py:496-500`). A config value of `"300kg"` or `"3-400"` (easy to produce when hand-editing the Sheet, which the ops workflow encourages) silently turns that filter off.

**Why it matters.** The user believes they have a 300 kg minimum; they get alerts for 180 kg weaners; trust erodes. Hand-edits to the config tab are part of the documented operating model, so this will happen.

**What to do.** Print a loud warning naming user, setting, and raw value on parse failure — or better, reject the user's config for the run (like the missing-`twilio_to` path at `cattle_scout.py:511-513`) so bad config is noticed at onboarding, not weeks later. Note `transform_form_response.parse_numeric` already sanitises form input; the gap is manual edits.

### M3. Age fallback regex can capture unrelated "N months" text from anywhere on the page

**What.** If the "14 - 15 Months" range pattern misses, the fallback takes the *first* `(\d+)\s*[Mm]onths?` match in the entire page text (`cattle_scout.py:1348-1351`) and uses it as both age_min and age_max. Page boilerplate routinely contains month strings (finance-widget terms, WHP wording, "6 months interest free").

**Why it matters.** A wrong age silently *rejects* listings for users with age filters (`cattle_scout.py:2062-2067`) and prints wrong ages in alerts that feed real buying decisions. I could not verify against live page text (uncertainty noted below), but the pattern is unanchored, so the risk is structural.

**What to do.** Anchor the fallback to the age section the same way fat score is anchored (`lines_after("Age", ...)`), or drop the fallback and accept `None` (age is a soft gate anyway — `None` passes through, which is the codebase's own stated preference).

### M4. `get_model_fair_value` blindly takes the last cell of column B

**What.** It reads `col_values(2)` and floats the final value (`cattle_scout.py:2286-2294`). Any trailing junk row, header, or partial write in `cattle_model_output` becomes the fair value; a non-numeric value throws inside the try and silently returns `None` — but a *numeric but wrong* value (e.g. a year, a row index) is used as-is.

**Why it matters.** The 🟢 UNDERVALUED / 🔴 OVERPRICED flag (`score_listing`, `cattle_scout.py:2297-2307`) is exactly the kind of output a buyer acts on. A stale or wrong anchor mislabels every priced listing in the run.

**What to do.** Add a header/shape check (expect a date in column A of the same row, sanity-bound the value to a plausible c/kg range, e.g. 100–2000), and log the value + its timestamp in the run output so a bad anchor is visible.

### M5. `extract_money_cents` fallback ternary is a no-op — verified

**What.** `source_parser_spikes.py:80`: `return None, amount if amount >= 100 else (amount, None)[0]` parses as `(None, amount)` in *both* branches — `(amount, None)[0]` is just `amount`. Verified: `extract_money_cents("$4.50")` → `(None, 4.5)`, i.e. $4.50/kg with no unit marker becomes **price_per_head = $4.50**. The magnitude heuristic the author intended is dead code.

**Why it matters.** Stockplace/RMA sources are feature-flagged off, so this is dormant — but it's wired into the runtime (`cattle_scout.py:1775`, `1811`) and will corrupt price data the day a source is enabled. It's also invisible: the tests only cover inputs with explicit "per kg" markers.

**What to do.** Rewrite explicitly: `if amount < 100: return amount, None` (c/kg) `else: return None, amount` ($/head) — or return `(None, None)` when the unit is unknown. Add the ambiguous-input cases to `test_source_parser_spikes.py`.

### M6. Eight scripts copy-paste the Sheets connection; no shared module

**What.** `cattle_scout.py:2449-2455`, `transform_form_response.py:196-210`, `validate_multi_user_config.py:32-40`, `activate_batch_validation_users.py:27-34`, the deactivate/inspect scripts, and `test_sheets.py` each re-implement scope + `ServiceAccountCredentials` + `gspread.authorize` + spreadsheet/tab names. The config-block row-parsing logic is also duplicated between `load_config` and `get_user_blocks` (twice).

**Why it matters.** Migrating off `oauth2client` (M7), renaming the spreadsheet, or changing the config schema means touching eight files, and the copies are already drifting (the ops scripts parse `active` as a string compare, the runtime as a bool field). Six months from now, someone will update one and not the others.

**What to do.** Extract a small `sheets_client.py` (connect, open tabs, read config blocks) and import it everywhere. This is the single highest-leverage refactor in the repo and can be done incrementally, script by script.

### M7. Deprecated auth library and unpinned dependencies

**What.** `oauth2client` was deprecated in 2017; the maintained path is `google-auth` (gspread supports it natively — `gspread.service_account(filename=...)` removes the boilerplate entirely). `requirements.txt` pins nothing, so every CI run installs whatever is latest; a breaking release of gspread/twilio/bs4 breaks production with no code change on your side.

**What to do.** Pin versions (`pip freeze` from the known-good venv into `requirements.txt`), and schedule the `oauth2client` → `google-auth` migration alongside M6 (it's ~5 lines once the connection code is shared).

### M8. Duplicate onboarding appends a second config block with confusing merge semantics

**What.** `transform_form_response.py:637-642` warns on an existing user_id but offers to APPEND a second row-block. `load_config` merges blocks per-setting in row order — later rows overwrite earlier ones key by key (`cattle_scout.py:502`). A re-submitted form that omits a setting present in the old block leaves the *old* value live: the resulting effective config is a row-order-dependent blend of two submissions that no one ever reviewed as a whole.

**Why it matters.** "Re-do your form and I'll re-run the transform" is the natural support path for a beta tester who wants to change criteria — and it produces exactly this blend.

**What to do.** On duplicate, offer to delete/replace the existing block instead of appending (the block's row range is easy to find since blocks are contiguous), or write the new block and explicitly mark the old rows inactive. At minimum, print the *effective merged* config after appending.

### M9. Documentation drift: version numbers and architecture claims disagree

**What.** Code self-identifies v2.3 throughout (`cattle_scout.py:18,32,169`); `docs/CURRENT_STATE.md:9` and `docs/status.md` say the runtime is v2.4. `docs/runtime-refactor-spec.md` marks the source abstraction "Proposed v0.1" while `CURRENT_STATE.md:17` says it is "now in place" (the code confirms it is in place). `README.md`/`docs/status.md` frame the product as AuctionsPlus-only while Stockplace/RMA paths now exist. Deleted docs (`Cattle_Scout_Schema_Reference_v2_1.md`, `docs/handover-chat14-to-chat15.md`) are still referenced from older material.

**Why it matters.** The docs are this project's main onboarding asset (and they're good). But an incoming collaborator — or a future agent session — will trust whichever doc they read first, and half of them are wrong about the current state. Version strings that don't match reality are worse than no version strings.

**What to do.** One pass: pick the real version (the docs' "v2.4" or the code's "v2.3"), update both sides, mark `runtime-refactor-spec.md` as Implemented, and stamp each doc with "accurate as of <date>". Keep `CURRENT_STATE.md` as the single source of truth and make other docs point at it rather than restating status.

### M10. Twilio WhatsApp delivery constraints are unaddressed in code (uncertain severity)

**What.** Business-initiated WhatsApp messages outside a 24-hour customer session require pre-approved templates on the Twilio WhatsApp Business API; the sandbox requires each recipient to have joined and re-join periodically. `send_alert` sends freeform bodies (`cattle_scout.py:2417-2418`) with no handling for either constraint. The beta docs mention an "explicit Twilio path choice," so this is likely known operationally — **I could not verify which Twilio path (sandbox vs. registered sender) is in use, so I'm flagging the code-level gap rather than asserting breakage.**

**Why it matters.** If beta testers are on the sandbox and their join lapses, sends fail — and per C1, those failures are currently silent *and* marked ALERTED. The two issues compound.

**What to do.** Resolve C1 first (failed sends must be visible/retryable). Then confirm the sender path: for a registered WhatsApp sender, freeform alerts to users who haven't messaged back within 24h will need a template.

---

## LOW

### L1. Repo cruft

- Five `.tmp_*.txt` scraper dumps (up to ~95 KB) at the root, *not* covered by `.gitignore` (it only ignores `tmp_icm_extract*` patterns) — one accidental `git add .` commits them.
- `codex-python-app-scaffold/`, `codex-starter-scaffold/` are generic templates with placeholder text; `files.zip`, four `.docx` references, `__pycache__/` with mixed 3.12/3.14 bytecode.
- `.venv/` is untracked but not named in the repo `.gitignore` — it's excluded only by a global/info ignore, which won't protect a fresh clone contributor.
- `cattle_scout_config.csv` is a legacy single-user config whose schema differs from the live multi-user one; it reads as current but isn't loaded by anything.

**Fix:** add `.tmp_*`, `.venv/` to `.gitignore`; move the scaffolds/docx/zip under `archive/` (or delete); delete or clearly rename the legacy CSV.

### L2. Small correctness/cosmetic items

- `TWILIO_TO` is loaded (`cattle_scout.py:70`) and injected by CI (`cattle_scout.yml:33`) but never used — per-user `twilio_to` replaced it. Delete both to avoid implying it does something.
- `build_log_listing_row` renders `num_head=None` as the string `"None"` (`cattle_scout.py:2149`).
- `datetime.now()` on GitHub runners is UTC; `logged_at` timestamps mix UTC (CI) and local time (manual runs) with no marker (`cattle_scout.py:2160,2210`). Use `datetime.now(timezone.utc)` or pin `TZ: Australia/Sydney` in the workflow.
- `is_EU = "EU" in accred_text` is a substring test on the accreditation block (`cattle_scout.py:1426`) — any block word containing "EU" false-positives; `" NE "` (`:1427`) misses NE at line boundaries. Use word-boundary regexes as done for WHP.
- The accreditation block scan (`cattle_scout.py:1413-1423`) never stops if none of the listed section headers follow — the "block" then absorbs the rest of the page. Bound it (e.g. max 15 lines).
- Dead code: the final `if` in `validate_transformed_config_rows` is a no-op `pass` (`transform_form_response.py:567-569`); `inspect_listing.py` appears superseded.
- Config naming inconsistency: `min_fat_score` vs `fat_score_max`, `min_weight_kg` vs `max_weight_range_kg` — pick one ordering convention when next touching the schema.
- Stockplace parser has no within-page dedup (RMA's has `seen_keys`, `source_parser_spikes.py:694`); nested `div` cards can yield duplicate records. The runtime's `seen_urls` (`cattle_scout.py:1879`) currently masks this.
- Workflow writes the JSON secret via `echo '${{ secrets... }}'` (`cattle_scout.yml:26`) — breaks if the secret ever contains a single quote. Prefer an env var + `printf '%s'`.

### L3. Print-based logging

All observability is `print()` to CI stdout. Fine for now, but there is no persistent record of *why* listings were rejected per user (the most common support question: "why didn't I get alerted for lot X?"). When that question arrives, consider writing rejection reasons for near-miss listings to a Sheet tab or artifact rather than adopting a logging framework wholesale.

---

## Assessment by review dimension

**Design & architecture.** The shape — one runtime script, Sheets as both config store and datastore, operator scripts around it, GitHub Actions cron — is *right* for a supervised beta; do not add a database or web layer yet. The source-definition registry (`get_source_definitions`, `cattle_scout.py:347-396`) is a genuinely good boundary: new sources are additive and feature-flagged, and `normalise_shared_listing` gives one canonical shape. Over-built for the stage: the ICM scaffolding (`_config/`, `stages/`, `setup/`, `shared/`, two `codex-*-scaffold` dirs) is a lot of meta-process for a repo whose product code has no CI tests; the ~70-field shared listing schema carries many always-None fields. Under-built: failure handling in the alert path (C1) and shared library code (M6). The 2,590-line single file is at its limit — the planned split (spec exists) should extract *parsers* and *sheets access* first, since those change most.

**Correctness.** The filter logic in `listing_match` is careful and mostly right; the soft-gate philosophy is thoughtfully applied except where noted (M1). The confirmed defects are C1 (pipeline failure handling), H2 (substring classification), M5 (dead ternary), with M3/M4 as probable-but-unverified-against-live-data. The parser itself is unavoidably fragile regex-over-HTML — the mitigation is fixtures and drift detection (H4, M1), not cleverness.

**Complexity & maintainability.** Could someone change this safely in six months? Mostly yes *within* a function — naming is clear, comments are unusually good and explain historical traps. Mostly no *across* the system: the alert/dedup/log invariants (what statuses exist, when rows are written, what `TEST_MODE` does and doesn't gate) live only in the code and this review. `listing_match` also assumes a fully-normalised listing dict (direct `listing[...]` indexing) — safe today because everything passes through `normalise_shared_listing`, but a KeyError trap for anyone who calls it directly. Document the status lifecycle (WATCHING → ALERTED, who writes what when) in `docs/schema.md`.

**Tests.** Covered: parser spikes (offline, good fixtures), notice transform (proper tempdir isolation), form→config→match contract (the best test in the repo). Missing: the AuctionsPlus parser, class detection, commercial-profile filter gates, dedup semantics — i.e. the logic that actually matters (H4). Two live-API scripts masquerade as tests (H4.4). Nothing runs in CI.

**Security.** Clean where it counts: no secrets tracked (verified via git index), `.env`/creds properly ignored, CI secrets injected at runtime, no credentials in source. Sheets writes use `value_input_option="RAW"`, which avoids formula-injection from scraped titles. Residual notes: scraped HTML is untrusted input but is only parsed, never executed or eval'd; beta testers' phone numbers live in the config Sheet (fine, but treat that Sheet's sharing settings as the security boundary); rotate the Twilio token if it was ever pasted into a chat during development.

**Naming, comments, documentation.** Above average. Comments explain intent and record why previous approaches failed — genuinely valuable for parser code. The docs corpus is extensive; its problem is drift (M9), not absence. Onboarding a new person from `README.md` → `CURRENT_STATE.md` → code would mostly work today.

**Top technical debt / takeover risks, ranked:** (1) alert-pipeline failure handling (C1) — the one that damages users; (2) untested 650-line parser against a changing website (H4) — the one that *will* break; (3) uncommitted working tree vs deployed master (H3) — the one that loses work; (4) TEST_MODE flip landmine (H1) — the one that ruins launch day; (5) copy-paste Sheets access (M6) — the one that makes every future change cost 8×.

---

## What I did not verify (honest uncertainty)

- **Live AuctionsPlus HTML.** All parser findings are from code reading plus in-memory execution of the functions; I did not fetch live pages. Claims marked "confirmed" in the code's own comments (field layouts, line sequences) were taken at face value.
- **The actual Google Sheet.** Tab schemas, existing log contents (including how many TEST-mode ALERTED rows exist), and the model tab's shape were not inspected.
- **Twilio account configuration** (sandbox vs. registered sender) — M10 severity depends on it.
- **M3 (age regex)** is a structural risk I could not confirm fires on real page text.
- The two live-API scripts and any network path were deliberately not executed.

## Test run record

`python -m unittest test_source_parser_spikes test_transform_authorized_notices test_transform_form_response_contract` (repo venv, Python 3.12): **12 tests, all pass**, ~0.2 s.
