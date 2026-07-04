**PROJECT BRIEF**

**Cattle Market Prediction Model**

| **Project Lead** Tom Flanagan | **Version** 1.0 — April 2026 |
| --- | --- |
| **Geographic Focus** Northern Rivers NSW (Casino, Lismore, Grafton) with future expansion to all of Australia once model has been validated. This could then be expanded built for beef producers globally. | **Model Class** Deterministic rules-based (weighted scoring) with the possibility of moving to a ML model in the future to increase power and accuracy |

# 1. Purpose & Objective

The model generates predictive buy/sell signals ("Restock" vs "Liquidate") for Australian beef cattle operations by synthesising three data domains: global commodity pricing floors, local environmental and pasture conditions, and seasonal/biological market cycles. These data domains may expand or contract as necessary to improve the prediction accuracy of the model. Additional data domains may be added for the same reason. 

Primary objective: capitalise on cyclical market inefficiencies to optimise liquidation and purchase timing for producers. This model will be the foundation for a product for beef producers in Australia that will help them to determine whether selling or purchasing cattle of any class or weight. The model will provide a prediction of sale/purchase prices for all beef cattle types to assist them in making business decisions that maximise the possibility of maximise their profits. 

Outputs: predictive price trends in both c/kg and $/head with confidence intervals, scenario-based decision triggers, and a daily Synthetic AUD Price with accompanying Global Sentiment Score.

# 2. Agreed Design Decisions

The following are locked decisions from prior design work. They are not subject to re-evaluation unless explicitly flagged.

| **Decision** | Agreed Position |
| --- | --- |
| **Model type** | Deterministic, rules-based weighted scoring — not ML. Chosen for interpretability and auditability given agricultural decision context. |
| **Primary output unit** | Unified Net Unit Value normalising c/kg live, c/kg carcase, and $/head for valid cross-category comparison. |
| **Confidence tiering** | High (90%+) for processor/export-driven variables. Variable (60–75%) for restocker/weather/sentiment variables. |
| **Deployment approach** | Python script via GitHub Actions on a cron schedule. Eliminates n8n subscription cost ($40/month). Enables future web deployment. |
| **Recalibration cadence** | Weekly — triggered by Wednesday afternoon Casino/NLRS market reports ingested via webhook/scraper. |
| **Global price proxy** | CME Live Cattle (LE=F / COW via Alpha Vantage) converted via AUD/USD forex. Corn and WTI Oil as input cost drag variables. |
| **Weather data** | Open-Meteo API for hyper-local rainfall. Nominatim (OpenStreetMap) for geocoding location inputs to lat/long. |

# 3. Model Architecture — Four Layers

## Layer 1: Global Magnet (Processor Floor)

Establishes the hard floor below which processor cattle will not trade. Driven by export demand, primarily US 90CL manufacturing beef.

| **Variable** | **Purpose** | **Status** |
| --- | --- | --- |
| CME Live Cattle (LE=F) | Global price ceiling/floor proxy | ✅ Validated |
| AUD/USD Forex | Currency conversion multiplier | ✅ Validated |
| Corn price (CORN) | Feedlot margin drag — bearish signal if >$5.00 | ✅ Validated |
| WTI Crude Oil | Transport/logistics drag — bearish if >$80 | ✅ Validated |
| Synthetic AUD/kg formula | (CME_price ÷ FX_rate) × 2.2046 | ✅ Validated |

## Layer 2: Local Environmental & Pasture Conditions

Drives restocker buyer sentiment in the Northern Rivers region. Pasture availability and soil moisture are the primary determinants of whether the market is in a restocking or destocking phase.

| **Variable** | **Purpose** | **Status** |
| --- | --- | --- |
| 30-day rainfall (Open-Meteo) | Grass Growth Lag and stocking confidence score | ✅ Blueprinted |
| 3-month trailing rainfall vs BOM outlook | Delta vs 10-year average for target postcode | ⚠️ Pending |
| Soil moisture threshold | Binary: Growth Phase (hold) / Arrested Phase (sell) | ⚠️ Pending |
| 14-day lagged rain variable | Price bounce predictor — T+7 from >25mm events | ⚠️ Pending |
| Pasture growth status | Categorised: Dormant / Maintaining / Active / Surplus | ✅ Blueprinted |

