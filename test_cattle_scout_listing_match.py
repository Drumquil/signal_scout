import unittest

from cattle_scout import listing_match


def make_config(overrides=None):
    config = {
        "active": True,
        "include_commercial": True,
        "include_breeding_females": False,
        "include_cow_calf_units": False,
        "include_bulls": False,
        "target_states": ["NSW"],
        "target_classes": ["yearling"],
        "target_sex": "steer",
        "min_head": 20,
        "max_head": 100,
        "sale_types": ["weaner"],
        "min_weight_kg": 250,
        "max_weight_kg": 450,
        "max_weight_range_kg": 80,
        "target_breeds": ["angus"],
        "min_fat_score": 2,
        "fat_score_max": 4,
        "age_min_months": 8,
        "age_max_months": 20,
        "require_EU": True,
        "require_NE": True,
        "exclude_WHP": True,
        "require_HGP_free": True,
        "require_polled": True,
        "require_quiet": True,
    }
    if overrides:
        config.update(overrides)
    return config


def make_listing(overrides=None):
    listing = {
        "listing_type": "commercial",
        "listing_category": "commercial",
        "title": "48 Yearling Steers",
        "pre_auction_text": "",
        "state": "NSW",
        "class": "yearling",
        "sex": "steer",
        "num_head": 48,
        "sale_name": "Eastern Weaner Sale",
        "avg_weight_kg": 330.0,
        "weight_range_kg": 60.0,
        "breed": "Angus",
        "fat_score": 3,
        "age_min_months": 12,
        "age_max_months": 14,
        "is_EU": True,
        "is_NE": True,
        "has_WHP": False,
        "HGP_free": True,
        "horn_status": "polled",
        "temperament": "quiet",
        "lifetime_traceable_pct": 100,
    }
    if overrides:
        listing.update(overrides)
    return listing


