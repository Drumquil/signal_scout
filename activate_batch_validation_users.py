"""
Activate dummy users for one controlled batch-write validation run.

The original dummy users are reactivated. A fresh validation pair is also added
so the run produces enough new per-user rows to exercise batched Sheet writes.
"""

import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

SPREADSHEET_NAME = "drumquil_scout"
CONFIG_TAB = "cattle_scout_config"
CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE")

USERS = [
    "dummy_multi_a",
    "dummy_multi_b",
    "dummy_batch_a",
    "dummy_batch_b",
]


def connect_config_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_NAME).worksheet(CONFIG_TAB)


def get_user_blocks(rows):
    blocks = {}
    for row in rows[1:]:
        if len(row) < 3:
            continue
        user_id = row[0].strip()
        setting = row[1].strip()
        value = row[2].strip()
        if user_id:
            blocks.setdefault(user_id, {})[setting] = value
    return blocks


def build_dummy_rows(user_id, twilio_to):
    notes = f"Codex {user_id} for batch-write validation. Broad criteria."

    def row(setting, value):
        return [user_id, setting, value]

    return [
        row("active", "TRUE"),
        row("twilio_to", twilio_to),
        row("target_states", ""),
        row("target_sex", ""),
        row("target_classes", ""),
        row("include_breeding_females", "FALSE"),
        row("include_bulls", "FALSE"),
        row("include_cow_calf_units", "FALSE"),
        row("min_head", "1"),
        row("max_head", "1000"),
        row("target_breeds", ""),
        row("min_weight_kg", ""),
        row("max_weight_kg", ""),
        row("max_weight_range_kg", ""),
        row("age_min_months", ""),
        row("age_max_months", ""),
        row("min_fat_score", ""),
        row("fat_score_max", ""),
        row("require_EU", "FALSE"),
        row("require_NE", "FALSE"),
        row("exclude_WHP", "FALSE"),
        row("require_HGP_free", "FALSE"),
        row("require_polled", "FALSE"),
        row("require_quiet", "FALSE"),
        row("notes", notes),
    ]


def main():
    ws = connect_config_sheet()
    rows = ws.get_all_values()
    blocks = get_user_blocks(rows)

    active_seed = None
    for user_id, cfg in blocks.items():
        if cfg.get("twilio_to") and user_id not in USERS:
            active_seed = (user_id, cfg["twilio_to"])
            break

    if not active_seed:
        raise RuntimeError("No seed user with twilio_to found.")

    seed_user_id, twilio_to = active_seed
    print(f"Using twilio_to from seed user: {seed_user_id} -> {twilio_to}")

    for user_id in USERS:
        if user_id not in blocks:
            ws.append_rows(build_dummy_rows(user_id, twilio_to), value_input_option="RAW")
            print(f"Added {user_id}.")
            continue

        active_updated = False
        twilio_updated = False
        for cell in ws.findall(user_id, in_column=1):
            setting = ws.cell(cell.row, 2).value
            if setting == "active":
                ws.update_cell(cell.row, 3, "TRUE")
                active_updated = True
            elif setting == "twilio_to":
                ws.update_cell(cell.row, 3, twilio_to)
                twilio_updated = True

        extra_rows = []
        if not active_updated:
            extra_rows.append([user_id, "active", "TRUE"])
        if not twilio_updated:
            extra_rows.append([user_id, "twilio_to", twilio_to])
        if extra_rows:
            ws.append_rows(extra_rows, value_input_option="RAW")
        print(f"Activated {user_id}.")

    print("Done.")


if __name__ == "__main__":
    main()
