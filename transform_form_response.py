"""
transform_form_response.py
Drumquil Signal — Signal Scout | v1.2 | May 2026

PURPOSE:
    Reads the most recent (or specified) row from the Signal Scout Google Form
    response Sheet and writes a correctly formatted row-block to cattle_scout_config.

    Run this manually once per new beta tester after they submit the form.
    Not a cron job.

USAGE:
    python transform_form_response.py
        → processes the most recent form response

    python transform_form_response.py --row 3
        → processes row 3 of the response Sheet (row 1 = header, row 2 = first response)

REQUIREMENTS:
    pip install gspread oauth2client python-dotenv
    .env file with GOOGLE_SHEETS_CREDS_FILE set

COLUMN HEADERS (response Sheet — current v2.1):
    Timestamp | Email address | Your name | Your WhatsApp number |
    Your property name (optional) | Which regions are you buying from? |
    Your nearest town or delivery point | Sex preference | Stage of production |
    Female breeding stock | Bulls | Minimum number of head in a lot |
    Maximum number of head in a lot | Which breeds will you consider? |
    Do you also want alerts for cross-bred cattle... |
    Minimum average liveweight (kg) | Maximum average liveweight (kg) |
    Maximum weight spread within the mob (kg) | Do you want to filter by age? |
    Minimum age (months) | Maximum age (months) |
    Minimum fat score | Maximum fat score |
    Require EU accreditation? | Require Greenham Never Ever (NE) accreditation? |
    Exclude listings with a chemical withholding period (WHP)? |
    Require HGP-free declaration? | Require polled (no horns)? |
    Require quiet / docile temperament rating? |
    Is there anything specific you're looking for that wasn't covered above?

NOTE ON FORM VERSION:
    This script is written for form v2.0/v2.1 headers.
    If you need to process a response from the old v1.0 form (which had
    "Commercial store / feeder cattle" instead of Sex / Stage questions),
    see the OLD FORM NOTE comments below.
"""

import os
import re
import sys
import argparse
from collections import Counter
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

# The main Drumquil Scout spreadsheet now hosts both the config tab and
# the linked Google Form responses tab.
CONFIG_SPREADSHEET_NAME   = "drumquil_scout"
CONFIG_TAB_NAME           = "cattle_scout_config"
RESPONSE_SPREADSHEET_NAME = CONFIG_SPREADSHEET_NAME
RESPONSE_SHEET_NAME       = "Form responses 1"

CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE")

RESPONSE_HEADER_ALIASES = {
    "Timestamp": ["Timestamp"],
    "Email address": ["Email address"],
    "Your name": ["Your name"],
    "Your WhatsApp number": ["Your WhatsApp number"],
    "Your property name (optional)": ["Your property name (optional)"],
    "Which regions are you buying from?": ["Which regions are you buying from?"],
    "Your nearest town or delivery point": ["Your nearest town or delivery point"],
    "Sex preference": ["Sex preference"],
    "Stage of production": ["Stage of production"],
    "Female breeding stock": ["Female breeding stock", "Breeding females"],
    "Bulls": ["Bulls"],
    "Minimum number of head in a lot": ["Minimum number of head in a lot"],
    "Maximum number of head in a lot": ["Maximum number of head in a lot"],
    "Which breeds will you consider?": ["Which breeds will you consider?"],
    "Do you also want alerts for cross-bred cattle where your selected breed is the primary breed?": [
        "Do you also want alerts for cross-bred cattle where your selected breed is the primary breed?",
        "Do you also want alerts for cross-bred cattle..."
    ],
    "Minimum average liveweight (kg)": ["Minimum average liveweight (kg)"],
    "Maximum average liveweight (kg)": ["Maximum average liveweight (kg)"],
    "Maximum weight spread within the mob (kg)": ["Maximum weight spread within the mob (kg)"],
    "Do you want to filter by age?": ["Do you want to filter by age?"],
    "Minimum age (months)": ["Minimum age (months)"],
    "Maximum age (months)": ["Maximum age (months)"],
    "Minimum fat score": ["Minimum fat score"],
    "Maximum fat score": ["Maximum fat score"],
    "Require EU accreditation?": ["Require EU accreditation?"],
    "Require Greenham Never Ever (NE) accreditation?": ["Require Greenham Never Ever (NE) accreditation?"],
    "Exclude listings with a chemical withholding period (WHP)?": ["Exclude listings with a chemical withholding period (WHP)?"],
    "Require HGP-free declaration?": ["Require HGP-free declaration?"],
    "Require polled (no horns)?": ["Require polled (no horns)?"],
    "Require quiet / docile temperament rating?": ["Require quiet / docile temperament rating?"],
    "Is there anything specific you're looking for that wasn't covered above?": [
        "Is there anything specific you're looking for that wasn't covered above?"
    ],
}
REQUIRED_RESPONSE_HEADERS = tuple(RESPONSE_HEADER_ALIASES.keys())

