# Cattle Scout — Schema Reference
**Drumquil Signal | Google Sheets Data Layer**
Version 2.1 | 21 May 2026

---

## Google Sheets Overview

**Sheet name:** `drumquil_scout`
**Google Cloud project:** `drumquil-scout`
**Service account:** `cattle-scout@drumquil-scout.iam.gserviceaccount.com`
**Credentials file:** `google_credentials.json` (same folder as script)

| Tab | Purpose |
|---|---|
| `cattle_scout_log` | Lean deduplication log and alert audit trail. Read at every run startup. 18 columns. |
| `cattle_scout_listings` | Full parsed field set for every alerted listing. Append-only analytical dataset. Model training data and web interface source. |
| `cattle_scout_config` | All user-configurable buying criteria |
| `cattle_model_output` | Receives fair value signal from `cattle_model.py` (integration point) |

---

## Tab 1: `cattle_scout_log`

Written by `log_listing()`. One row per alert event (WATCHING or ALERTED). Kept deliberately lean — this tab is read in full at every run startup for deduplication. Never add analytical fields here; those go in `cattle_scout_listings`.

**append_row call:** always uses `table_range="A1"` to anchor rows to column A. Without this, gspread drifts new rows rightward.

| Col | Header | Content | Example |
|---|---|---|---|
| A | URL | Listing URL | `https://auctionsplus.com.au/...` |
| B | Status | `WATCHING` or `ALERTED` | `ALERTED` |
| C | Title | Listing title | `46 Steers` |
| D | Category | `commercial`, `breeding_female`, `cow_calf_unit`, `bull` | `commercial` |
| E | Class | Detected class | `weaned`, `yearling`, `steer`, `heifer` |
| F | Breed | Primary breed | `Angus`, `Unknown` |
| G | Head | Head count (+ calf note if applicable) | `23` or `21 (+21 calves)` |
| H | Avg Weight | Avg liveweight kg at delivery | `231.2` |
| I | Weight Range | Mob weight spread kg | `69.0` |
| J | Fat Score | AuctionsPlus fat score 1–6 | `1` |
| K | Age | Age range | `7–9mo` |
| L | Accreditations | Space-separated accred codes | `EU NE` or `LPA HGP-free` |
| M | Price c/kg | Post-auction price (blank pre-auction) | `385.0` |
| N | Location | Property location | `CHINCHILLA, Southern Queensland` |
| O | Vendor | Agent / vendor name | `NUTRIEN AG SOLUTIONS CHINCHILLA` |
| P | Sale Date | Sale date string | `Fri, 22 May 2026` |
| Q | Flag | Valuation flag | `🟢 UNDERVALUED`, `🟡 FAIR`, `🔴 OVERPRICED`, `No valuation` |
| R | Logged At | Timestamp of log write | `2026-05-21 21:17` |

**Deduplication logic:** `get_log_status()` reads columns A and B into `{url: status}`. Status `ALERTED` → skip entirely on subsequent runs. Status `WATCHING` → re-evaluate for Stage 2 once catalogue drops.

**Log write resilience:** `log_listing()` wraps `append_row` in try/except with a single retry after 10s backoff. On double failure, prints URL and warning so the row can be added manually.

---

## Tab 2: `cattle_scout_listings` *(to be created — next session)*

Written by a separate `log_listing_full()` function (not yet implemented). One row per alerted listing. Captures the full parsed field set from `scrape_commercial_listing()`. This is the analytical dataset — model training data, Alert History source for web interface, and future analytics layer.

When multi-user architecture is implemented, add a `user_id` column (column A, shifting all others right).

### Schema

