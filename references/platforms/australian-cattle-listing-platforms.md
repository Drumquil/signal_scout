**DRUMQUIL SIGNAL**

Australian Cattle Listing Platforms — Reference

| **Version: 1.0** | **Date: May 2026** | **Author: Tom Flanagan** |
| --- | --- | --- |

# **1. Purpose**

Reference document for every Australian online cattle listing platform identified as of May 2026. Defines integration priority for Cattle Scout Phase 2 and beyond. To be updated as new platforms launch or existing platforms change.

Strategic principle: Cattle Scout's competitive moat is aggregation across multiple platforms with a valuation layer, not scraping any single platform. The value proposition strengthens proportionally to the number of integrated sources.

# **2. Integration Priority**

| **Priority** | **Platform** | **Domain** | **Model** | **Status** |
| --- | --- | --- | --- | --- |
| **1** | AuctionsPlus | auctionsplus.com.au | Auction (weekly) | Done — production |
| **2** | HerdOnline | herdonline.com.au | TBD — research needed | Phase 2 — first |
| **3** | On The Box | onthebox.com.au | Auction (multi-format) | Phase 2 — second |
| **4** | Stocklive | stocklive.com.au | Auction (staggered-close) | Phase 2 — third |
| **5** | FarmGate Auctions | farmgateauctions.com.au | Auction (offline-tolerant) | Phase 2 secondary |
| **6** | Cattlesales | cattlesales.com.au | Classifieds advertising | Phase 2 secondary |
| **7** | LocalAg | localag.com.au | Marketplace + escrow | Phase 3 (broader ag) |
| **8** | Farm Tender | farmtender.com.au | Marketplace | Phase 3 |

# **3. Platform Profiles**

## **1. AuctionsPlus (Production)**

Domain: auctionsplus.com.au

Ownership: Elders + Nutrien (agency consortium). Dominant since 2000.

Scale: ~215,000 unique monthly users. $1.2bn+ total transactions. 600k+ cattle delivered annually.

Model: Weekly real-time online commercial livestock auctions. Stock assessed by accredited assessors before listing. Sales conducted through licensed agents.

Scraping: Confirmed working via cattle_scout.py v1.6. Vue.js SPA but key fields (Location, Breed, Weight, Vendor) available in static HTML via ap-read-more components. Stage 1 pre-catalogue and Stage 2 post-catalogue logic both operational. Selector reference documented in AuctionsPlus HTML Selector Reference.

Recent context: Has attracted criticism for listing costs and user-friendliness. Several senior staff departures 2022-2023 led to founding of On The Box. Stocklive launched October 2025 as competitor.

## **2. HerdOnline (Phase 2 priority)**

Domain: herdonline.com.au

Status: Tom flagged for research. Platform details and scraping considerations to be documented after inspection.

Next steps: Run an inspection script equivalent to inspect_listing.py against HerdOnline listings. Document HTML structure, listing types, catalogue timing, page pagination, and any anti-scraping measures.

## **3. On The Box**

Domain: onthebox.com.au

Founded: December 2023 by Tim McRae (former MLA senior analyst, former AuctionsPlus senior manager) and Greg Szudrich (former Rabobank head of digital operations, former AuctionsPlus). Two named founders plus three additional investors.

Positioning: Independent (not agency-owned). Targets independent agents who feel that using AuctionsPlus supports their competitors Elders and Nutrien.

Listing fees: $5/head cattle, 80c/head sheep, 30c/head goats, $1/lot machinery + 1.5% on sold items up to $29. Significantly lower than AuctionsPlus.

Notable features: Transparent buyer identification (vs AuctionsPlus discrete buyer policy). Agent shop-front pages. No paid advertising for faster page loads in poor connectivity. Buyer bridging finance facility. ID verification (drivers licence) for all users.

Roadmap: Forward contracting on cattle with future delivery dates planned.

## **4. Stocklive**

Domain: stocklive.com.au

Ownership: AAM (Australian Agricultural Management). 100% Australian owned, not agency-owned.