## Layer 3: Market Supply & Demand

Physical throughput and supply chain constraints that create short-term price distortions.

| **Variable** | **Purpose** | **Status** |
| --- | --- | --- |
| Local yarding vs 5-year average (NLRS) | Identifies supply shocks vs trend-driven drops. Supply Shock Smoothing algorithm applied at 1.5× SD. | ⚠️ Pending (hardest integration) |
| Feedlot lead time / capacity | Hard price ceiling for feeder steers. Linear scale 1–5 (Empty→Waitlisted). | ⚠️ Pending |
| Processor vs restocker price crossover | "The Split" trigger: if processor bid > restocker bid, recommend scenario split. | ⚠️ Pending |

## Layer 4: Strategic & Seasonal Coefficients

Override logic derived from biological and temporal market cycles.

| **Variable** | **Logic** | **Status** |
| --- | --- | --- |
| Winter Offload cycle | Time-decay urgency to sell before May 4. Buyer discount window June–July on PTIC and maiden heifers. | ✅ Blueprinted |
| Seasonal decay coefficient | −3% to −7% per week from May 15 for breeder-class cattle. | ✅ Blueprinted |
| Carrying cost offset | Predicted_Price(T+n) − (Weekly_Cost × n) − Insurance. If Net < Current_Price → trigger SELL. | ⚠️ Pending (user-defined inputs required) |

# 4. Build Status & Phased Roadmap

| **#** | **Phase** | **Description** | **Status** |
| --- | --- | --- | --- |
| **1** | **Global Magnet** | Alpha Vantage integration: CME cattle, AUD/USD forex, corn, WTI oil. Synthetic AUD/kg calculation. Sentiment score baseline. | 🔵 Blueprinted |
| **2** | **Weather ****&**** Location Engine** | Nominatim geocoding + Open-Meteo 30-day rainfall. Pasture growth status categorisation. | 🔵 Blueprinted |
| **3** | **Python Pipeline Migration** | Translate validated n8n/JS logic to standalone Python script. Deploy via GitHub Actions cron. | 🟡 Active |
| **4** | **Market Dynamics Integration** | NLRS feedlot lead time scrape. Winter Offload date logic. Supply shock smoothing algorithm. | ⚪ Queued |
| **5** | **Frontend Deployment** | Web interface for producer location input. Backend Python engine. Customised market indicators per location. | ⚪ Queued — spec required |

# 5. Validated Code — JavaScript Math Engine

The following logic was validated in n8n and serves as the direct blueprint for the Python migration. It handles Alpha Vantage data aggregation, rate limit protection (5 calls/min free tier), and synthetic price calculation.

| // Defensive fetch — handles both Quote and Forex response shapes function fetchPrice(nodeName) {   try {     const node = $(nodeName).first();     if (node.json["Global Quote"]) return parseFloat(node.json["Global Quote"]["05. price"]);     if (node.json["Realtime Currency Exchange Rate"]) return parseFloat(node.json["Realtime Currency Exchange Rate"]["5. Exchange Rate"]);     return null;   } catch (e) { return null; } } // Pull all four data points const pCattle = fetchPrice("Get CME Cattle"); const pForex  = fetchPrice("Get Exchange Rate"); const pGrain  = fetchPrice("Get Grain Prices"); const pOil    = fetchPrice("Get Energy Prices"); // Rate limit guard — return holding state if any API call failed if (!pCattle ││ !pForex ││ !pGrain ││ !pOil) {   return { status: "Pending", message: "Waiting for API cooldown." }; } // Synthetic AUD/kg — converts US cents/lb to AUD/kg const conversionFactor = 2.2046; const syntheticAudKg = (pCattle / pForex) * conversionFactor; // Sentiment score — baseline 50, adjusted by market signals let sentiment = 50; if (pCattle > 180) sentiment += 10;  // Bullish cattle futures if (pGrain > 5.00) sentiment -= 10;  // Bearish — feedlot cost drag if (pOil > 80)    sentiment -= 5;   // Bearish — transport cost drag return {   cattle_aud_kg: parseFloat(syntheticAudKg.toFixed(2)),   exchange_rate: pForex,   grain_price_us: pGrain,   oil_price_us: pOil,   global_sentiment_score: sentiment,   timestamp: new Date().toLocaleString("en-AU", { timeZone: "Australia/Sydney" }) }; |
| --- |