| Col | Field name | Type | Source | Notes |
|---|---|---|---|---|
| A | `url` | str | Listing URL | Primary key for this tab |
| B | `logged_at` | str | Timestamp | `YYYY-MM-DD HH:MM` |
| C | `status` | str | `ALERTED` or `WATCHING` | |
| D | `sale_name` | str | Breadcrumb | e.g. `Weaner & Yearling Sale` |
| E | `sale_date` | str | Auction info panel | e.g. `Fri, 22 May 2026` |
| F | `lot_number` | int | `Lot NNN` near page top | For post-auction result matching |
| G | `listing_category` | str | Class detection | `commercial`, `breeding_female`, etc. |
| H | `class` | str | Class detection | `weaned`, `steer`, `heifer`, etc. |
| I | `title` | str | Title div | e.g. `46 Steers` |
| J | `num_head` | int | Title / head count field | |
| K | `state` | str | Location parsing | `NSW`, `QLD`, etc. |
| L | `location` | str | field-id="Location" | e.g. `WALLA WALLA, Riverina NSW` |
| M | `vendor` | str | Agent link div | e.g. `PAULL & SCOLLARD NUTRIEN AG SOLUTIONS ALBURY` |
| N | `breed` | str | Breeds section | Primary breed or `Unknown` |
| O | `breed_groups` | str | Breeds section | JSON or pipe-separated for mixed mobs |
| P | `avg_weight_kg` | float | Delivery weight block | Delivery-adjusted — the buying weight |
| Q | `weight_at_assessment_kg` | float | At Assessment block | Pre-adjustment, for shrinkage calc |
| R | `weight_min` | float | Delivery range | Low end kg |
| S | `weight_max` | float | Delivery range | High end kg |
| T | `weight_range_kg` | float | Derived | `weight_max - weight_min` |
| U | `delivery_adjustment_pct` | float | Del. Adj. field | Shrinkage % assumption |
| V | `liveweight_gain_per_day` | float | Live weight gain field | Condition trajectory signal |
| W | `dressing_pct` | float | Est. Av. Drs. field | Carcase yield signal |
| X | `fat_score` | int | Fat Scores block | 1–6 AuctionsPlus scale |
| Y | `age_min_months` | int | Age block | |
| Z | `age_max_months` | int | Age block | |
| AA | `hours_off_feed` | float | Hours off Feed block | <8hrs inflates liveweight |
| AB | `assessment_date` | str | Time Assessed block | Days-to-sale confidence signal |
| AC | `horn_status` | str | Polled/Horned field | `polled`, `horned`, `tipped`, `dehorned`, `scurred` |
| AD | `temperament` | str | Yards/Crush section | `docile`, `quiet`, `slightly stirry`, `stirry`, `aggressive` |
| AE | `store_condition` | str | Condition field | `forward_prime`, `forward_store`, `store`, `backward_store`, `poor` |
| AF | `is_EU` | bool | Accreditation(s) block | |
| AG | `is_NE` | bool | Accreditation(s) block | |
| AH | `is_LPA` | bool | Accreditation(s) block | |
| AI | `is_MSA` | bool | Accreditation(s) block | |
| AJ | `has_WHP` | bool | Accreditation(s) block | |
| AK | `HGP_free` | bool | HGP Status block | |
| AL | `lifetime_traceable_pct` | int | Lifetime Traceable field | % of mob |
| AM | `price_per_head` | float | Post-auction | Blank pre-auction |
| AN | `price_c_kg` | float | Post-auction | Blank pre-auction |
| AO | `sale_type_pricing` | str | Sale Types block | `$/head` or `c/kg` |
| AP | `valuation_flag` | str | score_listing() | `🟢 UNDERVALUED`, `🟡 FAIR`, `🔴 OVERPRICED`, `No valuation` |
| AQ | `fair_value_at_alert` | float | cattle_model_output tab | Model fair value c/kg at time of alert |
| AR | `catalogue_pending` | bool | Page text | True = WATCHING alert, False = full ALERT |

---

## Tab 3: `cattle_scout_config`

Read by `load_config()`. Column A = setting name, Column B = value. Row 1 is a header, skipped. Blank rows and rows with blank values are ignored.

### Field type rules

| Type | Stored in sheet | Returned in Python |
|---|---|---|
| List | Comma-separated: `NSW, QLD` | `["nsw", "qld"]` (lowercased) |
| Boolean | `TRUE` or `FALSE` | `True` or `False` |
| Numeric | Plain number: `180` | `float` |
| String | Plain text | `str` |

**Boolean fields recognised by load_config():** `active`, `require_EU`, `require_NE`, `exclude_WHP`, `include_breeding_females`, `include_bulls`, `include_stud`, `include_cow_calf_units`, `bull_require_EBV`, `require_vendor`, `require_HGP_free`, `require_polled`, `require_quiet`

