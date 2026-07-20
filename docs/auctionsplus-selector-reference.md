# AuctionsPlus HTML Selector Reference
**Drumquil Signal — Cattle Scout**
Version 2.0 | May 2026 | Updated from live page inspection (inspect_fields.py)

---

## Context

This document records the confirmed HTML structure of AuctionsPlus listing pages, derived from direct inspection of static HTML returned by BeautifulSoup — without JavaScript execution. All field extraction in `cattle_scout.py` is based on this reference.

**Critical finding (confirmed Chat 6):** All field data — including breed, fat score, weight, age, accreditations, and all extended fields — is present in the **static HTML** and accessible to BeautifulSoup. No JS rendering is required. Expandable sections appear collapsed in the browser but their content is present in the raw HTML.

---

## Page Types and Routing

### URL patterns

| Pattern | Meaning |
|---|---|
| `/auctions/cattle/{sale-slug}/{lot-slug}/assessed/{auction-id}-{lot-id}/browse` | Assessed commercial mob — always commercial |
| `/auctions/cattle/{sale-slug}/{lot-slug}/described/{auction-id}-{lot-id}/browse` | Described commercial mob — always commercial |
| `/auctions/cattle/{sale-slug}/{lot-slug}/listing/{auction-id}-{lot-id}/browse` | Ambiguous — stud OR commercial saleyard dispersal |

### Two-step routing (v2.0)

**Step 1 — Slug pre-filter (no HTTP request):** `is_stud_sale_url()` checks the URL against `STUD_SALE_SLUG_MARKERS`. If matched AND bulls/stud are disabled, skip without scraping.

```python
STUD_SALE_SLUG_MARKERS = [
    "bull-sale", "stud-genetics", "genetics-sale", "stud-sale",
    "female-sale", "heifer-sale", "on-property-bull",
    "annual-on-property", "weekly-cattle-stud",
]
```

**Step 2 — Content classification (post-fetch):** `detect_listing_type(url, soup, page_text)`:
- `/assessed/` → always `"commercial"`
- EBV data (`\bEBV\b|\bASBV\b`) present → always `"stud"`
- `/listing/` + head count > 1 in page_text → `"commercial"` (saleyard dispersal)
- `/listing/` + individual animal slug + no head count → `"stud"`
- Anything else → `"commercial"` (let filters decide)

**Important:** `/listing/` URLs are NOT reliably stud-only. The Mortlake store cattle sale (`wvlx-mortlake-may-21st-store-cattle-sale`) uses `/listing/` for commercial mob lots. URL path is a hint only — content classification takes precedence.

**Beta runtime note (July 2026):** `listing_type="stud"` no longer means
`listing_category="bull"`. Stud/genetics detail pages are parsed by stock type
so female-sale lots can surface as `breeding_female` or `cow_calf_unit` and
then pass through the normal buyer category, breed, head-count, and known-age
gates.
Unknown stud records stay unsupported rather than being silently treated as
bulls. Sale slugs such as `bull-female-sale` are not category evidence by
themselves; title and visible page text must carry the female or bull signal.

---

## Catalogue Release Timing

AuctionsPlus assessed listings carry full catalogue data (weight, breed, fat score, age, accreditations) before the auction. The catalogue is released some days before the sale date — not after. **Price is only available post-auction** — there is no pre-auction asking price on AuctionsPlus assessed listings. It is a bid-based system.

**catalogue_pending detection:**
```python
catalogue_pending = "Auction Catalogue is not released yet" in page_text
```
This string appears verbatim in static HTML when the catalogue has not yet been released for a specific lot. It is absent once the catalogue is live. Different sales on the same platform may release at different times (e.g. Tas Cattle Sale releases before Weaner & Yearling Sale).

**Two-stage alert system:**
- **Stage 1 (WATCHING):** `catalogue_pending = True` — pre-catalogue criteria pass → lightweight alert
- **Stage 2 (ALERT):** `catalogue_pending = False` — full criteria confirmed → full details alert

---

## Field Extraction Method (v2.0)

All post-catalogue field extraction uses **line-based parsing** on `page_lines` (clean non-empty lines split from `page_text`). This replaced the previous approach of HTML selectors with `field-id` attributes, which were found to be absent or unreliable in the static HTML.

