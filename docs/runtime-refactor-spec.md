# Signal Scout Runtime Refactor Spec
**Version 0.1 | Date: 31 May 2026 | Status: Proposed**

---

## 1. Purpose

This document defines the next engineering step recommended by `NEXT_CHAT_HANDOVER.md`:

- keep the current AuctionsPlus beta path working;
- remove duplicate per-user listing re-fetching;
- introduce a shared per-run normalised listing set;
- create the smallest source boundary that supports future source modules.

This is a runtime refactor spec, not a product-scope change.

---

## 2. Why This Refactor Is Needed Now

The current runtime already discovers AuctionsPlus listing URLs once per run, but it still scrapes each listing inside the per-user loop.

Current shape in `cattle_scout.py`:

1. `get_listing_urls()` runs once
2. `for user_config in all_users:`
3. `for url in listing_urls:`
4. `scrape_listing(url, user_config)`
5. `listing_match(listing, user_config)`

That means the same listing page is fetched again for every active user.

This is tolerable for:

- one source;
- one active user;
- twice-daily beta runs.

It is a bad fit for:

- 2+ active beta users;
- future multi-source expansion;
- more frequent schedules;
- controlled, legally conservative crawling.

---

## 3. Goals

This refactor should:

1. fetch each source listing page at most once per run;
2. parse each source listing into one shared listing object per run;
3. evaluate every active user against that shared set;
4. preserve the current Google Sheets tabs and dedup model;
5. keep the existing AuctionsPlus parser logic largely intact;
6. create a source abstraction that can later support non-AuctionsPlus modules.

---

## 4. Non-Goals

This refactor should not:

- add a second live source yet;
- change beta legal posture;
- redesign the Google Sheets schema now;
- introduce SQLite yet;
- implement concurrency yet;
- change alert copy or business logic unless needed for compatibility.

---

## 5. Current Constraints

- `cattle_scout_log` dedup remains keyed by `(url, user_id)`.
- `cattle_scout_listings` remains append-only and AuctionsPlus-shaped.
- `TEST_MODE` stays a separate beta decision.
- Soft-gate matching behaviour must remain unchanged.
- Stud/commercial classification and AuctionsPlus parsing rules remain source-specific behaviour, not generic matching logic.

---

## 6. Proposed Runtime Shape

### 6.1 High-level flow

Proposed run flow:

1. load all active users
2. load dedup log
3. load model fair value
4. collect source candidates once per source
5. scrape and normalise listings once per source
6. combine all normalised listings into one shared list
7. evaluate every user against every shared listing
8. send/log alerts per `(listing, user)`

This becomes:

```text
discover once -> scrape once -> normalise once -> match many users
```

### 6.2 Minimal boundary

Introduce two internal stages:

- `source ingestion`
- `user matching and alerting`

That is enough separation for Phase 1.5 / Phase 2 without overbuilding.

---

## 7. Proposed Internal Data Model

### 7.1 Shared per-run listing object

The runtime should operate on a shared normalised listing dict after source parsing.

Minimum required fields for Phase 1 refactor:

```python
{
    "source": str,
    "source_type": str,
    "url": str,
    "listing_id": str | None,
    "listing_type": str,
    "listing_category": str | None,
    "title": str | None,
    "sale_name": str | None,
    "sale_date": str | None,
    "lot_number": int | None,
    "state": str | None,
    "location": str | None,
    "vendor": str | None,
    "class": str | None,
    "sex": str | None,
    "num_head": int | None,
    "breed": str | None,
    "breed_groups": str | None,
    "avg_weight_kg": float | None,
    "weight_at_assessment_kg": float | None,
    "weight_min": float | None,
    "weight_max": float | None,
    "weight_range_kg": float | None,
    "delivery_adjustment_pct": float | None,
    "liveweight_gain_per_day": float | None,
    "dressing_pct": float | None,
    "fat_score": int | None,
    "age_min_months": int | None,
    "age_max_months": int | None,
    "hours_off_feed": float | None,
    "assessment_date": str | None,
    "horn_status": str | None,
    "temperament": str | None,
    "store_condition": str | None,
    "is_EU": bool | None,
    "is_NE": bool | None,
    "is_LPA": bool | None,
    "is_MSA": bool | None,
    "has_WHP": bool | None,
    "HGP_free": bool | None,
    "lifetime_traceable_pct": int | None,
    "price_per_head": float | None,
    "price_c_kg": float | None,
    "sale_type_pricing": str | None,
    "catalogue_pending": bool | None,
}
```

This should stay compatible with the current `log_listing()`, `log_listing_full()`, `listing_match()`, and `score_listing()` functions with minimal changes.

### 7.2 Source-specific extras

Optional source-only fields can be kept outside the current sheet contract for now, for example:

- `source_record_id`
- `source_confidence`
- `permission_status`
- `catalogue_url`
- `notes_raw`

Do not force these into the Sheets schema during this refactor.

---

## 8. Proposed Source Abstraction

### 8.1 Smallest useful interface

The first abstraction should be function-based, not class-heavy.

Suggested pattern:

