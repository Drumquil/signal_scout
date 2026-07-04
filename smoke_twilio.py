"""
smoke_twilio.py
Live smoke check — verifies the Twilio WhatsApp credentials work and that a
test message lands on the configured number.

This script has live side effects and is intentionally not named test_*.py.
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load credentials from .env in the same folder
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM        = os.getenv("TWILIO_FROM")
TWILIO_TO          = os.getenv("TWILIO_TO")

# Fail fast if any are missing
required = {
    "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
    "TWILIO_AUTH_TOKEN":  TWILIO_AUTH_TOKEN,
    "TWILIO_FROM":        TWILIO_FROM,
    "TWILIO_TO":          TWILIO_TO,
}
missing = [k for k, v in required.items() if not v]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

message = client.messages.create(
    body="Cattle Scout test — Twilio is working.",
    from_=TWILIO_FROM,
    to=TWILIO_TO
)

print(f"Message sent. SID: {message.sid}")
