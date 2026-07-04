"""
validate_multi_user_config.py

Create two broad-match dummy users in cattle_scout_config for multi-user
validation, reusing the first active user's WhatsApp destination so the live
runtime can exercise per-user alert routing without inventing a fake number.
"""

from sheets_client import open_worksheet

SPREADSHEET_NAME = "drumquil_scout"
CONFIG_TAB = "cattle_scout_config"

DUMMY_USERS = [
    {
        "user_id": "dummy_multi_a",
        "notes": "Codex dummy user A for multi-user validation. Broad criteria for guaranteed matches.",
    },
    {
        "user_id": "dummy_multi_b",
        "notes": "Codex dummy user B for multi-user validation. Broad criteria for guaranteed matches.",
    },
]


def connect_config_sheet():
    return open_worksheet(CONFIG_TAB, spreadsheet_name=SPREADSHEET_NAME)


def get_all_rows(config_ws):
    return config_ws.get_all_values()


def get_user_blocks(rows):
    blocks = {}
    for row in rows[1:]:
        if len(row) < 3:
            continue
        user_id = row[0].strip()
        setting = row[1].strip()
        value = row[2].strip()
        if not user_id:
            continue
        blocks.setdefault(user_id, {})[setting] = value
    return blocks


def build_dummy_rows(user_id, twilio_to, notes):
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
    config_ws = connect_config_sheet()
    rows = get_all_rows(config_ws)
    blocks = get_user_blocks(rows)

    active_users = [
        (user_id, cfg)
        for user_id, cfg in blocks.items()
        if cfg.get("active", "").upper() == "TRUE" and cfg.get("twilio_to")
    ]
    if not active_users:
        raise RuntimeError("No active user with twilio_to found in cattle_scout_config.")

    seed_user_id, seed_cfg = active_users[0]
    seed_twilio_to = seed_cfg["twilio_to"]
    print(f"Using twilio_to from active seed user: {seed_user_id} -> {seed_twilio_to}")

    for dummy in DUMMY_USERS:
        user_id = dummy["user_id"]
        notes = dummy["notes"]
        if user_id in blocks:
            print(f"User '{user_id}' already exists. Updating active and twilio_to only.")
            found_active = False
            found_twilio = False
            cell_list = config_ws.findall(user_id, in_column=1)
            for cell in cell_list:
                setting = config_ws.cell(cell.row, 2).value
                if setting == "active":
                    config_ws.update_cell(cell.row, 3, "TRUE")
                    found_active = True
                elif setting == "twilio_to":
                    config_ws.update_cell(cell.row, 3, seed_twilio_to)
                    found_twilio = True
            if not found_active or not found_twilio:
                extra_rows = []
                if not found_active:
                    extra_rows.append([user_id, "active", "TRUE"])
                if not found_twilio:
                    extra_rows.append([user_id, "twilio_to", seed_twilio_to])
                if extra_rows:
                    config_ws.append_rows(extra_rows, value_input_option="RAW")
        else:
            dummy_rows = build_dummy_rows(user_id, seed_twilio_to, notes)
            config_ws.append_rows(dummy_rows, value_input_option="RAW")
            print(f"Appended {len(dummy_rows)} rows for '{user_id}'.")

    print("Done.")


if __name__ == "__main__":
    main()
