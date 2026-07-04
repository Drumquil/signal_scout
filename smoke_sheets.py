"""
smoke_sheets.py
Live smoke check — verifies the Google Sheets service account credentials work
and writes to the cattle_scout_log tab.

This script has live side effects and is intentionally not named test_*.py.
"""

import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Load credentials from .env in the same folder
load_dotenv()

GOOGLE_SHEETS_CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE")

if not GOOGLE_SHEETS_CREDS_FILE:
    raise RuntimeError("GOOGLE_SHEETS_CREDS_FILE not found in .env file.")

# Define the permissions scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from the JSON key file (path comes from .env)
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDS_FILE, scope)

# Authenticate and open the sheet
client = gspread.authorize(creds)
sheet = client.open("drumquil_scout").worksheet("cattle_scout_log")

# Write a test row
result = sheet.append_row(["TEST", "Connection successful", "May 2026"])
print(f"append_row result: {result}")
print(f"Spreadsheet ID: {sheet.spreadsheet.id}")
print(f"Worksheet title: {sheet.title}")
print("✅ Google Sheets connection working.")
