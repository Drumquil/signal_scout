**DRUMQUIL SIGNAL**

Australian Cattle Listing Sites - Terms Review and Build Guidance

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Reference** |
| --- | --- | --- |

## 1. Purpose

This document is a best-effort national inventory of Australian cattle listing websites identified during the 31 May 2026 research pass, with a practical view of:

1. which sources matter for Signal Scout;
2. what each source appears to permit or prohibit;
3. where written agreement is the sensible or necessary path; and
4. what implementation shape each source would require.

This is a build reference, not legal advice. Website terms, robots rules, and platform ownership can change without notice and must be re-checked before any production integration.

## 2. Decision Rubric

| Decision | Meaning |
| --- | --- |
| `RED - agreement required` | Current terms explicitly prohibit scraping/automation, the platform is login-centric, or the commercial risk is too obvious to proceed without written permission. |
| `AMBER - permission-first` | No explicit scrape ban was confirmed in this pass, but the site restricts copying/reuse, has commercial sensitivity, or terms were incomplete. Limited research/testing may be possible, but production use should be permission-led. |
| `GREEN - public-page research likely workable` | No explicit anti-automation ban was found in the reviewed public terms, the data is meaningfully public, and a facts-only ingestion model looks defensible. Still re-check before launch. |

Operational rule for Signal Scout: if a source becomes core to the product, move it out of scraping ambiguity and into an API, licence, partnership, or written permission path.

## 3. Best-Effort National Inventory

| Source | Domain | Model | Cattle relevance | Current terms signal | Decision | Signal Scout build note |
| --- | --- | --- | --- | --- | --- | --- |
| AuctionsPlus | `auctionsplus.com.au` | Weekly online auction | Primary market source | User agreement governs platform access and user/content use; commercial platform with registered-user model | `AMBER - permission-first` | Continue current public-page beta use only. Before scale or paid launch, seek written comfort or commercial arrangement. |
| The Herd Online | `herdonline.com.au` | Listings / paddock sales / catalogues | High | Terms explicitly ban data mining, robots, scraping, indexing and copying/exploiting access | `RED - agreement required` | Do not scrape without written permission. Treat as partnership target. |
| On The Box / Up For Bids transition | `onthebox.com.au` | Auction / featured sales | High | Terms page found; no explicit scraping clause confirmed in this pass, but copying/profit-from-service restrictions are broad | `AMBER - permission-first` | Technically attractive, but move only with written consent if used in production. |
| StockLive | `stocklive.com.au` | Online auctions + saleyard bidding | High | Terms PDF located; no explicit scrape clause confirmed in search snippet | `AMBER - permission-first` | Worth direct outreach. Also strategically useful for physical saleyard adjacency. |
| Southern Livestock Exchange | `southernlivestockexchange.com.au` | Live-streamed exchange auction | Medium-high | Online bidding/live-stream presence confirmed; full terms posture not yet fully reviewed in this pass | `AMBER - incomplete review` | Relevant as an exchange-layer source rather than a pure national platform. |
| FarmGate Auctions | `farmgateauctions.com.au` | Online auctions | Medium | Terms page located; general contractual controls, no explicit scrape clause confirmed in snippet | `AMBER - permission-first` | Lower-volume source, but potentially reachable for permission. |
| Cattlesales | `cattlesales.com.au` | Cattle-only classifieds | High | Terms allow personal reference use and broadly prohibit copying/reproduction without approval | `AMBER - permission-first` | Valuable because it is cattle-specific, but not a green-light scrape source for commercial reuse. |
| LocalAg | `localag.com.au` | Marketplace / escrow-style | Medium | Terms found; no explicit scrape prohibition confirmed in reviewed snippet | `AMBER - permission-first` | Broader ag marketplace. Lower priority than cattle-specialist sites. |
| Agora Livestock | `agoralivestock.com.au` | Listings / saleyard + private sale tools | Medium-high | Terms explicitly prohibit scraping, robots, spiders, scripted responses, collection and repackaging | `RED - agreement required` | No scraping without permission. May still be a good commercial data conversation. |
| Farm Tender | `farmtender.com.au` | Marketplace | Medium | Terms explicitly prohibit robots, spiders, automatic devices or manual processes to monitor or data mine pages/content | `RED - agreement required` | Do not scrape without permission. Lower cattle priority anyway. |
| AgTrader | `agtrader.com.au` | Broad ag classifieds | Low-medium | Broad sale conditions located, but no clear public anti-scraping clause confirmed in this pass | `AMBER - permission-first` | Possible source for occasional cattle listings, but not a strong early target. |
| Farmbuy Livestock | `farmbuy.com/livestock` | Livestock marketplace / events / stud listings | Medium-high | Large public livestock directory/event layer confirmed; full terms review still incomplete | `AMBER - incomplete review` | Potentially useful as a discovery layer, but may aggregate rather than originate many listings. |
| The Sale Yards | `thesaleyards.com` | Saleyard comparison / marketplace services | Low-medium | Public positioning confirmed; terms review incomplete | `AMBER - incomplete review` | Likely more useful for saleyard intelligence than live lot alerts. |
| RLX - Regional Livestock Exchanges | `rlx.com.au` | Exchange network with online sale presence | Medium-high | Sale pages and RLX website terms confirmed; some online bidding is handled via StockLive or AuctionsPlus | `AMBER - permission-first` | Important source family, but build path may be exchange-page parsing plus third-party bidding link handling. |
| LivestockHub | `livestockhub.com.au` / similar | Listings marketplace | Unclear | Public terms not confidently located in this pass | `AMBER - incomplete review` | Do not build until terms and actual listing volume are verified. |
| Fivestock / similar emerging niche sites | varies | Niche marketplace | Low / unclear | Terms and volume not confirmed in this pass | `AMBER - incomplete review` | Monitor only. Not a beta priority. |

