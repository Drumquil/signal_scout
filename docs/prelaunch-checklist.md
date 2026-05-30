# Drumquil Signal — Pre-Launch Checklist
**Version 1.3 | 30 May 2026**
**Applies to: Signal Scout beta launch and paid launch**

---

## How to use this document

Items marked **🔴 HARD GATE** must be complete before any paying user is onboarded. No exceptions.
Items marked **🟡 BETA GATE** must be complete before any beta tester (free) is onboarded.
Items marked **🔵 PAID LAUNCH** must be complete before first paid subscription is taken.
Items marked **⚪ RECOMMENDED** are strongly advised but not blocking.

This document is updated as new requirements are identified. Do not close a gate without explicit sign-off recorded here.

---

## SECTION 1 — LEGAL & COMPLIANCE
*Hard gates. No paying users without these.*

### 1.1 Platform data agreements

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| L1 | **AuctionsPlus written consent** for commercial use of listing data | 🔴 HARD GATE (paid users only) | ❌ Open | Clause 3.3(b)(xii) and 11(c) of AuctionsPlus User Agreement (effective 1 July 2025) require prior written consent to exploit Content for commercial purposes. **Unpaid beta (~20 known users) may proceed without consent — low risk.** Contact before any paying user. Frame as partnership inquiry. Use beta traction + metrics as negotiating position. |
| L2 | **The Herd Online ToS review** before Phase 2 scraper build | 🔴 HARD GATE | ❌ Open | Review herdonline.com.au terms before any scraping code is written. Flagged in Strategy v1.0. |
| L3 | ToS review for each additional platform added | 🔴 HARD GATE | ❌ Open | Cattlesales, Farm Tender, agent websites — each requires ToS review before scraper is built. Do not assume consent. |

### 1.2 Product terms and privacy

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| L4 | **Terms of Use** for Signal Scout drafted and live | 🔴 HARD GATE (paid users only) | ❌ Open | **Deferred until after beta complete + metrics collected.** Beta evidence needed to inform legal work accurately. Draft before paid launch. Lawyer review before paid users. |
| L5 | **Privacy Policy** drafted and live | 🔴 HARD GATE (paid users only) | ❌ Open | **Deferred until after beta complete + metrics collected.** Must cover: data collected, use, storage, deletion, third-party sharing (none), Spam Act opt-in/unsubscribe, Australian Privacy Act compliance. |
| L6 | Lawyer review of Terms of Use and Privacy Policy | 🔴 HARD GATE (paid users only) | ❌ Open | **Deferred until after beta.** One-hour job for a tech/commercial lawyer. Required before paid users. |
| L7 | Signal Model legal framing confirmed | 🔴 HARD GATE | ❌ Open | All outputs must be framed as price signals and fair value estimates only — never explicit buy/sell recommendations. Review all output language before any Model signal is shown to users. Locked design decision. |

### 1.3 Intellectual property

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| L8 | Trademark search — "Signal Scout" and "Signal Model" | 🔵 PAID LAUNCH | ❌ Open | Search IP Australia before committing to brand names in paid context. Cost: ~$250/class via IP Australia. |
| L9 | Confirm no platform names in user-facing product copy | ⚪ RECOMMENDED | ✅ Done | AuctionsPlus references removed from form script 24 May 2026. Maintain discipline as product grows. |

---

## SECTION 2 — TECHNICAL READINESS
*Beta gate items must be complete before first beta tester is live.*