# Region → state code mapping
# Named regions from form → ISO state codes used in target_states config field
REGION_TO_STATES = {
    "Northern Rivers NSW":      ["NSW"],
    "Northern Tablelands NSW":  ["NSW"],
    "New England NSW":          ["NSW"],
    "Central & Western NSW":    ["NSW"],
    "Southern NSW / ACT":       ["NSW", "ACT"],
    "South East QLD":           ["QLD"],
    "Central QLD":              ["QLD"],
    "North QLD":                ["QLD"],
    "Victoria":                 ["VIC"],
    "South Australia":          ["SA"],
    "Western Australia":        ["WA"],
    "Tasmania":                 ["TAS"],
    "Any / no preference":      [],     # empty = no state filter
}
REGION_OPTIONS = tuple(REGION_TO_STATES.keys())

# Stage of production → target_classes mapping
# These match the class strings used by detect_class() in cattle_scout.py
STAGE_TO_CLASSES = {
    "Weaners / Weaned":                  ["weaner", "weaned"],
    "Yearlings":                         ["yearling"],
    "Backgrounders, Stores & Feeders":   ["backgrounder", "store", "feeder"],
    "Any stage — no preference":         [],  # empty = no class filter
}
STAGE_OPTIONS = tuple(STAGE_TO_CLASSES.keys())

