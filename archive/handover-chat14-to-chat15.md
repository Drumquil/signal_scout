# Drumquil Signal — Build Checkpoint
## Chat 14 → Chat 15 Handover
**Version: 1.1 | Date: 30 May 2026**

---

## How to Start Chat 15

```
Continuing the Drumquil Signal build.
Read AGENTS.md, docs/status.md, docs/schema.md, docs/prelaunch-checklist.md, and docs/auctionsplus-selector-reference.md first.
Current task: Commit/push v2.4 validation changes, decide whether to flip TEST_MODE for beta, and onboard the first real beta tester.
Paste terminal output from the next run you want to validate (local or Actions) to begin.
Do not re-explain prior decisions — locked in state documents.
```

---

## PROJECT STATE

Signal Scout v2.4 is built and validated locally. Stage 1 (WATCHING) and Stage 2 (ALERT) are both confirmed on live AuctionsPlus data (Stage 2 validated 29 May 2026). TEST_MODE remains True. One active beta user (`tom_steers`). v2.4 validation changes are not yet committed/pushed to GitHub.

### UPDATE — 29 May 2026 Validation Run
- Stage 2 ALERT path confirmed (local run): 168 listings processed, 22 ALERTED (widened criteria; Steer-Heifer browse category).
- Controlled live WhatsApp send delivered: 1 selected alert (32 Weaned Steers) received by Tom; TEST_MODE remained True (one-off send only).
- Location parsing: SYD timezone marker ignored; state derived from Location field.
- Breed parsing: risk confirmed non-blocking (soft gate; `breed="Unknown"` passes through Stage 2).

**Remaining beta blockers:** TEST_MODE still True, first beta tester not onboarded end-to-end, multi-user loop not validated with 2+ active users, and v2.4 not yet pushed to GitHub (Actions still runs v2.3).

---

## THIS SESSION — Chat 14

### 1. Task list reviewed and updated
Full task list produced from Chat 13 handover. Two items confirmed done by Tom: `tom` dev user block deleted from config Sheet, `transform_form_response.py` v1.2 uploaded to project KL.

### 2. Beta and legal sequencing decisions made
- AuctionsPlus consent: hard gate before **paid** users only. Unpaid beta (known network, up to ~20 users across rounds) may proceed without consent.
- Terms of Use + Privacy Policy: deferred until after beta complete and metrics collected. Beta evidence needed to inform legal work and AuctionsPlus negotiation.
- Rationale: need proof of tool viability before investing in legal/partnership conversations.

### 3. Stage 1 validated — first run (max_head=15)
Run with `tom_steers` config as written. 166 listings processed. 0 WATCHING, 0 ALERTS. All rejections correct — catalogue dominated by stud sales and large NSW mobs (>15 head). No false negatives identified.

### 4. `target_sex` filter implemented — v2.4
Two changes to `cattle_scout.py`:

**Change 1 — sex detection** added before return dict in `scrape_commercial_listing()`:
- `detected_class == "steer"` → `sex = "steer"` (unambiguous)
- `detected_class == "heifer"` → `sex = "heifer"` (unambiguous)
- Title scan: "mixed sex/sexes" → `"mixed"`, `\bsteers?\b` → `"steer"`, `\bheifers?\b` → `"heifer"`
- No match → `sex = None` (soft — passes through filter)
- Added `"sex": detected_sex` to listing dict

**Change 2 — sex gate** added in `listing_match()` after class filter:
- Fires only when `target_sex` is `"steer"` or `"heifer"`
- Skipped when `"either"`, blank, or `sex is None`
- Rejection format: `sex='heifer' != target_sex='steer'`

`target_sex` loads correctly via `load_config()` else branch (plain string — no type registration change needed).

### 5. Stage 1 re-validated with target_sex + max_head=50
Tom raised `max_head` to 50 in config Sheet for validation. Re-run with v2.4:
- 169 listings processed
- `target_sex` filter confirmed: 2 NSW heifer mobs correctly rejected (`31 Weaned Heifers`, `105 Weaned Heifers`)
- First real WATCHING alert fired: **27 Weaned Steers, CURRABUBULA, N.W. Slopes & Plains** (Davidson Cameron & Co, sale Fri 29 May 2026)
- Message format correct. WATCHING entry written to `cattle_scout_log`.

### 6. GitHub Actions extension installed in VS Code
Tom installed the recommended GitHub Actions VS Code extension. Gives syntax highlighting and validation for `.yml` workflow files.

---

## WHAT DIDN'T WORK

Nothing failed this session. All changes worked first time.

---

## OPEN QUESTIONS — Carried Forward

| # | Question | Notes |
|---|---|---|
| 1 | AuctionsPlus partnership/consent | Hard gate before paid users. Unpaid beta may proceed. |
| 2 | WATCH reply handler hosting | Railway vs Render free tier. Decide before Phase 1.5 build. |
| 3 | Freight calculation methodology | Per-km rate? Manual config? Required for Stage 3 message. |
| 4 | Seller-side tool scope and timing | Conceptually approved. Not yet a build task. |
| 5 | Outcross partnership approach | Approach after 60 days beta traction. |
| 6 | Beta pricing | $50–100/month working hypothesis. Decide before end of 3-month beta. |
| 7 | Model Phase 3 start timing | After beta stable. Competitor tool analysis session needed first. |
| 8 | The Herd Online ToS review | Hard gate L2. Before Phase 2 scraper build. |
| 9 | `target_sex` field not yet in Schema Reference v2.1 | Add in next schema update session. |