## 4. Source-by-Source Notes

### 4.1 AuctionsPlus

Why it matters:
- It is still the dominant cattle source and remains the right foundation for beta.
- Signal Scout already has working selectors and validated filtering logic against its public listing pages.

Legal posture:
- AuctionsPlus is not a casual public-content site; it is a regulated commercial transaction platform with account-based user terms.
- The current accessible user agreement is expansive around platform control and user/content use.
- Even where a public page can be technically parsed, the commercial-risk answer is still `permission-first`.

Build implication:
- Keep current beta posture narrow: public pages only, low-frequency access, no login automation, no republication of raw catalogue data.
- Before paid launch or source expansion, request written approval, API access, or a commercial data arrangement.

### 4.2 The Herd Online

Why it matters:
- It appears to publish saleyard and paddock-sale style information that could materially expand coverage.

Legal posture:
- This is the clearest `no` in the current research set.
- The reviewed terms explicitly prohibit copying/exploiting access and using data mining, robots, scraping, indexing or similar collection tools.

Build implication:
- No scraper build without written permission.
- If pursued, position Signal Scout as a buyer-discovery layer that drives traffic back to The Herd rather than replacing it.

### 4.3 On The Box / Up For Bids

Why it matters:
- High cattle relevance, independent-market positioning, and likely useful lot metadata.
- It also sits in the competitive lane opposite AuctionsPlus, which may make partnership more plausible.

Legal posture:
- In this pass, the public terms page did not surface an explicit anti-scraping clause.
- That is not a green light. The service still controls content and commercial use, and the platform is clearly intended as a proprietary marketplace.

Build implication:
- Suitable outreach target.
- If approved, this could be one of the most useful Phase 2 additions.

### 4.4 StockLive

Why it matters:
- Directly relevant for online cattle auctions and potentially adjacent to saleyard data flows.

Legal posture:
- Terms PDF located, but this pass did not confirm an explicit automation clause.
- Because StockLive is auction infrastructure rather than a passive public directory, production ingestion should still be treated as permission-first.

Build implication:
- Good candidate for direct business development.
- Potentially important if Signal Scout later wants online + physical saleyard signal convergence.

### 4.5 FarmGate Auctions

Why it matters:
- Lower strategic priority than AuctionsPlus / The Herd / On The Box / StockLive, but still a real cattle-capable channel.

Legal posture:
- Terms were locatable, but not enough evidence surfaced in this pass to classify it green.

Build implication:
- Reasonable to hold in the secondary pipeline, behind stronger-volume sources.

### 4.6 Cattlesales

Why it matters:
- Cattle-only focus makes it unusually relevant despite being a classifieds model rather than a timed auction.

Legal posture:
- The terms explicitly frame content use as personal reference and prohibit broader copying/reproduction/publication without prior approval.
- That does not read like an open commercial scrape target.

Build implication:
- Attractive source from a product point of view.
- Use only with permission if it becomes part of the production pool.

### 4.7 LocalAg

Why it matters:
- Broader marketplace with some livestock presence.

Legal posture:
- General terms located, but no clean scraping allowance surfaced.

Build implication:
- Not worth early engineering effort unless cattle inventory proves materially better than current evidence suggests.

### 4.8 Agora Livestock

Why it matters:
- Strong relevance because it speaks directly to agents, listings, saleyards and reports.

Legal posture:
- Terms expressly prohibit scraping, robots, spiders, scripted responses, collection, repackaging and related automated extraction.

Build implication:
- Clear permission-only source.

### 4.9 Farm Tender

Why it matters:
- Large marketplace footprint, but cattle is only one category among many.

Legal posture:
- Terms expressly prohibit robots, spiders, automatic devices and manual processes used to monitor or data mine pages/content.

Build implication:
- Not an acceptable scrape target without permission.

### 4.10 AgTrader, LivestockHub and other long-tail directories

Why they matter:
- They may fill coverage gaps in specific regions or categories.

Legal posture:
- Review confidence is lower here.
- Treat all of them as unapproved until the exact terms, access pattern and actual cattle listing density are verified.

