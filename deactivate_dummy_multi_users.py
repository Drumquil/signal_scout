"""
Deactivate the dummy multi-user validation blocks while leaving them in the
config sheet for later reuse.
"""

import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

SPREADSHEET_NAME = "drumquil_scout"
CONFIG_TAB = "cattle_scout_config"
CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE")
TARGET_USERS = {"dummy_multi_a", "dummy_multi_b"}


def main():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)
    ws = client.open(SPREADSHEET_NAME).worksheet(CONFIG_TAB)

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
