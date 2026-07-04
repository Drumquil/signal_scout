**DRUMQUIL SIGNAL**

Top Three Parser Specs - Stockplace, Sullivan, RMA

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Implementation Spec Draft** |
| --- | --- | --- |

## 1. Purpose

This document converts the top three parser feasibility candidates into implementation-facing specs.

The top three are deliberately different parser shapes:

1. `Stockplace Marketing` - direct listing cards and listing detail pages.
2. `Sullivan Livestock & Rural Services` - sale notice / upcoming-sale page.
3. `RMA Network` - agency-network sales index with optional sale-detail enrichment.

Important: these are parser specs only. They do not override the legal posture in the source register. All three remain `AMBER - permission-first` for systematic production extraction.

## 2. Shared Output Contract

The current production Sheets schema is AuctionsPlus-shaped. These new sources should first emit a normalised internal record before any Sheet write is attempted.

### 2.1 Proposed normalised source record

```python
{
    "source_name": str,
    "source_type": str,
    "source_url": str,
    "source_record_id": str | None,
    "scraped_at": str,
    "permission_status": str,
    "terms_risk_level": str,

    "listing_title": str | None,
    "listing_status": str | None,
    "listing_mode": str | None,
    "listing_category": str | None,

    "sale_name": str | None,
    "sale_type": str | None,
    "sale_date": str | None,
    "sale_time": str | None,
    "venue": str | None,

    "location": str | None,
    "state": str | None,

    "num_head": int | None,
    "class": str | None,
    "sex": str | None,
    "breed": str | None,
    "breed_groups": str | None,
    "avg_weight_kg": float | None,
    "weight_min": float | None,
    "weight_max": float | None,
    "weight_range_kg": float | None,

    "asking_price": float | None,
    "price_type": str | None,
    "price_c_kg": float | None,
    "price_per_head": float | None,

    "agent_name": str | None,
    "agent_branch": str | None,
    "contact_name": str | None,
    "contact_phone": str | None,
    "contact_email": str | None,

    "catalogue_url": str | None,
    "online_bidding_url": str | None,
    "notes_raw": str | None,
    "class_breakdown_raw": str | None,
}
```

### 2.2 Mapping to current `cattle_scout_listings`

| Normalised field | Current Sheet field | Mapping note |
| --- | --- | --- |
| `source_url` | `url` | direct |
| `listing_title` | `title` | direct, fallback to `sale_name` |
| `listing_category` | `listing_category` | map to existing values where possible; otherwise use `commercial` or source-specific extension later |
| `class` | `class` | derived from title / stock type / class breakdown |
| `num_head` | `num_head` | direct where present |
| `state` | `state` | derive from location string where possible |
| `location` | `location` | direct |
| `agent_name` / `contact_name` | `vendor` | use readable combined value such as `RMA - Shad Bailey` |
| `breed` | `breed` | direct or derived |
| `breed_groups` | `breed_groups` | pipe-separated if multiple breeds detected |
| `avg_weight_kg` | `avg_weight_kg` | direct where present |
| `price_per_head` | `price_per_head` | direct where price type is per head |
| `price_c_kg` | `price_c_kg` | direct where price type is per kg |
| `sale_type` / `price_type` | `sale_type_pricing` | map to `$/head`, `c/kg`, `auction`, `sale_notice`, or blank |
| `sale_name` | `sale_name` | direct |
| `sale_date` | `sale_date` | direct |
| `source_type` | no current column | do not force into current Sheet yet; keep in normalised record |
| `permission_status` | no current column | keep in source register / future source table |
| `terms_risk_level` | no current column | keep in source register / future source table |
| `catalogue_url` | no current column | future field; can be appended to `notes_raw` during prototyping |
| `online_bidding_url` | no current column | future field; can be appended to `notes_raw` during prototyping |

### 2.3 Stage classification

| Source shape | Suggested Signal Scout status |
| --- | --- |
| Direct listing with enough animal details | `WATCHING` if buyer criteria match but auction/catalogue detail is incomplete |
| Sale notice with counts/classes only | `WATCHING` only; not enough detail for full `ALERTED` unless later enriched |
| Completed or sold listing | skip for buyer alerts, optionally store for market intelligence |
| Wanted/order listing | skip for buyer alerts unless a future seller-side product exists |

