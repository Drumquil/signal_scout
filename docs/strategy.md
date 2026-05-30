# Drumquil Signal — Strategy & Architecture Reference
**Version: 1.0 | Date: 23 May 2026 | Author: Tom Flanagan**

---

## 1. Strategic Position

Drumquil Signal occupies a gap that no existing Australian tool fills: **buyer-side market intelligence for cattle restockers, combining criteria-matched pre-sale alerts with an independent, locally calibrated fair value signal.**

The two tools are distinct but tightly integrated:

- **Cattle Scout** — watches multiple listing platforms, filters against user-defined buying criteria, and delivers proactive WhatsApp alerts before the auction. Buyers set it and forget it.
- **Cattle Model** — produces a fair value estimate (c/kg lwt by category, with confidence interval) and a directional price signal (RESTOCK / HOLD / LIQUIDATE), synthesising global commodity pricing, local environmental conditions, seasonal biological cycles, and supply/demand dynamics.

Neither tool alone is the product. The integration — where Scout surfaces relevant lots and Model contextualises their value — is the product. This is what no competitor currently offers.

**Legal boundary (permanent):** Model outputs are price signals and fair value estimates, never explicit buy/sell recommendations. Output language: "Current fair value estimate: 390c/kg lwt (±15c, 68% CI). Signal: HOLD. Confidence: 67%." Not: "Buy now." This framing is a deliberate, permanent design decision.

---

## 2. Competitive Landscape — Australian Market

### The Herd Online (herdonline.com.au)
**What it does:** Aggregates paddock sales, AuctionsPlus pre-sale listings, saleyard information, and market reports. 5,000+ registered users, 100,000+ monthly views, 4,500 buyers/month. Agent-gated — must be invited by an agent to list. AuctionsPlus listings auto-populate when an agent activates the link at the AuctionsPlus upload stage.

**What it lacks:** No criteria matching. No alerts. No valuation layer. Buyers browse everything; the tool doesn't filter for their specific situation or tell them whether the price is right. The Herd is a directory; Drumquil Signal is intelligence.

**Relationship to Drumquil Signal:** The Herd Online is a data source for Phase 2 Scout (scraping public listings agents have loaded). It is not a direct competitor because it doesn't do what Drumquil Signal does.

### AuctionsPlus (auctionsplus.com.au)
**What it does:** Australia's dominant online livestock auction platform. Weekly commercial sales, saleyard interface, price discovery tool, market reports. Launched "Feeder Optimised" in March 2026 — criteria-matched pre-sale alerts for feedlot buyers specifically.

**What it lacks:** Platform-locked (AuctionsPlus listings only). Feeder Optimised targets feedlots, not restockers. No independent fair value signal — it shows what catalogue listings are asking, not what they're worth relative to current market conditions. No multi-source aggregation.

**Relationship to Drumquil Signal:** AuctionsPlus is Scout's primary data source and a validation that the buyer-alert concept has market demand. Feeder Optimised confirms the commercial direction; Drumquil Signal serves the restocker segment and adds the valuation layer AuctionsPlus doesn't provide. Not directly competing at this stage.

### Herd XL (MLA-backed Australian app)
**What it does:** Compares selling and buying scenarios — AuctionsPlus vs saleyards vs direct feedlot — factoring in commission, freight. Five tools for maximising profit from buying/selling decisions.

**What it lacks:** No live listing integration. No real-time market signal. No alerts. A calculator, not a market intelligence tool. Useful for scenario planning but doesn't replace a live buying signal.

### Agora Livestock (agoralivestock.com.au)
**What it does:** Livestock marketplace ("the realestate.com for livestock"). Agent lists cattle in under 3 minutes. Buyer login required for marketplace access.

**What it lacks:** Login wall for buyers. No valuation layer. No alerts. More like a classifieds platform than market intelligence. Buyer experience is passive — browse on demand rather than proactive notification.

---

## 3. Competitive Landscape — Global Reference Tools

### Cattle Krush / Performance Livestock Analytics (US)
**What it does:** Provides instant breakevens, profit alerts, and financial projections for feedlot buyers and cattle traders. Pulls CME Live Cattle, Feeder Cattle, and corn futures prices. Calculates cost-of-gain, expected closeout, breakeven buy price.

**Why it matters for Drumquil Signal:** This is the closest US analogue to what the Cattle Model is building. Cattle Krush is the price signal / decision-support layer; Performance Beef is the records layer. Bundled SaaS. Validates that the market for this product exists and that producers will pay for it. **Must be deeply analysed before Model Phase 3 coding begins.**

### Superior Livestock Auction (US)
**What it does:** America's largest video livestock auction. Publishes sale catalogues 1 week before major video auctions — mailed and emailed to 8,500+ registered buyers. Country Page listings available the day they're posted. Buyers receive proactive catalogue distribution for sales matching their buying history.