# Sex → target_sex mapping
SEX_TO_CONFIG = {
    "Steers":                                     "steer",
    "Heifers":                                    "heifer",
    "Either — steers, heifers, or mixed is fine": "",  # empty = no sex filter
}
BULL_OPTIONS = (
    "Registered / stud bulls",
    "Commercial bulls",
)
BREEDING_FEMALE_OPTIONS = (
    "Joined / PTIC / NSM Heifers",
    "Joined / PTIC / NSM Cows",
    "Cows with Calves at Foot (CAF)",
)
BREED_OPTIONS = (
    "Angus",
    "Red Angus",
    "Poll Hereford",
    "Hereford",
    "Murray Grey",
    "Shorthorn",
    "Simmental",
    "Charolais",
    "Limousin",
    "South Devon",
    "Devon",
    "Speckle Park",
    "Wagyu",
    "Blonde d'Aquitaine",
    "Gelbvieh",
    "Salers",
    "Maine-Anjou",
    "Marchigiana",
    "Romagnola",
    "Piedmontese",
    "Brahman",
    "Droughtmaster",
    "Santa Gertrudis",
    "Belmont Red",
    "Charbray",
    "Braford",
    "Brangus",
    "Ultrablack",
    "Beefmaster",
    "Brahmousin",
    "Simbrah",
    "Chiangus",
    "Akaushi",
    "Any / no preference",
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def connect_sheets():
    """
    Authenticate and return two spreadsheet objects:
      - response_ss: the Google Form response spreadsheet
      - config_ss:   the main drumquil_scout config spreadsheet
    """
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    response_ss = client.open(RESPONSE_SPREADSHEET_NAME)
    config_ss   = client.open(CONFIG_SPREADSHEET_NAME)
    return response_ss, config_ss

def get_worksheet_case_insensitive(spreadsheet, title):
    """Return worksheet by exact title, falling back to case-insensitive match."""
    try:
        return spreadsheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        wanted = title.casefold()
        for worksheet in spreadsheet.worksheets():
            if worksheet.title.casefold() == wanted:
                return worksheet
        raise

def slugify(name):
    """
    Convert a person's name to a safe user_id string.
    "Tom Flanagan" → "tom_flanagan"
    Strips special characters, lowercases, replaces spaces with underscores.
    """
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name

def normalise_whatsapp(raw):
    """
    Normalise a WhatsApp number to E.164 format with whatsapp: prefix.
    Handles common Australian input errors:
      - "0407139867"      → "whatsapp:+61407139867"  (missing country code)
      - "+61 407 139 867" → "whatsapp:+61407139867"  (spaces)
      - "61407139867"     → "whatsapp:+61407139867"  (missing + prefix)
      - "+61407139867"    → "whatsapp:+61407139867"  (already correct)
    Non-Australian numbers (not starting with 04 or 61) are passed through
    with spaces/dashes stripped — just the whatsapp: prefix is added.
    Raises ValueError if the result looks implausibly short.
    """
    # Strip whitespace, dashes, parentheses
    number = re.sub(r"[\s\-()]", "", raw.strip())

    # Strip existing whatsapp: prefix if present — we'll re-add it cleanly
    if number.lower().startswith("whatsapp:"):
        number = number[9:]

    # Australian mobile: starts with 04 → replace leading 0 with +61
    if re.match(r"^04\d{8}$", number):
        number = "+61" + number[1:]

    # Australian mobile: starts with 614 (missing +) → add +
    elif re.match(r"^614\d{8}$", number):
        number = "+" + number

    # Already has + — strip non-digits after + and reattach
    elif number.startswith("+"):
        digits = re.sub(r"\D", "", number)
        number = "+" + digits

    # Fallback: strip non-digits, assume needs + prefix
    else:
        digits = re.sub(r"\D", "", number)
        number = "+" + digits

    if len(number) < 10:
        raise ValueError(f"WhatsApp number '{raw}' is too short after normalisation — check it is correct.")

    return f"whatsapp:{number}"

def parse_list_field(raw):
    """
    Google Forms checkbox responses come back as comma-separated strings.
    e.g. "Angus, Hereford, Angus Cross"
    Returns a list of stripped strings, or [] if blank.
    """
    if not raw or not raw.strip():
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]

def parse_checkbox_field(raw, allowed_options):
    """
    Parse a Google Forms checkbox response using known option strings.

    This avoids mis-parsing options that themselves contain commas, such as
    "Backgrounders, Stores & Feeders".
    """
    if not raw or not raw.strip():
        return []

    pattern = "|".join(re.escape(option) for option in sorted(allowed_options, key=len, reverse=True))
    matches = re.findall(pattern, raw)
    if matches:
        return matches

    return parse_list_field(raw)

def parse_numeric(raw):
    """Strip non-numeric characters and return a number string, or '' if blank."""
    if not raw or not raw.strip():
        return ""
    cleaned = re.sub(r"[^0-9.]", "", raw.strip())
    return cleaned if cleaned else ""

def normalise_header_name(raw):
    """Normalise response headers to make light wording/spacing changes safe."""
    return " ".join((raw or "").strip().split())

def validate_response_headers(headers):
    """
    Validate the live response header row and build a canonical-header map.

    Supports the v2.1 live contract and the single known legacy alias
    "Breeding females" -> "Female breeding stock".
    """
    alias_to_canonical = {}
    for canonical, aliases in RESPONSE_HEADER_ALIASES.items():
        for alias in aliases:
            alias_to_canonical[normalise_header_name(alias)] = canonical

    canonical_hits = []
    seen_source_headers = set()
    for header in headers:
        normalised = normalise_header_name(header)
        if normalised in seen_source_headers:
            raise ValueError(f"Duplicate response header detected: {header!r}")
        seen_source_headers.add(normalised)
        canonical = alias_to_canonical.get(normalised)
        if canonical:
            canonical_hits.append(canonical)

    duplicate_canonical = [name for name, count in Counter(canonical_hits).items() if count > 1]
    if duplicate_canonical:
        dupes = ", ".join(sorted(duplicate_canonical))
        raise ValueError(
            f"Response sheet has multiple headers mapping to the same field: {dupes}. "
            "Keep one header per field before transforming."
        )

    missing = [header for header in REQUIRED_RESPONSE_HEADERS if header not in canonical_hits]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(
            "Response sheet is missing required v2.1 headers: "
            f"{missing_list}. Check the live form version and linked response tab."
        )

    return alias_to_canonical