Build implication:
- Useful watchlist, not immediate backlog.

## 5. What Signal Scout Should Actually Build

### 5.1 Best source-expansion order

1. Keep AuctionsPlus stable.
2. Build authorised agent email/PDF ingestion.
3. Build agent public-page/PDF ingestion where terms and permissions are acceptable.
4. Pursue direct permission with high-value platforms (`The Herd`, `On The Box`, `StockLive`, `Cattlesales`).
5. Only then consider wider marketplace expansion.

### 5.2 Data-model implications

Different source types will need different normalisation rules:

| Source type | Typical fields | Parsing difficulty | Product value |
| --- | --- | --- | --- |
| Auction listing pages | structured lot details, sale date, location, breed, weight, agent | medium | high |
| Classified listings | seller narrative, mixed field quality, looser timing | medium-high | medium-high |
| Agent PDFs | lot count, account/vendor, breed, sex, age, est. weight, notes | medium-high | high |
| Market reports | sale results, price recaps, little pre-sale utility | low-medium | low for alerts, high for intelligence |
| Email newsletters | structured sale notice + attachment | medium | very high if authorised |

Recommended additions to the common listing schema beyond current AuctionsPlus fields:

- `source_name`
- `source_type` (`auction`, `classified`, `agent_pdf`, `email_notice`, `saleyard_calendar`)
- `listing_status` (`upcoming`, `live`, `closed`, `report_only`)
- `sale_date`
- `agent_name`
- `contact_method`
- `source_url`
- `attachment_url`
- `terms_risk_level`
- `permission_status`

### 5.3 Product boundaries to keep

Signal Scout should remain a discovery and alerting layer, not a cloned listings site.

Practical rules:
- store facts, not full source-page replicas;
- link users back to the original source to transact;
- do not copy source photos unless licensed;
- avoid wholesale reproduction of descriptive text;
- stop immediately if a platform objects or blocks access.

## 6. Cross-Cutting Legal / Compliance Notes Relevant to Build

These points matter across all platforms, even where scraping risk looks manageable:

1. Public visibility does not override website terms.
2. Bare facts are generally safer than expressive catalogue copy, photos, layouts and branded content.
3. Agent names, mobile numbers, email addresses and sometimes property/vendor details may be personal information and should be handled cautiously.
4. No login-wall automation. If a source requires an account to reach useful data, that is already a strong sign to stop and seek permission.
5. Outbound user alerts must stay consent-based and unsubscribe-capable.

## 7. Immediate Recommendations

### Recommendation 1

Do not build a The Herd scraper in the current repo without a written agreement.

### Recommendation 2

Treat `AuctionsPlus`, `On The Box`, `StockLive`, `FarmGate Auctions`, and `Cattlesales` as business-development targets, not just parser targets.

### Recommendation 3

Prioritise source expansion where the legal shape is strongest:

- authorised email newsletters;
- agent-provided PDFs;
- public branch sale calendars and sale-entry documents;
- direct partnerships with the largest market platforms.

### Recommendation 4

Before building any new source, add a per-source checklist to the implementation workflow:

1. confirm public URL pattern;
2. archive terms page URL and review date;
3. check robots rules;
4. test selector stability on at least 20 listings/documents;
5. record permission status;
6. set source risk level in code/config.

## 8. Reviewed Sources

Primary pages reviewed or relied on in this pass:

- AuctionsPlus user agreement landing page: `https://pages.auctionsplus.com.au/about/operating-conditions`
- AuctionsPlus user agreement PDF (March 2026 version surfaced in search): `https://pages.auctionsplus.com.au/hubfs/User%20Agreements/AuctionsPlus%20User%20Agreement%20-%2001.03.26.pdf?hsLang=en-au`
- AuctionsPlus operating conditions PDF: `https://media.auctionsplus.com.au/Doc/OperatingConditions.pdf`
- The Herd Online terms: `https://herdonline.com.au/terms-and-conditions`
- On The Box terms: `https://onthebox.com.au/help/toc/`
- Cattlesales terms: `https://cattlesales.com.au/Terms-and-Conditions`
- LocalAg terms: `https://www.localag.com.au/terms-and-conditions`
- Agora Livestock terms: `https://agoralivestock.com.au/terms-of-use/`
- Farm Tender terms: `https://www.farmtender.com.au/terms-and-conditions`
- StockLive terms PDF: `https://stocklive.com.au/terms_and_conditions.pdf`
- FarmGate Auctions terms: `https://farmgateauctions.com.au/terms-and-conditions/`

Related Australian compliance references relevant to implementation:

- OAIC personal information guidance: `https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/what-is-personal-information`
- ACMA spam guidance: `https://www.acma.gov.au/avoid-sending-spam`
- Google Workspace API user data and developer policy: `https://developers.google.com/gmail/api/policy`
- Australian Government copyright basics: `https://www.ag.gov.au/rights-and-protections/copyright/copyright-basics`