### Commercial Cattle Filters

| Setting name | Type | Current value | Description |
|---|---|---|---|
| `active` | Boolean | `TRUE` | Master on/off switch |
| `target_states` | List | `NSW, QLD` | States to include |
| `target_classes` | List | `Weaned, Weaner, Vealer, Calf, Yearling, Backgrounder, Store, Feeder, Steer, Heifer` | Commercial classes to match |
| `target_breeds` | List | `Angus, Hereford, Angus Cross, Hereford Cross` | Breeds to pass filter (soft gate — skipped if breed = Unknown) |
| `sale_types` | List | `Weaner & Yearling Sale, Eastern States Cattle Sale` | Sale names to match (substring) |
| `min_head` | Numeric | `20` | Minimum mob size |
| `max_head` | Numeric | `100` | Maximum mob size |
| `min_weight_kg` | Numeric | `180` | Minimum avg liveweight at delivery |
| `max_weight_kg` | Numeric | `380` | Maximum avg liveweight at delivery |
| `max_weight_range_kg` | Numeric | `100` | Maximum weight spread (mob evenness) |
| `fat_score_max` | Numeric | `2` | Maximum fat score |
| `min_fat_score` | Numeric | `1` | Minimum fat score |
| `age_min_months` | Numeric | `6` | Minimum age |
| `age_max_months` | Numeric | `18` | Maximum age |
| `max_price_per_head` | Numeric | *(blank)* | Price ceiling $/head — logic not yet implemented (price post-auction only) |
| `require_EU` | Boolean | `FALSE` | Require EU accreditation |
| `require_NE` | Boolean | `FALSE` | Require Greenham Never Ever |
| `exclude_WHP` | Boolean | `FALSE` | Exclude listings with withdrawal period |
| `require_HGP_free` | Boolean | `FALSE` | Require explicit HGP-free declaration |
| `require_polled` | Boolean | `FALSE` | Require polled horn status |
| `require_quiet` | Boolean | `FALSE` | Require quiet or docile temperament |
| `min_lifetime_traceable_pct` | Numeric | *(blank)* | Minimum lifetime traceable % (blank = not enforced) |
| `preferred_vendors` | List | *(blank)* | Vendor whitelist — logic not yet implemented |
| `exclude_vendors` | List | *(blank)* | Vendor blacklist — logic not yet implemented |
| `require_vendor` | Boolean | `FALSE` | Vendor filter gate — not yet active |

### Category Toggles

| Setting name | Type | Current value | Description |
|---|---|---|---|
| `include_breeding_females` | Boolean | `FALSE` | Enable alerts for PTIC, NSM, station mated, etc. |
| `include_cow_calf_units` | Boolean | `FALSE` | Enable alerts for cow-and-calf compound lots |
| `include_bulls` | Boolean | `FALSE` | Enable alerts for bull listings |
| `include_stud` | Boolean | `FALSE` | Enable alerts for stud/genetics individual listings |

### Bull Filters *(active only when include_bulls = TRUE)*

| Setting name | Type | Current value |
|---|---|---|
| `bull_breeds` | List | `Angus, Brangus, Ultrablack` |
| `bull_min_age_months` | Numeric | `12` |
| `bull_max_age_months` | Numeric | `36` |
| `bull_min_weight_kg` | Numeric | `400` |
| `bull_max_weight_kg` | Numeric | `900` |
| `bull_min_fat_score` | Numeric | `2` |
| `bull_max_fat_score` | Numeric | `4` |
| `bull_require_EBV` | Boolean | `FALSE` |
| `bull_EBV_*` fields | Numeric | All blank | Pending bull breed research |

---

## Tab 4: `cattle_model_output`

Written by `cattle_model.py`. Read by `get_model_fair_value()` in Cattle Scout. Column B contains the most recent fair value estimate in c/kg lwt. Returns `None` if blank or unreadable — Scout alerts still fire without a fair value, but without a valuation flag.

---

*© 2026 Drumquil Signal. All rights reserved. | Cattle Scout Schema Reference v2.1 | 21 May 2026*
