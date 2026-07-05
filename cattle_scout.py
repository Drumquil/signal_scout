"""
cattle_scout.py
Drumquil Signal — Cattle Scout Phase 1
Scrapes AuctionsPlus public cattle listings, filters against user-defined
buying criteria stored in Google Sheets, and sends WhatsApp alerts via Twilio.

Single-stage alert system:
  Listing appears → parse all available fields → match against full buyer
  criteria → send alert. AuctionsPlus assessed listings carry full catalogue
  data (weight, breed, fat score, age) before the auction. There is no
  pre-catalogue period. Price is only available post-auction.

Three-class detection hierarchy (applied in order, first match wins):
  1. Cow-and-calf unit  — title contains "&" + "calves" or "calves at foot" in pre-auction text
  2. Breeding female    — title contains joining/pregnancy status qualifier (PTIC, NSM, AID, etc.)
  3. Commercial store   — weaners, yearlings, feeders, backgrounders, etc.

Multi-user architecture (v2.4 runtime, v2.3 Sheet schema):
  cattle_scout_config tab uses row-block-per-user layout.
  Column A = user_id, Column B = setting, Column C = value.
  load_config() returns a list of dicts — one per active user.
  The main loop iterates over all users. Deduplication is per-user:
  a listing that alerted User 1 will still alert User 2 if they match.
  Each user has their own twilio_to field in their config block.

Requires:
  - pip install python-dotenv
  - A .env file in the same folder containing TWILIO_* and GOOGLE_SHEETS_CREDS_FILE.
    See .env.example for the required variables.

Author: Tom Flanagan
Version: 2.4 — July 2026
"""

import json
import os
from pathlib import Path
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from gspread.exceptions import WorksheetNotFound
from twilio.rest import Client
from datetime import datetime, timezone
from dotenv import load_dotenv
from sheets_client import get_credentials_file, open_spreadsheet

# Load credentials from the .env file in the same folder.
# Must run BEFORE any os.getenv() calls below.
load_dotenv()

# Force UTF-8 stdout/stderr on Windows consoles that default to cp1252.
# Prevents UnicodeEncodeError when printing box-drawing chars or emojis.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────
# CREDENTIALS — loaded from .env (never hardcoded)
# ─────────────────────────────────────────────

# Twilio WhatsApp — rotate auth token via Twilio console if exposed
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.getenv("TWILIO_FROM")
TWILIO_WHATSAPP_MODE = os.getenv("TWILIO_WHATSAPP_MODE", "").strip().lower()

# ─────────────────────────────────────────────
# BEHAVIOURAL CONFIG — kept in source for visibility
# ─────────────────────────────────────────────

SPREADSHEET_NAME = "drumquil_scout"
LOG_TAB          = "cattle_scout_log"
LISTINGS_TAB     = "cattle_scout_listings"   # v2.2: full analytical dataset tab
CONFIG_TAB       = "cattle_scout_config"
MODEL_TAB        = "cattle_model_output"

# AuctionsPlus search — steer/heifer category; regional and buyer filtering done in script
SEARCH_URL = (
    "https://auctionsplus.com.au/browse/livestock/cattle"
    "?category=Steer-Heifer"
    "&mapView=0"
)
AUCTIONSPLUS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MAX_PAGES     = 5
REQUEST_DELAY = 3
TEST_MODE     = os.getenv("TEST_MODE", "TRUE").strip().upper() in ("1", "TRUE", "YES", "Y")
UNDERVALUED_THRESHOLD = 0.10
OVERVALUED_THRESHOLD  = 0.10
BATCH_WRITE_RETRIES   = 4
BATCH_WRITE_BACKOFFS  = [15, 45, 90, 180]
MODEL_FAIR_VALUE_MIN_C_KG = 100
MODEL_FAIR_VALUE_MAX_C_KG = 2000
ENABLE_AUTHORIZED_NOTICE_SOURCE = os.getenv("ENABLE_AUTHORIZED_NOTICE_SOURCE", "FALSE").upper() == "TRUE"
AUTHORIZED_NOTICE_SOURCE_DIR = os.getenv("AUTHORIZED_NOTICE_SOURCE_DIR", "authorized_notice_samples")
ENABLE_STOCKPLACE_SOURCE = os.getenv("ENABLE_STOCKPLACE_SOURCE", "FALSE").upper() == "TRUE"
STOCKPLACE_INDEX_URL = os.getenv("STOCKPLACE_INDEX_URL", "https://www.stockplace.com.au/stock")
ENABLE_RMA_SOURCE = os.getenv("ENABLE_RMA_SOURCE", "FALSE").upper() == "TRUE"
RMA_INDEX_URL = os.getenv("RMA_INDEX_URL", "https://www.rma.com.au/sales/cattle")

SHARED_LISTING_DEFAULTS = {
    "source": None,
    "source_type": None,
    "source_record_id": None,
    "source_confidence": None,
    "permission_status": None,
    "sender_email": None,
    "received_at": None,
    "attachment_name": None,
    "message_id": None,
    "catalogue_url": None,
    "notes_raw": None,
    "listing_id": None,
    "listing_type": "commercial",
    "listing_category": "commercial",
    "url": None,
    "title": "Unknown",
    "sale_name": "",
    "sale_date": "",
    "lot_number": None,
    "catalogue_pending": False,
    "vendor": "Unknown",
    "pre_auction_text": "",
    "num_head": None,
    "num_calves": None,
    "state": "Unknown",
    "location": "Location unknown",
    "class": "",
    "sex": None,
    "breed": "Unknown",
    "breed_groups": [],
    "horn_status": None,
    "store_condition": None,
    "temperament": None,
    "avg_weight_kg": None,
    "weight_at_assessment_kg": None,
    "weight_min": None,
    "weight_max": None,
    "weight_range_kg": None,
    "delivery_adjustment_pct": None,
    "liveweight_gain_per_day": None,
    "dressing_pct": None,
    "fat_score": None,
    "age_min_months": None,
    "age_max_months": None,
    "hours_off_feed": None,
    "assessment_date": None,
    "is_EU": False,
    "is_NE": False,
    "is_LPA": False,
    "is_MSA": False,
    "has_WHP": False,
    "HGP_free": None,
    "lifetime_traceable_pct": None,
    "price_per_head": None,
    "price_c_kg": None,
    "sale_type_pricing": None,
}

# ─────────────────────────────────────────────
# GOOGLE SHEETS TAB SCHEMAS (v2.3)
# ─────────────────────────────────────────────

LOG_HEADER_V23 = [
    "user_id", "url", "status", "title", "category", "class", "breed", "head",
    "avg_weight_kg", "weight_range_kg", "fat_score", "age", "accreditations",
    "price_c_kg", "location", "vendor", "sale_date", "flag", "logged_at",
]

LOG_HEADER_DISPLAY_V23 = [
    "user_id", "URL", "Status", "Title", "Category", "Class", "Breed", "Head",
    "Avg Weight", "Weight Range", "Fat Score", "Age", "Accreditations",
    "Price c/kg", "Location", "Vendor", "Sale Date", "Flag", "Logged At",
]

LISTINGS_HEADER_V23 = [
    "user_id",
    "url", "logged_at", "status", "sale_name", "sale_date",
    "lot_number", "listing_category", "class", "title", "num_head",
    "state", "location", "vendor", "breed", "breed_groups",
    "avg_weight_kg", "weight_at_assessment_kg", "weight_min",
    "weight_max", "weight_range_kg", "delivery_adjustment_pct",
    "liveweight_gain_per_day", "dressing_pct", "fat_score",
    "age_min_months", "age_max_months", "hours_off_feed",
    "assessment_date", "horn_status", "temperament",
    "store_condition", "is_EU", "is_NE", "is_LPA", "is_MSA",
    "has_WHP", "HGP_free", "lifetime_traceable_pct",
    "price_per_head", "price_c_kg", "sale_type_pricing",
    "valuation_flag", "fair_value_at_alert", "catalogue_pending",
]

LISTINGS_HEADER_NO_USER_ID = LISTINGS_HEADER_V23[1:]


def get_or_create_worksheet(spreadsheet, title, rows, cols):
    """Get a worksheet by title, or create it if missing."""
    try:
        return spreadsheet.worksheet(title)
    except WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
        print(f"  ✅  Created missing worksheet: {title}")
        return ws


def header_matches(existing_header, expected_header):
    return existing_header[: len(expected_header)] == expected_header


def ensure_header_row(worksheet, expected_header, accepted_headers=None):
    """
    Ensure row 1 contains the expected header.

    If the sheet is empty, inserts the header at row 1.
    If row 1 exists but doesn't match, raise RuntimeError rather than silently
    writing data into a mismatched schema.
    """
    existing = worksheet.row_values(1)
    if not existing or not any(v.strip() for v in existing if isinstance(v, str)):
        worksheet.insert_row(expected_header, index=1)
        print(f"  ✅  Header row written: {worksheet.title}")
        return

    valid_headers = [expected_header] + (accepted_headers or [])
    if not any(header_matches(existing, header) for header in valid_headers):
        raise RuntimeError(
            f"Worksheet '{worksheet.title}' has an unexpected header row.\n"
            f"Expected: {expected_header}\n"
            f"Found:    {existing}\n"
            "Fix the tab schema (or create a new empty tab) before running again."
        )


def ensure_listings_header(worksheet):
    """
    Ensure cattle_scout_listings uses the v2.3 user_id-prefixed schema.

    Older v2.2 sheets started at url. When found, insert user_id as column A so
    existing analytical rows are preserved and future rows align correctly.
    """
    existing = worksheet.row_values(1)
    if not existing or not any(v.strip() for v in existing if isinstance(v, str)):
        worksheet.insert_row(LISTINGS_HEADER_V23, index=1)
        print(f"  ✅  Header row written: {worksheet.title}")
        return

    if header_matches(existing, LISTINGS_HEADER_V23):
        return

    if header_matches(existing, LISTINGS_HEADER_NO_USER_ID):
        worksheet.insert_cols([["user_id"]], col=1)
        print("  ✅  Migrated cattle_scout_listings header to v2.3 user_id layout.")
        return

    ensure_header_row(worksheet, LISTINGS_HEADER_V23)


def build_requests_session(headers=None):
    """Create a per-source session for one run."""
    session = requests.Session()
    if headers:
        session.headers.update(headers)
    return session


def normalise_shared_listing(listing, source_def):
    """
    Fill in shared runtime defaults and attach source metadata.

    Existing AuctionsPlus parsers can keep returning sparse source-specific
    dicts; this normaliser makes them safe for shared matching/logging.
    """
    shared = dict(SHARED_LISTING_DEFAULTS)
    shared.update(listing or {})

    shared["source"] = source_def["name"]
    shared["source_type"] = source_def["source_type"]
    shared["permission_status"] = source_def.get("permission_status")
    shared["source_confidence"] = source_def.get("source_confidence")
    shared["catalogue_url"] = shared.get("catalogue_url") or shared.get("url")

    if not shared.get("url"):
        return None

    if shared.get("source_record_id") is None:
        shared["source_record_id"] = shared.get("listing_id")

    if shared.get("breed_groups") is None:
        shared["breed_groups"] = []

    return shared


def parser_record_to_shared_listing(record):
    """
    Map a standalone parser-spike record into the shared runtime listing shape.

    This lets new source modules reuse the parser spike normalised contract
    without forcing AuctionsPlus-specific fields into the parser itself.
    """
    if not isinstance(record, dict):
        return None

    return {
        "url": record.get("source_url"),
        "source_record_id": record.get("source_record_id"),
        "source_confidence": record.get("source_confidence"),
        "catalogue_url": record.get("catalogue_url"),
        "title": record.get("listing_title") or record.get("sale_name") or "Unknown",
        "sale_name": record.get("sale_name") or record.get("listing_title") or "",
        "sale_date": record.get("sale_date") or "",
        "listing_type": "commercial",
        "listing_category": record.get("listing_category") or "commercial",
        "catalogue_pending": bool(record.get("catalogue_pending", False)),
        "vendor": (
            record.get("agent_name")
            or record.get("contact_name")
            or record.get("source_name")
            or "Unknown"
        ),
        "pre_auction_text": record.get("class_breakdown_raw") or record.get("notes_raw") or "",
        "num_head": record.get("num_head"),
        "state": record.get("state") or "Unknown",
        "location": record.get("location") or "Location unknown",
        "class": record.get("class") or "",
        "sex": record.get("sex"),
        "breed": record.get("breed") or "Unknown",
        "breed_groups": record.get("breed_groups") or [],
        "avg_weight_kg": record.get("avg_weight_kg"),
        "weight_min": record.get("weight_min"),
        "weight_max": record.get("weight_max"),
        "weight_range_kg": record.get("weight_range_kg"),
        "price_per_head": record.get("price_per_head"),
        "price_c_kg": record.get("price_c_kg"),
        "sale_type_pricing": record.get("price_type") or record.get("sale_type"),
        "notes_raw": record.get("notes_raw"),
    }