## 3. Parser Spec - Stockplace Marketing

### 3.1 Sample URLs

Primary index:
- `https://www.stockplace.com.au/stock`

Observed sample detail URL pattern:
- `https://www.stockplace.com.au/stock/livestock-for-sale/listing/800-crossbred-flatback-heifers-280-kg-21912`

Related source areas:
- `https://www.stockplace.com.au/stock/livestock-for-sale`
- `https://www.stockplace.com.au/stock/livestock-order-wanted-to-buy`

### 3.2 Parser goal

Build a direct cattle listing parser that emits one normalised record per livestock listing.

This parser should prioritise `Livestock For Sale` entries and ignore `Livestock Order - WANTED` entries for buyer alerts.

### 3.3 Page pattern

The index page exposes repeated listing blocks with:

- title link;
- optional status text such as `S O L D`, `Order filled`, or `Available`;
- location;
- labeled fields such as `No. of Head`, `Breed`, `Stock Type`, `Av. Weight (kg)`, `Price Type`;
- short description link;
- price text where present;
- date added.

### 3.4 Extraction rules

| Field | Rule |
| --- | --- |
| `source_name` | constant `Stockplace Marketing` |
| `source_type` | `agent_direct_listing` |
| `source_url` | listing detail URL if present, otherwise index URL |
| `source_record_id` | parse trailing numeric id from listing URL |
| `listing_title` | listing heading text |
| `listing_status` | detect `S O L D`, `Available`, `Order filled`, `UNDER OFFER`, `Order filling` |
| `listing_mode` | `for_sale`, `wanted`, `live_export_order`, `auction_plus_reference` |
| `num_head` | parse integer after `No. of Head:` or from title if missing |
| `breed` | parse `Breed:` field |
| `breed_groups` | split obvious compound breeds into pipe-separated values later; keep raw breed first |
| `class` | derive from `Stock Type:` and title |
| `sex` | derive from stock type/title using existing `steer` / `heifer` / `mixed` rules |
| `avg_weight_kg` | parse float after `Av. Weight (kg):` |
| `price_type` | parse `Price Type:` field |
| `price_c_kg` | if `Price Type` is `Per Kg`, parse leading dollar value and convert dollars/kg to c/kg |
| `price_per_head` | if `Price Type` is `Per head`, parse leading dollar value |
| `location` | text line between title/status and labeled fields |
| `state` | usually not explicit; leave `None` unless detail page provides it |
| `notes_raw` | short description link text plus any unparsed price/status text |

### 3.5 Filtering rules

Skip for buyer alerts when:

- `listing_mode == "wanted"`;
- `listing_status` contains `S O L D`;
- `listing_status` contains `Order filled`;
- title or status indicates the order is no longer available.

Allow into buyer matching when:

- listing is livestock/cattle;
- status is blank, `Available`, or not obviously closed;
- stock type is cattle-relevant.

### 3.6 Output schema example

```python
{
    "source_name": "Stockplace Marketing",
    "source_type": "agent_direct_listing",
    "source_url": "https://www.stockplace.com.au/stock/livestock-for-sale/listing/800-crossbred-flatback-heifers-280-kg-21912",
    "source_record_id": "21912",
    "permission_status": "permission_first",
    "terms_risk_level": "AMBER",
    "listing_title": "800 crossbred flatback heifers. 280 kg",
    "listing_status": None,
    "listing_mode": "for_sale",
    "listing_category": "commercial",
    "location": "Richmond",
    "num_head": 800,
    "class": "heifer",
    "sex": "heifer",
    "breed": "Composite",
    "avg_weight_kg": 280.0,
    "price_type": "Per Kg",
    "price_c_kg": 390.0,
    "notes_raw": "Good quality feeder or breeding heifers"
}
```

### 3.7 Complexity and risks

Complexity: `Low-Medium`

