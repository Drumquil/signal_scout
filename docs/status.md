# Signal Scout â€” Project State Document
**Drumquil Signal | Version: 2.3 | Date: 30 May 2026 | Status: Phase 1 Active â€” Stage 2 Validated (local)**

---

## 1. Project Purpose & Scope

**Signal Scout** (formerly Cattle Scout) is an automated monitoring tool that scrapes publicly available cattle sale listings across multiple Australian platforms, filters them against user-defined buying criteria, and delivers WhatsApp alerts when matching listings appear before the auction.

**Signal Model** (formerly Cattle Model / Drumquil Signal Cattle Model) is the companion price prediction tool. Build deferred behind Scout beta stabilisation.

**Product rename status:** Signal Scout / Signal Model are the locked product names. Rename pass across code, Sheets, and documents is deliberately deferred until beta is stable. A dedicated rename task exists in the backlog.

**Strategic position:** Platform aggregation plus an independent fair value signal layer â€” neither exists together in the Australian market.

**Commercial entity:** Drumquil Signal (ABN registered). Domain: drumquilsignal.com. Google Workspace active: tom@drumquilsignal.com.

---

## 2. Completed Setup â€” Chats 1â€“14

| Item | Status |
|---|---|
| Python 3.14, VS Code, required libraries installed | Done |
| Twilio sandbox active, WhatsApp confirmed, credentials rotated | Done |
| Google Cloud project, service account, JSON key rotated | Done |
| Google Sheet drumquil_scout with 4 tabs (log, listings, config, model_output) | Done |
| AuctionsPlus scraping confirmed â€” 164+ listings, 5 pages | Done |
| Two-stage alert system implemented and validated | Done |
| v2.3 â€” multi-user config, per-user dedup, twilio_to per user | Done |
| v2.3 validated locally â€” 165 listings, 5 WATCHING, Sheet writes confirmed | Done |
| v2.3 committed and pushed â€” commit 9e713d1 | Done |
| GitHub Actions cron confirmed firing (scheduling variance ~3hr normal on free tier) | Done |
| **Chat 11 â€” Beta intake form and legal review** | |
| Signal Scout Google Form spec completed (revised) | Done |
| `build_signal_scout_form.gs` v1.0 written | Done |
| AuctionsPlus User Agreement reviewed â€” legal risk identified | Done |
| Pre-Launch Checklist v1.0 created â€” 10 hard gates identified | Done |
| **Chat 12 â€” Form redesign, transform script, architecture decisions** | |
| Stock category taxonomy confirmed against AuctionsPlus Assessment Manual 2024 | Done |
| Form redesigned: commercial class blob â†’ Sex axis + Stage axis (two questions) | Done |
| Form redesigned: "Mob size" â†’ "Number of Head" section | Done |
| Form redesigned: Age section made optional with gateway question | Done |
| Form redesigned: Condition (fat score) â€” required=false, help text updated | Done |
| Form redesigned: Accreditations â€” all required=false | Done |
| Form redesigned: help text throughout updated | Done |
| `build_signal_scout_form_v2.gs` written â€” new form created and submitted (Tom) | Done |
| New form headers confirmed against transform script column mapping | Done |
| `transform_form_response.py` v1.0 written | Done |
| Multiple-profile-per-user architecture decision made (see Section 6a) | Done |
| Alert deactivation design confirmed for beta (manual by Tom) | Done |
| **Chat 13 â€” Onboarding pipeline validated, WhatsApp normalisation** | |
| `transform_form_response.py` v1.2 â€” WhatsApp number normalisation added | Done |
| Onboarding pipeline validated end-to-end â€” 25 config rows written for `tom_steers` | Done |
| `tom` dev user block deleted from config Sheet | Done |
| **Chat 14 â€” Stage 1 validated, target_sex filter implemented** | |
| Stage 1 (WATCHING) output validated on live AuctionsPlus â€” 24 May 2026 | Done |
| `target_sex` filter implemented in `cattle_scout_v2_4.py` | Done |
| Beta/legal sequencing decisions made â€” see Section 10 | Done |

---

## 3. Validation Run Log