**Why it matters:** Demonstrates what pre-sale catalogue distribution looks like when one operator controls both the data and the buyer relationship end-to-end. Australian saleyards haven't reached this because the agent relationship model is fragmented. This is the model Outcross/NRLX should aspire to, and the partnership argument for Drumquil Signal.

### LiveAg (US)
**What it does:** Combines video auction model with physical sale barn network. First national company to bridge online video auctions and local auction markets. Ex-Superior Livestock leadership.

**Why it matters:** Shows the convergence direction for the industry — digital pre-sale marketing layered on top of physical saleyards. The Australian equivalent doesn't yet exist at scale.

### Tools to analyse before Model Phase 3 coding:
This list is not exhaustive. The standing requirement is a structured comparative analysis of all tools in this space (livestock, commodity, adjacent markets) before any Model architecture decisions are finalised. Start with:
- Cattle Krush / Performance Livestock Analytics
- Terrain Agri (pasture/rainfall analytics tools)
- Ever.Ag (supply chain risk + livestock analytics)
- Elders Market Intelligence reports (methodology)
- MLA's own indicator methodology and confidence reporting
- Commodity price signal tools in adjacent markets (wool, grain) for UX patterns

---

## 4. Integrated Platform Architecture

### Scout — Three-Tier Structure

**Tier 1 — Source modules**
Each source is self-contained: URL discovery, parser, field mapping → standardised listing dict. The main loop is source-agnostic. Each source declares `DATA_CONFIDENCE` (float 0–1).

| Source | Confidence | Status |
|---|---|---|
| AuctionsPlus assessed | 0.9 | Built (v2.2) |
| The Herd Online | 0.65 | Phase 2 |
| Agent websites | 0.45 | Phase 2 |
| Facebook via Make | 0.35 | Phase 3 |
| Outcross/NextLot direct | 0.9 | Partnership-dependent |

**Tier 2 — Unified listing object**
44-field dict (Schema Reference v2.1) plus two Phase 2 additions: `source` (string) and `data_confidence` (float). All sources return the same shape. Sparse sources leave non-available fields as `None` — soft gates skip them. The filter logic never needs to know the source.

**Tier 3 — Intelligence layer**
Scout reads the Cattle Model's current fair value from `cattle_model_output` tab. `score_listing()` returns a valuation flag for ALERTED listings. In Phase 1.5, this extends to the WATCH reply handler — producing a full Stage 3 price signal message incorporating `data_confidence` from the listing source.

### Model — Four-Layer Confidence Cascade

The Model always produces output at whatever layers are available. It never waits for all four layers. Confidence is reported alongside every signal.

| Layers | Confidence range | Availability |
|---|---|---|
| Layer 1 only (Global Magnet) | 90% | Always — Alpha Vantage CME/FX weekly |
| Layers 1+4 (Global + Seasonal) | 70–75% | Always — seasonal indexes from NLRS historical |
| Layers 1+2+4 (adds Local Environment) | 75–80% | Always — Open-Meteo no key required |
| All four layers | 80–87% | Weekly after Wednesday NLRS publish |

**Output format (fixed):**
```
Fair value: 350–390c/kg lwt (±25c, 68% CI)
Signal: RESTOCK | Confidence: 72%
Layers active: 1+2+4 (Layer 3 unavailable — MLA data not current)
```

### Integration — Google Sheets Data Layer

| Tab | Owner | Consumer | Purpose |
|---|---|---|---|
| cattle_scout_log | Scout writes | Scout reads (dedup) | 18-col lean audit trail |
| cattle_scout_listings | Scout writes | Model reads (training) | 44-col full analytical dataset |
| cattle_scout_config | Tom writes (Form→script) | Scout reads | User buying criteria |
| cattle_model_output | Model writes | Scout reads | Current fair value by category |

The `cattle_scout_listings` tab is the integration compound. As it accumulates post-auction price outcomes alongside pre-auction assessment data, it becomes proprietary training material for calibrating the Model's seasonal indexes and basis adjustments — data no competitor can replicate without building the same pipeline and waiting years.

---

## 5. Pre-Sale Saleyard Data — Research Findings

**The practical conclusion:** Pre-sale lot data for Casino (NRLX), Lismore, and Grafton regular weekly sales does not exist in any accessible structured digital format. Infrastructure exists (NextLot, agent websites) but is not populated before sale day for routine store/prime sales.

**Casino (NRLX) — Outcross/NextLot:**
- `nrlx.nextlot.com/public/sales/{id}/lots` pages exist for every sale type
- Fully JS-rendered SPA — not accessible via requests/BeautifulSoup
- API undocumented — reverse engineering requires browser network tab inspection
- NRLX website calendar is a JPG image (not machine-readable)
- Outcross Stockyard software manages internal booking/lot data — no public exposure
- Partnership with Outcross is the only path to structured pre-sale data

**Lismore and Grafton:**
- No catalogue platform. Agent Facebook posts are the primary digital channel (12-48h before sale, aggregate counts only)
- Donovan Livestock (Grafton) has an AuctionsPlus agent profile — some lots appear there
- Regular store/fat sales: no digital lot-level pre-sale data exists anywhere

