**DRUMQUIL SIGNAL**

Signal Scout Parser Feasibility Shortlist

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Working Build Shortlist** |
| --- | --- | --- |

## 1. Purpose

This document turns the `parser-first` agency/network sources into a practical parser shortlist.

For each source, it answers:

1. what page type we would actually parse;
2. which fields look extractable;
3. how structurally stable the source appears;
4. what the expected parser complexity is;
5. whether the source should be built now, soon, or later.

This is not a final implementation spec. It is the decision layer before engineering work begins.

## 2. Ranking Key

### Feasibility

| Value | Meaning |
| --- | --- |
| `High` | Strong candidate for first parser build |
| `Medium` | Good candidate, but with notable caveats |
| `Low` | Real source, but not yet attractive enough for parser effort |

### Complexity

| Value | Meaning |
| --- | --- |
| `Low` | Simple repeated HTML cards or tables |
| `Medium` | Multi-page extraction, mixed templates, or extra normalisation needed |
| `High` | Significant ambiguity, mixed content types, or substantial heuristics required |

## 3. Shortlist Table

| Source | Primary page pattern | Likely target fields | Structural signal | Feasibility | Complexity | Best initial parser unit | Key risks / caveats | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stockplace Marketing | listing index + individual stock listing pages | title, date, head count, breed, stock type, avg weight, price type, status, location, notes | repeated listing cards and detail pages with labeled fields | `High` | `Low-Medium` | single listing-detail parser + index crawler | some entries are wanted orders or AuctionsPlus references rather than direct paddock/private listings | Start here for direct listing parser design |
| Sullivan Livestock & Rural Services | upcoming sales page + linked special sale/catalogue pages | sale name, sale date, venue, yarding counts by class, contact details, linked catalogue, linked AuctionsPlus/bidding URL | highly structured sale page with repeated blocks and clear headings | `High` | `Medium` | upcoming-sales parser | more sale-notice oriented than lot-by-lot listing source; linked catalogues may vary in format | Start early as sale-schedule / pre-sale notice parser |
| GDL | featured livestock sales cards + detail pages | title, sale type, location, town, venue, private sale vs saleyard sale, description, contact/salesperson | strong repeated cards on homepage/livestock pages | `High` | `Medium` | featured-sale card parser + detail page parser | may mix commercial cattle, stud sales, agistment and non-cattle entries; needs filtering | Strong candidate for Queensland-focused source |
| CIAA | livestock-for-sale cards + auction/market pages | title, sale type, price or terms, head count, category, contact name/phone, location, market name | genuine public for-sale inventory plus market pages | `High` | `Medium` | livestock-for-sale parser | SA collective means entries may vary by member agent quality; some inventory may be wanted/agistment rather than sale | Very strong collective-source candidate |
| RMA Network | cattle sales listing cards + sale detail pages | sale name, type, sale status, contact agency, contact phone, location, category | repeated public sale cards with filters and contact metadata | `High` | `Medium` | cattle-sales index parser | more sale/event aggregator than direct lot inventory; may require second-layer parsing on detail pages | Worth building as a feature-sale discovery layer |
| Quality Livestock | sales landing pages + saleyard pages + stock-for-sale pages | sale type, saleyard, sale day/time, stock-for-sale entries, contact details, subscribe path | multi-section but clearly livestock-focused site | `High` | `Medium` | stock-for-sale parser or saleyard-page parser | likely split across multiple templates; subscriber/SMS path may become more valuable than site alone | Good parser candidate with strong outreach upside |

## 4. Source-by-Source Notes

### 4.1 Stockplace Marketing

Observed page shape:
- listing index with categories such as `Livestock For Sale` and `Livestock Order - WANTED`
- individual listing pages with labeled cattle fields

Likely extractable fields:
- `source_name`
- `listing_title`
- `listing_date`
- `listing_status`
- `head_count`
- `breed`
- `stock_type`
- `avg_weight_kg`
- `price_type`
- `location`
- `notes_raw`
- `source_url`

Why it stands out:
- It is the cleanest candidate for a true `direct listing parser`.
- The site exposes repeated structured fields rather than hiding everything in long prose.

Expected implementation shape:
1. crawl listing index
2. filter cattle listings vs wanted orders
3. open detail page
4. map labeled fields into common schema

Recommendation:
- first parser spike candidate

### 4.2 Sullivan Livestock & Rural Services

Observed page shape:
- highly structured `Upcoming Sales` page
- sale notices with per-class yarding counts
- outbound links to catalogues, ABRI, Brahman catalogues, AuctionsPlus and event pages

Likely extractable fields:
- `sale_name`
- `sale_date`
- `venue`
- `sale_type`
- `yarding_total`
- `class_breakdown_raw`
- `contact_names`
- `contact_phone`
- `catalogue_url`
- `online_bidding_url`
- `source_url`

Why it stands out:
- Excellent pre-sale signal source.
- Especially good for physical and special sales where early lot-level structure may be partial but still commercially useful.

Expected implementation shape:
1. parse upcoming-sales page
2. create one `sale_notice` record per event
3. optionally attach linked catalogue/bidding URLs

Recommendation:
- build as `sale notice / schedule parser`, not as a full lot-detail parser

### 4.3 GDL