```python
page_lines = [l.strip() for l in page_text.split("\n") if l.strip()]

def lines_after(header, page_lines, n=5):
    for i, line in enumerate(page_lines):
        if header.lower() in line.lower():
            return page_lines[i+1:i+1+n]
    return []
```

---

## Confirmed Field Structures — Commercial Lot Page

All structures confirmed from `inspect_fields.py` runs against:
- Tylden VIC (32 Feeder Steers, catalogue released, full data) — 300 lines
- Campania TAS (12 Weaned Heifers, catalogue released, full data) — 100 lines
- Alpha QLD (31 Heifers, catalogue pending) — 100 lines

---

### Title

Not in `<h1>`. AuctionsPlus uses a styled div:

```python
title_div = soup.find("div", class_=lambda c: c and "text-headline-sm" in c and "font-medium" in c)
title = title_div.get_text(strip=True)
```

Fallback: `<title>` tag — format `"32 Feeder Steers | AuctionsPlus"`, split on `|`.

---

### Location

```python
loc_field = soup.find(attrs={"field-id": "Location"})
```

`field-id="Location"` is confirmed present in static HTML. Use `soup.find(attrs={"field-id": "Location"})` — tag-free form traverses the full DOM.

State extraction — three-pass approach:
1. Strip dotted abbreviations (S.A. → SA), then regex `\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b`
2. Spelled-out state names (Tasmania → TAS, Victoria → VIC, etc.)
3. `REGION_STATE_MAP` lookup for region-only strings (e.g. "N.W. Slopes & Plains" → NSW)

**Do NOT use `(SYD, NSW) AEST`** — this is AuctionsPlus's fixed timezone marker, present on every listing regardless of property location.

---

### Sale Name

From breadcrumb link — static HTML, reliable:

```python
for a in soup.find_all("a", href=True):
    if "auction-results/cattle/" in a.get("href", ""):
        sale_name = a.get_text(strip=True)
        break
```

Confirmed sale names: `"Weaner & Yearling Sale"`, `"Eastern States Cattle Sale"`, `"Tas Cattle Sale"`, `"Mortlake May 21st Store Cattle Sale"`.

---

### Vendor / Agent Name

```python
for a in soup.find_all("a", href=True):
    if "/agentlistings/" in a.get("href", ""):
        vendor_div = a.find("div")
        vendor = vendor_div.get_text(strip=True)
        break
```

---

### Sale Date

```python
re.search(r"((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\d{1,2}\s+\w+\s+\d{4})", page_text)
```

Always apply `re.sub(r"\s+", " ", match).strip()` — date string may contain embedded newlines.

---

### Lot Number

```python
for line in page_lines[:30]:
    lot_m = re.match(r"^Lot\s+(\d+)$", line.strip())
    if lot_m:
        lot_number = int(lot_m.group(1))
        break
```

Present on Tas Cattle Sale listings (e.g. "Lot 335"). Not all sale types include lot numbers.

---

### Average Weight (delivery-adjusted)

Page structure (confirmed):
```
At Est Kill/Del Date
23/05/2026 (2 days)
Live
350.1 kgs based on -3% Del. Adj.   ← target
```

```python
for i, line in enumerate(page_lines):
    if "At Est Kill/Del Date" in line or "Del. Adj." in line.lower():
        for nearby in page_lines[i:i+6]:
            w = re.search(r"(\d{2,4}(?:\.\d+)?)\s*kgs?\b", nearby)
            if w:
                avg_weight_kg = float(w.group(1))
                break
```

The delivery-adjusted weight is the correct buying weight. The assessment weight (higher, pre-adjustment) is also captured separately as `weight_at_assessment_kg`.

---

### Weight Range at Delivery

Page structure (confirmed):
```
Weight Range
297 kgs to 432 kgs Liveweight at delivery   ← target
```

```python
re.search(
    r"(\d{2,4}(?:\.\d+)?)\s*kgs?\s+to\s+(\d{2,4}(?:\.\d+)?)\s*kgs?\s+Liveweight at delivery",
    page_text, re.IGNORECASE
)
```

**Previous parser used `(min)` and `(max)` literals — these do not exist in the page. Old approach was always wrong.**

