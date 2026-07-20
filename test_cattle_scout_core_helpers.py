import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

import cattle_scout
from cattle_scout import (
    cache_key_for_item,
    detect_listing_type,
    filter_target_users,
    get_cached_listing,
    get_model_fair_value,
    infer_location_town,
    location_within_target_radius,
    parse_float_runtime_value,
    parse_int_runtime_value,
    prune_listing_cache,
    score_listing,
    set_cached_listing,
)


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

    def test_listing_cache_helpers_store_and_expire_payloads(self):
        cache = {}
        key = cache_key_for_item("auctionsplus", "https://example.test/listing")
        set_cached_listing(cache, key, {"title": "Cached Lot"})

        self.assertEqual(get_cached_listing(cache, key, now=cache[key]["fetched_at"] + 1), {"title": "Cached Lot"})
        self.assertIsNone(get_cached_listing(cache, key, now=cache[key]["fetched_at"] + 999999))
        self.assertTrue(key.startswith(cattle_scout.LISTING_CACHE_SCHEMA_VERSION + ":"))

    def test_listing_cache_uses_shorter_ttl_for_pending_catalogues(self):
        cache = {}
        key = cache_key_for_item("auctionsplus", "https://example.test/pending")
        original_pending_ttl = cattle_scout.LISTING_CACHE_PENDING_TTL_SECONDS
        cattle_scout.LISTING_CACHE_PENDING_TTL_SECONDS = 10
        try:
            set_cached_listing(cache, key, {"title": "Pending Lot", "catalogue_pending": True})
        finally:
            cattle_scout.LISTING_CACHE_PENDING_TTL_SECONDS = original_pending_ttl

        self.assertEqual(cache[key]["ttl_seconds"], 10)
        self.assertIsNone(get_cached_listing(cache, key, now=cache[key]["fetched_at"] + 11))

    def test_listing_cache_caps_stored_ttl_to_current_runtime_ttl(self):
        cache = {}
        key = cache_key_for_item("auctionsplus", "https://example.test/stale")
        original_ttl = cattle_scout.LISTING_CACHE_TTL_SECONDS
        try:
            cattle_scout.LISTING_CACHE_TTL_SECONDS = 100
            cache[key] = {
                "fetched_at": 1000.0,
                "ttl_seconds": 200,
                "payload": {"title": "Stale under current config"},
            }

            self.assertIsNone(get_cached_listing(cache, key, now=1100.0))
        finally:
            cattle_scout.LISTING_CACHE_TTL_SECONDS = original_ttl

    def test_prune_listing_cache_removes_expired_and_wrong_schema_entries(self):
        now = 1000.0
        valid_key = cache_key_for_item("auctionsplus", "https://example.test/valid")
        wrong_schema_key = "old-schema:auctionsplus:https://example.test/old"
        cache = {
            valid_key: {"fetched_at": now, "ttl_seconds": 100, "payload": {"title": "Valid"}},
            wrong_schema_key: {"fetched_at": now, "ttl_seconds": 100, "payload": {"title": "Old"}},
            cache_key_for_item("auctionsplus", "https://example.test/expired"): {
                "fetched_at": now - 200,
                "ttl_seconds": 100,
                "payload": {"title": "Expired"},
            },
        }

        self.assertEqual(list(prune_listing_cache(cache, now=now)), [valid_key])

    def test_runtime_value_parsers_clamp_out_of_range_values(self):
        self.assertEqual(parse_int_runtime_value("100", 1, min_value=1, max_value=8), 8)
        self.assertEqual(parse_int_runtime_value("-5", 1, min_value=1, max_value=8), 1)
        self.assertEqual(parse_int_runtime_value("not-int", 3, min_value=1, max_value=8), 3)
        self.assertEqual(parse_float_runtime_value("-1", 1.0, min_value=0.1, max_value=30.0), 0.1)

    def test_filter_target_users_selects_or_fails_explicit_targets(self):
        users = [{"user_id": "alpha"}, {"user_id": "beta"}]

        self.assertEqual(filter_target_users(users, ""), users)
        self.assertEqual(filter_target_users(users, "beta"), [{"user_id": "beta"}])
        with self.assertRaisesRegex(RuntimeError, "did not match"):
            filter_target_users(users, "missing")

    def test_location_radius_helpers_match_known_towns(self):
        self.assertEqual(infer_location_town("GRAFTON, Northern Rivers NSW"), "grafton")
        self.assertEqual(infer_location_town("Near Casino NSW"), "casino")

        config = {"target_location_town": "Lismore", "target_radius_km": 130}
        self.assertEqual(
            location_within_target_radius({"location": "GRAFTON, Northern Rivers NSW"}, config),
            (True, None),
        )

        within_radius, reason = location_within_target_radius({"location": "COWRA, Central West NSW"}, config)
        self.assertFalse(within_radius)
        self.assertIn("radius=130", reason)

        self.assertEqual(
            location_within_target_radius({"location": "Location unknown"}, config),
            (True, "listing location has no known town coordinate"),
        )

    def test_collect_source_listings_uses_opt_in_cache(self):
        scrape_calls = []
        now = 1000.0
        cached_key = cache_key_for_item("cached_source", "https://example.test/1")
        cache = {
            cached_key: {
                "fetched_at": now,
                "ttl_seconds": cattle_scout.LISTING_CACHE_TTL_SECONDS,
                "payload": {"url": "https://example.test/1", "title": "Cached"},
            }
        }

        def scrape_item(item, session=None):
            scrape_calls.append(item)
            return {"url": item, "title": "Fetched"}

        source_def = {
            "name": "cached_source",
            "source_type": "test",
            "discover_items": lambda session=None: ["https://example.test/1", "https://example.test/2"],
            "scrape_item": scrape_item,
            "session_factory": None,
            "cache_items": True,
        }

        original_delay = cattle_scout.REQUEST_DELAY
        original_workers = cattle_scout.SCRAPE_WORKERS
        cattle_scout.REQUEST_DELAY = 0
        cattle_scout.SCRAPE_WORKERS = 1
        try:
            with patch("cattle_scout.time.time", return_value=now), \
                 patch("cattle_scout.load_listing_cache", return_value=cache), \
                 patch("cattle_scout.save_listing_cache") as save_cache:
                listings = cattle_scout.collect_source_listings([source_def])
        finally:
            cattle_scout.REQUEST_DELAY = original_delay
            cattle_scout.SCRAPE_WORKERS = original_workers

        self.assertEqual(scrape_calls, ["https://example.test/2"])
        self.assertEqual([listing["title"] for listing in listings], ["Cached", "Fetched"])
        save_cache.assert_called_once()

    def test_collect_source_listings_does_not_cache_unmarked_sources(self):
        scrape_calls = []
        uncached_key = cache_key_for_item("uncached_source", "https://example.test/1")
        cache = {
            uncached_key: {
                "fetched_at": 1000.0,
                "ttl_seconds": cattle_scout.LISTING_CACHE_TTL_SECONDS,
                "payload": {"url": "https://example.test/1", "title": "Cached"},
            }
        }

        def scrape_item(item, session=None):
            scrape_calls.append(item)
            return {"url": item, "title": "Fresh"}

        source_def = {
            "name": "uncached_source",
            "source_type": "test",
            "discover_items": lambda session=None: ["https://example.test/1"],
            "scrape_item": scrape_item,
            "session_factory": None,
        }

        with patch("cattle_scout.load_listing_cache", return_value=cache), \
             patch("cattle_scout.save_listing_cache") as save_cache:
            listings = cattle_scout.collect_source_listings([source_def])

        self.assertEqual(scrape_calls, ["https://example.test/1"])
        self.assertEqual(listings[0]["title"], "Fresh")
        save_cache.assert_not_called()


if __name__ == "__main__":
    unittest.main()
