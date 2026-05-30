# Cattle Scout — Schema Reference
**Drumquil Signal | Google Sheets Data Layer**
Version 2.3 | 26 May 2026

---

## Google Sheets Overview

**Sheet name:** `drumquil_scout`
**Google Cloud project:** `drumquil-scout`
**Service account:** `cattle-scout@drumquil-scout.iam.gserviceaccount.com`
**Credentials file:** `google_credentials.json` (path referenced by `GOOGLE_SHEETS_CREDS_FILE` in `.env`)

| Tab | Purpose |
|---|---|
| `cattle_scout_log` | Lean deduplication log + alert audit trail. Read at every run startup. **Per-user keyed** (multi-user). |
| `cattle_scout_listings` | Full parsed field set for every alerted listing. Append-only analytical dataset. **Per-user keyed** (multi-user). |
| `cattle_scout_config` | Multi-user buying criteria: `user_id | setting | value` |
| `cattle_model_output` | Latest fair value signal (integration point) |

---

## Tab 1: `cattle_scout_log` (v2.3)

Written by `log_listing()`. One row per alert event (`WATCHING` or `ALERTED`). Kept deliberately lean — this tab is read in full at every run startup for deduplication.

**Multi-user dedup key:** `(url, user_id)` so one listing can alert multiple users independently.

**append_row call:** always uses `table_range="A1"` to anchor rows to column A. Without this, gspread can drift new rows rightward.

| Col | Header | Content |
|---|---|---|
| A | `user_id` | User identifier (from config tab) |
| B | `url` | Listing URL |
| C | `status` | `WATCHING` or `ALERTED` |
| D | `title` | Listing title |
| E | `category` | `commercial`, `breeding_female`, `cow_calf_unit`, `bull` |
| F | `class` | Detected class (`weaned`, `yearling`, `steer`, `heifer`, etc.) |
| G | `breed` | Primary breed or `Unknown` |
| H | `head` | Head count (+ calf note if applicable) |
| I | `avg_weight_kg` | Avg liveweight at delivery (kg) |
| J | `weight_range_kg` | Mob weight spread (kg) |
| K | `fat_score` | AuctionsPlus fat score (1–6) |
| L | `age` | Age range string (e.g. `7–9mo`) |
| M | `accreditations` | Space-separated accred codes (e.g. `EU NE`, `LPA HGP-free`) |
| N | `price_c_kg` | Post-auction price c/kg (blank pre-auction) |
| O | `location` | Property location string |
| P | `vendor` | Agent / vendor string |
| Q | `sale_date` | Sale date string |
| R | `flag` | Valuation flag string (or blank) |
| S | `logged_at` | Timestamp `YYYY-MM-DD HH:MM` |

---

## Tab 2: `cattle_scout_listings` (v2.3)

Written by `log_listing_full()`. One row per alerted listing — append-only, never updated in place.

This is the analytical dataset used for:
- Model training data (post-auction price backfill against pre-auction traits)
- Alert History source for the web interface
- Future analytics/learning layers

**append_row call:** always uses `table_range="A1"` to anchor rows to column A.

| Col | Field name | Type | Notes |
|---|---|---|---|
| A | `user_id` | str | User identifier (from config tab) |
| B | `url` | str | Primary key for this tab |
| C | `logged_at` | str | `YYYY-MM-DD HH:MM` |
| D | `status` | str | `ALERTED` or `WATCHING` |
| E | `sale_name` | str | Breadcrumb sale name |
| F | `sale_date` | str | Auction info panel |
| G | `lot_number` | int | `Lot NNN` |
| H | `listing_category` | str | `commercial`, `breeding_female`, etc. |
| I | `class` | str | Detected class |
| J | `title` | str | Listing title |
| K | `num_head` | int | Head count |
| L | `state` | str | `NSW`, `QLD`, etc. |
| M | `location` | str | Location field |
| N | `vendor` | str | Agent/vendor field |
| O | `breed` | str | Primary breed or `Unknown` |
| P | `breed_groups` | str | Pipe-separated for mixed mobs |
| Q | `avg_weight_kg` | float | Delivery-adjusted |
| R | `weight_at_assessment_kg` | float | Pre-adjustment |
| S | `weight_min` | float | Delivery range low |
| T | `weight_max` | float | Delivery range high |
| U | `weight_range_kg` | float | `weight_max - weight_min` |
| V | `delivery_adjustment_pct` | float | Shrinkage % assumption |
| W | `liveweight_gain_per_day` | float | kg/day |
| X | `dressing_pct` | float | % |
| Y | `fat_score` | int | 1–6 scale |
| Z | `age_min_months` | int |  |
| AA | `age_max_months` | int |  |
| AB | `hours_off_feed` | float |  |
| AC | `assessment_date` | str |  |
| AD | `horn_status` | str | `polled`, `horned`, `tipped`, etc. |
| AE | `temperament` | str | `docile`, `quiet`, etc. |
| AF | `store_condition` | str | `forward_prime`, `store`, etc. |
| AG | `is_EU` | bool | Written as `TRUE`/`FALSE`/blank |
| AH | `is_NE` | bool | Written as `TRUE`/`FALSE`/blank |
| AI | `is_LPA` | bool | Written as `TRUE`/`FALSE`/blank |
| AJ | `is_MSA` | bool | Written as `TRUE`/`FALSE`/blank |
| AK | `has_WHP` | bool | Written as `TRUE`/`FALSE`/blank |
| AL | `HGP_free` | bool | Written as `TRUE`/`FALSE`/blank |
| AM | `lifetime_traceable_pct` | int | % of mob |
| AN | `price_per_head` | float | Post-auction (blank pre-auction) |
| AO | `price_c_kg` | float | Post-auction (blank pre-auction) |
| AP | `sale_type_pricing` | str | `$/head` or `c/kg` |
| AQ | `valuation_flag` | str | `🟢 UNDERVALUED`, `🟡 FAIR`, `🔴 OVERPRICED`, `No valuation` |
| AR | `fair_value_at_alert` | float | Model fair value c/kg at alert time |
| AS | `catalogue_pending` | bool | Written as `TRUE`/`FALSE`/blank |

---

## Tab 3: `cattle_scout_config` (v2.3 multi-user)

Read by `load_config()`.

| Col | Header | Meaning |
|---|---|---|
| A | `user_id` | Stable identifier, e.g. `tom`, `user_002` |
| B | `setting` | Setting name |
| C | `value` | Setting value |

Notes:
- Users with `active = FALSE` are excluded.
- `twilio_to` is mandatory per user (recipient WhatsApp number).
- Field parsing rules match v2.1: lists are comma-separated, booleans are `TRUE`/`FALSE`, numerics parse to float.

---

## Tab 4: `cattle_model_output`

Written by `cattle_model.py`. Read by `get_model_fair_value()`. Column B contains the most recent fair value estimate in c/kg lwt. Returns `None` if blank or unreadable.

---

*© 2026 Drumquil Signal. All rights reserved. | Cattle Scout Schema Reference v2.3 | 26 May 2026*