| Version | Date | Trigger | Listings | Alerts | Notes |
|---|---|---|---|---|---|
| v1.7 | 18 May 2026 | Local | 169 | 7 WATCHING | Zero Unknown states. Zero credential errors. |
| v1.9 | 20 May 2026 | Local | 166 | 1 ALERTED | Per-gate rejection logging confirmed. |
| v2.1 | 21 May 2026 | Local | 167 | 9 ALERTED | All new parser fields resolving on live catalogue. |
| v2.2 | 22 May 2026 | Local | 164 | 4 WATCHING | cattle_scout_listings tab correct. |
| v2.2 | 23 May 2026 | GitHub Actions (manual) | ~164 | 1 WATCHING | First cloud run. End-to-end confirmed. Sheet write confirmed. |
| v2.3 | 24 May 2026 | Local | 165 | 5 WATCHING | Multi-user config working. 1 active user (tom). Sheet writes confirmed. |
| v2.3 | 24 May 2026 | GitHub Actions (scheduled) | â€” | â€” | Cron confirmed firing. ~3hr delay on free tier â€” normal. |
| v2.3 | 24 May 2026 | Local (Stage 1 validation) | 166 | 0 | All rejections correct. No NSW steer mobs â‰¤15 head in catalogue. |
| v2.4 | 24 May 2026 | Local (target_sex + max_head=50) | 169 | 1 WATCHING | target_sex filter confirmed working. First WATCHING alert for real NSW steer mob: 27 Weaned Steers, CURRABUBULA. |
| v2.4 | 29 May 2026 | Local TEST_MODE (Steer-Heifer category + widened criteria) | 168 | 22 ALERTED | Stage 2 ALERT path confirmed. Search URL changed to `category=Steer-Heifer`; `max_head=130`, `max_weight_range_kg=150`. |
| v2.4 | 29 May 2026 | Controlled live WhatsApp send | 1 selected alert | 1 delivered | Twilio sandbox rejoined, one real alert for `32 Weaned Steers` received by Tom. Source `TEST_MODE` remained `True`; send used one-off process only. |
| v2.4 | 30 May 2026 | Local TEST_MODE (post-push validation) | 160 | 0 | Runtime path healthy; `category=Steer-Heifer`; 1 active user only (`tom_steers`), so multi-user validation remains open. |

---

## 4. GitHub Repository â€” Current State

| Item | Value |
|---|---|
| Repo URL | https://github.com/Drumquil/signal_scout |
| Visibility | Private |
| Branch | master |
| Latest v2.4 runtime commit pushed to GitHub | fc7bb1a - "Stabilize v2.4 beta validation path" |
| Runtime code status | GitHub Actions now runs v2.4 runtime code from master. |
| Local working state | Runtime v2.4 pushed 30 May 2026. Active docs added to repo; reference imports still local. |
| Workflow file | .github/workflows/cattle_scout.yml |
| Cron schedule | 21:00 UTC (7am AEST) and 03:00 UTC (1pm AEST) daily |
| Manual trigger | Available via Actions tab â†’ Run workflow |
| Secrets configured | TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, GOOGLE_SHEETS_CREDS |
| TEST_MODE | True â€” no live WhatsApp messages until first beta tester onboarded |

**Files in repo (current):**
- `cattle_scout.py` - main script (GitHub origin now includes v2.4 validation changes)
- `inspect_listing.py` â€” AuctionsPlus diagnostic tool
- `test_sheets.py` â€” Google Sheets connection test
- `test_twilio.py` â€” Twilio connection test
- `Cattle_Scout_Schema_Reference_v2_1.md` â€” field schema reference
- `transform_form_response.py` â€” onboarding transform script v1.2 (writes config row-blocks)
- `requirements.txt` â€” Python dependencies
- `.env.example` â€” credential template
- `.gitignore` â€” excludes .env, google_credentials.json, CSV, zip, superseded docs
- `.github/workflows/cattle_scout.yml` â€” GitHub Actions workflow

**Files NOT in repo (local only or project docs):**
- `build_signal_scout_form_v2.gs` â€” Google Apps Script; lives in Apps Script project, not repo

---

## 5. Two-Stage Alert Architecture (Locked)

**Stage 1 â€” WATCHING** (`catalogue_pending = True`): pre-catalogue criteria pass. Gates: listing_type, active, category, region/state, class, sex, head count. Sends lightweight WhatsApp alert.

