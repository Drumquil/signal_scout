import os

import gspread
from dotenv import load_dotenv


DEFAULT_SPREADSHEET_NAME = "drumquil_scout"
CONFIG_TAB = "cattle_scout_config"
LOG_TAB = "cattle_scout_log"
LISTINGS_TAB = "cattle_scout_listings"
MODEL_TAB = "cattle_model_output"


def get_credentials_file():
    load_dotenv()
    creds_file = os.getenv("GOOGLE_SHEETS_CREDS_FILE")
    if not creds_file:
        raise RuntimeError("GOOGLE_SHEETS_CREDS_FILE is missing from the environment.")
    return creds_file


def get_client(creds_file=None):
    return gspread.service_account(filename=creds_file or get_credentials_file())


def open_spreadsheet(spreadsheet_name=DEFAULT_SPREADSHEET_NAME, creds_file=None, client=None):
    sheets_client = client or get_client(creds_file)
    return sheets_client.open(spreadsheet_name)


def open_worksheet(tab_name, spreadsheet_name=DEFAULT_SPREADSHEET_NAME, creds_file=None, client=None):
    return open_spreadsheet(spreadsheet_name, creds_file=creds_file, client=client).worksheet(tab_name)