Observed page shape:
- repeated `Featured Livestock Sales` cards
- cattle and private-sale entries mixed together
- detail pages likely hold the richer listing narrative

Likely extractable fields:
- `listing_title`
- `sale_type`
- `location`
- `town`
- `venue`
- `listing_mode` (`private sale`, `saleyard sale`, etc.)
- `detail_url`
- potentially `head_count`, `breed`, `sex/class` from detail page

Why it stands out:
- Good repeated public card structure.
- Useful Queensland source with both private and saleyard-linked cattle opportunities.

Expected implementation shape:
1. parse featured-sale card index
2. filter to cattle
3. open detail pages for richer metadata

Recommendation:
- second-wave parser spike after Stockplace and Sullivan

### 4.4 CIAA

Observed page shape:
- live `Livestock For Sale` entries
- auction market pages for Dublin, Mt Compass, Crystal Brook
- member-agent collective context

Likely extractable fields:
- `listing_title`
- `asking_price` or terms
- `head_count`
- `breed/class`
- `weight_range_or_avg`
- `location`
- `contact_name`
- `contact_phone`
- `market_name`
- `sale_type`
- `source_url`

Why it stands out:
- This is a real live inventory layer, not just marketing copy.
- It could cover SA opportunities that otherwise only surface through fragmented agent channels.

Expected implementation shape:
1. parse `livestock-for-sale` index
2. parse auction/market pages separately
3. classify entries into `for_sale`, `wanted`, `agistment`, `auction_market`

Recommendation:
- high-value collective source; good second-wave parser candidate

### 4.5 RMA Network

Observed page shape:
- dedicated cattle sales index
- repeated sale cards with contact agencies and sale types
- likely detail pages per sale/event

Likely extractable fields:
- `sale_name`
- `sale_type`
- `sale_status`
- `agency_name`
- `contact_phone`
- `location`
- `detail_url`

Why it stands out:
- One parser could expose multiple independent agencies at once.
- Strong discovery value for feature sales and upcoming cattle events.

Expected implementation shape:
1. parse cattle-sales index
2. create one record per sale card
3. optionally enrich from detail page

Recommendation:
- good feature-sale aggregator parser; strong complement to direct listing sources

### 4.6 Quality Livestock

Observed page shape:
- livestock sales landing area
- separate saleyard and stock-for-sale sections
- SMS subscribe and contact hooks

Likely extractable fields:
- `sale_location`
- `sale_day`
- `sale_time`
- `stock_for_sale` entry fields where present
- `contact_details`
- `subscribe_path`

Why it stands out:
- Not just parseable; it also has a clean subscriber pathway.
- Strong dual value: site parsing plus relationship-driven direct notices.

Expected implementation shape:
1. parse saleyard pages for recurring schedule metadata
2. parse stock-for-sale section if stable enough
3. separately record subscriber path as an outreach/enrichment channel

Recommendation:
- good hybrid parser candidate with strategic outreach upside

## 5. Normalised Target Field Sets by Parser Type

### 5.1 Direct listing parser

Best fit:
- `Stockplace`
- parts of `CIAA`
- parts of `Quality`

Target fields:
- `listing_title`
- `head_count`
- `breed`
- `stock_type`
- `sex_or_class`
- `avg_weight_kg`
- `price_type`
- `asking_price`
- `location`
- `status`
- `contact_name`
- `contact_phone`
- `source_url`

### 5.2 Sale notice / sale schedule parser

Best fit:
- `Sullivan`
- `RMA`
- `GDL`
- `CIAA` market pages
- `Quality` saleyard pages

Target fields:
- `sale_name`
- `sale_type`
- `sale_date`
- `sale_time`
- `venue`
- `location`
- `yarding_total`
- `class_breakdown_raw`
- `catalogue_url`
- `online_bidding_url`
- `contact_name`
- `contact_phone`
- `source_url`

### 5.3 Hybrid parser with later enrichment

Best fit:
- `GDL`
- `Quality`
- `CIAA`

Approach:
- capture public schedule/listing facts first
- later attach PDFs, catalogue links, or newsletter ingestion where permission allows

## 6. Recommended Build Order

### Phase A: fastest parser wins

1. `Stockplace`
2. `Sullivan`
3. `RMA`

Why:
- each has a clear public index page pattern;
- each gives a different source shape;
- together they test `direct listing`, `sale notice`, and `aggregated sales` models.

### Phase B: broader regional coverage

4. `GDL`
5. `CIAA`
6. `Quality`

Why:
- they extend geographic spread;
- they add more heterogeneous structures after the parser framework is proven.

## 7. Expected Extraction Complexity Summary

| Source | Complexity summary |
| --- | --- |
| Stockplace | simplest structured-field parser in this group |
| Sullivan | easy top-level parse, but linked catalogues will vary |
| RMA | clear sales cards, but may need two-stage extraction |
| GDL | repeated cards, but more filtering/normalisation needed |
| CIAA | good inventory, but content variety is wider |
| Quality | likely multi-template parsing across sales sections |

## 8. Recommendation

If only three parser spikes are approved next, they should be:

1. `Stockplace`
2. `Sullivan`
3. `RMA`

That set gives Signal Scout:
- one direct cattle-listing parser,
- one sale-notice parser,
- one agency-network sales aggregator,

without betting everything on a single content model.