def get_source_definitions():
    """
    Return the enabled source modules for this run.

    AuctionsPlus stays live by default. Authorised notice ingestion remains
    opt-in until Tom has a real mailbox/feed to point it at.
    """
    sources = [
        {
            "name": "auctionsplus",
            "source_type": "auction_listing",
            "enabled": True,
            "discover_items": get_auctionsplus_listing_urls,
            "scrape_item": scrape_auctionsplus_listing,
            "session_factory": lambda: build_requests_session(AUCTIONSPLUS_HEADERS),
            "permission_status": "permission_first_beta",
            "source_confidence": 0.9,
        },
        {
            "name": "authorised_notice_proto",
            "source_type": "email_notice",
            "enabled": ENABLE_AUTHORIZED_NOTICE_SOURCE,
            "discover_items": get_authorized_notice_paths,
            "scrape_item": scrape_authorized_notice,
            "session_factory": None,
            "permission_status": "authorised_feed_only",
            "source_confidence": 0.45,
        },
        {
            "name": "stockplace",
            "source_type": "agent_direct_listing",
            "enabled": ENABLE_STOCKPLACE_SOURCE,
            "discover_items": get_stockplace_source_pages,
            "scrape_item": scrape_stockplace_source,
            "session_factory": lambda: build_requests_session(AUCTIONSPLUS_HEADERS),
            "permission_status": "permission_first_prototype",
            "source_confidence": 0.5,
        },
        {
            "name": "rma",
            "source_type": "agency_network_sale_index",
            "enabled": ENABLE_RMA_SOURCE,
            "discover_items": get_rma_source_pages,
            "scrape_item": scrape_rma_source,
            "session_factory": lambda: build_requests_session(AUCTIONSPLUS_HEADERS),
            "permission_status": "permission_first_prototype",
            "source_confidence": 0.5,
        },
    ]
    return [source for source in sources if source["enabled"]]

# ─────────────────────────────────────────────
# CLASS DETECTION CONSTANTS
# These are the joining/pregnancy status qualifiers that identify breeding
# females and cow-and-calf units. Checked before commercial class detection.
# Stored here (not in Sheets) because they are structural to the parser logic,
# not user buying criteria.
# ─────────────────────────────────────────────

# Pass 1: cow-and-calf detection — title must contain "&" AND one of these calf indicators
CALF_INDICATORS = ["calves", "calf"]

# Pass 2: breeding female qualifiers — presence in title overrides commercial class detection
# "ai'd" and "ai'" cover the AuctionsPlus rendering of AI-joined heifers
BREEDING_FEMALE_QUALIFIERS = [
    "ptic", "nsm", "aid", "ai'd", "ai'", "caf", "station mated", "joined",
    "mated", "future breeder", "future breeders", "joining"
]


def contains_phrase(text, phrase, allow_plural=False):
    """
    Boundary-aware phrase match for cattle class terms.

    Uses alphanumeric boundaries rather than raw substring matching so town
    names like Braidwood do not trigger the "aid" breeding qualifier.
    """
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    if allow_plural and " " not in phrase and not phrase.endswith("s"):
        if phrase == "calf":
            escaped = r"(?:calf|calves)"
        else:
            escaped = f"{escaped}s?"
    pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    return re.search(pattern, text) is not None


# ─────────────────────────────────────────────
# STEP 1 — LOAD CONFIG FROM GOOGLE SHEETS
# ─────────────────────────────────────────────

def load_config(worksheet_config):
    """
    Reads the cattle_scout_config tab from Google Sheets.

    Tab layout (v2.3 multi-user):
      Row 1: header — user_id | setting | value
      Subsequent rows: one row per setting per user.
      Column A = user_id (e.g. "tom", "user_002")
      Column B = setting name
      Column C = value

    Returns a LIST of dicts — one dict per active user.
    Each dict contains all settings for that user, plus:
      "user_id"   — the user identifier string from column A
      "twilio_to" — the user's WhatsApp number (required field)

    Users with active = FALSE are excluded from the returned list.
    Raises RuntimeError if the Sheet cannot be read.
    """
    try:
        rows = worksheet_config.get_all_values()
    except Exception as e:
        raise RuntimeError(
            f"Could not read config from Google Sheets: {e}\n"
            "Check your service account credentials and network connection."
        ) from e

    # Field type lookup tables — same as before, used when parsing each row's value
    list_fields = {
        "target_states", "target_classes", "target_breeds", "sale_types",
        "breeding_female_classes", "bull_breeds",
        "preferred_vendors", "exclude_vendors"
    }
    bool_fields = {
        "active", "require_EU", "require_NE", "exclude_WHP",
        "include_breeding_females", "include_bulls", "include_stud",
        "include_cow_calf_units", "include_commercial", "bull_require_EBV", "require_vendor",
        "require_HGP_free", "require_polled", "require_quiet",
    }
    numeric_fields = {
        "min_head", "max_head", "min_weight_kg", "max_weight_kg",
        "max_weight_range_kg", "fat_score_max", "age_min_months", "age_max_months",
        "min_fat_score", "max_price_per_head",
        "bull_min_age_months", "bull_max_age_months", "bull_min_weight_kg",
        "bull_max_weight_kg", "bull_max_price_per_head", "bull_min_fat_score",
        "bull_max_fat_score", "bull_EBV_BWT_max", "bull_EBV_200DG_min",
        "bull_EBV_400DW_min", "bull_EBV_600DW_min", "bull_EBV_MILK_min",
        "bull_EBV_DTC_max", "bull_EBV_DOC_min", "bull_EBV_CWT_min",
        "bull_EBV_EMA_min", "bull_EBV_MARB_min", "bull_EBV_RIB_min",
        "bull_EBV_SS_min", "bull_EBV_SRI_min", "bull_EBV_beef_value_min"
    }

    # Build a dict-of-dicts keyed by user_id while reading rows.
    # We preserve insertion order so users alert in the order they appear in the Sheet.
    raw_users = {}   # { user_id: { setting: parsed_value, ... } }
    invalid_numeric_values = {}  # { user_id: [(setting, raw_value), ...] }

    for row in rows[1:]:   # skip header row
        # Each row must have at least 3 columns: user_id | setting | value
        if len(row) < 3:
            continue
        user_id = row[0].strip()
        key     = row[1].strip()
        value   = row[2].strip()
        if not user_id or not key or not value:
            continue

        # Initialise the user's dict on first encounter
        if user_id not in raw_users:
            raw_users[user_id] = {"user_id": user_id}

        # Parse the value into the correct Python type
        if key in list_fields:
            raw_users[user_id][key] = [v.strip().lower() for v in value.split(",") if v.strip()]
        elif key in bool_fields:
            raw_users[user_id][key] = value.upper() == "TRUE"
        elif key in numeric_fields:
            try:
                raw_users[user_id][key] = float(value.replace(",", ""))
            except ValueError:
                raw_users[user_id][key] = None
                invalid_numeric_values.setdefault(user_id, []).append((key, value))
        else:
            raw_users[user_id][key] = value

    # Filter out inactive users and validate required fields.
    # twilio_to is mandatory — a user without it cannot receive alerts.
    active_users = []
    for user_id, cfg in raw_users.items():
        if not cfg.get("active", True):
            print(f"  Config: user '{user_id}' is inactive — skipping.")
            continue
        if not cfg.get("twilio_to"):
            print(f"  ⚠️  Config: user '{user_id}' has no twilio_to — skipping.")
            continue
        if invalid_numeric_values.get(user_id):
            bad_values = ", ".join(
                f"{setting}={raw_value!r}"
                for setting, raw_value in invalid_numeric_values[user_id]
            )
            print(f"  ⚠️  Config: user '{user_id}' has invalid numeric setting(s): {bad_values} — skipping.")
            continue
        active_users.append(cfg)

    print(f"Config loaded: {len(active_users)} active user(s): {[u['user_id'] for u in active_users]}")
    return active_users


# ─────────────────────────────────────────────
# STEP 2 — SCRAPE LISTING URLS
# ─────────────────────────────────────────────

