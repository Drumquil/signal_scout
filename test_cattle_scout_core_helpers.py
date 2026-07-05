import unittest

from bs4 import BeautifulSoup

from cattle_scout import detect_listing_type, get_model_fair_value, score_listing


EMPTY_SOUP = BeautifulSoup("<html></html>", "html.parser")


class RowsWorksheet:
    def __init__(self, rows):
        self._rows = rows

    def get_all_values(self):
        return self._rows


class CoreHelperTests(unittest.TestCase):
    def test_detect_listing_type_uses_assessed_path_as_commercial(self):
        self.assertEqual(
            detect_listing_type(
                "https://auctionsplus.com.au/auctions/cattle/sale/48-steers/assessed/123",
                EMPTY_SOUP,
                "EBV data should not override assessed commercial path",
            ),
            "commercial",
        )

    def test_detect_listing_type_resolves_ambiguous_listing_paths(self):
        cases = [
            (
                "https://auctionsplus.com.au/auctions/cattle/sale/24-feeder-steers/listing/123",
                "24 Head",
                "commercial",
            ),
            (
                "https://auctionsplus.com.au/auctions/cattle/sale/lotus-bull/listing/456",
                "Expected Breeding Value table",
                "stud",
            ),
            (
                "https://auctionsplus.com.au/auctions/cattle/sale/lotus-bull/listing/456",
                "Individual animal profile",
                "stud",
            ),
            (
                "https://auctionsplus.com.au/auctions/cattle/pentire-angus-14th-annual-sale/benson/listing/128329-1370143/browse",
                "1 Head",
                "stud",
            ),
            (
                "https://auctionsplus.com.au/auctions/cattle/alc-brahmans-bull-sale/25-7977/listing/127584-1363429/browse",
                "1 Head",
                "stud",
            ),
            (
                "https://auctionsplus.com.au/auctions/cattle/sale/unknown-path/123",
                "No decisive fields",
                "commercial",
            ),
        ]

        for url, page_text, expected in cases:
            with self.subTest(url=url, expected=expected):
                self.assertEqual(detect_listing_type(url, EMPTY_SOUP, page_text), expected)

    def test_score_listing_classifies_price_against_fair_value(self):
        self.assertIsNone(score_listing({"price_c_kg": None}, 100.0))
        self.assertIsNone(score_listing({"price_c_kg": 100.0}, None))
        self.assertEqual(score_listing({"price_c_kg": 80.0}, 100.0), "🟢 UNDERVALUED")
        self.assertEqual(score_listing({"price_c_kg": 100.0}, 100.0), "🟡 FAIR")
        self.assertEqual(score_listing({"price_c_kg": 115.0}, 100.0), "🔴 OVERPRICED")

    def test_get_model_fair_value_uses_latest_plausible_dated_row(self):
        worksheet = RowsWorksheet([
            ["timestamp", "fair_value_c_kg"],
            ["2026-07-01", "360"],
            ["2026-07-02", "2026"],
            ["not a date", "410"],
            ["2026-07-03", "not numeric"],
            ["2026-07-04 09:00", "375.5"],
            ["", "999"],
        ])

        self.assertEqual(get_model_fair_value(worksheet), 375.5)

    def test_get_model_fair_value_returns_none_without_plausible_value(self):
        worksheet = RowsWorksheet([
            ["timestamp", "fair_value_c_kg"],
            ["not a date", "360"],
            ["2026-07-02", "99"],
            ["2026-07-03", "2500"],
            ["2026-07-04", "junk"],
        ])

        self.assertIsNone(get_model_fair_value(worksheet))


if __name__ == "__main__":
    unittest.main()