**Available digital window by sale type:**
- AuctionsPlus (when agents opt in): days before sale — already captured by Scout
- Agent Facebook posts: 12-48 hours before sale — Phase 3 via Make
- Casino store sale Outcross catalogue: potentially 8am day-of — requires partnership
- Special/feature sales: notices often weeks in advance on agent websites and Facebook

**Partnership timing:** Approach Outcross after 60 days of demonstrated beta traction. Pitch centres on buyer routing, not data access.

---

## 6. MVP Roadmap — Beta Launch

**Standing startup principles applied (YC / HBS):**
- Riskiest assumption to test is behavioural, not technical: will Northern Rivers restockers find this valuable enough to change their buying behaviour?
- Maximum validated learning per unit of effort — build only what tests that assumption
- Do things that don't scale: manually configure beta testers in the Sheet, have conversations rather than building dashboards
- Charge as soon as there's evidence of value — free beta is time-limited (3 months), ends with a direct conversion conversation

**Beta target:** 3-5 Northern Rivers NSW restockers. Recruitment via Tom's DPIRD/extension network. Tom himself is User 0 — his own buying behaviour is the first test case.

### Sequential build tasks before beta:

**1. GitHub Actions cron (highest priority — absolute blocker)**
Single YAML file + GitHub Secrets for .env variables. Twice-daily schedule (7am, 1pm). Nothing runs unattended without this.

**2. Google Form for criteria intake**
Replaces raw Sheet entry as the onboarding interface. Build in Google Forms, ~90 minutes. Auto-populates config tab via short Python transform script. Fields: personal info, geography, cattle type, class, size, quality, breed, accreditations, sale types. Resolves criteria-entry-as-blocker without building a web interface prematurely.

**3. Multi-user config in script**
Extend `load_config()` and main loop to iterate over multiple user rows. Each row has `user_id` and `twilio_to`. `log_listing_full()` already has `user_id` column placeholder.

**4. Recruit 3-4 beta testers**
Conversation-based. Form is the onboarding artefact. Manually confirm their first alert fires before leaving them unattended.

**5. WATCH reply handler (Phase 1.5)**
Twilio inbound webhook → small Flask/FastAPI endpoint → Stage 3 price signal message. Hosting: Railway or Render (free tier). Requires Cattle Model Layer 1+2+4 to be producing output before this is useful. Can be stubbed with a placeholder message initially.

**6. Beta feedback collection**
WhatsApp reply surveys via Twilio webhook → `beta_feedback` tab. MS Forms for structured phone call notes. Otter.ai for call transcription (300 min/month free tier). Key metrics: did alert lead to attending sale? Did buyer bid? Did buyer purchase? Was price outcome better than typical experience?

**7. Outcross partnership approach (after 60 days of evidence)**
Not before. Evidence needed: X buyers receiving alerts for NRLX lots, Y of them attending sale, Z purchasing. That story opens the data access conversation.

---

## 7. Revenue Model — To Be Decided

**Working hypothesis (not locked):** Buyer SaaS subscription. $50-100 AUD/month per user. Comparable to AgriWebb pricing tier. Well below the value of one good cattle purchase.

**Alternative models to evaluate post-beta:**
- Agent B2B: agents pay per-sale to distribute lots to Drumquil Signal's matched buyer list. Revenue aligned with agent value (more buyers = higher prices).
- Saleyard/Outcross white-label: Drumquil Signal licensed to NRLX as buyer engagement service. Highest revenue potential, most partnership-dependent.
- Two-sided freemium: agents list free; buyers pay for intelligence layer. Requires network effects to be viable.

**Pricing decision timing (YC principle):** Charge as soon as there's evidence of value. Beta is free but 3-month time-limited. End of beta = direct conversation: "The beta is finishing. I'm launching at $X/month. Are you in?" That conversation is the most important user research of the product.

---

## 8. Open Questions — Do Not Close Without Tom's Decision

| # | Question | Notes |
|---|---|---|
| 1 | WATCH handler hosting | Railway vs Render free tier vs paid. Affects reliability. Decide before building |
| 2 | Freight calculation methodology | Per-km rate? Manual config per user? Agent quote API? Required for Stage 3 message |
| 3 | Seller-side tool scope and timing | Conceptually approved as strategic direction. Not yet a build task. When? Phase 2? Separate product? |
| 4 | Outcross partnership approach | When to make contact, who reaches out, what to offer |
| 5 | Beta pricing | $50/month? $100/month? Tiered? Decide before end of 3-month beta |
| 6 | Model Phase 3 start timing | After beta is running and stable. Competitor tool analysis session needed first |
| 7 | The Herd Online scraper legality | herdonline.com.au terms of service review before Phase 2 build |

---

*© 2026 Drumquil Signal. All rights reserved. | Strategy & Architecture Reference v1.0 | 23 May 2026*
