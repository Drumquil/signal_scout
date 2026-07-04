import unittest

from cattle_scout import detect_class


class DetectClassTests(unittest.TestCase):
    def test_detect_class_uses_word_boundaries(self):
        cases = [
            ("45 Weaner Steers Braidwood", "", ("weaner", "commercial")),
            ("40 Highland Calves", "", ("calf", "commercial")),
            ("12 Sandy Yearling Steers", "", ("yearling", "commercial")),
        ]

        for title, pre_auction_text, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(detect_class(title, pre_auction_text), expected)

    def test_detect_class_preserves_breeding_qualifiers(self):
        cases = [
            ("12 PTIC Angus Heifers", "", ("ptic", "breeding_female")),
            ("20 AI'd Angus Heifers", "", ("ai'd", "breeding_female")),
            ("30 Station Mated Cows", "", ("station mated", "breeding_female")),
            ("8 CAF Cows", "", ("caf", "breeding_female")),
        ]

        for title, pre_auction_text, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(detect_class(title, pre_auction_text), expected)

    def test_detect_class_handles_compound_cow_calf_titles(self):
        cases = [
            ("21 NSM Heifers & 21 Calves", "", ("cow-and-calf", "cow_calf_unit")),
            ("21 NSM Heifers and 21 Calves", "", ("cow-and-calf", "cow_calf_unit")),
            ("21 NSM Heifers Highland Calves", "", ("nsm", "breeding_female")),
        ]

        for title, pre_auction_text, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(detect_class(title, pre_auction_text), expected)

    def test_detect_class_preserves_plural_commercial_classes(self):
        cases = [
            ("40 Feeder Steers", "", ("feeder", "commercial")),
            ("12 Bulls", "", ("bull", "bull")),
            ("36 Commercial Cows", "", ("cow", "commercial")),
        ]

        for title, pre_auction_text, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(detect_class(title, pre_auction_text), expected)


if __name__ == "__main__":
    unittest.main()