Risks:
- title/detail links may include AuctionsPlus references rather than direct listings;
- wanted/order listings share the same source family and must be filtered;
- some locations are not state-qualified;
- detail pages may not always be fetchable by simple request.

### 3.8 First implementation task

Create a standalone parser spike that:

1. fetches `https://www.stockplace.com.au/stock`;
2. extracts the first 10 `Livestock For Sale` records;
3. normalises status, head count, breed, stock type, weight, price type and date;
4. writes JSON to stdout only.

## 4. Parser Spec - Sullivan Livestock & Rural Services

### 4.1 Sample URLs

Primary page:
- `https://www.sullivanlivestock.com.au/livestock/upcoming-sales`

Supporting pages:
- `https://www.sullivanlivestock.com.au/livestock`
- `https://www.sullivanlivestock.com.au/livestock/paddock-sales`
- `https://www.sullivanlivestock.com.au/livestock/market-reports-industry-news`

Observed outbound catalogue / bidding links:
- Brahman catalogue PDF and flipbook links
- ABRI online database catalogue links
- AuctionsPlus online bidding links

### 4.2 Parser goal

Build a sale notice parser that emits one `sale_notice` record per sale event, with optional child `sale_line` records for class breakdown lines where structure is strong enough.

This is not initially a full lot parser.

### 4.3 Page pattern

The upcoming-sales page is mostly text blocks with:

- sale heading;
- sale date;
- sale time;
- yarding total;
- class headings such as `Steers`, `Heifers`, `Cows & Calves`;
- individual line descriptions under each class;
- agent contact names and phone numbers;
- catalogue / online bidding links for some special sales.

### 4.4 Extraction rules

| Field | Rule |
| --- | --- |
| `source_name` | constant `Sullivan Livestock & Rural Services` |
| `source_type` | `agent_sale_notice` |
| `source_url` | upcoming-sales URL |
| `sale_name` | uppercase heading before date, e.g. `GYMPIE CATTLE SALE` |
| `sale_date` | parse full date lines such as `MONDAY 1st JUNE 2026` |
| `sale_time` | parse times from lines such as `Liveweight Store Sale 10 am` |
| `venue` | infer from sale name or page context; e.g. `Gympie` |
| `yarding_total` | parse count from lines like `1500 CATTLE` |
| `class_breakdown_raw` | preserve all class lines beneath each class heading |
| `contact_name` | parse names preceding phone numbers in contact section |
| `contact_phone` | parse AU phone-like patterns |
| `catalogue_url` | capture PDF, flipbook, database and catalogue links |
| `online_bidding_url` | capture AuctionsPlus or other bidding links |
| `listing_category` | `commercial` for store/meatworks sale notices unless stud/breed-specific |
| `notes_raw` | retain unparsed sale text |

### 4.5 Sale line parsing

Where possible, parse child lines from class sections into this lightweight shape:

```python
{
    "parent_sale_name": str,
    "line_class": str,
    "num_head": int | None,
    "breed": str | None,
    "sex": str | None,
    "age_raw": str | None,
    "vendor_or_account": str | None,
    "notes_raw": str,
}
```

Example line rule:

- `180 D/Master x steers 18mths - 2yrs`
  - `num_head = 180`
  - `breed = "D/Master x"`
  - `sex = "steer"`
  - `age_raw = "18mths - 2yrs"`

Do not overfit the first parser. Store `notes_raw` whenever a line cannot be parsed confidently.

### 4.6 Filtering rules

Allow into buyer matching as `WATCHING` when:

- sale is upcoming;
- class breakdown includes cattle lines;
- line class or text includes target sex/class signals.

Do not send full `ALERTED` stage from Sullivan sale notices unless:

- a linked catalogue is parsed later; or
- enough animal-level detail exists to satisfy Stage 2 fields.

### 4.7 Output schema example

