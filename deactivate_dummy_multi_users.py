"""
Deactivate the dummy multi-user validation blocks while leaving them in the
config sheet for later reuse.
"""

from sheets_client import open_worksheet

SPREADSHEET_NAME = "drumquil_scout"
CONFIG_TAB = "cattle_scout_config"
TARGET_USERS = {"dummy_multi_a", "dummy_multi_b"}


def main():
    ws = open_worksheet(CONFIG_TAB, spreadsheet_name=SPREADSHEET_NAME)

    rows = ws.get_all_values()
    updates = 0
    for idx, row in enumerate(rows[1:], start=2):
        if len(row) < 3:
            continue
        if row[0].strip() in TARGET_USERS and row[1].strip() == "active":
            ws.update_cell(idx, 3, "FALSE")
            updates += 1

    print(f"Updated active=FALSE for {updates} dummy user blocks.")


if __name__ == "__main__":
    main()