```python
def get_source_definitions():
    return [
        {
            "name": "auctionsplus",
            "enabled": True,
            "discover_listing_urls": get_auctionsplus_listing_urls,
            "scrape_listing": scrape_auctionsplus_listing,
        }
    ]
```

Each source module should own:

- candidate URL discovery;
- request headers/session usage;
- source-specific parsing/classification;
- output as one shared normalised listing dict.

The main runtime should own:

- loading configs;
- user matching;
- dedup;
- scoring;
- alerting;
- sheet writes;
- run summaries.

### 8.2 AuctionsPlus mapping

Existing functions can be adapted rather than rewritten:

- `get_listing_urls()` -> `get_auctionsplus_listing_urls()`
- `scrape_listing()` -> `scrape_auctionsplus_listing()`
- `scrape_commercial_listing()` remains source-specific
- `scrape_stud_listing()` remains source-specific

This keeps the current parser stable while giving it a clearer boundary.

---

## 9. Proposed Main Loop

### 9.1 New structure

Suggested structure:

```python
def collect_source_listings(source_defs):
    all_listings = []
    for source_def in source_defs:
        if not source_def["enabled"]:
            continue
        urls = source_def["discover_listing_urls"]()
        for url in urls:
            listing = source_def["scrape_listing"](url)
            if listing:
                all_listings.append(listing)
            time.sleep(REQUEST_DELAY)
    return all_listings
```

Then:

```python
shared_listings = collect_source_listings(get_source_definitions())

for user_config in all_users:
    for listing in shared_listings:
        existing_status = log_status.get((listing["url"], user_config["user_id"]))
        ...
        matched, reason = listing_match(listing, user_config)
        ...
```

### 9.2 Important behavioural change

`scrape_listing()` must stop depending on per-user config for parsing decisions.

Today it uses `config` mainly for stud/bull skip logic.

After refactor:

- source ingestion should parse what the source exposes;
- user-specific inclusion decisions should happen in matching.

That means obvious source-level skips are still allowed, but user-specific parser branching should be removed from ingestion.

---

## 10. Handling Stud/Bull Logic Safely

The current `scrape_listing(url, config)` performs a config-aware skip when the URL or content looks like a stud listing and the current user does not include bulls/stud.

That behaviour becomes incorrect once ingestion is shared across users.

Recommended change:

1. ingestion always classifies the listing faithfully;
2. ingestion may still skip clearly irrelevant non-cattle or broken pages;
3. `listing_match()` becomes the only place where user-specific bull/stud inclusion gates fire.

This is the cleanest way to avoid:

- scraping the same stud page for one user but not another;
- source ingestion behaviour changing based on whichever user happens to be processed first.

---

## 11. Session and Request Handling

As part of this refactor, add `requests.Session()` usage for AuctionsPlus.

Minimum change:

- one session per source per run;
- source-specific headers set once;
- `REQUEST_DELAY` preserved between listing detail requests.

This is useful now and stays compatible with later bounded concurrency if needed.

---

## 12. Compatibility With Current Sheets

No sheet schema changes are required for this refactor.

Compatibility rules:

- `url` remains the dedup key component
- `user_id` remains added only at logging time
- `cattle_scout_listings` still stores one row per user-alert event
- the listing object remains shaped so `log_listing_full()` can keep writing the current schema

This keeps the refactor operationally small.

---

## 13. Implementation Plan

### Phase A - narrow internal refactor

1. extract AuctionsPlus discovery into a source-specific function name
2. extract AuctionsPlus scrape dispatcher into a source-specific function name
3. remove per-user config dependency from source scraping
4. add shared `collect_source_listings()` stage
5. move user loop to operate on shared listings

### Phase B - safety and observability

6. add source/run counters:
   - URLs discovered
   - listings scraped successfully
   - listings skipped
   - listings matched per user
7. add duplicate URL guard within a run
8. keep current print-level observability; do not add new infrastructure

### Phase C - post-refactor verification

9. run a local dry run with current single user
10. verify sheet writes still align correctly
11. verify WATCHING/ALERTED dedup still works
12. then validate with 2+ active users

---

## 14. Test and Validation Checklist

Before merging the runtime refactor:

1. single-user local run still completes without schema drift
2. listing counts are similar to pre-refactor runs
3. one known matching listing still produces expected WATCHING or ALERTED behaviour
4. one known rejected listing still shows a correct rejection reason
5. no listing page is fetched more than once per run for the same source
6. `cattle_scout_log` still dedups by `(url, user_id)`
7. a second active user can receive an alert for the same listing independently

---

## 15. Recommended Next Steps After This Spec

Priority order:

1. implement this narrow runtime refactor in `cattle_scout.py`
2. validate with 2+ active users
3. only then choose the first non-AuctionsPlus ingestion spike
4. keep `Stockplace` as the first likely parser spike
5. decide later whether source metadata belongs in Sheets or a small local store

---

## 16. Decision

Recommended decision for the next engineering pass:

Implement the scrape-once / match-many refactor before:

- adding a second live source, or
- onboarding multiple real beta users at the same time.

That gives Signal Scout a cleaner runtime without dragging the project into premature infrastructure work.