Background: Existed since 2017 as remote bidding interface for physical saleyard sales. Absorbed former Elite Livestock Auctions interface.

Online auctions launched: October 2025. Soft launch with fortnightly Thursday cattle sales, moving to weekly. Sheep on alternate Thursdays from November.

Notable feature: Staggered-lot closing. Each lot closes individually with bid extensions on competitive lots. Significantly different from AuctionsPlus single-window-close model.

Listing fees: Cheaper than AuctionsPlus. Specific schedule on Stocklive website.

## **5. FarmGate Auctions**

Domain: farmgateauctions.com.au

Ownership: Australian-owned, independent.

Notable features: Offline-tolerant assessment form ("no wifi, no worries" — assessments saved offline, synced when connection returns). Digital signature on-farm. Integrated accredited assessor training (online multi-choice test required to become sell-permitted).

Categories: Cattle, sheep, goats. Store stock, breeding stock, fat stock, stud stock.

Strategic fit: Lower volume than top 4 but the offline-tolerance design suggests serious thought about producer UX. Worth integrating to broaden coverage.

## **6. Cattlesales**

Domain: cattlesales.com.au

Model: Pure classifieds advertising — not an auction platform. Single category: cattle only.

Use cases: Pre-marketing saleyard cattle, pre-marketing online auction cattle, paddock cattle.

Strategic fit: Different from auction platforms — produces persistent listings rather than time-bound auction events. Cattle Scout would treat as a separate listing-type pipeline.

## **7. LocalAg**

Domain: localag.com.au

Ownership: Feed Central.

Scale: $20M+ in trades completed. 600+ successful sales.

Model: Marketplace with escrow-style payment system. Funds held securely until both sides confirm satisfactory delivery.

Categories: Hay, grain, machinery, livestock (including cattle). Broader agricultural scope than cattle-only platforms.

Strategic fit: Phase 3. Different model (escrow direct trades vs auction). Integration adds breadth for producers with mixed enterprises.

## **8. Farm Tender**

Domain: farmtender.com.au

Model: Marketplace, broader agricultural scope.

Status: Details to be researched. Phase 3 priority.

# **4. Pre-Integration Checklist (Per Platform)**

Before adding any new platform to Cattle Scout, complete the following:

1. Review the platform's Terms of Service. Identify any anti-scraping clauses. Document compliance approach (respectful delay, browser-identified User-Agent, public-listings-only).

2. Check robots.txt at platform.com.au/robots.txt. Document allowed paths.

3. Run an inspection script against 25+ random listings. Document HTML structure, field locations, listing type variations.

4. Confirm catalogue release timing for time-bound platforms (auction sites). Adjust two-stage filter logic if different from AuctionsPlus.

5. Build the scraper module conforming to common Listing schema (see Web Interface Build Plan Section 8).

6. Test against 50+ listings before adding to production rotation.

7. Update the Australian Platforms Reference document with detailed profile.

# **5. Legal ****&**** Ethical Boundaries**

Cattle Scout's scraping must remain on the right side of three lines:

• Public data only. Never authenticated content, never private listings, never data behind a login wall. All target platforms make their public listings publicly accessible — that's the basis of operation.

• Respectful request patterns. 3-second minimum delay between requests, standard browser User-Agent, no parallel hammering. Match human browsing patterns.

• No replication or redistribution of raw listing data. Cattle Scout's output is a derived signal (alerts, valuations, decisions). Producers using Cattle Scout still need to go to the source platform to bid or contact agents. Cattle Scout is a buyer's discovery tool, not a competing listings feed.

If any platform sends a takedown notice or blocks the scraper, the response is: respect the block, contact the platform directly to discuss whether a sanctioned data access arrangement is possible, document the outcome. Don't attempt to circumvent.

# **6. Living Document**

This document is updated whenever:

• A new Australian platform launches or is identified.

• An existing platform changes its architecture, terms, or ownership.

• A new integration is built or an existing one is updated.

• The strategic priority order changes.

*© 2026 Drumquil Signal. All rights reserved.  |  Australian Cattle Listing Platforms Reference v1.0  |  May 2026*