---

### Delivery Adjustment %

```python
re.search(r"([-+]?\d+(?:\.\d+)?)\s*%\s*Del(?:\.|ivery)?\s*Adj", page_text, re.IGNORECASE)
```

Appears inline in the delivery weight line: `"350.1 kgs based on -3% Del. Adj."`

---

### Liveweight Gain Per Day

```python
re.search(
    r"(?:Live\s+weight\s+gain|Weight\s+Gain)[:\s]+([+-]?\d+(?:\.\d+)?)\s*(?:kgs?|g)(?:/day)?",
    page_text, re.IGNORECASE
)
```

---

### Hours Off Feed

Page structure:
```
Hours off Feed
5 hours   ← next line
```

```python
for line in lines_after("Hours off Feed", page_lines, n=3):
    h = re.search(r"(\d+(?:\.\d+)?)\s*hours?", line, re.IGNORECASE)
    if h:
        hours_off_feed = float(h.group(1))
        break
```

Standard is 8 hours. Values below 8 hours indicate the liveweight may be inflated (gut fill not fully voided). The `send_alert()` function flags non-standard hours with a ⚠️ warning.

---

### Dressing Percentage

```python
re.search(r"Est\.?\s*Av\.?\s*Drs\.?\s*(\d+(?:\.\d+)?)\s*%", page_text, re.IGNORECASE)
```

Appears inline: `"166.0 kgs (Est. Av. Drs. 46%)"`.

---

### Breed

Page structure (confirmed, lines 135–140 of Tylden 300-line output):
```
Breeds
Sire
Dam
32 Head        ← head count line
Angus          ← sire breed
Angus          ← dam breed
```

For mixed mobs, multiple head/sire/dam groups follow in sequence.

```python
for i, line in enumerate(page_lines):
    if line.strip() == "Breeds":
        j = i + 1
        while j < min(i + 40, len(page_lines)):
            head_m = re.match(r"^(\d+)\s+Head$", page_lines[j].strip(), re.IGNORECASE)
            if head_m:
                # Next two non-empty lines are sire and dam breed
                ...
```

**Important:** `field-id="Breed"` attribute is confirmed absent from the static HTML. Previous parser using this selector never worked. The breed data is in plain text lines only.

Pure detection: sire breed == dam breed → pure. Otherwise → `"{sire} Cross"`.
Mixed mob: find dominant group by head count, classify from that group.

---

### Fat Score

Page structure (confirmed, lines 81–82 of Tylden output):
```
Fat Scores
2              ← value on NEXT line (not inline)
Totals
```

```python
for line in lines_after("Fat Scores", page_lines, n=3):
    fat_m = re.match(r"^(\d)\b", line.strip())
    if fat_m:
        fat_score = int(fat_m.group(1))
        break
```

**Previous regex `fat\s*score\s*(\d)` required the number on the same line. This format does not exist — old approach never matched.**

Fat score scale: 1 (0–2mm) through 6 (33mm+). See AuctionsPlus Assessment Manual 2024 for full definitions.

---

### Age

```python
re.search(r"(\d+)\s*[-–]\s*(\d+)\s*[Mm]onths?", page_text)
```

Format confirmed: `"14 - 15 Months"`. Working correctly in v1.7, unchanged.

---

### Horn Status

```python
horn_terms = ["Polled", "Horned", "Tipped", "Scurred", "Dehorned"]
for line in page_lines:
    for term in horn_terms:
        if re.search(r"\b" + term + r"\b", line, re.IGNORECASE):
            horn_status = term.lower()
```

Appears as `"32 Polled"` in the page lines near the breed section.

---

### Temperament

Score map: Docile=5, Quiet=4, Slightly Stirry=3, Stirry=2, Aggressive=1. Dominant (highest score found) wins.

```python
for term, score in temp_score_map.items():
    if re.search(r"\b" + term + r"\b", page_text, re.IGNORECASE):
        if score > best_score:
            best_score = score
            temperament = term
```

---

### Accreditations

Page structure (confirmed):
```
Accreditation(s)
LPA
Verification(s)
Greenham NEVER EVER
```