```python
{
    "source_name": "Sullivan Livestock & Rural Services",
    "source_type": "agent_sale_notice",
    "source_url": "https://www.sullivanlivestock.com.au/livestock/upcoming-sales",
    "permission_status": "permission_first",
    "terms_risk_level": "AMBER",
    "sale_name": "GYMPIE CATTLE SALE",
    "sale_date": "MONDAY 1st JUNE 2026",
    "sale_time": "10 am",
    "venue": "Gympie",
    "listing_category": "commercial",
    "class_breakdown_raw": "Steers... Heifers... Cows & Calves...",
    "contact_name": "Dan Sullivan; Pat Sullivan; Darryl Fitzgerald; Ethan Carter",
    "contact_phone": "0408 883 921; 0439 958 450; 0438 863 230; 0427 561 923",
    "catalogue_url": None,
    "online_bidding_url": None,
    "notes_raw": "Liveweight Store Sale 10 am; Liveweight Meatworks Sale 8 am"
}
```

### 4.8 Complexity and risks

Complexity: `Medium`

Risks:
- page is semi-structured text, not clean cards;
- special-event links vary by event;
- sale line parsing will need conservative heuristics;
- sale dates may need year inference if the page changes format.

### 4.9 First implementation task

Create a parser spike that:

1. fetches the upcoming-sales page;
2. splits content into sale sections by uppercase sale headings and date lines;
3. extracts sale-level records only;
4. stores line breakdown as `class_breakdown_raw`;
5. emits JSON to stdout.

## 5. Parser Spec - RMA Network

### 5.1 Sample URLs

Primary index:
- `https://www.rma.com.au/sales/cattle`

Observed sample detail URLs:
- `https://www.rma.com.au/sales/cattle/25048`
- `https://www.rma.com.au/sales/cattle/25247`
- `https://www.rma.com.au/sales/cattle/26919`

### 5.2 Parser goal

Build a cattle sales index parser that emits one record per RMA sale card, with optional enrichment from detail pages.

RMA is best treated as a network sales aggregator, not purely a direct listing site.

### 5.3 Page pattern

The cattle-sales page exposes category sections such as:

- `Feature`
- `For Sale`
- `Auction`

Each card may include:

- sale/listing title;
- location;
- sale date/time or price-like text;
- one or more agency/contact blocks;
- contact phone numbers;
- `View Sale` link.

### 5.4 Extraction rules

| Field | Rule |
| --- | --- |
| `source_name` | constant `RMA Network` |
| `source_type` | `agency_network_sale_index` |
| `source_url` | `View Sale` detail URL if present |
| `source_record_id` | trailing numeric id from detail URL |
| `listing_title` | card heading |
| `sale_name` | same as heading for sale/event cards |
| `listing_mode` | derive from section: `feature`, `for_sale`, `auction`, `wanted` |
| `sale_type` | derive from section plus title: `auction`, `for_sale`, `store_sale`, `stud_sale`, etc. |
| `sale_date` | parse date/time line when present |
| `sale_time` | parse time from date/time line |
| `location` | location line below title where present |
| `state` | parse postcode/state from location line |
| `num_head` | parse from title for direct animal listings, e.g. `32 Feeder Steers` |
| `class` | derive from title |
| `sex` | derive from title |
| `contact_name` | contact block names |
| `agent_name` | agency names where distinct from individual contact |
| `contact_phone` | contact phone numbers |
| `notes_raw` | any detail-card text not mapped |

### 5.5 Detail page enrichment

Detail pages can hold richer narrative or catalogue-style content.

Optional detail-page fields:

- `notes_raw`
- `catalogue_url`
- `online_bidding_url`
- `agent_branch`
- `vendor_or_account`
- richer sale terms

Do not block the index parser on detail-page completeness. Index extraction alone has value.

### 5.6 Filtering rules

Skip for buyer alerts when:

- section is `Wanted`;
- title clearly indicates a non-cattle or non-sale item;
- event date is past and no current inventory remains.

Allow as `WATCHING` when:

- title contains target cattle class signals;
- date is current/upcoming or unknown;
- section is `Feature`, `For Sale`, or `Auction`.

### 5.7 Output schema example