def build_response_row_dict(headers, data_row):
    """Return one response row keyed by canonical header names."""
    alias_to_canonical = validate_response_headers(headers)
    row_dict = {}
    for idx, header in enumerate(headers):
        canonical = alias_to_canonical.get(normalise_header_name(header))
        if not canonical:
            continue
        row_dict[canonical] = data_row[idx] if idx < len(data_row) else ""
    return row_dict

def map_breeding_female_classes(raw_breeding):
    """
    Convert selected breeding-female form options into coarse matcher classes.

    Current runtime only needs to distinguish cow lines from heifer lines.
    Cow-and-calf units are handled separately via include_cow_calf_units.
    """
    classes = []
    for option in raw_breeding:
        option_lower = option.lower()
        if "heifer" in option_lower or "future breeder" in option_lower:
            classes.append("heifer")
        if "cow" in option_lower and "calf" not in option_lower and "caf" not in option_lower:
            classes.append("cow")

    seen = set()
    return [cls for cls in classes if not (cls in seen or seen.add(cls))]

def user_id_exists(config_ws, user_id):
    """Check if a user_id block already exists in the config tab."""
    col_a = config_ws.col_values(1)  # all values in column A
    return user_id in col_a

# ─────────────────────────────────────────────
# CORE TRANSFORM
# ─────────────────────────────────────────────