### 2.1 Core script

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| T1 | GitHub Actions cron confirmed firing on schedule | 🟡 BETA GATE | ✅ Done | Both 7am and 1pm AEST runs confirmed. ~3hr scheduling variance on free tier is normal — not a bug. Closed Chat 13. |
| T2 | Stage 2 ALERT path validated on live catalogue in v2.4 | 🟡 BETA GATE | ✅ Done | Validated 29 May 2026 local run (post-catalogue): Stage 2 full criteria gates executed and alerts produced. Controlled WhatsApp send also delivered (single selected alert). |
| T3 | TEST_MODE switched to False | 🟡 BETA GATE | ❌ Open | Stage 2 is now validated. Switch when ready to begin real beta sends (and after first beta tester is onboarded + opted-in). |
| T4 | Breed detection failures diagnosed on live catalogue | 🟡 BETA GATE | ✅ Done | Breed extraction risk is now non-blocking: Stage 2 treats `breed="Unknown"` as a pass-through (soft gate) to prevent silent false negatives. Track Unknown rate as a quality metric. |
| T5 | Location parsing ("SYD, NSW" issue) validated | 🟡 BETA GATE | ✅ Done | Location/state parsing updated to use `field-id="Location"` and explicitly ignore the fixed timezone marker `(SYD, NSW) AEST`. Confirmed via 29 May 2026 run + selector reference update. |
| T6 | Multi-user loop validated with 2+ active users | 🟡 BETA GATE | ❌ Open | Currently only `tom_steers` active. Validate with first beta tester added. |

### 2.2 Signal Model (before any Model output is shown to users)

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| T7 | 52-week backtesting against NLRS Casino/Lismore data | 🔴 HARD GATE | ❌ Open | Non-negotiable. No Model signal shown to any user until complete. Minimum window: 52 weeks. |
| T8 | Brier score log implemented in Google Sheets | 🔴 HARD GATE | ❌ Open | Build alongside Phase 3 pipeline. |
| T9 | Confidence-tiered output format implemented | 🔴 HARD GATE | ❌ Open | Format: `Fair value: 350–390c/kg lwt (68% CI) | Signal: RESTOCK | Confidence: 67%`. |

### 2.3 Infrastructure

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| T10 | 2FA enabled on all admin accounts | 🟡 BETA GATE | ❌ Confirm | GitHub, Google, Twilio, Porkbun, Cloudflare, Anthropic. Confirm before beta. |
| T11 | Credential rotation log current | 🟡 BETA GATE | ✅ Done | Last rotation 18 May 2026 (Twilio + Google service account). Logged in Cybersecurity Reference v1.1. |
| T12 | `.env` and `google_credentials.json` confirmed excluded from all commits | 🟡 BETA GATE | ✅ Done | `.gitignore` confirmed. |
| T13 | Incident response runbook developed in full | 🟡 BETA GATE | ❌ Open | Draft exists in Cybersecurity Reference v1.1. Needs final review before beta. |
| T14 | Twilio WhatsApp production approval (Meta Business) | 🔵 PAID LAUNCH | ❌ Open | Sandbox sufficient for beta (50 messages/day). Production approval required for paid users. |

---

## SECTION 3 — PRODUCT READINESS

### 3.1 Onboarding

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| P1 | Signal Scout Google Form built and live | 🟡 BETA GATE | ✅ Done | `build_signal_scout_form_v2.gs` v2.0. Tom's test response submitted and headers confirmed. |
| P2 | Config transform script built and tested end-to-end | 🟡 BETA GATE | ✅ Done | `transform_form_response.py` v1.2. Run against Tom's test response 24 May 2026 — 25 config rows written to Sheet. WhatsApp normalisation included. Fully closed Chat 13. |
| P3 | First beta tester onboarded end-to-end via form | 🟡 BETA GATE | ❌ Open | Validates full onboarding pipeline with a real user. After Stage 2 validated + TEST_MODE off. |

### 3.2 Communication

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| P4 | README written for GitHub repo | ⚪ RECOMMENDED | ✅ Done | Root `README.md` created 30 May 2026. |
| P5 | 1-page user guide for beta testers | 🟡 BETA GATE | ❌ Open | What Signal Scout does, how alerts work, how to respond (PASS/WATCH), who to contact. |
| P6 | Beta feedback channel established | 🟡 BETA GATE | ❌ Open | WhatsApp group or similar. Otter.ai for call transcription. MS Forms for structured feedback. |