**Stage 2 â€” ALERT** (`catalogue_pending = False`): full criteria confirmed. Additional gates: weight (soft), mob evenness (soft), breed (soft), fat score (soft), age (soft), accreditations, HGP_free, polled, quiet, lifetime_traceable. Sends full alert with all parsed fields.

**Soft gate principle:** if a field is None or Unknown, the gate is skipped. Never suppress a match because the parser missed a field. Silent misses are categorically worse than false positives for a buy-side tool.

**`sale_types` filter:** Deprecated â€” to be removed from script, config, and Sheet in a dedicated pass. Region-based filtering replaces it.

---

## 6. Multi-User Architecture (Locked â€” implemented v2.3)

**Config tab schema:** Row-block-per-user. Column A = user_id, Column B = setting, Column C = value. Row 1 = header (skipped). Each user occupies a contiguous block of rows. Adding a user = appending a new block.

**Required fields per user:** `active` (TRUE/FALSE), `twilio_to` (WhatsApp number). Users missing either are skipped at load time with a printed warning.

**Dedup key:** `(url, user_id)` â€” a listing that alerted User 1 will still alert User 2 if they match criteria.

**twilio_to:** Lives in config Sheet per user. Not in .env or GitHub Secrets.

**Main loop:** Scrapes URLs once. Evaluates each URL against every active user's config independently. Per-user and total counters in run summary.

### 6a. Multiple Filter Profiles Per User â€” DEFERRED (decided Chat 12)

**Problem:** A user who wants alerts for two different cattle types (e.g. steers AND PTIC heifers) cannot currently have two independent filter profiles running simultaneously.

**Decision:** Defer full multi-profile support to post-beta. Implement as Option A when time permits.

**Option A (target architecture â€” build post-beta):** Add `profile_id` as a fourth column to the config schema: `user_id | profile_id | setting | value`. Requires changes to `load_config()`, the main loop evaluator, and `transform_form_response.py`.

**Interim workaround for beta (Option C):** Users who need two profiles submit the form twice using slightly different names â€” generating separate `user_id` blocks, both pointing to the same `twilio_to` number.

**âš ï¸ BACKLOG ITEM â€” POST-BETA:** Implement Option A multi-profile architecture.

### 6b. Alert Deactivation â€” Beta Design (decided Chat 12)

For beta, alert deactivation is manual: the user WhatsApps Tom, Tom sets `active = FALSE` in the config Sheet for that user_id block. No code required.

---

## 7. `target_sex` Filter â€” Implemented v2.4

**Sex detection logic** (in `scrape_commercial_listing()`):
- `detected_class == "steer"` â†’ `sex = "steer"`
- `detected_class == "heifer"` â†’ `sex = "heifer"`
- Title contains "mixed sex" / "mixed sexes" â†’ `sex = "mixed"`
- Title regex `\bsteers?\b` â†’ `sex = "steer"`
- Title regex `\bheifers?\b` â†’ `sex = "heifer"`
- No match â†’ `sex = None` (soft â€” filter passes through)

**Filter gate** (in `listing_match()`): applied after class filter. Only fires when `target_sex` is `"steer"` or `"heifer"`. Skipped when `"either"`, blank, or `sex is None`.

**Rejection message format:** `sex='heifer' != target_sex='steer'`

**Validated 24 May 2026:** Two NSW heifer mobs correctly rejected in live run.

---

## 8. `target_sex` in Config Sheet

`target_sex` is written by `transform_form_response.py` as a plain string (`steer`, `heifer`, `either`). It falls through `load_config()`'s else branch and is stored as a string â€” correct, no type registration change needed.

---

## 9. Onboarding Pipeline â€” Current State

| Component | Version | Status |
|---|---|---|
| Google Form | v2.0 | Live â€” `build_signal_scout_form_v2.gs` |
| Response Sheet | `Signal Scout Responses` â†’ tab `Form responses 1` | Active |
| Transform script | `transform_form_response.py` v1.2 | Validated â€” WhatsApp normalisation included |
| Config Sheet | `cattle_scout_config` tab in `drumquil_scout` | 1 active user: `tom_steers` |

**Active beta users:** `tom_steers` (25 config rows, validated end-to-end 24 May 2026)

---

## 10. Beta & Legal Sequencing (decided Chat 14)