```python
{
    "source_name": "RMA Network",
    "source_type": "agency_network_sale_index",
    "source_url": "https://www.rma.com.au/sales/cattle/26919",
    "source_record_id": "26919",
    "permission_status": "permission_first",
    "terms_risk_level": "AMBER",
    "listing_title": "Binnaway Store Sale",
    "listing_mode": "feature",
    "sale_name": "Binnaway Store Sale",
    "sale_type": "store_sale",
    "location": None,
    "contact_name": "David Grant Livestock Agency",
    "contact_phone": "02 6842 7963",
    "notes_raw": None
}
```

Direct animal-listing example:

```python
{
    "source_name": "RMA Network",
    "source_type": "agency_network_sale_index",
    "listing_title": "32 Feeder Steers",
    "listing_mode": "auction",
    "sale_type": "auction",
    "location": "Tylden, VIC 3444",
    "state": "VIC",
    "sale_date": "Friday, 29th May",
    "sale_time": "09:00am",
    "num_head": 32,
    "class": "feeder",
    "sex": "steer",
    "contact_name": "Michael White",
    "contact_phone": "0407501212"
}
```

### 5.8 Complexity and risks

Complexity: `Medium`

Risks:
- duplicated cards may appear across sections or repeated site output;
- some cards are sale events, while others are animal listings;
- detail pages include older historical records;
- many contacts are agency names rather than individual agents;
- date parsing must handle missing years.

### 5.9 First implementation task

Create a parser spike that:

1. fetches `https://www.rma.com.au/sales/cattle`;
2. preserves section context (`Feature`, `For Sale`, `Auction`, `Wanted`);
3. extracts card title, location/date line, contact block and `View Sale` link;
4. derives `num_head`, `class` and `sex` from title where possible;
5. deduplicates by `source_record_id` or `(title, contact_phone, sale_date)`;
6. emits JSON to stdout.

## 6. Common Normalisation Rules

### 6.1 Head count

Use this order:

1. explicit labeled field such as `No. of Head`;
2. leading number in title or line;
3. `x` pattern for cow/calf pairs, preserving raw note;
4. leave `None`.

Examples:
- `800 crossbred flatback heifers` -> `num_head = 800`
- `10 x 10 Cross Bred cows & calves` -> `num_head = 10`, `notes_raw` includes pair detail
- `1500 CATTLE` -> sale-level `yarding_total = 1500`, not `num_head`

### 6.2 Sex and class

Reuse the current Signal Scout philosophy:

- detect obvious `steer`, `heifer`, `cow`, `bull`, `mixed`;
- leave unknown fields as `None`;
- never suppress a potential match because a new-source parser cannot infer a field.

### 6.3 Status

Normalise to:

- `available`
- `sold`
- `under_offer`
- `order_filling`
- `order_filled`
- `upcoming_sale`
- `closed`
- `unknown`

### 6.4 Source dedup

Use:

1. `(source_name, source_record_id)` when a stable URL id exists;
2. `(source_name, source_url)` when URL is stable;
3. fallback `(source_name, listing_title, sale_date, contact_phone)`.

Do not reuse current `(url, user_id)` alert dedup directly until the source URL is stable.

## 7. Implementation Order

Build parser spikes in this order:

1. `Stockplace` - fastest direct-listing proof.
2. `RMA` - broadest network/card proof.
3. `Sullivan` - strongest sale-notice proof, but more text parsing.

This is a slight change from the feasibility shortlist order. Sullivan is still strategically excellent, but RMA gives cleaner repeated cards and a wider regression surface for the first shared parser framework.

## 8. Acceptance Criteria for Parser Spikes

Each parser spike should:

1. fetch only the public sample URL;
2. extract at least 10 records where available;
3. emit normalised JSON records;
4. include raw source URL and scrape timestamp;
5. leave unknown fields as `None`;
6. avoid writing to Google Sheets;
7. avoid sending WhatsApp alerts;
8. record skipped/closed/wanted entries separately in stdout summary.

## 9. Next Spec Work

Before production code:

1. add explicit permission status for each source;
2. check robots rules and current terms again;
3. decide whether source-derived records get a new Sheet tab or extend `cattle_scout_listings`;
4. implement source abstraction so new parsers cannot disturb the AuctionsPlus beta path.