### 3.3 Code hygiene

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| P7 | Product rename applied throughout codebase | ⚪ RECOMMENDED | ❌ Open | Signal Scout / Signal Model rename deferred until beta stable. Touches: script filename, print statements, Sheet tab names, docs, README. Do as a dedicated pass. |
| P8 | `sale_types` filter removed from script and config | ⚪ RECOMMENDED | ❌ Open | Deprecated in favour of region-based filtering. Remove from `load_config()`, filter logic, and Sheet config tab in a dedicated pass. |
| P9 | `max_price_per_head` filter logic implemented | ⚪ RECOMMENDED | ❌ Open | Config field read, logic not implemented. Price not available pre-auction — may remain deferred. |
| P10 | `preferred_vendors` / `exclude_vendors` filter logic implemented | ⚪ RECOMMENDED | ❌ Open | Config fields read, filter logic not implemented. |
| P11 | `target_sex` filter implemented in cattle_scout.py | ⚪ RECOMMENDED | ✅ Done | Implemented in v2.4 — Chat 14. Sex detection in parser + soft gate in listing_match(). Validated on live run 24 May 2026. |
| P12 | Option A multi-profile architecture (user_id \| profile_id \| setting \| value) | ⚪ POST-BETA | ❌ Open | Option C workaround in use for beta. See Project State v2.2 Section 6a. |

---

## SECTION 4 — COMMERCIAL READINESS

| # | Item | Gate | Status | Notes |
|---|---|---|---|---|
| C1 | Beta pricing decision made | 🔵 PAID LAUNCH | ❌ Open | Working hypothesis: $50–100 AUD/month. Decide before end of 3-month beta. Direct conversion conversation with each beta tester. |
| C2 | Payment processing set up | 🔵 PAID LAUNCH | ❌ Open | Stripe recommended. ABN required (already registered). |
| C3 | ABN displayed on all invoices and receipts | 🔵 PAID LAUNCH | ❌ Open | Legal requirement for business-to-business transactions. |
| C4 | GST registration decision | 🔵 PAID LAUNCH | ❌ Open | Required if annual turnover exceeds $75,000. Not relevant at beta. Review at paid launch. |
| C5 | AuctionsPlus partnership/consent formalised | 🔴 HARD GATE (paid users only) | ❌ Open | See L1. Required before any paying user. Unpaid beta may proceed. |

---

## SECTION 5 — SIGN-OFF LOG

*Record gate closures here as they occur.*

| Date | Item # | Item | Closed by | Notes |
|---|---|---|---|---|
| 24 May 2026 | L9 | AuctionsPlus name removed from form | Tom/Claude | build_signal_scout_form_v2.gs updated |
| 24 May 2026 | P1 | Signal Scout Form built and live | Tom/Claude | v2.0 form created, Tom's test response submitted, headers confirmed |
| 24 May 2026 | T1 | GitHub Actions cron confirmed firing | Tom/Claude | Both runs confirmed. ~3hr variance normal on free tier. Closed Chat 13. |
| 24 May 2026 | P2 | Config transform script built and tested end-to-end | Tom/Claude | v1.2. 25 rows written to Sheet. WhatsApp normalisation validated. Closed Chat 13. |
| 24 May 2026 | P11 | `target_sex` filter implemented | Tom/Claude | v2.4. Validated on live run — 2 NSW heifer mobs correctly rejected. Closed Chat 14. |
| 29 May 2026 | T2 | Stage 2 ALERT path validated on live catalogue | Tom | v2.4 local run produced 22 ALERTED with widened criteria; stage behaviour confirmed. |
| 29 May 2026 | T5 | Location parsing validated (SYD marker ignored) | Tom | State derived from Location field; timezone marker no longer misclassified as location. |
| 29 May 2026 | T4 | Breed detection risk downgraded (soft gate) | Tom | `breed="Unknown"` no longer blocks Stage 2; alert quality item only. |
| 30 May 2026 | P4 | README written for GitHub repo | Codex | Root `README.md` created. |

---

*© 2026 Drumquil Signal. All rights reserved. | Pre-Launch Checklist v1.3 | 30 May 2026*