def get_auctionsplus_listing_urls(max_pages=MAX_PAGES, session=None):
    """Collect individual lot URLs from AuctionsPlus search results pages."""
    listing_urls = []
    http = session or requests

    for page in range(1, max_pages + 1):
        url = f"{SEARCH_URL}&page={page}"
        print(f"Scanning page {page}: {url}")
        try:
            response = http.get(url, headers=AUCTIONSPLUS_HEADERS, timeout=15)
        except Exception as e:
            # Network error on a search page — log and skip to next page rather than abort
            print(f"  ⚠️  Network error fetching page {page}: {e} — skipping page.")
            time.sleep(REQUEST_DELAY)
            continue

        if response.status_code != 200:
            print(f"  ⚠️  Page {page} returned status {response.status_code} — stopping.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        lot_links = soup.find_all("a", href=re.compile(r"/auctions/cattle/.+/browse"))

        if not lot_links:
            print(f"  No listings found on page {page} — end of results.")
            break

        for link in lot_links:
            href = link.get("href", "")
            full_url = f"https://auctionsplus.com.au{href}" if href.startswith("/") else href
            if full_url not in listing_urls:
                listing_urls.append(full_url)

        print(f"  Found {len(lot_links)} listings on page {page}.")
        time.sleep(REQUEST_DELAY)

    print(f"\nTotal listing URLs found: {len(listing_urls)}")
    return listing_urls


def get_listing_urls(max_pages=MAX_PAGES, session=None):
    """Backward-compatible wrapper for existing helpers/tests."""
    return get_auctionsplus_listing_urls(max_pages=max_pages, session=session)


def get_authorized_notice_paths():
    """
    Discover local authorised notice samples.

    The prototype source is intentionally file-based and opt-in so we can test
    the shared runtime without scraping a second live platform yet.
    """
    source_dir = Path(AUTHORIZED_NOTICE_SOURCE_DIR)
    if not source_dir.exists():
        print(f"Authorised notice source directory not found: {source_dir}")
        return []

    paths = sorted(source_dir.glob("*.json"))
    print(f"Authorised notice sample files found: {len(paths)}")
    return [str(path) for path in paths]


def get_stockplace_source_pages(session=None):
    """
    Discover the public Stockplace index pages to parse.

    The runtime starts with a single index URL and lets the parser module
    extract multiple listing records from that one page.
    """
    del session
    return [STOCKPLACE_INDEX_URL]


def get_rma_source_pages(session=None):
    """
    Discover the public RMA cattle sales index pages to parse.

    The runtime starts with a single RMA sales page and lets the parser module
    emit multiple sale records from that one source page.
    """
    del session
    return [RMA_INDEX_URL]


# ─────────────────────────────────────────────
# STEP 3 — LISTING TYPE DETECTION
# ─────────────────────────────────────────────

# Sale slug fragments that reliably identify stud/genetics auctions.
# Kept as a helper for source-specific classification work and future
# optimisations, but the shared-listing runtime no longer uses it to make
# user-specific scrape decisions.
# Saleyard dispersals, store cattle sales, and on-property commercial sales
# must NOT appear here.
STUD_SALE_SLUG_MARKERS = [
    "bull-sale",
    "stud-genetics",
    "genetics-sale",
    "stud-sale",
    "female-sale",          # elite female genetics sales
    "heifer-sale",          # stud heifer genetics sales (distinct from commercial heifer lots)
    "on-property-bull",     # on-property bull sales
    "annual-on-property",   # annual on-property stud events
    "weekly-cattle-stud",   # AuctionsPlus weekly stud genetics rotation
]

# Individual animal identifiers — stud lots are typically single animals
# with a registered name slug (e.g. "wattletop-so-right-v27", "alumy-creek-v067").
# Commercial mob lots always start with a number ("32-feeder-steers").
# Used in content-based classification as a supporting signal.
INDIVIDUAL_ANIMAL_SLUG_PATTERN = re.compile(
    r"/auctions/cattle/[^/]+/(?!\d+-)([a-z][a-z0-9\-]+)/(?:listing|assessed|described)/",
    re.IGNORECASE
)


def is_stud_sale_url(url):
    """
    Returns True if the URL's sale slug contains a known stud/genetics marker.
    Used as a cheap pre-scrape filter — no HTTP request needed.
    Only rejects listings that are unambiguously stud genetics sales.
    Errs on the side of scraping: if the slug doesn't match a known stud marker,
    the listing is fetched and content-classified instead.
    """
    url_lower = url.lower()
    return any(marker in url_lower for marker in STUD_SALE_SLUG_MARKERS)


def detect_listing_type(url, soup, page_text):
    """
    Content-based listing type classifier. Runs AFTER fetching the listing.
    Uses URL path as a hint, but content signals take precedence.

    Classification logic:
      1. URL path hint: /assessed/ or /described/ → strong commercial signal
         /listing/ → weak stud signal (also used by some commercial saleyard sales)
      2. Head count: mob of >1 head → commercial signal
         Single head with no mob weight → stud signal
      3. EBV data present → stud signal
      4. Known stud sale slug with no mob head count → stud signal
      5. Individual animal name in slug (non-numeric start) → stud signal

    Returns: "commercial", "stud", or "unknown"
    """
    # URL path hints
    has_assessed   = "/assessed/" in url or "/described/" in url
    has_listing    = "/listing/" in url

    # Content signals
    # Head count from page text — mob lots always show a number of head
    head_match = re.search(r"(\d+)\s+Head\b", page_text, re.IGNORECASE)
    head_count = int(head_match.group(1)) if head_match else None

    # EBV tables are a reliable stud-only signal
    has_ebv = bool(re.search(
        r"\bEBV\b|\bExpected Breeding Value\b|\bASBV\b", page_text, re.IGNORECASE
    ))

    # Individual animal slug: sale slug starts with a letter, not a number
    is_individual_slug = bool(INDIVIDUAL_ANIMAL_SLUG_PATTERN.search(url))

    # Decision tree
    if has_assessed:
        # /assessed/ is always commercial — AuctionsPlus only uses this path
        # for mob lots that have been independently assessed
        return "commercial"

    if has_ebv:
        # EBV data is definitive — stud animals only
        return "stud"

    if has_listing:
        # /listing/ is ambiguous. Resolve by content:
        if head_count and head_count > 1:
            # Mob of animals — commercial saleyard dispersal
            return "commercial"
        elif is_stud_sale_url(url) and not head_count:
            # Some stud lots use numeric identifiers instead of a named slug
            return "stud"
        elif is_individual_slug and not head_count:
            # Named individual with no head count — stud genetics
            return "stud"
        else:
            # Can't determine — scrape as commercial, filters will reject if wrong
            return "commercial"

    # No recognised path pattern — treat as commercial and let filters decide
    return "commercial"


# ─────────────────────────────────────────────
# STEP 4 — CLASS DETECTION (three-pass hierarchy)
# ─────────────────────────────────────────────

def detect_class(title, pre_auction_text):
    """
    Three-pass class detection. Applied in order — first match wins.

    Pass 1 — Cow-and-calf unit:
      Title contains "&" AND (title contains a calf indicator OR pre-auction
      text contains "calves at foot"). E.g. "21 NSM Heifers & 21 Calves".

    Pass 2 — Breeding female:
      Title contains a joining/pregnancy qualifier (PTIC, NSM, AID, etc.).
      These are females that are joined, pregnancy-tested, or AI'd.

    Pass 3 — Commercial store class:
      Linear scan of commercial class keywords in title only.

    Returns a tuple: (detected_class, listing_category)
      detected_class: the specific class string (e.g. "nsm", "weaner", "cow-and-calf")
      listing_category: one of "commercial", "breeding_female", "cow_calf_unit", "bull"
    """
    title_lower = title.lower()
    pre_lower   = pre_auction_text.lower() if pre_auction_text else ""

    # ── Pass 1: Cow-and-calf ──
    # Title must contain "&" (compound lot) AND a calf indicator in title or pre-auction text
    has_ampersand  = "&" in title or re.search(r"\band\b", title_lower) is not None
    has_calf       = any(contains_phrase(title_lower, c, allow_plural=True) for c in CALF_INDICATORS)
    has_calf_foot  = "calves at foot" in pre_lower or "calf at foot" in pre_lower
    if has_ampersand and (has_calf or has_calf_foot):
        return ("cow-and-calf", "cow_calf_unit")

    # ── Pass 2: Breeding female ──
    for qualifier in BREEDING_FEMALE_QUALIFIERS:
        if contains_phrase(title_lower, qualifier):
            return (qualifier, "breeding_female")

    # ── Pass 3: Commercial store class ──
    commercial_classes = [
        "weaned", "weaner", "vealer", "calf", "yearling",
        "backgrounder", "store", "feeder", "steer", "heifer", "cow", "bull"
    ]
    for cls in commercial_classes:
        if contains_phrase(title_lower, cls, allow_plural=True):
            category = "bull" if cls == "bull" else "commercial"
            return (cls, category)

    return ("unknown", "commercial")


# ─────────────────────────────────────────────
# FIELD EXTRACTION HELPER
# ─────────────────────────────────────────────

def get_field_text(soup, field_id):
    """
    Extracts text from an AuctionsPlus field-id element, handling both
    the Vue component pattern and the static HTML pattern.

    AuctionsPlus renders structured fields in two ways:
      Pattern A (Vue component — confirmed on Location field):
        <ap-read-more field-id="Location" text="WILLOW TREE, N.W. Slopes & Plains">
        The value is in the 'text' attribute, not element text content.

      Pattern B (static HTML — may appear on some fields):
        <div field-id="Location"><p>NARRANDERA, Riverina NSW</p></div>
        The value is in a child <p> element's text content.

    Tries Pattern A first, then Pattern B, then raw get_text() as a last resort.
    Returns an empty string if the field element is not found.
    """
    field = soup.find(attrs={"field-id": field_id})
    if not field:
        return ""

    # Pattern A: text attribute on the element itself (Vue ap-read-more component)
    text_attr = field.get("text", "").strip()
    if text_attr:
        return text_attr

    # Pattern B: child <p> element
    p = field.find("p")
    if p:
        return p.get_text(strip=True)

    # Last resort: raw text content of the element
    return field.get_text(separator=" ", strip=True)


# ─────────────────────────────────────────────
# REGION-TO-STATE LOOKUP TABLE
# ─────────────────────────────────────────────

# Maps common Australian agricultural region name fragments (lowercase) to state
# abbreviations. Used as Pass 3 in state extraction when no abbreviation or
# spelled-out state name appears in the location string.
#
# Ordering within each state is arbitrary — all entries are checked.
# Entries are substrings, so "new england" matches "New England Tablelands".
# More specific entries should be listed before broader ones where ambiguity exists.

REGION_STATE_MAP = {
    # ── NSW ──────────────────────────────────────────────────────────────
    "new england":          "NSW",   # New England Tablelands
    "northern tablelands":  "NSW",
    "n.w. slopes":          "NSW",   # N.W. Slopes & Plains
    "northwest slopes":     "NSW",
    "north west slopes":    "NSW",
    "liverpool plains":     "NSW",
    "namoi":                "NSW",
    "central western":      "NSW",   # Central Western NSW (already has NSW but handle fragment)
    "central tablelands":   "NSW",
    "southern tablelands":  "NSW",
    "south west slopes":    "NSW",
    "riverina":             "NSW",
    "murrumbidgee":         "NSW",
    "murray":               "NSW",   # Murray region (shared with VIC — resolved by other signals)
    "hunter":               "NSW",
    "manning":              "NSW",
    "mid north coast":      "NSW",
    "north coast":          "NSW",
    "far north coast":      "NSW",
    "northern rivers":      "NSW",
    "new south wales":      "NSW",

    # ── QLD ──────────────────────────────────────────────────────────────
    "darling downs":        "QLD",
    "maranoa":              "QLD",
    "warrego":              "QLD",
    "channel country":      "QLD",
    "central highlands":    "QLD",
    "central queensland":   "QLD",
    "north queensland":     "QLD",
    "far north queensland": "QLD",
    "cape york":            "QLD",
    "gulf country":         "QLD",
    "queensland":           "QLD",
    "burnett":              "QLD",
    "lockyer":              "QLD",
    "south east queensland":"QLD",
    "granite belt":         "QLD",

    # ── VIC ──────────────────────────────────────────────────────────────
    "gippsland":            "VIC",
    "western district":     "VIC",
    "wimmera":              "VIC",
    "mallee":               "VIC",   # shared with SA — context usually resolves
    "loddon":               "VIC",
    "ovens":                "VIC",
    "north east victoria":  "VIC",
    "southern victoria":    "VIC",
    "victoria":             "VIC",

    # ── SA ──────────────────────────────────────────────────────────────
    "south australia":      "SA",
    "mid north":            "SA",    # SA Mid North
    "eyre peninsula":       "SA",
    "yorke peninsula":      "SA",
    "fleurieu":             "SA",
    "murraylands":          "SA",
    "upper south east":     "SA",
    "lower south east":     "SA",
    "south east s.a":       "SA",
    "kangaroo island":      "SA",

    # ── WA ──────────────────────────────────────────────────────────────
    "western australia":    "WA",
    "great southern":       "WA",
    "south west w.a":       "WA",
    "wheatbelt":            "WA",
    "goldfields":           "WA",
    "pilbara":              "WA",
    "kimberley":            "WA",
    "midwest":              "WA",

    # ── TAS ──────────────────────────────────────────────────────────────
    "tasmania":             "TAS",
    "northern tasmania":    "TAS",
    "southern tasmania":    "TAS",
    "north west tasmania":  "TAS",

    # ── NT ──────────────────────────────────────────────────────────────
    "northern territory":   "NT",
    "top end":              "NT",
    "barkly":               "NT",
    "katherine":            "NT",
    "victoria river":       "NT",
}


# ─────────────────────────────────────────────
# STEP 5A — COMMERCIAL MOB PARSER
# ─────────────────────────────────────────────

def scrape_commercial_listing(url, soup, page_text):
    """
    Parses a commercial mob listing (/assessed/ or /described/).
    Uses direct DOM element selectors where available (more robust than regex).
    Falls back to regex on page_text only where no structured element exists.

    Pre-catalogue fields (always available):
      title, num_head, num_calves, state, location, vendor, sale_name,
      sale_date, detected_class, listing_category

    Post-catalogue fields (only after catalogue release):
      avg_weight_kg, weight_range_kg, breed, fat_score, age_months,
      accreditations (EU, NE, WHP), price
    """

    # ── Title — dedicated div, not h1 ──
    # AuctionsPlus uses: <div class="text-headline-sm lg:text-headline-medium font-medium text-brand-dark">
    title_div = soup.find("div", class_=lambda c: c and "text-headline-sm" in c and "font-medium" in c)
    title = title_div.get_text(strip=True) if title_div else None

    # Fallback to page <title> tag (also contains the lot title before the pipe)
    if not title:
        page_title_tag = soup.find("title")
        if page_title_tag:
            raw = page_title_tag.get_text(strip=True)
            # Format: "21 NSM Heifers & 21 Calves | AuctionsPlus"
            title = raw.split("|")[0].strip()

    # Final fallback to URL slug
    if not title:
        slug_match = re.search(r"/cattle/[^/]+/([^/]+)/(?:assessed|described)/", url)
        title = slug_match.group(1).replace("-", " ").title() if slug_match else "Unknown"

    # ── Pre-auction details free text ──
    # Contains plain-English lot description: "21 2YR OLD HEIFERS WITH CALVES AT FOOT"
    pre_auction_text = ""
    pre_section = soup.find("div", string=re.compile(r"Pre-auction details", re.IGNORECASE))
    if pre_section:
        # The text is in the next sibling div
        pre_content = pre_section.find_next("p")
        if pre_content:
            pre_auction_text = pre_content.get_text(strip=True)
    # Broader fallback: look for the pre-auction details panel by heading text
    if not pre_auction_text:
        for span in soup.find_all("span"):
            if "Pre-auction details" in span.get_text():
                parent = span.find_parent("div")
                if parent:
                    p = parent.find_next("p")
                    if p:
                        pre_auction_text = p.get_text(strip=True)
                        break

    # ── Three-pass class detection ──
    detected_class, listing_category = detect_class(title, pre_auction_text)

    # ── Head count — leading number in title ──
    head_match = re.match(r"^(\d+)\s+", title)
    num_head   = int(head_match.group(1)) if head_match else None

    # ── Calf count — second number after "&" in title (cow-and-calf units) ──
    num_calves = None
    if listing_category == "cow_calf_unit":
        # "21 NSM Heifers & 21 Calves" → second number
        calf_match = re.search(r"&\s*(\d+)\s+(?:calves?)", title, re.IGNORECASE)
        if calf_match:
            num_calves = int(calf_match.group(1))
        elif num_head:
            # Assume 1:1 ratio if not explicitly stated
            num_calves = num_head

    # ── Location and State ──
    # AuctionsPlus renders location in the field-id="Location" element in static HTML.
    # Confirmed present in BeautifulSoup-accessible HTML from page inspection.
    # The correct BeautifulSoup syntax for custom attributes is soup.find(attrs={...})
    # without specifying a tag — this traverses the full tree.
    #
    # State extraction uses a two-pass approach:
    #   Pass 1: look for a state abbreviation in the location string
    #   Pass 2: look for a spelled-out state name in the location string
    # This handles both "NARRANDERA, Riverina NSW" and "WILLOW TREE, N.W. Slopes & Plains"
    # and "PENNA, Southern Tasmania".
    #
    # The sale time string "(SYD, NSW) AEST" is NOT used for state — it is a fixed
    # AuctionsPlus timezone reference present on every listing regardless of property state.

    location = "Location unknown"
    state    = "Unknown"

    # Primary: get_field_text() handles both the Vue <ap-read-more text="..."> attribute
    # pattern (confirmed on Location field) and the static <div><p> pattern.
    loc_text = get_field_text(soup, "Location")
    if loc_text:
        location = loc_text

    # Fallback: regex on page_text for "TOWN, Region STATE" pattern.
    # Only runs if the field-id element returned nothing.
    if location == "Location unknown":
        boilerplate_towns = {"SYD", "MEL", "BNE", "ADL", "PER", "DAR", "CBR"}
        for m in re.finditer(
            r"\b([A-Z][A-Z0-9\s\-\']{2,}),\s*([A-Za-z][A-Za-z\s\']*?)\s*(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b",
            page_text
        ):
            town = m.group(1).strip()
            if town not in boilerplate_towns:
                location = f"{town}, {m.group(2).strip()} {m.group(3)}".strip()
                break

    # State extraction — three passes, first match wins.
    loc_lower = location.lower()

    # Pass 1: state abbreviation directly in the location string.
    # Handles both standard form (SA, WA) and dotted form (S.A., W.A.)
    # by stripping dots from the location string before matching.
    location_nodots = re.sub(r"\b([A-Z])\.([A-Z])\.(?:([A-Z])\.)?",
                             lambda m: m.group(1) + m.group(2) + (m.group(3) or ""),
                             location)
    state_abbrev = re.search(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", location_nodots)
    if state_abbrev:
        state = state_abbrev.group(1)
    else:
        # Pass 2: spelled-out state name (e.g. "Southern Tasmania" → TAS)
        spelled = {
            "new south wales": "NSW", "queensland": "QLD", "victoria": "VIC",
            "south australia": "SA",  "western australia": "WA",
            "tasmania": "TAS", "northern territory": "NT",
            "australian capital territory": "ACT",
        }
        for name, abbrev in spelled.items():
            if name in loc_lower:
                state = abbrev
                break

    # Pass 3: agricultural region name lookup (handles region-only strings
    # such as "N.W. Slopes & Plains" that carry no state identifier).
    # REGION_STATE_MAP is defined at module level above scrape_commercial_listing().
    if state == "Unknown":
        for region, abbrev in REGION_STATE_MAP.items():
            if region in loc_lower:
                state = abbrev
                break

    # ── Sale name — from breadcrumb link to auction-results (static HTML, reliable) ──
    sale_name = "Unknown Sale"
    for a in soup.find_all("a", href=True):
        if "auction-results/cattle/" in a.get("href", ""):
            sale_name = a.get_text(strip=True)
            break

    # ── Vendor / agent name ──
    # The agent contact panel is JS-rendered but the agency name link appears
    # in the static HTML in the agent section.
    # Known pattern: <div ...>NUTRIEN AG SOLUTIONS NARRANDERA</div> inside an <a> tag
    # pointing to /agentlistings/...
    vendor = "Unknown"
    for a in soup.find_all("a", href=True):
        if "/agentlistings/" in a.get("href", ""):
            vendor_div = a.find("div")
            if vendor_div:
                vendor = vendor_div.get_text(strip=True)
                break
    # Fallback: regex on page_text for uppercase agency name patterns
    if vendor == "Unknown":
        vendor_match = re.search(
            r"((?:[A-Z][A-Z\s&]{3,}(?:AG|BEEF|STOCK|RURAL|PASTORAL|LIVESTOCK|SOLUTIONS|ELDERS|PTY)[A-Z\s]*?))\n",
            page_text
        )
        if vendor_match:
            vendor = vendor_match.group(1).strip()

    # ── Sale date ──
    # Normalise whitespace in captured date — the raw page_text may contain
    # newlines and indentation within the date string e.g. "Fri,\n    22 May 2026"
    sale_date = "Date unknown"
    date_match = re.search(r"((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\d{1,2}\s+\w+\s+\d{4})", page_text)
    if date_match:
        sale_date = re.sub(r"\s+", " ", date_match.group(1)).strip()
    else:
        date_match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", page_text)
        if date_match:
            sale_date = re.sub(r"\s+", " ", date_match.group(1)).strip()

    # ── Catalogue status ──
    catalogue_pending = "Auction Catalogue is not released yet" in page_text

    # ════════════════════════════════════════
    # POST-CATALOGUE FIELDS
    # Populated from static HTML after catalogue release.
    # All fields confirmed present in BeautifulSoup-accessible HTML via
    # inspect_fields.py runs against live Tylden (VIC) and Campania (TAS) listings.
    # Page structure confirmed: all field data is in static HTML — no JS rendering
    # required. Expandable sections are collapsed in the browser but present in HTML.
    #
    # Field extraction uses line-based parsing on the rendered text (page_lines),
    # not raw HTML selectors, because AuctionsPlus renders field values as plain
    # text lines in a predictable sequence after each field header.
    # ════════════════════════════════════════

    # Split page_text into clean non-empty lines for line-based field extraction
    page_lines = [l.strip() for l in page_text.split("\n") if l.strip()]

    def lines_after(header, page_lines, n=5):
        """Return up to n lines following the first line matching header (case-insensitive)."""
        for i, line in enumerate(page_lines):
            if header.lower() in line.lower():
                return page_lines[i+1:i+1+n]
        return []

    # ── Average weight (delivery-adjusted) ──
    # Page structure (confirmed):
    #   "At Est Kill/Del Date"
    #   "23/05/2026 (2 days)"
    #   "Live"
    #   "350.1 kgs based on -3% Del. Adj."   ← target
    # The delivery-adjusted weight is the correct buying weight — it accounts for
    # the shrinkage between assessment and delivery.
    avg_weight_kg = None
    for i, line in enumerate(page_lines):
        if "At Est Kill/Del Date" in line or "Del. Adj." in line.lower():
            # Scan next 5 lines for a weight value
            for nearby in page_lines[i:i+6]:
                w = re.search(r"(\d{2,4}(?:\.\d+)?)\s*kgs?\b", nearby)
                if w:
                    avg_weight_kg = float(w.group(1))
                    break
            if avg_weight_kg:
                break
    # Fallback: find "kgs based on" pattern directly
    if avg_weight_kg is None:
        m = re.search(r"(\d{2,4}(?:\.\d+)?)\s*kgs?\s+based on", page_text, re.IGNORECASE)
        if m:
            avg_weight_kg = float(m.group(1))

    # ── Weight range at delivery ──
    # Page structure (confirmed): "297 kgs to 432 kgs Liveweight at delivery"
    # Previous parser looked for "(min)" and "(max)" literals — wrong format.
    weight_min = None
    weight_max = None
    weight_range_kg = None
    range_match = re.search(
        r"(\d{2,4}(?:\.\d+)?)\s*kgs?\s+to\s+(\d{2,4}(?:\.\d+)?)\s*kgs?\s+Liveweight at delivery",
        page_text, re.IGNORECASE
    )
    if range_match:
        weight_min = float(range_match.group(1))
        weight_max = float(range_match.group(2))
        weight_range_kg = round(weight_max - weight_min, 1)

    # ── Weight at assessment (pre-adjustment) ──
    # Page structure: "At Assessment" → date → "Live" → "361.0 kgs"
    # Distinct from avg_weight_kg (delivery). Used for shrinkage calculation.
    weight_at_assessment_kg = None
    for i, line in enumerate(page_lines):
        if line.strip() == "At Assessment":
            for nearby in page_lines[i+1:i+5]:
                w = re.search(r"(\d{2,4}(?:\.\d+)?)\s*kgs?\b", nearby)
                if w:
                    weight_at_assessment_kg = float(w.group(1))
                    break
            break

    # ── Delivery adjustment % ──
    # Page structure: "350.1 kgs based on -3% Del. Adj."
    # The adjustment is the shrinkage assumption built into avg_weight_kg.
    delivery_adjustment_pct = None
    adj_match = re.search(r"([-+]?\d+(?:\.\d+)?)\s*%\s*Del(?:\.|ivery)?\s*Adj", page_text, re.IGNORECASE)
    if adj_match:
        delivery_adjustment_pct = float(adj_match.group(1))

    # ── Liveweight gain per day ──
    # Page structure: "Live weight gain 0 kgs/day" or "Weight Gain: 0.7 kgs/day"
    liveweight_gain_per_day = None
    gain_match = re.search(
        r"(?:Live\s+weight\s+gain|Weight\s+Gain)[:\s]+([+-]?\d+(?:\.\d+)?)\s*(?:kgs?|g)(?:/day)?",
        page_text, re.IGNORECASE
    )
    if gain_match:
        liveweight_gain_per_day = float(gain_match.group(1))

    # ── Hours off feed ──
    # Page structure: "Hours off Feed" → "5 hours" or "Hours off feed: 5 hours"
    # Standard is 8 hours — deviation affects liveweight accuracy.
    hours_off_feed = None
    for line in lines_after("Hours off Feed", page_lines, n=3):
        h = re.search(r"(\d+(?:\.\d+)?)\s*hours?", line, re.IGNORECASE)
        if h:
            hours_off_feed = float(h.group(1))
            break
    if hours_off_feed is None:
        h = re.search(r"Hours\s+off\s+[Ff]eed[:\s]+(\d+(?:\.\d+)?)", page_text)
        if h:
            hours_off_feed = float(h.group(1))

    # ── Dressing percentage ──
    # Page structure: "166.0 kgs (Est. Av. Drs. 46%)" — dressing % in parens after dressed weight
    dressing_pct = None
    drs_match = re.search(r"Est\.?\s*Av\.?\s*Drs\.?\s*(\d+(?:\.\d+)?)\s*%", page_text, re.IGNORECASE)
    if drs_match:
        dressing_pct = float(drs_match.group(1))

    # ── Assessment date ──
    # Page structure: "Time Assessed" → "1:00pm 19/05/2026"
    assessment_date = None
    for line in lines_after("Time Assessed", page_lines, n=2):
        d = re.search(r"(\d{1,2}/\d{2}/\d{4})", line)
        if d:
            assessment_date = d.group(1)
            break

    # ── Lot number ──
    # Page structure: "Lot 335" appears in page_lines near the top
    # Useful for post-auction result matching.
    lot_number = None
    for line in page_lines[:30]:
        lot_m = re.match(r"^Lot\s+(\d+)$", line.strip())
        if lot_m:
            lot_number = int(lot_m.group(1))
            break

    # ── Breed ──
    # Page structure (confirmed from inspect_fields.py output, lines 135-140):
    #   "Breeds"
    #   "Sire"
    #   "Dam"
    #   "32 Head"     ← head count line (pattern: digits + " Head")
    #   "Angus"       ← sire breed
    #   "Angus"       ← dam breed
    # For mixed mobs there are multiple head/sire/dam groups in sequence.
    # Previous parser used field-id="Breed" selector — this attribute does not
    # exist in the static HTML. The data is in plain text lines only.
    KNOWN_BREEDS = [
        "Angus", "Hereford", "Red Angus", "Brahman", "Droughtmaster",
        "Santa Gertrudis", "Charolais", "Limousin", "Simmental", "Murray Grey",
        "Shorthorn", "Wagyu", "Brangus", "Composite", "Fleckvieh", "Speckle Park",
        "Belmont Red", "Senepol", "Ultrablack", "Poll Hereford", "Black Baldy",
        "Piedmontese", "Charbray", "Simbrah",
    ]

    detected_breed = "Unknown"
    breed_groups = []  # list of (head_count, sire_breed, dam_breed)

    for i, line in enumerate(page_lines):
        if line.strip() == "Breeds":
            # Scan forward for head-count lines (e.g. "32 Head")
            j = i + 1
            while j < min(i + 40, len(page_lines)):
                head_m = re.match(r"^(\d+)\s+Head$", page_lines[j].strip(), re.IGNORECASE)
                if head_m:
                    head_n = int(head_m.group(1))
                    # Next two non-empty lines after the head count are sire and dam breed
                    remaining = [l for l in page_lines[j+1:j+6] if l.strip()]
                    sire_breed = None
                    dam_breed = None
                    for breed_line in remaining[:2]:
                        matched = next(
                            (b for b in KNOWN_BREEDS if b.lower() == breed_line.strip().lower()),
                            None
                        )
                        if matched:
                            if sire_breed is None:
                                sire_breed = matched
                            else:
                                dam_breed = matched
                                break
                    if sire_breed:
                        breed_groups.append((head_n, sire_breed, dam_breed or sire_breed))
                j += 1
            break

    if breed_groups:
        if len(breed_groups) == 1:
            _, sire, dam = breed_groups[0]
            detected_breed = sire if sire.lower() == dam.lower() else f"{sire} Cross"
        else:
            # Multiple breed groups — classify from dominant group by head count
            dominant = max(breed_groups, key=lambda x: x[0])
            _, sire, dam = dominant
            detected_breed = sire if sire.lower() == dam.lower() else f"{sire} Cross"
    else:
        # Fallback: scan page_text for known breed names
        # Used when "Breeds" section is absent (e.g. pre-catalogue or described listings)
        for breed in KNOWN_BREEDS:
            if re.search(r"\b" + re.escape(breed) + r"\b", page_text, re.IGNORECASE):
                detected_breed = breed
                break

    # ── Horn status ──
    # Page structure: "32 Polled" or "Horn Status" → "32 Polled"
    # From assessment form: Polled / Tipped / Scurred / Horned / Dehorned
    horn_status = None
    horn_terms = ["Polled", "Horned", "Tipped", "Scurred", "Dehorned"]
    for line in page_lines:
        for term in horn_terms:
            if re.search(r"\b" + term + r"\b", line, re.IGNORECASE):
                horn_status = term.lower()
                break
        if horn_status:
            break

    # ── Store condition ──
    # From assessment form: Fwd/Prime, Fwd/Store, Store, Back/Store, Poor
    # Page renders as percentage breakdown — capture dominant condition.
    store_condition = None
    condition_map = {
        "fwd/prime": "forward_prime", "fwd/store": "forward_store",
        "forward to prime": "forward_prime", "forward store": "forward_store",
        "back/store": "backward_store", "backward store": "backward_store",
        "store": "store", "poor": "poor",
    }
    for term, val in condition_map.items():
        if term.lower() in page_text.lower():
            store_condition = val
            break

    # ── Fat score ──
    # Page structure (confirmed from inspect_fields.py output, lines 81-82):
    #   "Fat Scores"
    #   "2"            ← fat score value on NEXT line
    #   "Totals"
    # Previous parser used inline regex "fat score N" — wrong format.
    # The fat score is the first standalone single digit on the line after "Fat Scores".
    fat_score = None
    for line in lines_after("Fat Scores", page_lines, n=3):
        fat_m = re.match(r"^(\d)\b", line.strip())
        if fat_m:
            fat_score = int(fat_m.group(1))
            break
    # Fallback: inline format (some listing types may use this)
    if fat_score is None:
        fat_m = re.search(r"fat\s*score\s*[:\s]?(\d)", page_text, re.IGNORECASE)
        if fat_m:
            fat_score = int(fat_m.group(1))

    # ── Age in months ──
    # Page structure: "14 - 15 Months" — working correctly in v1.7, unchanged.
    age_min_months = None
    age_max_months = None
    age_match = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*[Mm]onths?", page_text)
    if age_match:
        age_min_months = int(age_match.group(1))
        age_max_months = int(age_match.group(2))
    else:
        for line in lines_after("Age", page_lines, n=5):
            single_age = re.search(r"\b(\d+)\s*[Mm]onths?\b", line)
            if single_age:
                age_min_months = int(single_age.group(1))
                age_max_months = age_min_months
                break

    # ── HGP status ──
    # Page structure: "HGP Status" → "The owner declares that the cattle have not been treated
    #   with HGP at any period of their lives"
    # OR: "HGP Treated?" field from assessment form → "Yes" / "No"
    # HGP-free is a premium signal and required for Greenham Never Ever program.
    HGP_free = None
    hgp_lines = lines_after("HGP", page_lines, n=4)
    for line in hgp_lines:
        if re.search(r"not been treated|HGP.{0,10}free|never.*treated", line, re.IGNORECASE):
            HGP_free = True
            break
        elif re.search(r"\byes\b|\btreated\b", line, re.IGNORECASE):
            HGP_free = False
            break
    # Fallback: NE accreditation implies HGP-free
    if HGP_free is None and re.search(r"NEVER EVER|Greenham NE\b", page_text, re.IGNORECASE):
        HGP_free = True

    # ── Lifetime traceable percentage ──
    # Page structure: "100 % of cattle in this lot are Lifetime Traceable"
    lifetime_traceable_pct = None
    lt_match = re.search(r"(\d+)\s*%\s+of\s+cattle.{0,30}Lifetime\s+Traceable", page_text, re.IGNORECASE)
    if lt_match:
        lifetime_traceable_pct = int(lt_match.group(1))

    # ── Temperament ──
    # Page structure: "Yards" → "Quiet: 32 head"
    # Dominant temperament: most head recorded at quietest level wins.
    # Score map: Docile=5, Quiet=4, Slightly Stirry=3, Stirry=2, Aggressive=1
    temperament = None
    temp_score_map = {
        "docile": 5, "quiet": 4, "slightly stirry": 3, "stirry": 2, "aggressive": 1
    }
    best_score = 0
    for term, score in temp_score_map.items():
        if re.search(r"\b" + term + r"\b", page_text, re.IGNORECASE):
            if score > best_score:
                best_score = score
                temperament = term

    # ── Accreditations ──
    # Page structure (confirmed from inspect_fields.py output):
    #   "Accreditation(s)"
    #   "LPA"
    #   "Verification(s)"
    #   "Greenham NEVER EVER"
    # Previous parser used freetext \bEU\b etc. — this fires on Featured Lots
    # boilerplate at the bottom of every page, causing false positives.
    # Fix: extract only from the Accreditation(s) and Verification(s) blocks.
    # Canonical accreditation tokens from assessment form:
    #   EU, LPA, Grass-Fed, Greenham Never Ever (NE), MSA, Organic Certified,
    #   Antibiotic Free, WHP (withdrawal period — a disqualifier, not a positive)

    is_EU   = False
    is_NE   = False
    is_LPA  = False
    is_MSA  = False
    has_WHP = False

    # Extract text from Accreditation(s) / Verification(s) blocks only.
    accred_block = []
    in_accred = False
    for line in page_lines:
        if "Accreditation" in line or "Verification" in line:
            in_accred = True
            continue
        if in_accred:
            # Stop at next recognised section header
            if any(h in line for h in ["Delivery", "Trading Terms", "NLIS", "Movement", "Special", "Sale Types", "Featured"]):
                break
            if len(accred_block) >= 15:
                break
            accred_block.append(line)

    accred_text = " ".join(accred_block).upper()
    is_EU   = bool(re.search(r"\bEU\b", accred_text)) and "EUROPEAN" not in accred_text
    is_NE   = bool(re.search(r"\bNE\b", accred_text)) or "NEVER EVER" in accred_text
    is_LPA  = bool(re.search(r"\bLPA\b", accred_text))
    is_MSA  = bool(re.search(r"\bMSA\b", accred_text))
    has_WHP = bool(re.search(r"\bWHP\b", accred_text))

    # ── Price ──
    # AuctionsPlus assessed listings are bid-based — no asking price pre-auction.
    # Post-auction prices appear as $/head or c/kg after the sale closes.
    # The finance widget shows $/day/head figures (e.g. "$0.68/day/head") which
    # the previous parser was capturing as price — now excluded by requiring
    # the value to be above a plausible minimum (>$100/head).
    price_per_head = None
    price_c_kg     = None

    for m in re.finditer(r"\$\s*([\d,]+(?:\.\d+)?)\s*/?\s*[Hh]ead", page_text):
        val = float(m.group(1).replace(",", ""))
        if val > 100:  # exclude finance widget values ($0.49, $0.68 etc.)
            price_per_head = val
            break

    price_ckg_match = re.search(r"(\d{3,4}(?:\.\d+)?)\s*c/kg", page_text, re.IGNORECASE)
    if price_ckg_match:
        price_c_kg = float(price_ckg_match.group(1))

    if price_per_head and avg_weight_kg and not price_c_kg:
        price_c_kg = round((price_per_head / avg_weight_kg) * 100, 1)

    # ── Sale type pricing unit ──
    # From assessment form: $/Head, c/kg liveweight, c/kg dressed weight
    # Appears in page as "Sale Types" → "$/Head"
    sale_type_pricing = None
    for line in lines_after("Sale Types", page_lines, n=3):
        if "$/head" in line.lower() or "$/Head" in line:
            sale_type_pricing = "$/head"
        elif "c/kg" in line.lower():
            sale_type_pricing = "c/kg"
        if sale_type_pricing:
            break

    # ── Sex detection ──
    # Derived from detected_class first (unambiguous), then title scan (for
    # mixed-sex class terms like "weaned", "yearling", "backgrounder", etc.).
    # Returns "steer", "heifer", "mixed", or None (unknown — filter passes through).
    title_lower_sex = title.lower()
    if detected_class in ("steer",):
        detected_sex = "steer"
    elif detected_class in ("heifer",):
        detected_sex = "heifer"
    elif any(t in title_lower_sex for t in ("mixed sex", "mixed sexes")):
        detected_sex = "mixed"
    elif re.search(r"\bsteers?\b", title_lower_sex):
        detected_sex = "steer"
    elif re.search(r"\bheifers?\b", title_lower_sex):
        detected_sex = "heifer"
    else:
        detected_sex = None   # unknown — sex filter will pass through

    return {
        # ── Metadata ──
        "listing_type":             "commercial",
        "listing_category":         listing_category,
        "url":                      url,
        "title":                    title,
        "sale_name":                sale_name,
        "sale_date":                sale_date,
        "lot_number":               lot_number,
        "catalogue_pending":        catalogue_pending,
        "vendor":                   vendor,
        "pre_auction_text":         pre_auction_text,

        # ── Pre-catalogue filters ──
        "num_head":                 num_head,
        "num_calves":               num_calves,
        "state":                    state,
        "location":                 location,
        "class":                    detected_class,
        "sex":                      detected_sex,       # steer/heifer/mixed/None

        # ── Breed & physical traits ──
        "breed":                    detected_breed,
        "breed_groups":             breed_groups,       # full list for mixed mobs
        "horn_status":              horn_status,        # polled/horned/tipped/scurred/dehorned
        "store_condition":          store_condition,    # forward_prime/forward_store/store/backward_store/poor
        "temperament":              temperament,        # docile/quiet/slightly stirry/stirry/aggressive

        # ── Weight fields ──
        "avg_weight_kg":            avg_weight_kg,      # delivery-adjusted, the correct buying weight
        "weight_at_assessment_kg":  weight_at_assessment_kg,  # pre-adjustment, for shrinkage calc
        "weight_min":               weight_min,         # delivery range low
        "weight_max":               weight_max,         # delivery range high
        "weight_range_kg":          weight_range_kg,    # spread for mob evenness filter
        "delivery_adjustment_pct":  delivery_adjustment_pct,  # shrinkage % assumption
        "liveweight_gain_per_day":  liveweight_gain_per_day,  # condition trajectory signal
        "dressing_pct":             dressing_pct,       # carcase yield signal

        # ── Age ──
        "age_min_months":           age_min_months,
        "age_max_months":           age_max_months,

        # ── Fat score ──
        "fat_score":                fat_score,          # 1-6 AuctionsPlus scale

        # ── Assessment metadata ──
        "assessment_date":          assessment_date,
        "hours_off_feed":           hours_off_feed,     # <8hrs inflates liveweight

        # ── Accreditations ──
        "is_EU":                    is_EU,
        "is_NE":                    is_NE,
        "is_LPA":                   is_LPA,
        "is_MSA":                   is_MSA,
        "has_WHP":                  has_WHP,
        "HGP_free":                 HGP_free,
        "lifetime_traceable_pct":   lifetime_traceable_pct,

        # ── Price ──
        "price_per_head":           price_per_head,     # post-auction only; None pre-auction
        "price_c_kg":               price_c_kg,         # post-auction only; None pre-auction
        "sale_type_pricing":        sale_type_pricing,  # $/head or c/kg
    }


# ─────────────────────────────────────────────
# STEP 5B — STUD/GENETICS PARSER
# ─────────────────────────────────────────────

def scrape_stud_listing(url, soup, page_text):
    """
    Parses a stud/genetics individual animal listing (/listing/).
    Captured for completeness but filtered out when include_bulls and include_stud are FALSE.
    """
    # Title — same div pattern as commercial listings
    title_div = soup.find("div", class_=lambda c: c and "text-headline-sm" in c and "font-medium" in c)
    title = title_div.get_text(strip=True) if title_div else "Unknown"

    # Location — use get_field_text() to handle both Vue attribute and static HTML patterns
    location = get_field_text(soup, "Location")
    if not location:
        location = "Location unknown"

    # Three-pass state extraction — same logic as scrape_commercial_listing()
    loc_lower = location.lower()
    state = "Unknown"

    # Handles both standard form (SA, WA) and dotted form (S.A., W.A., N.S.W. etc.)
    location_nodots = re.sub(r"\b([A-Z])\.([A-Z])\.(?:([A-Z])\.)?",
                             lambda m: m.group(1) + m.group(2) + (m.group(3) or ""),
                             location)
    state_abbrev = re.search(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", location_nodots)
    if state_abbrev:
        state = state_abbrev.group(1)
    else:
        spelled = {
            "new south wales": "NSW", "queensland": "QLD", "victoria": "VIC",
            "south australia": "SA",  "western australia": "WA",
            "tasmania": "TAS", "northern territory": "NT",
            "australian capital territory": "ACT",
        }
        for name, abbrev in spelled.items():
            if name in loc_lower:
                state = abbrev
                break

    if state == "Unknown":
        for region, abbrev in REGION_STATE_MAP.items():
            if region in loc_lower:
                state = abbrev
                break

    return {
        "listing_type":      "stud",
        "listing_category":  "bull",
        "url":               url,
        "title":             title,
        "sale_name":         "Stud Sale",
        "sale_date":         "Unknown",
        "catalogue_pending": False,
        "vendor":            "Unknown",
        "pre_auction_text":  "",
        "num_head":          1,
        "num_calves":        None,
        "state":             state,
        "location":          location,
        "class":             "bull",
        "avg_weight_kg":     None,
        "weight_min":        None,
        "weight_max":        None,
        "weight_range_kg":   None,
        "breed":             "Unknown",
        "fat_score":         None,
        "age_min_months":    None,
        "age_max_months":    None,
        "is_EU":             False,
        "is_NE":             False,
        "has_WHP":           False,
        "price_per_head":    None,
        "price_c_kg":        None,
    }


# ─────────────────────────────────────────────
# STEP 6 — SCRAPE DISPATCHER
# ─────────────────────────────────────────────

def scrape_auctionsplus_listing(url, session=None):
    """
    Fetches a listing page and routes it to the correct parser.

    Two-step classification:
      Step 1 — Content classification (post-fetch):
        detect_listing_type() inspects the fetched HTML to determine whether
        the listing is a commercial mob or a stud/genetics individual.
        URL path is a hint only — content takes precedence.
    """
    http = session or requests

    try:
        print(f"  Scraping: {url}")
        response = http.get(url, headers=AUCTIONSPLUS_HEADERS, timeout=15)
        if response.status_code != 200:
            return None
        soup      = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(separator="\n", strip=True)

        # Step 1: content-based classification
        listing_type = detect_listing_type(url, soup, page_text)

        if listing_type == "commercial":
            return scrape_commercial_listing(url, soup, page_text)
        elif listing_type == "stud":
            return scrape_stud_listing(url, soup, page_text)
        else:
            return None
    except Exception as e:
        print(f"  ⚠️  Error scraping {url}: {e}")
        return None


def scrape_listing(url, session=None):
    """Backward-compatible wrapper for existing helpers/tests."""
    return scrape_auctionsplus_listing(url, session=session)


def scrape_authorized_notice(path, session=None):
    """
    Parse a locally stored authorised notice record.

    Expected file shape: one JSON object using either shared-listing field names
    directly or simple aliases such as source_url, source_record_id, and
    listing_title.
    """
    del session  # File-backed source does not use HTTP sessions.

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as e:
        print(f"  ⚠️  Error reading authorised notice {path}: {e}")
        return None

    if not isinstance(payload, dict):
        print(f"  ⚠️  Authorised notice file must contain one JSON object: {path}")
        return None

    source_url = payload.get("url") or payload.get("source_url") or f"file://{Path(path).resolve().as_posix()}"
    listing = {
        "url": source_url,
        "source_record_id": payload.get("source_record_id"),
        "source_confidence": payload.get("source_confidence"),
        "sender_email": payload.get("sender_email"),
        "received_at": payload.get("received_at"),
        "attachment_name": payload.get("attachment_name"),
        "message_id": payload.get("message_id"),
        "title": payload.get("title") or payload.get("listing_title") or payload.get("sale_name") or Path(path).stem,
        "sale_name": payload.get("sale_name") or payload.get("title") or "",
        "sale_date": payload.get("sale_date") or "",
        "listing_type": payload.get("listing_type") or "commercial",
        "listing_category": payload.get("listing_category") or "commercial",
        "catalogue_pending": bool(payload.get("catalogue_pending", False)),
        "vendor": payload.get("vendor") or payload.get("agent_name") or "Unknown",
        "pre_auction_text": payload.get("pre_auction_text") or payload.get("notes_raw") or "",
        "num_head": payload.get("num_head"),
        "num_calves": payload.get("num_calves"),
        "state": payload.get("state") or "Unknown",
        "location": payload.get("location") or "Location unknown",
        "class": payload.get("class") or payload.get("stock_type") or "",
        "sex": payload.get("sex"),
        "breed": payload.get("breed") or "Unknown",
        "breed_groups": payload.get("breed_groups") or [],
        "horn_status": payload.get("horn_status"),
        "store_condition": payload.get("store_condition"),
        "temperament": payload.get("temperament"),
        "avg_weight_kg": payload.get("avg_weight_kg"),
        "weight_at_assessment_kg": payload.get("weight_at_assessment_kg"),
        "weight_min": payload.get("weight_min"),
        "weight_max": payload.get("weight_max"),
        "weight_range_kg": payload.get("weight_range_kg"),
        "delivery_adjustment_pct": payload.get("delivery_adjustment_pct"),
        "liveweight_gain_per_day": payload.get("liveweight_gain_per_day"),
        "dressing_pct": payload.get("dressing_pct"),
        "fat_score": payload.get("fat_score"),
        "age_min_months": payload.get("age_min_months"),
        "age_max_months": payload.get("age_max_months"),
        "hours_off_feed": payload.get("hours_off_feed"),
        "assessment_date": payload.get("assessment_date"),
        "is_EU": payload.get("is_EU", False),
        "is_NE": payload.get("is_NE", False),
        "is_LPA": payload.get("is_LPA", False),
        "is_MSA": payload.get("is_MSA", False),
        "has_WHP": payload.get("has_WHP", False),
        "HGP_free": payload.get("HGP_free"),
        "lifetime_traceable_pct": payload.get("lifetime_traceable_pct"),
        "price_per_head": payload.get("price_per_head"),
        "price_c_kg": payload.get("price_c_kg"),
        "sale_type_pricing": payload.get("sale_type_pricing"),
        "catalogue_url": payload.get("catalogue_url") or source_url,
        "notes_raw": payload.get("notes_raw"),
    }
    return listing


def scrape_stockplace_source(url, session=None):
    """
    Parse the public Stockplace index page into one or more shared listings.

    This source stays disabled by default. It is wired behind a feature flag so
    we can prove the shared source boundary before exposing it to beta users.
    """
    try:
        from source_parser_spikes import parse_stockplace_html
    except Exception as e:
        print(f"  ⚠️  Could not import Stockplace parser: {e}")
        return None

    http = session or requests
    try:
        response = http.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"  ⚠️  Error fetching Stockplace page {url}: {e}")
        return None

    def detail_fetcher(detail_url):
        detail_response = http.get(detail_url, timeout=30)
        detail_response.raise_for_status()
        return detail_response.text

    try:
        records, _summary = parse_stockplace_html(response.text, url, detail_fetcher=detail_fetcher)
    except Exception as e:
        print(f"  ⚠️  Error parsing Stockplace page {url}: {e}")
        return None

    listings = []
    for record in records:
        listing = parser_record_to_shared_listing(record)
        if listing:
            listings.append(listing)

    return listings


def scrape_rma_source(url, session=None):
    """
    Parse the public RMA cattle sales index into one or more shared listings.

    This source stays opt-in so we can prove the aggregator path before using
    it in any live beta-facing run.
    """
    try:
        from source_parser_spikes import parse_rma_html
    except Exception as e:
        print(f"  ⚠️  Could not import RMA parser: {e}")
        return None

    http = session or requests
    try:
        response = http.get(url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"  ⚠️  Error fetching RMA page {url}: {e}")
        return None

    try:
        records, _summary = parse_rma_html(response.text, url)
    except Exception as e:
        print(f"  ⚠️  Error parsing RMA page {url}: {e}")
        return None

    listings = []
    for record in records:
        listing = parser_record_to_shared_listing(record)
        if listing:
            listings.append(listing)

    return listings


def collect_listings(listing_urls, session=None):
    """
    Scrape each listing URL once for the whole run.

    The returned shared listing set is then matched independently against each
    active user config. This avoids re-fetching the same page per user.
    """
    shared_listings = []

    for url in listing_urls:
        listing = scrape_listing(url, session=session)
        time.sleep(REQUEST_DELAY)
        if listing:
            shared_listings.append(listing)

    print(f"Shared listings scraped this run: {len(shared_listings)}")
    return shared_listings


def collect_source_listings(source_defs):
    """
    Discover and scrape each enabled source once per run.

    Returns one shared normalised listing list for downstream per-user matching.
    """
    shared_listings = []

    for source_def in source_defs:
        print(f"\nCollecting source: {source_def['name']}")
        session = source_def["session_factory"]() if source_def.get("session_factory") else None
        items = source_def["discover_items"](session=session) if session else source_def["discover_items"]()

        discovered = len(items)
        scraped = 0
        skipped = 0
        seen_urls = set()

        for item in items:
            listing = source_def["scrape_item"](item, session=session)
            if session:
                time.sleep(REQUEST_DELAY)
            if not listing:
                skipped += 1
                continue

            listing_batch = listing if isinstance(listing, list) else [listing]
            batch_scraped = 0

            for single_listing in listing_batch:
                shared = normalise_shared_listing(single_listing, source_def)
                if not shared:
                    skipped += 1
                    continue

                if shared["url"] in seen_urls:
                    skipped += 1
                    continue

                seen_urls.add(shared["url"])
                shared_listings.append(shared)
                scraped += 1
                batch_scraped += 1

            if batch_scraped == 0:
                skipped += 1

        print(
            f"  Source summary [{source_def['name']}]: "
            f"discovered={discovered}, scraped={scraped}, skipped={skipped}"
        )

    print(f"\nShared listings scraped this run: {len(shared_listings)}")
    return shared_listings


def breeding_female_type_matches(listing, config):
    """
    Match breeding-female listings against coarse female-type preferences.

    "cow" means a female that has already calved.
    "heifer" means a female that has not yet calved.
    """
    allowed_types = [t.lower() for t in config.get("breeding_female_classes", []) if t]
    if not allowed_types:
        return True

    title_lower = listing.get("title", "").lower()
    pre_lower = listing.get("pre_auction_text", "").lower()
    combined = f"{title_lower} {pre_lower}"

    if "heifer" in combined:
        female_type = "heifer"
    elif "cow" in combined:
        female_type = "cow"
    else:
        female_type = None

    if female_type is None:
        return True

    return female_type in allowed_types


# ─────────────────────────────────────────────
# STEP 7 — SINGLE-STAGE FILTER
# ─────────────────────────────────────────────

def listing_match(listing, config):
    """
    Single-stage filter. Returns (True, "match") if the listing passes all
    applicable criteria, or (False, "reason") identifying the specific gate
    that rejected it.

    Mandatory gates (always applied):
      listing type, active flag, category toggle, known state, known class,
      head count, known sale type.

    Soft gates (skipped when field is None or "Unknown"):
      state, class, sale type, weight, weight range, breed, fat score, age,
      accreditations.
      Never suppress a match because the parser missed a field — silent misses
      are worse than false positives for a buy-side alert tool.

    Price ceiling not applied pre-auction — prices only available post-sale.
    """
    if listing["listing_type"] != "commercial":
        return False, "listing_type not commercial"

    if not config.get("active", True):
        return False, "config inactive"

    # ── Category gate ──
    category = listing.get("listing_category")
    if category == "cow_calf_unit":
        if not config.get("include_cow_calf_units"):
            return False, "cow_calf_units disabled"
    elif category == "breeding_female":
        if not config.get("include_breeding_females"):
            return False, "breeding_females disabled"
        if not breeding_female_type_matches(listing, config):
            return False, "breeding_female type mismatch"
    elif category == "bull":
        if not config.get("include_bulls"):
            return False, "bulls disabled"
    elif category == "commercial":
        if not config.get("include_commercial", True):
            return False, "commercial disabled"

    # ── State filter ──
    target_states = [s.upper() for s in config.get("target_states", [])]
    if target_states and listing["state"] != "Unknown" and listing["state"] not in target_states:
        return False, f"state={listing['state']} not in {target_states}"

    # ── Class filter — commercial only ──
    listing_class = (listing.get("class") or "").lower()
    if category == "commercial":
        active_classes = list(config.get("target_classes", []))
        if active_classes and listing_class not in ("", "unknown") and not any(tc in listing_class for tc in active_classes):
            return False, f"class={listing['class']!r} not in target_classes"

    # ── Sex filter — soft gate ──
    # Only applied when target_sex is "steer" or "heifer" (not "either" or blank).
    # If the parser could not determine sex (detected_sex is None), pass through —
    # silent misses are worse than false positives for a buy-side alert tool.
    target_sex = config.get("target_sex", "").lower().strip()
    if target_sex and target_sex != "either":
        detected_sex = listing.get("sex")
        if detected_sex is not None and detected_sex != target_sex:
            return False, f"sex={detected_sex!r} != target_sex={target_sex!r}"

    # ── Head count ──
    head_count = listing["num_head"]
    if head_count is not None:
        min_head = config.get("min_head")
        max_head = config.get("max_head")
        if min_head and head_count < min_head:
            return False, f"head={head_count} < min_head={min_head}"
        if max_head and head_count > max_head:
            return False, f"head={head_count} > max_head={max_head}"

    # ── Sale type filter ──
    sale_types = [st.lower() for st in config.get("sale_types", [])]
    sale_name_lower = (listing.get("sale_name") or "").lower()
    if sale_types and sale_name_lower not in ("", "unknown sale") and not any(st in sale_name_lower for st in sale_types):
        return False, f"sale_name={listing.get('sale_name')!r} not in sale_types"

    # ── Select weight/age/fat config set ──
    is_bull = (category == "bull")
    if is_bull:
        min_wt  = config.get("bull_min_weight_kg")
        max_wt  = config.get("bull_max_weight_kg")
        fat_max = config.get("bull_max_fat_score")
        fat_min = config.get("bull_min_fat_score")
        age_min = config.get("bull_min_age_months")
        age_max = config.get("bull_max_age_months")
    else:
        min_wt  = config.get("min_weight_kg")
        max_wt  = config.get("max_weight_kg")
        fat_max = config.get("fat_score_max")
        fat_min = config.get("min_fat_score")
        age_min = config.get("age_min_months")
        age_max = config.get("age_max_months")

    # ── Weight — soft gate ──
    if listing["avg_weight_kg"] is not None:
        if min_wt and listing["avg_weight_kg"] < min_wt:
            return False, f"weight={listing['avg_weight_kg']}kg < min={min_wt}kg"
        if max_wt and listing["avg_weight_kg"] > max_wt:
            return False, f"weight={listing['avg_weight_kg']}kg > max={max_wt}kg"

    # ── Mob evenness — soft gate ──
    max_range = config.get("max_weight_range_kg")
    if max_range and listing["weight_range_kg"] is not None:
        if listing["weight_range_kg"] > max_range:
            return False, f"weight_range={listing['weight_range_kg']}kg > max={max_range}kg"

    # ── Breed — soft gate, only if parser returned a known breed ──
    if category in ("commercial", "bull"):
        if listing["breed"] != "Unknown":
            target_breeds = config.get("target_breeds", [])
            if target_breeds and listing["breed"].lower() not in target_breeds:
                return False, f"breed={listing['breed']!r} not in target_breeds"

    # ── Bull breed — hard gate (bulls must have confirmed breed) ──
    if is_bull:
        bull_breeds   = [b.lower() for b in config.get("bull_breeds", [])]
        listing_breed = listing["breed"].lower()
        if bull_breeds and not any(b in listing_breed for b in bull_breeds):
            return False, f"bull breed={listing['breed']!r} not in bull_breeds"

    # ── Fat score — soft gate ──
    if listing["fat_score"] is not None:
        if fat_max and listing["fat_score"] > fat_max:
            return False, f"fat_score={listing['fat_score']} > max={fat_max}"
        if fat_min and listing["fat_score"] < fat_min:
            return False, f"fat_score={listing['fat_score']} < min={fat_min}"

    # ── Age — soft gate ──
    if listing["age_max_months"] is not None and age_min:
        if listing["age_max_months"] < age_min:
            return False, f"age_max={listing['age_max_months']}mo < min={age_min}mo"
    if listing["age_min_months"] is not None and age_max:
        if listing["age_min_months"] > age_max:
            return False, f"age_min={listing['age_min_months']}mo > max={age_max}mo"

    # ── Accreditations ──
    if config.get("require_EU") and not listing["is_EU"]:
        return False, "require_EU not met"
    if config.get("require_NE") and not listing["is_NE"]:
        return False, "require_NE not met"
    if config.get("exclude_WHP") and listing["has_WHP"]:
        return False, "has_WHP excluded"
    if config.get("require_HGP_free") and listing["HGP_free"] is False:
        return False, "require_HGP_free not met"
    if config.get("require_polled") and listing["horn_status"] not in (None, "polled"):
        return False, f"require_polled not met (horn_status={listing['horn_status']})"
    if config.get("require_quiet"):
        temp = listing.get("temperament")
        if temp and temp not in ("docile", "quiet"):
            return False, f"require_quiet not met (temperament={temp})"
    min_lt = config.get("min_lifetime_traceable_pct")
    if min_lt and listing["lifetime_traceable_pct"] is not None:
        if listing["lifetime_traceable_pct"] < min_lt:
            return False, f"lifetime_traceable={listing['lifetime_traceable_pct']}% < min={min_lt}%"

    # ── Vendor filters — placeholder ──
    # preferred_vendors and exclude_vendors checks will go here

    return True, "match"


# ─────────────────────────────────────────────
# STEP 8 — DEDUPLICATION LOG
# ─────────────────────────────────────────────

def get_log_status(worksheet):
    """
    Returns a dict of {(url, user_id): status} from the log sheet.

    Keyed on the tuple (url, user_id) so that deduplication is per-user:
    a listing that alerted User 1 will still alert User 2 if they match.

    Column A = user_id (v2.3 — prepended; was url in v2.2)
    Column B = url
    Column C = status
    """
    try:
        rows = worksheet.get_all_values()
        status_map = {}
        for row in rows[1:]:   # skip header
            if len(row) >= 3:
                user_id = row[0]
                url     = row[1]
                status  = row[2]
                status_map[(url, user_id)] = status
        return status_map
    except Exception as e:
        print(f"  ⚠️  Could not read log: {e}")
        raise RuntimeError("Could not read dedup log; aborting run to avoid duplicate alerts.") from e


def runtime_log_status(status):
    """Keep TEST_MODE rows from suppressing the first live production send."""
    return f"TEST_{status}" if TEST_MODE else status


def is_dedup_alerted(status):
    """Production ALERTED always suppresses; TEST_ALERTED suppresses test runs only."""
    return status == "ALERTED" or (TEST_MODE and status == "TEST_ALERTED")


def is_dedup_watching(status):
    """Production WATCHING always suppresses; TEST_WATCHING suppresses test runs only."""
    return status == "WATCHING" or (TEST_MODE and status == "TEST_WATCHING")


def utc_timestamp():
    """Consistent Sheets timestamp for CI and local runs."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def build_log_listing_row(listing, status, user_id, flag=None):
    """
    Build a lean cattle_scout_log row for batched writing.

    Column layout (v2.3 — user_id prepended):
      A: user_id  B: url  C: status  D: title  E: category  F: class
      G: breed  H: head  I: avg_weight  J: weight_range  K: fat_score
      L: age  M: accreditations  N: price_c_kg  O: location  P: vendor
      Q: sale_date  R: flag  S: logged_at
    """
    accreds = " ".join(filter(None, [
        "EU"  if listing["is_EU"]   else "",
        "NE"  if listing["is_NE"]   else "",
        "WHP" if listing["has_WHP"] else "",
    ]))
    calf_info = f" (+{listing['num_calves']} calves)" if listing.get("num_calves") else ""
    head = "" if listing.get("num_head") is None else str(listing["num_head"])
    row = [
        user_id,                                                                    # A  user_id
        listing["url"],                                                             # B  url
        status,                                                                     # C  status
        listing["title"],                                                           # D  title
        listing["listing_category"],                                                # E  category
        listing["class"],                                                           # F  class
        listing["breed"],                                                           # G  breed
        head + calf_info,                                                           # H  head
        listing["avg_weight_kg"],                                                   # I  avg_weight
        listing["weight_range_kg"],                                                 # J  weight_range
        listing["fat_score"],                                                       # K  fat_score
        f"{listing['age_min_months']}–{listing['age_max_months']}mo" if listing["age_min_months"] else "",  # L age
        accreds,                                                                    # M  accreditations
        listing["price_c_kg"],                                                      # N  price_c_kg
        listing["location"],                                                        # O  location
        listing["vendor"],                                                          # P  vendor
        listing["sale_date"],                                                       # Q  sale_date
        flag or "",                                                                 # R  flag
        utc_timestamp(),                                                            # S  logged_at
    ]
    return row


def build_listing_full_row(listing, status, flag, fair_value, user_id):
    """
    Build the full cattle_scout_listings row for batched writing.

    One row per alerted listing — append-only, never updated in place.

    Column layout (v2.3 — user_id prepended to column A, all others shift right):
      A: user_id  B: url  C: logged_at  D: status  E: sale_name  F: sale_date
      G: lot_number  H: listing_category  I: class  J: title  K: num_head
      L: state  M: location  N: vendor  O: breed  P: breed_groups
      Q: avg_weight_kg  R: weight_at_assessment_kg  S: weight_min  T: weight_max
      U: weight_range_kg  V: delivery_adjustment_pct  W: liveweight_gain_per_day
      X: dressing_pct  Y: fat_score  Z: age_min_months  AA: age_max_months
      AB: hours_off_feed  AC: assessment_date  AD: horn_status  AE: temperament
      AF: store_condition  AG: is_EU  AH: is_NE  AI: is_LPA  AJ: is_MSA
      AK: has_WHP  AL: HGP_free  AM: lifetime_traceable_pct  AN: price_per_head
      AO: price_c_kg  AP: sale_type_pricing  AQ: valuation_flag
      AR: fair_value_at_alert  AS: catalogue_pending
    """
    def b(val):
        # Python bool → Sheets string. None → "" (unknown, distinct from FALSE).
        if val is True:
            return "TRUE"
        if val is False:
            return "FALSE"
        return ""

    def n(val):
        # None → empty string; everything else passes through unchanged.
        return "" if val is None else val

    breed_groups_str = ""
    if listing.get("breed_groups"):
        bg = listing["breed_groups"]
        if isinstance(bg, list) and len(bg) > 0:
            if isinstance(bg[0], tuple):
                breed_groups_str = "|".join(f"{sire}/{dam}" for _, sire, dam in bg)
            else:
                breed_groups_str = "|".join(str(x) for x in bg)
        elif isinstance(bg, str):
            breed_groups_str = bg

    row = [
        user_id,                                            # A  user_id
        listing["url"],                                     # B  url
        utc_timestamp(),                                    # C  logged_at
        status,                                             # D  status
        n(listing.get("sale_name")),                        # E  sale_name
        n(listing.get("sale_date")),                        # F  sale_date
        n(listing.get("lot_number")),                       # G  lot_number
        n(listing.get("listing_category")),                 # H  listing_category
        n(listing.get("class")),                            # I  class
        n(listing.get("title")),                            # J  title
        n(listing.get("num_head")),                         # K  num_head
        n(listing.get("state")),                            # L  state
        n(listing.get("location")),                         # M  location
        n(listing.get("vendor")),                           # N  vendor
        n(listing.get("breed")),                            # O  breed
        breed_groups_str,                                   # P  breed_groups
        n(listing.get("avg_weight_kg")),                    # Q  avg_weight_kg
        n(listing.get("weight_at_assessment_kg")),          # R  weight_at_assessment_kg
        n(listing.get("weight_min")),                       # S  weight_min
        n(listing.get("weight_max")),                       # T  weight_max
        n(listing.get("weight_range_kg")),                  # U  weight_range_kg
        n(listing.get("delivery_adjustment_pct")),          # V  delivery_adjustment_pct
        n(listing.get("liveweight_gain_per_day")),          # W  liveweight_gain_per_day
        n(listing.get("dressing_pct")),                     # X  dressing_pct
        n(listing.get("fat_score")),                        # Y  fat_score
        n(listing.get("age_min_months")),                   # Z  age_min_months
        n(listing.get("age_max_months")),                   # AA age_max_months
        n(listing.get("hours_off_feed")),                   # AB hours_off_feed
        n(listing.get("assessment_date")),                  # AC assessment_date
        n(listing.get("horn_status")),                      # AD horn_status
        n(listing.get("temperament")),                      # AE temperament
        n(listing.get("store_condition")),                  # AF store_condition
        b(listing.get("is_EU")),                            # AG is_EU
        b(listing.get("is_NE")),                            # AH is_NE
        b(listing.get("is_LPA")),                           # AI is_LPA
        b(listing.get("is_MSA")),                           # AJ is_MSA
        b(listing.get("has_WHP")),                          # AK has_WHP
        b(listing.get("HGP_free")),                         # AL HGP_free (None → "" = unknown)
        n(listing.get("lifetime_traceable_pct")),           # AM lifetime_traceable_pct
        n(listing.get("price_per_head")),                   # AN price_per_head
        n(listing.get("price_c_kg")),                       # AO price_c_kg
        n(listing.get("sale_type_pricing")),                # AP sale_type_pricing
        flag or "No valuation",                             # AQ valuation_flag
        n(fair_value),                                      # AR fair_value_at_alert
        b(listing.get("catalogue_pending")),                # AS catalogue_pending
    ]
    return row


def append_rows_with_retry(worksheet, rows, label):
    """Append buffered rows in one API call, retrying across quota windows."""
    if not rows:
        print(f"No {label} rows to write.")
        return True

    for attempt in range(1, BATCH_WRITE_RETRIES + 1):
        try:
            worksheet.append_rows(rows, value_input_option="RAW", table_range="A1")
            print(f"  ✅  Wrote {len(rows)} {label} row(s) in one batch.")
            return True
        except Exception as e:
            if attempt == BATCH_WRITE_RETRIES:
                print(
                    f"  ⚠️  {label} batch write FAILED after {attempt} attempts: {e}\n"
                    f"  {len(rows)} buffered {label} row(s) were not written."
                )
                return False

            delay = BATCH_WRITE_BACKOFFS[min(attempt - 1, len(BATCH_WRITE_BACKOFFS) - 1)]
            print(f"  ⚠️  {label} batch write failed on attempt {attempt}: {e}")
            print(f"  Retrying {label} batch in {delay}s...")
            time.sleep(delay)


# ─────────────────────────────────────────────
# STEP 9 — VALUATION
# ─────────────────────────────────────────────

def is_date_like(value):
    """Return True when a model timestamp cell looks like a date."""
    text = str(value or "").strip()
    return bool(
        re.search(r"\b\d{4}-\d{1,2}-\d{1,2}\b", text)
        or re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)
    )


def get_model_fair_value(worksheet_model):
    """Reads the most recent plausible fair value from cattle_model.py output."""
    try:
        rows = worksheet_model.get_all_values()
    except Exception as e:
        print(f"  ⚠️  Could not read model fair value: {e}")
        return None

    for row in reversed(rows[1:]):  # skip header
        if len(row) < 2:
            continue

        timestamp = row[0].strip()
        raw_value = row[1].strip()
        if not raw_value:
            continue

        if not is_date_like(timestamp):
            print(f"  ⚠️  Ignoring model row without date-like timestamp: {row[:2]}")
            continue

        try:
            fair_value = float(raw_value.replace(",", ""))
        except ValueError:
            print(f"  ⚠️  Ignoring non-numeric model fair value: {raw_value!r}")
            continue

        if not (MODEL_FAIR_VALUE_MIN_C_KG <= fair_value <= MODEL_FAIR_VALUE_MAX_C_KG):
            print(f"  ⚠️  Ignoring implausible model fair value: {fair_value}c/kg at {timestamp}")
            continue

        print(f"  Model fair value source: {fair_value}c/kg at {timestamp}")
        return fair_value

    print("  ⚠️  No plausible model fair value found.")
    return None


def score_listing(listing, fair_value_c_kg):
    """Compares listing price against model fair value."""
    if not listing["price_c_kg"] or not fair_value_c_kg:
        return None
    ratio = listing["price_c_kg"] / fair_value_c_kg
    if ratio < (1 - UNDERVALUED_THRESHOLD):
        return "🟢 UNDERVALUED"
    elif ratio > (1 + OVERVALUED_THRESHOLD):
        return "🔴 OVERPRICED"
    else:
        return "🟡 FAIR"


# ─────────────────────────────────────────────
# STEP 10 — WHATSAPP ALERTS
# ─────────────────────────────────────────────

def send_watching_alert(listing, twilio_to):
    """
    Stage 1 WATCHING alert — catalogue not yet released.
    Sends lightweight pre-catalogue notification: class, head count, location, sale date.
    Weight, breed, fat score and age are not yet available — full alert follows
    when catalogue releases and the lot is re-processed.

    twilio_to: the recipient's WhatsApp number for this specific user.
    """
    calf_line = f" · {listing['num_calves']} calves at foot" if listing.get("num_calves") else ""
    message = (
        f"👁 WATCHING — {listing['title']}\n"
        f"{listing['num_head']} head{calf_line} · {listing['class'].title()}\n"
        f"{listing['location']} · {listing['sale_date']}\n"
        f"Catalogue not yet released — full alert to follow.\n"
        f"Agent: {listing['vendor']}\n"
        f"{listing['url']}"
    )
    if TEST_MODE:
        print(f"  [TEST MODE — no WhatsApp sent]\n  Message would be:\n{message}")
        return True
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=twilio_to)
        print(f"  👁  Watching alert sent: {listing['title']}")
        return True
    except Exception as e:
        print(f"  ⚠️  Watching alert FAILED for {listing['title']}: {e}")
        return False


def send_alert(listing, flag, fair_value_c_kg, twilio_to):
    """
    Single alert function. Sends full listing details.
    Fields that the parser could not populate are omitted cleanly.

    twilio_to: the recipient's WhatsApp number for this specific user.
    """
    flag_line  = f"{flag} — " if flag else ""
    calf_line  = f" · {listing['num_calves']} calves at foot" if listing.get("num_calves") else ""

    # Breed line
    breed_str  = listing["breed"] if listing["breed"] != "Unknown" else ""
    breed_line = f"{listing['num_head']} head{calf_line} · {breed_str + ' · ' if breed_str else ''}{listing['class'].title()}\n"

    # Weight / condition line
    weight_str = f"Avg {listing['avg_weight_kg']}kg" if listing["avg_weight_kg"] else ""
    range_str  = f" · Range {listing['weight_range_kg']}kg" if listing["weight_range_kg"] else ""
    age_str    = f" · {listing['age_min_months']}–{listing['age_max_months']}mo" if listing["age_min_months"] else ""
    fat_str    = f" · Fat {listing['fat_score']}" if listing["fat_score"] else ""
    cond_str   = f" · {listing['store_condition'].replace('_',' ').title()}" if listing.get("store_condition") else ""
    detail_line = f"{weight_str}{range_str}{age_str}{fat_str}{cond_str}\n" if weight_str or age_str else ""

    # Hours off feed note — flag if non-standard (not 8hrs)
    feed_note = ""
    if listing.get("hours_off_feed") is not None and listing["hours_off_feed"] != 8:
        feed_note = f"⚠️ {listing['hours_off_feed']}hrs off feed (std 8hrs — weight may be inflated)\n"

    # Liveweight gain note
    gain_note = ""
    if listing.get("liveweight_gain_per_day") is not None:
        gain_note = f"LWG: {listing['liveweight_gain_per_day']} kg/day\n"

    # Accreditations
    accreds = " ".join(filter(None, [
        "EU"  if listing.get("is_EU")   else "",
        "NE"  if listing.get("is_NE")   else "",
        "LPA" if listing.get("is_LPA")  else "",
        "MSA" if listing.get("is_MSA")  else "",
        "HGP-free" if listing.get("HGP_free") else "",
        "WHP" if listing.get("has_WHP") else "",
    ]))
    accred_line = f"Accreditations: {accreds}\n" if accreds else ""

    # Horn / temperament
    trait_parts = []
    if listing.get("horn_status"):
        trait_parts.append(listing["horn_status"].title())
    if listing.get("temperament"):
        trait_parts.append(listing["temperament"].title())
    trait_line = f"{' · '.join(trait_parts)}\n" if trait_parts else ""

    # Price / valuation
    price_line = ""
    if fair_value_c_kg:
        price_line = f"Model fair value: {fair_value_c_kg}c/kg lwt\n"

    message = (
        f"🐄 ALERT — {flag_line}{listing['title']}\n"
        f"{breed_line}"
        f"{detail_line}"
        f"{feed_note}"
        f"{gain_note}"
        f"{trait_line}"
        f"{accred_line}"
        f"{price_line}"
        f"{listing['location']} · {listing['sale_date']}\n"
        f"Agent: {listing['vendor']}\n"
        f"{listing['url']}"
    )

    if TEST_MODE:
        print(f"  [TEST MODE — no WhatsApp sent]\n  Message would be:\n{message}")
        return True
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_FROM, to=twilio_to)
        print(f"  🐄  Alert sent: {listing['title']}")
        return True
    except Exception as e:
        print(f"  ⚠️  Alert FAILED for {listing['title']}: {e}")
        return False


def validate_twilio_delivery_mode():
    """
    Require an explicit WhatsApp sender path before live sends.

    The sandbox and registered sender paths have different delivery constraints;
    forcing the operator to declare the path prevents accidental live runs with
    an unexamined Twilio setup.
    """
    if TEST_MODE:
        return

    if TWILIO_WHATSAPP_MODE not in ("sandbox", "registered"):
        raise RuntimeError(
            "Set TWILIO_WHATSAPP_MODE to 'sandbox' or 'registered' before live sends."
        )

    if TWILIO_WHATSAPP_MODE == "sandbox":
        print("  Twilio WhatsApp mode: sandbox — every recipient must have joined the sandbox.")
    else:
        print("  Twilio WhatsApp mode: registered — confirm freeform/template policy before live sends.")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Cattle Scout — starting run")
    print(f"Time: {utc_timestamp()}")
    print("=" * 60)

    # Fail fast if any required credential is missing from .env.
    required_vars = {
        "TWILIO_ACCOUNT_SID":       TWILIO_ACCOUNT_SID,
        "TWILIO_AUTH_TOKEN":        TWILIO_AUTH_TOKEN,
        "TWILIO_FROM":              TWILIO_FROM,
    }
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {missing}. "
            f"Check your .env file. See .env.example for the template."
        )
    validate_twilio_delivery_mode()

    # Connect to Google Sheets
    spreadsheet = open_spreadsheet(SPREADSHEET_NAME, creds_file=get_credentials_file())

    worksheet_log = get_or_create_worksheet(
        spreadsheet, LOG_TAB, rows=5000, cols=len(LOG_HEADER_V23)
    )
    ensure_header_row(worksheet_log, LOG_HEADER_V23, accepted_headers=[LOG_HEADER_DISPLAY_V23])

    worksheet_listings = get_or_create_worksheet(
        spreadsheet, LISTINGS_TAB, rows=5000, cols=len(LISTINGS_HEADER_V23)
    )
    ensure_listings_header(worksheet_listings)

    try:
        worksheet_config = spreadsheet.worksheet(CONFIG_TAB)
    except WorksheetNotFound as e:
        raise RuntimeError(
            f"Missing required worksheet '{CONFIG_TAB}' in spreadsheet '{SPREADSHEET_NAME}'."
        ) from e

    try:
        worksheet_model = spreadsheet.worksheet(MODEL_TAB)
    except WorksheetNotFound as e:
        raise RuntimeError(
            f"Missing required worksheet '{MODEL_TAB}' in spreadsheet '{SPREADSHEET_NAME}'."
        ) from e

    # Load all active user configs from the Sheet.
    # Returns a list of dicts — one per active user with a valid twilio_to.
    all_users = load_config(worksheet_config)

    if not all_users:
        print("No active users found in config — exiting.")
        return

    # Load the dedup log once — keyed on (url, user_id) so each user's
    # alert history is independent. A listing seen by User 1 can still
    # alert User 2 if it matches their criteria.
    log_status = get_log_status(worksheet_log)
    print(f"Log entries: {len(log_status)}")

    # Read the model fair value once — same value applies to all users.
    fair_value = get_model_fair_value(worksheet_model)
    print(f"Model fair value: {fair_value}c/kg lwt" if fair_value else "Model fair value: not available.")

    # Discover and scrape listings once per enabled source — the shared result
    # set is then evaluated independently for each user.
    source_defs = get_source_definitions()
    print(f"Enabled sources this run: {[source['name'] for source in source_defs]}")
    shared_listings = collect_source_listings(source_defs)

    # ── Outer loop: iterate over each active user ──
    # For each user we run the full filter and alert pipeline independently.
    total_alerts   = 0
    total_watching = 0

    for user_config in all_users:
        user_id   = user_config["user_id"]
        twilio_to = user_config["twilio_to"]

        print(f"\n{'─' * 40}")
        print(f"Processing user: {user_id}")
        print(f"{'─' * 40}")

        if not user_config.get("active", True):
            # Redundant safety check — load_config already excludes inactive users,
            # but belt-and-braces given the consequence of mis-alerting.
            print(f"  User '{user_id}' inactive — skipping.")
            continue

        alerts_sent   = 0
        watching_sent = 0
        user_log_rows = []
        user_listing_rows = []

        for listing in shared_listings:
            url = listing["url"]
            # Per-user dedup: check (url, user_id) tuple in the log.
            existing_status = log_status.get((url, user_id))

            if is_dedup_alerted(existing_status):
                print(f"  Skipping (already alerted {user_id}, status={existing_status}): {url}")
                continue

            matched, reason = listing_match(listing, user_config)
            if not matched:
                print(
                    f"  No match [{reason}]: {listing['title']} "
                    f"({listing['state']} · {listing['listing_category']} · "
                    f"{listing['class']} · {listing['num_head']} head)"
                )
                continue

            # ── Two-stage alert logic ──
            if listing["catalogue_pending"]:
                if not is_dedup_watching(existing_status):
                    if not send_watching_alert(listing, twilio_to):
                        print("  Watching alert not logged; it will retry on the next run.")
                        continue

                    status = runtime_log_status("WATCHING")
                    user_log_rows.append(build_log_listing_row(listing, status, user_id))
                    user_listing_rows.append(build_listing_full_row(listing, status, None, None, user_id))
                    # Update local log_status immediately so this run dedups
                    # against buffered writes before they are flushed.
                    log_status[(url, user_id)] = status
                    watching_sent += 1
                else:
                    print(f"  Already watching ({user_id}): {listing['title']}")
            else:
                flag = score_listing(listing, fair_value)
                if not send_alert(listing, flag, fair_value, twilio_to):
                    print("  Alert not logged; it will retry on the next run.")
                    continue

                status = runtime_log_status("ALERTED")
                user_log_rows.append(
                    build_log_listing_row(listing, status, user_id, flag or "No valuation")
                )
                user_listing_rows.append(
                    build_listing_full_row(listing, status, flag, fair_value, user_id)
                )
                log_status[(url, user_id)] = status
                alerts_sent += 1

        if user_log_rows or user_listing_rows:
            print(f"\nFlushing Google Sheets writes for user '{user_id}'...")
            log_write_ok = append_rows_with_retry(worksheet_log, user_log_rows, "log")
            if not log_write_ok:
                raise RuntimeError(
                    "Dedup log write failed after successful alert sends; "
                    "aborting before processing more users."
                )

            listings_write_ok = append_rows_with_retry(worksheet_listings, user_listing_rows, "listings")
            if not listings_write_ok:
                print("  ⚠️  Analytical listings history may be incomplete because listing rows failed to write.")

        print(f"  User '{user_id}' — Watching: {watching_sent}. Alerts: {alerts_sent}.")
        total_alerts   += alerts_sent
        total_watching += watching_sent

    print("=" * 60)
    print(f"Run complete. Users: {len(all_users)}. Watching: {total_watching}. Alerts: {total_alerts}.")
    print("=" * 60)


if __name__ == "__main__":
    main()
