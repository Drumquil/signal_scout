import unittest

from cattle_scout import load_config, listing_match
from transform_form_response import (
    REQUIRED_RESPONSE_HEADERS,
    build_response_row_dict,
    delete_user_rows,
    find_user_row_indices,
    transform_response,
    validate_transformed_config_rows,
)


class FakeWorksheet:
    def __init__(self, rows):
        self._rows = rows

    def get_all_values(self):
        return self._rows


class MutableFakeWorksheet(FakeWorksheet):
    def col_values(self, column):
        return [row[column - 1] if len(row) >= column else "" for row in self._rows]

    def delete_rows(self, row_number):
        del self._rows[row_number - 1]


def make_response_row(overrides=None, use_legacy_breeding_header=False):
    overrides = overrides or {}
    headers = list(REQUIRED_RESPONSE_HEADERS)
    if use_legacy_breeding_header:
        headers[headers.index("Female breeding stock")] = "Breeding females"

    defaults = {
        "Timestamp": "2026-06-20 09:00:00",
        "Email address": "beta@example.com",
        "Your name": "Beta Tester",
        "Your WhatsApp number": "0407139867",
        "Your property name (optional)": "Drumquil",
        "Which regions are you buying from?": "Any / no preference",
        "Your nearest town or delivery point": "Casino",
        "Sex preference": "",
        "Stage of production": "",
        "Female breeding stock": "",
        "Bulls": "",
        "Minimum number of head in a lot": "",
        "Maximum number of head in a lot": "",
        "Which breeds will you consider?": "Any / no preference",
        "Do you also want alerts for cross-bred cattle where your selected breed is the primary breed?": "Doesn't matter — alert me regardless",
        "Minimum average liveweight (kg)": "",
        "Maximum average liveweight (kg)": "",
        "Maximum weight spread within the mob (kg)": "",
        "Do you want to filter by age?": "No preference — show me all ages",
        "Minimum age (months)": "",
        "Maximum age (months)": "",
        "Minimum fat score": "No preference",
        "Maximum fat score": "No preference",
        "Require EU accreditation?": "No — doesn't matter",
        "Require Greenham Never Ever (NE) accreditation?": "No — doesn't matter",
        "Exclude listings with a chemical withholding period (WHP)?": "No — doesn't matter",
        "Require HGP-free declaration?": "No — doesn't matter",
        "Require polled (no horns)?": "No — doesn't matter",
        "Require quiet / docile temperament rating?": "No — doesn't matter",
        "Is there anything specific you're looking for that wasn't covered above?": "",
    }
    defaults.update(overrides)

    values = []
    for header in headers:
        canonical = "Female breeding stock" if header == "Breeding females" else header
        values.append(defaults.get(canonical, ""))
    return headers, values


def transform_to_runtime_config(overrides=None, use_legacy_breeding_header=False):
    headers, values = make_response_row(overrides, use_legacy_breeding_header)
    row_dict = build_response_row_dict(headers, values)
    config_rows = transform_response(row_dict)
    validate_transformed_config_rows(config_rows)
    worksheet_rows = [["user_id", "setting", "value"], *config_rows]
    return load_config(FakeWorksheet(worksheet_rows))[0]


def make_listing(overrides=None):
    listing = {
        "listing_type": "commercial",
        "listing_category": "commercial",
        "title": "Test Listing",
        "pre_auction_text": "",
        "state": "NSW",
        "class": "yearling",
        "sex": None,
        "num_head": 40,
        "sale_name": "Test Sale",
        "avg_weight_kg": None,
        "weight_range_kg": None,
        "breed": "Unknown",
        "fat_score": None,
        "age_min_months": None,
        "age_max_months": None,
        "is_EU": True,
        "is_NE": True,
        "has_WHP": False,
        "HGP_free": True,
        "horn_status": "polled",
        "temperament": "quiet",
        "lifetime_traceable_pct": None,
    }
    if overrides:
        listing.update(overrides)
    return listing


class TransformFormResponseContractTests(unittest.TestCase):
    def test_duplicate_user_rows_are_found_and_deleted_bottom_up(self):
        worksheet = MutableFakeWorksheet([
            ["user_id", "setting", "value"],
            ["beta_tester", "active", "TRUE"],
            ["other_user", "active", "TRUE"],
            ["beta_tester", "twilio_to", "whatsapp:+61400000000"],
        ])

        self.assertEqual(find_user_row_indices(worksheet, "beta_tester"), [2, 4])
        self.assertEqual(delete_user_rows(worksheet, "beta_tester"), 2)
        self.assertEqual(worksheet.get_all_values(), [
            ["user_id", "setting", "value"],
            ["other_user", "active", "TRUE"],
        ])

    def test_commercial_only_profile_writes_commercial_gate(self):
        config = transform_to_runtime_config(
            {
                "Sex preference": "Steers",
                "Stage of production": "Yearlings, Backgrounders, Stores & Feeders",
                "Minimum number of head in a lot": "20",
                "Maximum number of head in a lot": "120",
            }
        )

        self.assertTrue(config["include_commercial"])
        self.assertEqual(config["target_sex"], "steer")
        self.assertEqual(config["target_classes"], ["yearling", "backgrounder", "store", "feeder"])
        self.assertFalse(config["include_breeding_females"])
        self.assertFalse(config["include_cow_calf_units"])

    def test_breeding_heifer_only_profile_disables_commercial_and_matches_heifers(self):
        config = transform_to_runtime_config(
            {
                "Female breeding stock": "Joined / PTIC / NSM Heifers",
            }
        )

        self.assertFalse(config["include_commercial"])
        self.assertTrue(config["include_breeding_females"])
        self.assertEqual(config["breeding_female_classes"], ["heifer"])
        self.assertFalse(config["include_cow_calf_units"])

        heifer_listing = make_listing(
            {
                "listing_category": "breeding_female",
                "title": "Joined Angus Heifers",
                "class": "heifer",
                "sex": "heifer",
                "breed": "Angus",
            }
        )
        cow_listing = make_listing(
            {
                "listing_category": "breeding_female",
                "title": "PTIC Angus Cows",
                "class": "cow",
                "breed": "Angus",
            }
        )

        self.assertEqual(listing_match(heifer_listing, config), (True, "match"))
        self.assertEqual(listing_match(cow_listing, config), (False, "breeding_female type mismatch"))

    def test_breeding_cow_only_profile_uses_legacy_header_alias(self):
        config = transform_to_runtime_config(
            {
                "Female breeding stock": "Joined / PTIC / NSM Cows",
            },
            use_legacy_breeding_header=True,
        )

        self.assertFalse(config["include_commercial"])
        self.assertTrue(config["include_breeding_females"])
        self.assertEqual(config["breeding_female_classes"], ["cow"])
        self.assertFalse(config["include_cow_calf_units"])

    def test_caf_only_profile_stays_separate_from_breeding_female_classes(self):
        config = transform_to_runtime_config(
            {
                "Female breeding stock": "Cows with Calves at Foot (CAF)",
            }
        )

        self.assertFalse(config["include_commercial"])
        self.assertFalse(config["include_breeding_females"])
        self.assertEqual(config.get("breeding_female_classes", []), [])
        self.assertTrue(config["include_cow_calf_units"])


if __name__ == "__main__":
    unittest.main()