def transform_response(row_dict):
    """
    Takes a dict of {column_header: value} for one form response row.
    Returns a list of [user_id, setting, value] rows ready to append to config.
    """
    rows = []

    # ── user_id and twilio_to ──
    name = row_dict.get("Your name", "").strip()
    user_id = slugify(name)
    whatsapp = row_dict.get("Your WhatsApp number", "").strip()

    if not user_id:
        raise ValueError("Name is blank — cannot generate user_id.")
    if not whatsapp:
        raise ValueError("WhatsApp number is blank — required field.")

    def r(setting, value):
        rows.append([user_id, setting, value])

    # ── Required fields ──
    r("active",    "TRUE")
    r("twilio_to", normalise_whatsapp(whatsapp))

    # ── Region → target_states ──
    raw_regions = parse_checkbox_field(
        row_dict.get("Which regions are you buying from?", ""),
        REGION_OPTIONS,
    )
    states = []
    any_region = False
    for region in raw_regions:
        if region == "Any / no preference":
            any_region = True
            break
        states.extend(REGION_TO_STATES.get(region, []))
    # Deduplicate while preserving order
    seen = set()
    states = [s for s in states if not (s in seen or seen.add(s))]
    r("target_states", ", ".join(states) if not any_region else "")

    # ── Sex → target_sex ──
    raw_sex = row_dict.get("Sex preference", "").strip()
    target_sex = SEX_TO_CONFIG.get(raw_sex, "")
    r("target_sex", target_sex)

    # ── Stage → target_classes ──
    raw_stages = parse_checkbox_field(
        row_dict.get("Stage of production", ""),
        STAGE_OPTIONS,
    )
    classes = []
    any_stage = False
    for stage in raw_stages:
        if stage == "Any stage — no preference":
            any_stage = True
            break
        classes.extend(STAGE_TO_CLASSES.get(stage, []))
    target_classes_value = ", ".join(classes) if not any_stage else ""
    r("target_classes", target_classes_value)

    include_commercial = bool(raw_sex or raw_stages)
    r("include_commercial", "TRUE" if include_commercial else "FALSE")

    # ── Breeding females and bulls ──
    raw_breeding = parse_checkbox_field(
        row_dict.get("Female breeding stock", ""),
        BREEDING_FEMALE_OPTIONS,
    )
    breeding_female_classes = map_breeding_female_classes(raw_breeding)
    include_breeding = len(breeding_female_classes) > 0
    r("include_breeding_females", "TRUE" if include_breeding else "FALSE")
    r("breeding_female_classes", ", ".join(breeding_female_classes))

    raw_bulls = parse_checkbox_field(row_dict.get("Bulls", ""), BULL_OPTIONS)
    include_bulls = len(raw_bulls) > 0
    r("include_bulls", "TRUE" if include_bulls else "FALSE")

    # Cow-and-calf units: activated if "Cows with Calves at Foot (CAF)" ticked
    include_caf = any("calf" in b.lower() or "caf" in b.lower() for b in raw_breeding)
    r("include_cow_calf_units", "TRUE" if include_caf else "FALSE")

    # ── Number of head ──
    r("min_head", parse_numeric(row_dict.get("Minimum number of head in a lot", "")))
    r("max_head", parse_numeric(row_dict.get("Maximum number of head in a lot", "")))

    # ── Breed ──
    raw_breeds = parse_checkbox_field(
        row_dict.get("Which breeds will you consider?", ""),
        BREED_OPTIONS,
    )
    any_breed = "Any / no preference" in raw_breeds
    if any_breed:
        r("target_breeds", "")
    else:
        # Check cross-breed preference and append "X Cross" variants if Yes
        cross_pref = row_dict.get(
            "Do you also want alerts for cross-bred cattle where your selected breed is the primary breed?", ""
        ).strip()
        if cross_pref.startswith("Yes"):
            cross_breeds = [f"{b} Cross" for b in raw_breeds]
            all_breeds = raw_breeds + cross_breeds
        else:
            all_breeds = raw_breeds
        r("target_breeds", ", ".join(all_breeds))

    # ── Weight ──
    r("min_weight_kg",       parse_numeric(row_dict.get("Minimum average liveweight (kg)", "")))
    r("max_weight_kg",       parse_numeric(row_dict.get("Maximum average liveweight (kg)", "")))
    r("max_weight_range_kg", parse_numeric(row_dict.get("Maximum weight spread within the mob (kg)", "")))

    # ── Age — only applied if gateway question = "Yes" ──
    age_gate = row_dict.get("Do you want to filter by age?", "").strip()
    if age_gate.startswith("Yes"):
        r("age_min_months", parse_numeric(row_dict.get("Minimum age (months)", "")))
        r("age_max_months", parse_numeric(row_dict.get("Maximum age (months)", "")))
    else:
        # No age filter — write blank so load_config() ignores it
        r("age_min_months", "")
        r("age_max_months", "")

    # ── Fat score ──
    fat_min_raw = row_dict.get("Minimum fat score", "").strip()
    fat_max_raw = row_dict.get("Maximum fat score", "").strip()
    r("min_fat_score", "" if fat_min_raw in ("", "No preference") else fat_min_raw)
    r("fat_score_max", "" if fat_max_raw in ("", "No preference") else fat_max_raw)

    # ── Accreditations — "Yes — X only" → TRUE, anything else → FALSE ──
    def accred(col_header, setting):
        val = row_dict.get(col_header, "").strip()
        r(setting, "TRUE" if val.startswith("Yes") else "FALSE")

    accred("Require EU accreditation?",                               "require_EU")
    accred("Require Greenham Never Ever (NE) accreditation?",         "require_NE")
    accred("Exclude listings with a chemical withholding period (WHP)?", "exclude_WHP")
    accred("Require HGP-free declaration?",                           "require_HGP_free")
    accred("Require polled (no horns)?",                              "require_polled")
    accred("Require quiet / docile temperament rating?",              "require_quiet")

    # ── Free text notes (stored for Tom's reference, not used by script) ──
    notes = row_dict.get(
        "Is there anything specific you're looking for that wasn't covered above?", ""
    ).strip()
    r("notes", notes)

    return rows

