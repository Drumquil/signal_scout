"""
smoke_sheets.py
Live smoke check — verifies the Google Sheets service account credentials work
and writes to the cattle_scout_log tab.

This script has live side effects and is intentionally not named test_*.py.
"""

from sheets_client import open_worksheet


sheet = open_worksheet("cattle_scout_log", spreadsheet_name="drumquil_scout")

# Write a test row
result = sheet.append_row(["TEST", "Connection successful", "May 2026"])
print(f"append_row result: {result}")
print(f"Spreadsheet ID: {sheet.spreadsheet.id}")
print(f"Worksheet title: {sheet.title}")
print("Google Sheets connection working.")