**Block-scoped extraction — do NOT use freetext regex on full page_text.** The page footer and Featured Lots section contain EU, NE, WHP tokens from other listings, causing false positives with freetext approach.

```python
accred_block = []
in_accred = False
for line in page_lines:
    if "Accreditation" in line or "Verification" in line:
        in_accred = True
        continue
    if in_accred:
        if any(h in line for h in ["Delivery", "Trading Terms", "NLIS", "Movement", "Special", "Sale Types", "Featured"]):
            break
        accred_block.append(line)

accred_text = " ".join(accred_block).upper()
is_EU  = "EU" in accred_text and "EUROPEAN" not in accred_text
is_NE  = "NEVER EVER" in accred_text or " NE " in accred_text
is_LPA = "LPA" in accred_text
is_MSA = "MSA" in accred_text
has_WHP = bool(re.search(r"\bWHP\b", accred_text))
```

Canonical accreditation tokens (from AuctionsPlus Individual Assessment Form 2026): EU, LPA, Grass-Fed, Greenham Never Ever (NE), MSA, Organic Certified, Antibiotic Free, WHP.

---

### HGP Status

```python
hgp_lines = lines_after("HGP", page_lines, n=4)
for line in hgp_lines:
    if re.search(r"not been treated|HGP.{0,10}free|never.*treated", line, re.IGNORECASE):
        HGP_free = True
    elif re.search(r"\byes\b|\btreated\b", line, re.IGNORECASE):
        HGP_free = False
```

HGP-free is required for Greenham Never Ever accreditation. If NE accreditation is confirmed and HGP_free not explicitly parsed, set HGP_free = True.

---

### Lifetime Traceable %

```python
re.search(r"(\d+)\s*%\s+of\s+cattle.{0,30}Lifetime\s+Traceable", page_text, re.IGNORECASE)
```

Appears as: `"100 % of cattle in this lot are Lifetime Traceable"`.

---

### Price

AuctionsPlus assessed listings are bid-based. **No asking price exists pre-auction.** Post-auction price appears as $/head or c/kg after the lot closes.

Finance widget shows `$0.49/day/head` or `$0.68/day/head` — these are not prices. Parser excludes values under $100:

```python
for m in re.finditer(r"\$\s*([\d,]+(?:\.\d+)?)\s*/?\s*[Hh]ead", page_text):
    val = float(m.group(1).replace(",", ""))
    if val > 100:
        price_per_head = val
        break
```

---

## Search Results Page

**URL:** `https://auctionsplus.com.au/browse/livestock/cattle?category=Steer-Heifer&mapView=0&page={n}`

The broad cattle browse URL can prioritise stud/bull sale listings ahead of commercial steer/heifer lots. Use the category-specific URL for the Phase 1 commercial buyer alert path.

```python
lot_links = soup.find_all("a", href=re.compile(r"/auctions/cattle/.+/browse"))
```

Typically 38 listings per page. Stop when `lot_links` is empty. Prepend `https://auctionsplus.com.au` to each relative href.

---

## Known Rendering Behaviour

| Field | In Static HTML | Notes |
|---|---|---|
| Title div | ✅ Yes | `text-headline-sm` class — NOT in h1 |
| field-id="Location" | ✅ Yes | Confirmed present |
| field-id="Breed" | ❌ No | Attribute absent — use line-based parsing on page_lines |
| field-id="Weight" | ✅ Partial | Attribute present but value parsing unreliable — use line-based approach |
| Breed section | ✅ Yes | Plain text lines: Breeds → Sire → Dam → N Head → breed → breed |
| Fat score | ✅ Yes | Plain text: "Fat Scores" header, value on next line |
| Weight range | ✅ Yes | "X kgs to Y kgs Liveweight at delivery" |
| Accreditations | ✅ Yes | In Accreditation(s) / Verification(s) blocks — NOT freetext |
| Agent contact phone/email | ❌ No | JS-rendered only |
| Price (pre-auction) | ❌ No | Not available pre-auction — bid-based system |
| Price (post-auction) | ✅ Yes | $/head or c/kg after sale closes |
| Finance widget prices | ✅ Yes | Present but must be excluded ($0.49/day/head etc.) |

---

*Drumquil Signal | AuctionsPlus HTML Selector Reference v2.0 | May 2026*
