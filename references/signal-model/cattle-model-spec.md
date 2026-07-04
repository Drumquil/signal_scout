# CATTLE_MODEL_SPEC.md
*Permanent project reference — update only when architecture or locked decisions change*
*Version: 1.0 | Created: May 2026 | Owner: Tom Flanagan, NSW DPIRD*

---

## What This Is

A deterministic, rules-based (non-ML) buy/sell signal generator for cattle markets in the Northern Rivers region of NSW. It is not a price prediction tool — it generates confidence-weighted signals based on a structured hierarchy of market variables.

---

## Who Tom Is

- Senior Project Lead, Agtech Applications, NSW DPIRD
- Agricultural extension officer and researcher, 6 years
- Postgrad in behavioural science and environmental science/ecology
- Beginner-level coder
- Response style: direct, concise, peer-level, no bullet points by default, plain-English code comments

---

## Target Saleyards

- Casino (primary)
- Lismore
- Grafton

---

## Four-Layer Architecture

### Layer 1 — Global Magnet (CME Live Cattle)
Sets the directional ceiling/floor for the signal. CME Live Cattle price (USD/cwt) converted via AUD/USD forex rate.

- **Data source:** Alpha Vantage API (CME proxy — quality flag: unresolved, see Design Tensions)
- **Status:** Blueprinted

### Layer 2 — Local Environmental (Rainfall / Pasture Pressure)
Adjusts the global signal based on local conditions that affect supply-side behaviour.

- **Data source:** Open-Meteo API (free, no key required)
- **Variables:** Rainfall (mm), derived pasture pressure index
- **Status:** Blueprinted

### Layer 3 — Market Supply/Demand (NLRS Yarding Data)
Ground-truth layer. Actual yarding numbers and category breakdowns from Casino/Lismore/Grafton.

- **Data source:** NLRS (MLA) — integration method unresolved (see Design Tensions)
- **Variables:** Total yardings, category mix (steers, heifers, cows, bulls), price benchmarks by category
- **Status:** Pending — NLRS integration is the highest-risk dependency

### Layer 4 — Strategic/Seasonal Coefficients
Applies known seasonal patterns and structural market tendencies as multipliers on the base signal.

- **Variables:** Seasonal index (month-based), special event flags (e.g., drought declarations, flood events)
- **Status:** Blueprinted

---

## Drag Variables

Applied as dampeners or amplifiers to the global signal:

| Variable | Source | Direction | Status |
|---|---|---|---|
| Corn price (USD/bushel) | Alpha Vantage | Drag (feed cost proxy) | Blueprinted |
| WTI Oil price (USD/bbl) | Alpha Vantage | Drag (transport cost proxy) | Blueprinted |
| AUD/USD forex | Alpha Vantage | Conversion + sentiment | Blueprinted |

---

## Validated Components

**JavaScript math engine** — validated in n8n prior to migration. This is the confirmed computational logic for signal generation. Python build must replicate this logic exactly before extending it.

The JS engine handles:
- CME price conversion (USD/cwt → AUD/kg liveweight)
- Drag variable weighting
- Confidence tier classification (High / Medium / Low / No Signal)

---

## Build Phase Status (as of April 2026)

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Architecture and design | Complete |
| Phase 2 | JS math engine validation (n8n) | Complete — validated |
| Phase 3 | Python build | Not started — blocked by interrogation phase |
| Phase 4 | NLRS integration | Not started — method unresolved |
| Phase 5 | Frontend / output layer | Not started — format unresolved |

---

## Locked Design Decisions

1. Deterministic rules-based logic only — no ML, no probabilistic modelling
2. Northern Rivers NSW focus — Casino, Lismore, Grafton saleyards only
3. Python as the build language for Phase 3+
4. Alpha Vantage as the CME/forex/commodity data source
5. Open-Meteo as the rainfall data source (free tier)
6. Signal output has three tiers: High Confidence / Medium Confidence / Low or No Signal

---

## Unresolved Design Tensions (must resolve before Phase 3)

### T1 — Primary Audience
Restocker-focused vs processor-focused changes variable weighting, confidence thresholds, and product framing fundamentally. **This is the most consequential unresolved decision.**

### T2 — NLRS Data Integration
NLRS (MLA) publishes yarding data but has no public API. Options: manual CSV download, scraping, MLA data partnership, or proxy via AuctionsPlus. Method affects automation viability and data freshness.

### T3 — Frontend / Output Definition
Is the output a Python script (CLI), a simple dashboard, a report PDF, an API endpoint, or something else? Affects Phase 5 architecture and commercial viability.

### T4 — CME Data Quality for Commercial Use
Alpha Vantage provides CME Live Cattle as a proxy. Suitability for commercial-grade signals (vs personal/research use) has not been verified. May require Quandl, CME DataMine, or a paid alternative.

---

## Interrogation Agenda (pre-Phase 3)

Seven structured topics to be worked through sequentially before resuming the Python build:

1. Purpose and primary use case
2. Primary audience (T1 resolution)
3. Market and competitive analysis
4. Product design and output format (T3 resolution)
5. Customer profiles and use cases
6. NLRS integration strategy (T2 resolution)
7. Commercialisation and data licensing (T4 resolution)

---

## Key Files in Project Knowledge Library

| File | Purpose |
|---|---|
| `Cattle_Model_Project_Brief_v1.0.docx` | Full architecture and interrogation agenda |
| Original Gemini handover PDFs (x2) | Prior session history and design rationale |
| `CATTLE_MODEL_SPEC.md` | This file — permanent reference |
| `SESSION_LOG.md` | Rolling session log — read before starting any session |