def validate_transformed_config_rows(config_rows):
    """
    Sanity-check the transformed row-block against the live runtime contract.

    This keeps common onboarding mistakes from silently reaching the config tab.
    """
    settings = {setting: value for _, setting, value in config_rows}

    required_settings = {
        "active", "twilio_to", "target_states", "target_sex", "target_classes",
        "include_commercial", "include_breeding_females", "breeding_female_classes",
        "include_bulls", "include_cow_calf_units",
    }
    missing = sorted(required_settings - settings.keys())
    if missing:
        raise ValueError(f"Transform output is missing required config settings: {', '.join(missing)}")

    if settings["include_commercial"] == "FALSE":
        if settings["target_sex"] or settings["target_classes"]:
            raise ValueError("Commercial filters were written even though include_commercial is FALSE.")

    if settings["include_breeding_females"] == "FALSE" and settings["breeding_female_classes"]:
        raise ValueError("breeding_female_classes should be blank when include_breeding_females is FALSE.")

    if settings["include_breeding_females"] == "TRUE" and not settings["breeding_female_classes"]:
        raise ValueError("include_breeding_females is TRUE but no breeding_female_classes were written.")

    if settings["include_cow_calf_units"] == "TRUE" and "cow" in settings["breeding_female_classes"].lower():
        # Valid, but worth keeping explicit that CAF is a separate toggle from cow lines.
        pass


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Transform a Signal Scout form response into a config row-block.")
    parser.add_argument("--row", type=int, default=None,
                        help="Row number to process (2 = first response). Default: most recent row.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and preview the transform without writing to cattle_scout_config.")
    args = parser.parse_args()

    print("Connecting to Google Sheets...")
    response_ss, config_ss = connect_sheets()

    # Get form response worksheet
    try:
        response_ws = get_worksheet_case_insensitive(response_ss, RESPONSE_SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        print(f"ERROR: Could not find tab '{RESPONSE_SHEET_NAME}' in '{RESPONSE_SPREADSHEET_NAME}'")
        print("Check the tab name in your Google Sheet exactly matches RESPONSE_SHEET_NAME in this script.")
        sys.exit(1)

    # Get all values including header
    all_rows = response_ws.get_all_values()
    if len(all_rows) < 2:
        print("ERROR: No responses found in the response Sheet.")
        sys.exit(1)

    headers = all_rows[0]

    # Determine which row to process
    if args.row is not None:
        row_index = args.row - 1  # convert to 0-based
        if row_index < 1 or row_index >= len(all_rows):
            print(f"ERROR: Row {args.row} doesn't exist. Sheet has {len(all_rows) - 1} response(s).")
            sys.exit(1)
    else:
        row_index = len(all_rows) - 1  # most recent

    data_row = all_rows[row_index]
    try:
        row_dict = build_response_row_dict(headers, data_row)
    except ValueError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    print(f"\nProcessing response from row {row_index + 1}:")
    print(f"  Name:      {row_dict.get('Your name', '(blank)')}")
    print(f"  Timestamp: {row_dict.get('Timestamp', '(blank)')}")
    print(f"  WhatsApp:  {row_dict.get('Your WhatsApp number', '(blank)')}")

    # Transform
    try:
        config_rows = transform_response(row_dict)
        validate_transformed_config_rows(config_rows)
    except ValueError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    user_id = config_rows[0][0]  # first row always has user_id
    print(f"\n  user_id will be: {user_id}")

    # Check for duplicate in config Sheet
    config_ws = config_ss.worksheet(CONFIG_TAB_NAME)
    if user_id_exists(config_ws, user_id):
        print(f"\nWARNING: user_id '{user_id}' already exists in cattle_scout_config.")
        confirm = input("  Overwrite? This will APPEND a second block — review manually. [y/N] ")
        if confirm.strip().lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # Preview
    print(f"\nAbout to append {len(config_rows)} rows to '{CONFIG_TAB_NAME}':")
    for row in config_rows:
        val_preview = str(row[2])[:60] + "..." if len(str(row[2])) > 60 else str(row[2])
        print(f"  {row[0]:<20} {row[1]:<30} {val_preview}")

    if args.dry_run:
        print("\nDry run only — nothing written.")
        sys.exit(0)

    confirm = input("\nLooks correct? Append to config Sheet? [y/N] ")
    if confirm.strip().lower() != "y":
        print("Aborted — nothing written.")
        sys.exit(0)

    # Append to config Sheet
    config_ws.append_rows(config_rows, value_input_option="RAW")

    print(f"\n✅ Done — {len(config_rows)} rows written for user '{user_id}'.")
    print("   Restart or re-run cattle_scout.py to pick up the new config.")


if __name__ == "__main__":
    main()