| Gate | Trigger | Status |
|---|---|---|
| AuctionsPlus consent | Before **paid** users. Unpaid beta may proceed. | â¬œ |
| Terms of Use + Privacy Policy | After beta complete + metrics collected. | â¬œ |
| Lawyer review | Same as above. | â¬œ |

**Rationale:** Need beta evidence to confirm tool viability before investing in legal and partnership conversations. Unpaid beta with known users (DPIRD/extension network) is low-risk. Up to 20 users across multiple beta rounds is acceptable before formalising. AuctionsPlus consent remains a hard gate before any paid user.

---

## 11. Pre-Launch Checklist â€” Gate Status

**Hard Gates (ðŸ”´ â€” no paying users without these):**
- L1: AuctionsPlus written consent âŒ (hard gate before paid users only â€” unpaid beta may proceed)
- L2: The Herd Online ToS review âŒ
- L3: ToS review for each additional platform âŒ
- L4: Terms of Use drafted and live âŒ (after beta + metrics)
- L5: Privacy Policy drafted and live âŒ (after beta + metrics)
- L6: Lawyer review of ToU and Privacy Policy âŒ (after beta + metrics)
- L7: Signal Model legal framing confirmed âŒ
- T7: 52-week Signal Model backtesting complete âŒ
- T8: Brier score log implemented âŒ
- T9: Confidence-tiered output format implemented âŒ
- C5: AuctionsPlus partnership/consent formalised âŒ

**Beta Gates (ðŸŸ¡ â€” no free testers without these):**
- T1: Stage 1 (WATCHING) path validated on live catalogue âœ… (24 May 2026)
- T2: Stage 2 ALERT path validated on live catalogue âœ… (29 May 2026 â€” local validation run)
- T3: TEST_MODE switched to False âŒ
- T4: Breed detection risk confirmed non-blocking âœ… (soft gate; Unknown passes through)
- T5: Location parsing validated on live catalogue âœ… (SYD timezone marker ignored; Location field used)
- T6: Multi-user loop validated with 2+ active users âŒ
- P1: Signal Scout form built and live âœ…
- P2: Config transform script built and tested âœ…
- P3: First beta tester onboarded end-to-end âŒ
- P5: 1-page user guide written âŒ
- P6: Beta feedback channel established âŒ

---

## 12. Known Issues â€” Updated 30 May 2026

| # | Issue | Priority | Notes |
|---|---|---|---|
| 1 | TEST_MODE = True | Beta blocker | Stage 2 is validated (29 May). Flip to False only when ready to start real beta sends. |
| 2 | Multi-user loop not validated with 2+ active users | Beta blocker | Requires onboarding at least one real beta tester and confirming per-user dedup + per-user twilio_to works in the same run. |
| 3 | First beta tester not onboarded end-to-end | Beta blocker | Needs: form submission â†’ transform script run â†’ config rows appended â†’ TEST_MODE off â†’ first live run. |
| 4 | 1-page beta user guide not written | Beta gate | Needed before onboarding to set expectations and reduce support load. |
| 5 | Beta feedback channel not established | Beta gate | WhatsApp group or equivalent + structured feedback intake. |
| 6 | Incident response runbook not finalised | Beta gate | Draft exists in cybersecurity reference; needs final review and a short operational checklist. |
| 7 | AuctionsPlus consent not obtained | Hard gate before paid users | Unpaid beta may proceed (known network, limited user count). |
| 8 | `sale_types` filter still in script | Low | Remove in dedicated pass - deprecated. |
| 9 | Terms of Use and Privacy Policy not written | Hard gate (paid users) | After beta + metrics. |
| 10 | Multi-profile per user (Option A) not built | Post-beta | Option C workaround for beta. |

---

## 13. Next Tasks â€” Sequenced