---

## NEXT TASKS — Sequenced

| Priority | Task | Notes |
|---|---|---|
| **1** | Commit + push v2.4 (including 29 May validation changes) | Brings GitHub Actions up to date; Stage 2 validation was local. |
| **2** | Switch TEST_MODE to False + start beta sends | After explicit approval + first beta tester opted-in. |
| **3** | Onboard first beta tester + validate 2-user loop | Confirms per-user dedup + per-user twilio_to in one run. |
| **4** | Beta tester recruitment | 3–4 people initial round, up to 20 across rounds |
| **5** | README for repo | One paragraph, ~10 min |
| **6** | Contact AuctionsPlus re: data consent | Hard gate before paid users |
| **7** | Terms of Use + Privacy Policy | After beta complete + metrics |
| **Phase 1.5** | WATCH reply handler | Flask/FastAPI + Railway/Render |
| **Phase 2** | Source abstraction | The Herd Online first. ToS review first. |
| **Model Phase 3** | Signal Model Python pipeline | Competitor analysis first. Layer 1 first. |

---

## LOCKED DECISIONS — Full List Carried Forward

| Decision | Position |
|---|---|
| Product names | Signal Scout / Signal Model. Rename pass deferred until beta stable. |
| Multi-user config schema | LOCKED. Row-block-per-user. Col A=user_id, B=setting, C=value |
| Multi-profile per user | LOCKED (interim). Option C workaround for beta. Option A post-beta. |
| Two-stage alert system | LOCKED. catalogue_pending=True → WATCHING; False → ALERT |
| Per-user dedup | LOCKED. Key = (url, user_id) |
| twilio_to per user | LOCKED. In config Sheet, not .env |
| Alert deactivation (beta) | LOCKED. Manual — Tom sets active=FALSE in Sheet on request. |
| sale_types filter | DEPRECATED. Remove in dedicated pass. Region replaces it. |
| Breed "Any / no preference" | LOCKED. Suppresses target_breeds filter entirely. |
| Region-based geography | LOCKED. Named regions in form → state codes in transform script. |
| Sex/Stage as independent axes | LOCKED. Sex = steer/heifer/either. Stage = weaner/yearling/backgrounder/any. |
| target_sex filter | LOCKED. Soft gate. Passes through when sex=None or target_sex="either". |
| Age filter optional | LOCKED. Gateway question. Only applied if "Yes" selected. Always shown in alert. |
| Fat score/accreditations optional | LOCKED. required=false. Always shown in alert if available. |
| Content-based listing router | LOCKED. URL path hint only; content classification takes precedence. |
| Field schema | Determined by AuctionsPlus assessment form, not reverse-engineered. |
| Two-tab log architecture | LOCKED. cattle_scout_log = lean dedup; cattle_scout_listings = full dataset. |
| Silent misses worse than false positives | STANDING PRINCIPLE |
| Ground-truth first | STANDING PRINCIPLE |
| Beta criteria entry | LOCKED. Google Form → transform script → config Sheet |
| Beta feedback | LOCKED. WhatsApp reply surveys + MS Forms + Otter.ai |
| Legal boundary | LOCKED. Price signals and fair value only. Never explicit buy/sell. |
| Parallel scraping | Deferred to Phase 2. ThreadPoolExecutor. |
| No platform names in user-facing copy | LOCKED. Describe functionally as "online cattle listing platforms". |
| AuctionsPlus consent | Hard gate before paid users. Unpaid beta (~20 users) may proceed. |
| ToS + Privacy Policy timing | LOCKED. After beta complete + metrics collected. |

---

## CONFIGURATION SNAPSHOT

| Setting | Value |
|---|---|
| Script version | v2.4 (local — not yet committed) |
| Project folder | `C:\Users\Drumquil\Documents\Drumquil\Drumquil Signal\Cattle Scout` |
| GitHub repo | `https://github.com/Drumquil/signal_scout` |
| Latest committed | `9e713d1` (v2.3) |
| Credentials (local) | `.env` file (never committed) |
| Credentials (Actions) | GitHub Secrets: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, GOOGLE_SHEETS_CREDS |
| Google Sheet | `drumquil_scout` |
| Log tab | `cattle_scout_log` |
| Listings tab | `cattle_scout_listings` |
| Config tab | `cattle_scout_config` |
| Response Sheet | `Signal Scout Responses` → tab `Form responses 1` |
| Model output tab | `cattle_model_output` |
| TEST_MODE | `True` |
| MAX_PAGES | `5` |
| REQUEST_DELAY | `3` seconds |
| Cron | 7am + 1pm AEST daily. ~3hr variance normal on free tier. |
| Active beta users | `tom_steers` |
| transform script | `transform_form_response.py` v1.2 |
| tom_steers max_head | 50 (temporarily raised for validation — reset to preferred value before beta) |

---

*© 2026 Drumquil Signal. All rights reserved. | Signal Scout Checkpoint Chat 14 → Chat 15 | 24 May 2026*