class CommercialListingMatchTests(unittest.TestCase):
    def test_commercial_profile_matches_base_listing(self):
        self.assertEqual(listing_match(make_listing(), make_config()), (True, "match"))

    def test_commercial_profile_rejects_hard_gates(self):
        cases = [
            ({"state": "VIC"}, {}, "state=VIC not in ['NSW']"),
            ({"class": "feeder"}, {}, "class='feeder' not in target_classes"),
            ({"sex": "heifer"}, {}, "sex='heifer' != target_sex='steer'"),
            ({"num_head": 10}, {}, "head=10 < min_head=20"),
            ({"num_head": 140}, {}, "head=140 > max_head=100"),
            ({"sale_name": "Prime Cattle Sale"}, {}, "sale_name='Prime Cattle Sale' not in sale_types"),
        ]

        for listing_overrides, config_overrides, reason in cases:
            with self.subTest(reason=reason):
                self.assertEqual(
                    listing_match(make_listing(listing_overrides), make_config(config_overrides)),
                    (False, reason),
                )

    def test_commercial_profile_rejects_known_location_outside_radius(self):
        config = make_config({
            "target_states": ["NSW"],
            "target_location_town": "Lismore",
            "target_radius_km": 130,
        })

        matched, reason = listing_match(make_listing({"location": "COWRA, Central West NSW"}), config)

        self.assertFalse(matched)
        self.assertIn("location='cowra'", reason)
        self.assertIn("radius=130", reason)

    def test_commercial_profile_allows_known_location_inside_radius(self):
        config = make_config({
            "target_states": ["NSW"],
            "target_location_town": "Lismore",
            "target_radius_km": 130,
        })

        self.assertEqual(
            listing_match(make_listing({"location": "GRAFTON, Northern Rivers NSW"}), config),
            (True, "match"),
        )

    def test_commercial_profile_rejects_soft_gates_when_known(self):
        cases = [
            ({"avg_weight_kg": 240.0}, "weight=240.0kg < min=250kg"),
            ({"avg_weight_kg": 470.0}, "weight=470.0kg > max=450kg"),
            ({"weight_range_kg": 95.0}, "weight_range=95.0kg > max=80kg"),
            ({"breed": "Hereford"}, "breed='Hereford' not in target_breeds"),
            ({"fat_score": 5}, "fat_score=5 > max=4"),
            ({"fat_score": 1}, "fat_score=1 < min=2"),
            ({"age_max_months": 7}, "age_max=7mo < min=8mo"),
            ({"age_min_months": 24}, "age_min=24mo > max=20mo"),
        ]

        for listing_overrides, reason in cases:
            with self.subTest(reason=reason):
                self.assertEqual(listing_match(make_listing(listing_overrides), make_config()), (False, reason))

    def test_commercial_profile_allows_unknown_soft_gate_fields(self):
        unknown_listing = make_listing({
            "state": "Unknown",
            "class": "unknown",
            "sex": None,
            "sale_name": "Unknown Sale",
            "avg_weight_kg": None,
            "weight_range_kg": None,
            "breed": "Unknown",
            "fat_score": None,
            "age_min_months": None,
            "age_max_months": None,
        })

        self.assertEqual(listing_match(unknown_listing, make_config()), (True, "match"))

    def test_commercial_profile_rejects_accreditation_and_trait_gates(self):
        cases = [
            ({"is_EU": False}, "require_EU not met"),
            ({"is_NE": False}, "require_NE not met"),
            ({"has_WHP": True}, "has_WHP excluded"),
            ({"HGP_free": False}, "require_HGP_free not met"),
            ({"horn_status": "horned"}, "require_polled not met (horn_status=horned)"),
            ({"temperament": "stirry"}, "require_quiet not met (temperament=stirry)"),
            ({"lifetime_traceable_pct": 70}, "lifetime_traceable=70% < min=80%"),
        ]

        for listing_overrides, reason in cases:
            with self.subTest(reason=reason):
                config = make_config({"min_lifetime_traceable_pct": 80})
                self.assertEqual(listing_match(make_listing(listing_overrides), config), (False, reason))

    def test_breeding_female_profile_matches_stud_female_listing(self):
        config = make_config({
            "include_commercial": False,
            "include_breeding_females": True,
            "breeding_female_classes": ["cow"],
            "target_classes": [],
            "target_sex": "",
            "sale_types": [],
            "target_breeds": ["brangus", "brangus cross"],
            "min_head": 1,
            "max_head": 30,
            "age_min_months": 36,
            "age_max_months": 72,
            "require_EU": False,
            "require_NE": False,
            "exclude_WHP": False,
            "require_HGP_free": False,
            "require_polled": True,
            "require_quiet": False,
        })
        listing = make_listing({
            "listing_type": "stud",
            "listing_category": "breeding_female",
            "title": "PROMISED LAND PRUE V47 Brangus Cow",
            "class": "cow",
            "sex": None,
            "num_head": 1,
            "sale_name": "The Grafton Angus Brangus Bull Female Sale",
            "breed": "Brangus",
            "age_min_months": None,
            "age_max_months": None,
            "horn_status": "polled",
        })

        self.assertEqual(listing_match(listing, config), (True, "match"))

    def test_breeding_female_profile_rejects_wrong_known_breed(self):
        config = make_config({
            "include_commercial": False,
            "include_breeding_females": True,
            "breeding_female_classes": ["cow"],
            "target_classes": [],
            "target_sex": "",
            "sale_types": [],
            "target_breeds": ["brangus"],
            "require_EU": False,
            "require_NE": False,
            "exclude_WHP": False,
            "require_HGP_free": False,
            "require_polled": False,
            "require_quiet": False,
        })
        listing = make_listing({
            "listing_category": "breeding_female",
            "title": "12 PTIC Angus Cows",
            "class": "cow",
            "breed": "Angus",
        })

        self.assertEqual(
            listing_match(listing, config),
            (False, "breed='Angus' not in target_breeds"),
        )

    def test_breeding_female_profile_rejects_known_wrong_female_type(self):
        config = make_config({
            "include_commercial": False,
            "include_breeding_females": True,
            "breeding_female_classes": ["cow"],
            "target_classes": [],
            "target_sex": "",
            "sale_types": [],
            "target_breeds": ["brangus"],
            "require_EU": False,
            "require_NE": False,
            "exclude_WHP": False,
            "require_HGP_free": False,
            "require_polled": False,
            "require_quiet": False,
        })
        listing = make_listing({
            "listing_type": "stud",
            "listing_category": "breeding_female",
            "title": "PROMISED LAND V49",
            "class": "heifer",
            "sex": "heifer",
            "num_head": 1,
            "breed": "Brangus",
        })

        self.assertEqual(listing_match(listing, config), (False, "breeding_female type mismatch"))

    def test_commercial_target_sex_does_not_reject_breeding_female_category(self):
        config = make_config({
            "include_commercial": True,
            "include_breeding_females": True,
            "breeding_female_classes": ["cow"],
            "target_classes": ["yearling"],
            "target_sex": "heifer",
            "sale_types": [],
            "target_breeds": ["brangus"],
            "min_head": 1,
            "max_head": 30,
            "require_EU": False,
            "require_NE": False,
            "exclude_WHP": False,
            "require_HGP_free": False,
            "require_polled": False,
            "require_quiet": False,
        })
        listing = make_listing({
            "listing_type": "stud",
            "listing_category": "breeding_female",
            "title": "PROMISED LAND PRUE V47",
            "class": "cow",
            "sex": "cow",
            "num_head": 1,
            "breed": "Brangus",
        })

        self.assertEqual(listing_match(listing, config), (True, "match"))

    def test_cow_calf_unit_matches_caf_only_profile(self):
        config = make_config({
            "include_commercial": False,
            "include_breeding_females": False,
            "include_cow_calf_units": True,
            "target_classes": [],
            "target_sex": "",
            "sale_types": [],
            "target_breeds": ["brangus"],
            "min_head": 1,
            "max_head": 30,
            "require_EU": False,
            "require_NE": False,
            "exclude_WHP": False,
            "require_HGP_free": False,
            "require_polled": False,
            "require_quiet": False,
        })
        listing = make_listing({
            "listing_type": "stud",
            "listing_category": "cow_calf_unit",
            "title": "PROMISED LAND PRUE V51",
            "class": "cow-and-calf",
            "sex": "cow",
            "num_head": 1,
            "breed": "Brangus",
        })

        self.assertEqual(listing_match(listing, config), (True, "match"))


if __name__ == "__main__":
    unittest.main()