| Priority | Task | Notes |
|---|---|---|
| **1** | Onboard first beta tester via form | Current response Sheet still only contains `tom_steers`; next real tester must submit the form first. |
| **2** | Append first tester config block with `transform_form_response.py` | Tab-name bug fixed 30 May 2026; dry run now reaches the response Sheet and blocks duplicate `tom_steers`. |
| **3** | Switch TEST_MODE to False + start beta sends | After explicit approval + first beta tester opted-in. |
| **4** | Validate 2+ active users in one run | Confirms per-user dedup, per-user `twilio_to`, and full end-to-end reliability. |
| **5** | Beta tester recruitment | 3-4 people initial round. Up to 20 across rounds. DPIRD/extension network. |
| **6** | Contact AuctionsPlus re: data consent | Hard gate before paid users |
| **7** | Terms of Use + Privacy Policy | After beta complete + metrics collected |
| **Phase 1.5** | WATCH reply handler | Flask/FastAPI + Railway/Render. Hosting decision: Railway vs Render. |
| **Phase 2** | Source abstraction | The Herd Online first. ToS review first. |
| **Post-beta** | Option A multi-profile architecture | See Section 6a |
| **Model Phase 3** | Signal Model Python pipeline | Competitor analysis first. Layer 1 first. |

---

## 14. Signal Model â€” Current Status

Build deferred behind Scout beta stabilisation. No Python code written yet. Architecture fully specified in `Cattle_Model_Project_Brief_v1_0.docx`.

**Standing requirement before Phase 3 coding:** Structured comparative analysis of all similar tools globally (Cattle Krush first). This happens at the start of Model Phase 3, not after.

**Confidence-tiered output (locked):** Format: `Fair value: 350â€“390c/kg lwt (68% CI) | Signal: RESTOCK | Confidence: 67% (Layers 1+2+4, Layer 3 unavailable)`.

**Backtesting requirement (hard gate):** 52-week minimum window against NLRS Casino/Lismore data before any Model signal is shared with any user.

---

## 15. Current Config Values â€” `tom_steers`

| Setting | Value |
|---|---|
| Script version | v2.4 |
| TEST_MODE | TRUE |
| user_id | tom_steers |
| twilio_to | whatsapp:+61XXXXXXXXX |
| active | TRUE |
| target_states | NSW |
| target_sex | either |
| target_classes | Weaned, Weaner, Vealer, Calf, Yearling, Backgrounder, Store, Feeder, Steer, Heifer |
| target_breeds | Angus, Brangus, Ultrablack, Angus Cross, Brangus Cross, Ultrablack Cross |
| min_head / max_head | 5 / 130 |
| min_weight_kg / max_weight_kg | 0 / 350 |
| max_weight_range_kg | 150 |
| fat_score range | (not set) |
| age range months | (not set) |
| require_HGP_free / require_polled / require_quiet | All FALSE |
| valuation thresholds | Â±10% |
| MAX_PAGES | 5 |
| REQUEST_DELAY | 3 seconds |
| AuctionsPlus search category | Steer-Heifer |

---

## 16. Credentials Architecture

| Location | Credentials stored |
|---|---|
| Local `.env` file | TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, GOOGLE_SHEETS_CREDS_FILE |
| GitHub Secrets | TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, GOOGLE_SHEETS_CREDS |
| Config Sheet | twilio_to per user (WhatsApp destination number) |
| `.gitignore` | .env and google_credentials.json excluded from all commits |

---

## 17. Knowledge Library â€” Current Documents

| Document | Version | Status |
|---|---|---|
| Signal_Scout_Project_State_v2_2.md | v2.2 | This document â€” Chat 14 output |
| Signal_Scout_Checkpoint_Chat14_to_Chat15.md | v1.0 | Chat 14 handover |
| build_signal_scout_form_v2.gs | v2.0 | Current |
| transform_form_response.py | v1.2 | Current â€” WhatsApp normalisation included |
| cattle_scout_v2_4.py | v2.4 | Current script â€” target_sex filter added |
| Drumquil_Signal_PreLaunch_Checklist_v1_1.md | v1.1 | Current |
| Drumquil_Signal_Strategy_v1_0.md | v1.0 | Current |
| AuctionsPlus_HTML_Selector_Reference_v2.md | v2 | Current |
| Cattle_Scout_Schema_Reference_v2_1.md | v2.1 | sex field to be added in next schema update |
| Cattle_Model_Project_Brief_v1_0.docx | v1.0 | Current |
| AuctionsPlus User Agreement (OperatingConditions.pdf) | Jul 2025 | Reviewed Chat 11 |
| drumquil_scout.xlsx | â€” | Google Sheet snapshot |
| AuctionsPlus 2026 assessment forms (PDFs) | â€” | Current |

---

*Â© 2026 Drumquil Signal. All rights reserved. | Signal Scout Project State v2.2 | 24 May 2026*
