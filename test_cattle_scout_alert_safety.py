import unittest
from unittest.mock import patch

import cattle_scout


WATCHING_LISTING = {
    "title": "12 Weaner Steers",
    "num_calves": None,
    "num_head": 12,
    "class": "weaner",
    "location": "Braidwood, NSW",
    "sale_date": "Monday, 6 July 2026",
    "vendor": "Example Agent",
    "url": "https://example.test/listing/1",
}


class FailingWorksheet:
    def get_all_values(self):
        raise RuntimeError("sheet unavailable")


class RowsWorksheet:
    def __init__(self, rows):
        self.rows = rows

    def get_all_values(self):
        return self.rows


class AlertSafetyTests(unittest.TestCase):
    def test_get_log_status_failure_aborts_run(self):
        with self.assertRaisesRegex(RuntimeError, "Could not read dedup log"):
            cattle_scout.get_log_status(FailingWorksheet())

    def test_test_mode_watching_send_counts_as_success_without_twilio(self):
        original_test_mode = cattle_scout.TEST_MODE
        cattle_scout.TEST_MODE = True
        try:
            with patch("cattle_scout.Client") as client:
                self.assertTrue(cattle_scout.send_watching_alert(WATCHING_LISTING, "whatsapp:+61400000000"))
                client.assert_not_called()
        finally:
            cattle_scout.TEST_MODE = original_test_mode

    def test_production_watching_send_failure_is_reported(self):
        original_test_mode = cattle_scout.TEST_MODE
        cattle_scout.TEST_MODE = False
        try:
            with patch("cattle_scout.Client", side_effect=RuntimeError("twilio unavailable")):
                self.assertFalse(cattle_scout.send_watching_alert(WATCHING_LISTING, "whatsapp:+61400000000"))
        finally:
            cattle_scout.TEST_MODE = original_test_mode

    def test_test_alerted_does_not_suppress_production_dedup(self):
        original_test_mode = cattle_scout.TEST_MODE
        try:
            cattle_scout.TEST_MODE = True
            self.assertTrue(cattle_scout.is_dedup_alerted("TEST_ALERTED"))

            cattle_scout.TEST_MODE = False
            self.assertFalse(cattle_scout.is_dedup_alerted("TEST_ALERTED"))
            self.assertTrue(cattle_scout.is_dedup_alerted("ALERTED"))
        finally:
            cattle_scout.TEST_MODE = original_test_mode

    def test_invalid_numeric_config_skips_user(self):
        worksheet = RowsWorksheet([
            ["user_id", "setting", "value"],
            ["beta_tester", "active", "TRUE"],
            ["beta_tester", "twilio_to", "whatsapp:+61400000000"],
            ["beta_tester", "min_weight_kg", "300kg"],
        ])

        self.assertEqual(cattle_scout.load_config(worksheet), [])

    def test_comma_numeric_config_is_accepted(self):
        worksheet = RowsWorksheet([
            ["user_id", "setting", "value"],
            ["beta_tester", "active", "TRUE"],
            ["beta_tester", "twilio_to", "whatsapp:+61400000000"],
            ["beta_tester", "max_price_per_head", "1,200"],
        ])

        users = cattle_scout.load_config(worksheet)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["max_price_per_head"], 1200.0)

    def test_twilio_delivery_mode_is_required_for_live_sends(self):
        original_test_mode = cattle_scout.TEST_MODE
        original_mode = cattle_scout.TWILIO_WHATSAPP_MODE
        try:
            cattle_scout.TEST_MODE = True
            cattle_scout.TWILIO_WHATSAPP_MODE = ""
            cattle_scout.validate_twilio_delivery_mode()

            cattle_scout.TEST_MODE = False
            with self.assertRaisesRegex(RuntimeError, "TWILIO_WHATSAPP_MODE"):
                cattle_scout.validate_twilio_delivery_mode()

            for mode in ("sandbox", "registered"):
                cattle_scout.TWILIO_WHATSAPP_MODE = mode
                cattle_scout.validate_twilio_delivery_mode()
        finally:
            cattle_scout.TEST_MODE = original_test_mode
            cattle_scout.TWILIO_WHATSAPP_MODE = original_mode

    def test_log_listing_row_keeps_unknown_head_blank(self):
        listing = {
            "url": "https://example.test/listing/2",
            "title": "Unknown head listing",
            "listing_category": "commercial",
            "class": "feeder",
            "breed": "Angus",
            "num_head": None,
            "num_calves": None,
            "avg_weight_kg": None,
            "weight_range_kg": None,
            "fat_score": None,
            "age_min_months": None,
            "age_max_months": None,
            "is_EU": False,
            "is_NE": False,
            "has_WHP": False,
            "price_c_kg": None,
            "location": "Roma, QLD",
            "vendor": "Example Agent",
            "sale_date": "Monday, 6 July 2026",
        }

        row = cattle_scout.build_log_listing_row(listing, "TEST_WATCHING", "beta_tester")

        self.assertEqual(row[7], "")
        self.assertTrue(row[18].endswith(" UTC"))


if __name__ == "__main__":
    unittest.main()
