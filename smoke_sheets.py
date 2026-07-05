"""
smoke_sheets.py
Live smoke check — verifies the Google Sheets service account credentials work
and writes to the cattle_scout_log tab.

This script has live side effects and is intentionally not named test_*.py.
"""

from datetime import datetime, timezone

from sheets_client import open_worksheet


sheet = open_worksheet("cattle_scout_log", spreadsheet_name="drumquil_scout")

logged_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
row = [
    "smoke_test",
    "smoke_sheets.py",
    "SMOKE_TEST",
    "Google Sheets connection successful",
    "ops",
    "smoke",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "Google Sheets",
    "Signal Scout",
    "",
    "manual smoke",
    logged_at,
]

result = sheet.append_row(row, value_input_option="RAW")
print(f"append_row result: {result}")
print(f"Spreadsheet ID: {sheet.spreadsheet.id}")
print(f"Worksheet title: {sheet.title}")
print("Google Sheets connection working.")