# 6. Open Questions & Design Tensions

These are unresolved issues requiring deliberate decisions before Phase 3 build continues. They are not blockers for the interrogation phase but must be resolved before coding resumes.

| **⚠️  TENSION 1 — Restocker vs Processor Primary Audience** |
| --- |
| The spec document is optimised for restocker/breeder market dynamics (Northern Rivers). |
| The handover document frames outputs primarily around processor floor pricing (export-driven). |
| These are different primary users with different dominant variables and decision triggers. |
| Decision required: Is the primary output restocker sentiment or processor floor? Or is it a tiered output serving both? |

| **⚠️  TENSION 2 — NLRS Data Access** |
| --- |
| NLRS yarding data is the most commercially valuable and the hardest to automate. |
| Real-time NLRS access likely requires scraping the public website or negotiating API access. |
| This is the variable most likely to determine whether the model generates genuinely novel signals vs. lagging public info. |
| Decision required: What is the NLRS integration strategy — scrape, manual upload, or MLA partnership? |

| **⚠️  TENSION 3 — Frontend Product Definition** |
| --- |
| Step 5 (Frontend Deployment) is currently underspecified for a commercial product. |
| "A web interface where producers input their location" could mean anything from a simple dashboard to a SaaS subscription product. |
| The commercialisation interrogation phase needs to fully define this before any frontend work begins. |
| Decision required: What is the product? Who pays for it? How is it distributed? |

| **⚠️  TENSION 4 — CME Proxy Accuracy** |
| --- |
| Alpha Vantage's CME cattle proxy (COW / LE=F) on the free tier has known data quality limitations. |
| This is the foundation of the Synthetic AUD/kg calculation — inaccuracy here propagates through all outputs. |
| Decision required: Is the free-tier proxy sufficient for a commercial product, or does the build need a paid data feed? |

# 7. Interrogation Agenda — Pre-Build Phase

Before build resumes at Phase 3, the following topics require systematic interrogation. These will be run as structured conversations within the Claude Project.

| **#** | **Topic** | **Key Questions** |
| --- | --- | --- |
| **1** | **Purpose ****&**** Use Case Refinement** | Who is the primary user — producer, advisor, or aggregator? Is this a personal decision tool or a commercial product from day one? |
| **2** | **Market Analysis** | Who else is doing this? What do MLA, AuctionsPlus, and private agtech firms already offer? Where is the genuine gap? |
| **3** | **Product Design** | What does the output look like? Dashboard? Alert/SMS? PDF report? API feed? What is the minimum viable signal? |
| **4** | **Customer Profiles** | Who are the two or three specific user types? What decision are they making, on what timescale, with what data currently? |
| **5** | **Commercialisation** | SaaS subscription, one-off licence, or embedded service? What is the pricing logic? Who is the distribution channel? |
| **6** | **Data ****&**** IP Strategy** | What data is proprietary? Can derived signals be IP-protected? What are the obligations around NLRS data reuse? |
| **7** | **Claude Project Skills Setup** | What Python libraries, API patterns, and GitHub Actions workflows should be loaded as project knowledge before Phase 3 build? |

# 8. Project Setup Instructions

When migrating this project to Claude Projects, use the following setup:

### Project Knowledge (upload all three):

- This document — Project Brief v1.0

- cattle_price_ai_model_specification.pdf — original spec

- Australian_Cattle_Model_Handover.pdf — technical handover

### Project Instructions (paste into Claude Project system prompt):

| You are the technical and strategic co-builder for Tom Flanagan's cattle market prediction model project. Tom's background: Agricultural extension officer and researcher, NSW DPIRD, 6 years. Senior Project Lead Agtech Applications. Post-grad in behavioural science and environmental science/ecology. Beginner-level coder. Project context: Full architecture is documented in the Project Brief and two handover PDFs in project knowledge. Read these before responding to any technical or strategic question. Response style: Direct, concise, peer-level. Lead with the answer. No preamble. Prose over bullet points. For code, provide working examples with plain-English comments. Current priority: Interrogation phase — purpose, market, product design, customer profiles, and commercialisation — before resuming the Python build at Phase 3. |
| --- |

Cattle Market Prediction Model — Project Brief v1.0 | April 2026 | Tom Flanagan