import unittest

from bs4 import BeautifulSoup

from cattle_scout import scrape_commercial_listing


COMMERCIAL_LISTING_HTML = """
<html>
  <head><title>48 Yearling Steers | AuctionsPlus</title></head>
  <body>
    <div class="text-headline-sm font-medium text-brand-dark">48 Yearling Steers</div>
    <ap-read-more field-id="Location" text="NARRANDERA, Riverina NSW"></ap-read-more>
    <a href="/auction-results/cattle/eastern-weaner-sale">Eastern Weaner Sale</a>
    <a href="/agentlistings/nutrien"><div>NUTRIEN AG SOLUTIONS NARRANDERA</div></a>
    <div>Lot 335</div>
    <div>Fri, 22 May 2026</div>
    <section>
      <div>At Est Kill/Del Date</div>
      <div>23/05/2026 (2 days)</div>
      <div>Live</div>
      <div>350.1 kgs based on -3% Del. Adj.</div>
      <div>297 kgs to 432 kgs Liveweight at delivery</div>
    </section>
    <section>
      <div>At Assessment</div>
      <div>19/05/2026</div>
      <div>Live</div>
      <div>361.0 kgs</div>
      <div>Live weight gain 0.7 kgs/day</div>
      <div>Hours off Feed</div>
      <div>5 hours</div>
      <div>166.0 kgs (Est. Av. Drs. 46%)</div>
      <div>Time Assessed</div>
      <div>1:00pm 19/05/2026</div>
    </section>
    <section>
      <div>Breeds</div>
      <div>Sire</div>
      <div>Dam</div>
      <div>48 Head</div>
      <div>Angus</div>
      <div>Angus</div>
      <div>48 Polled</div>
      <div>Store</div>
      <div>Fat Scores</div>
      <div>3</div>
      <div>Totals</div>
      <div>14 - 15 Months</div>
    </section>
    <section>
      <div>HGP Status</div>
      <div>The owner declares that the cattle have not been treated with HGP at any period of their lives</div>
      <div>100 % of cattle in this lot are Lifetime Traceable</div>
      <div>Yards</div>
      <div>Quiet: 48 head</div>
    </section>
    <section>
      <div>Accreditation(s)</div>
      <div>EU</div>
      <div>LPA</div>
      <div>Verification(s)</div>
      <div>Greenham NEVER EVER</div>
      <div>MSA</div>
      <div>Delivery</div>
    </section>
    <section>
      <div>$1,260 / Head</div>
      <div>Sale Types</div>
      <div>$/Head</div>
    </section>
  </body>
</html>
"""


class AuctionsPlusCommercialParserTests(unittest.TestCase):
    def test_scrape_commercial_listing_extracts_golden_fields(self):
        soup = BeautifulSoup(COMMERCIAL_LISTING_HTML, "html.parser")
        page_text = soup.get_text(separator="\n", strip=True)

        listing = scrape_commercial_listing(
            "https://auctionsplus.com.au/auctions/cattle/eastern-weaner-sale/48-yearling-steers/assessed/123",
            soup,
            page_text,
        )

        expected = {
            "listing_type": "commercial",
            "listing_category": "commercial",
            "title": "48 Yearling Steers",
            "sale_name": "Eastern Weaner Sale",
            "sale_date": "Fri, 22 May 2026",
            "lot_number": 335,
            "catalogue_pending": False,
            "vendor": "NUTRIEN AG SOLUTIONS NARRANDERA",
            "num_head": 48,
            "num_calves": None,
            "state": "NSW",
            "location": "NARRANDERA, Riverina NSW",
            "class": "yearling",
            "sex": "steer",
            "breed": "Angus",
            "breed_groups": [(48, "Angus", "Angus")],
            "horn_status": "polled",
            "store_condition": "store",
            "temperament": "quiet",
            "avg_weight_kg": 350.1,
            "weight_at_assessment_kg": 361.0,
            "weight_min": 297.0,
            "weight_max": 432.0,
            "weight_range_kg": 135.0,
            "delivery_adjustment_pct": -3.0,
            "liveweight_gain_per_day": 0.7,
            "dressing_pct": 46.0,
            "age_min_months": 14,
            "age_max_months": 15,
            "fat_score": 3,
            "assessment_date": "19/05/2026",
            "hours_off_feed": 5.0,
            "is_EU": True,
            "is_NE": True,
            "is_LPA": True,
            "is_MSA": True,
            "has_WHP": False,
            "HGP_free": True,
            "lifetime_traceable_pct": 100,
            "price_per_head": 1260.0,
            "price_c_kg": 359.9,
            "sale_type_pricing": "$/head",
        }

        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(listing[key], value)

    def test_single_age_fallback_is_anchored_to_age_section(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">10 Weaner Steers</div>
            <ap-read-more field-id="Location" text="ROMA, QLD"></ap-read-more>
            <div>Finance widget</div>
            <div>6 Months interest free</div>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_commercial_listing("https://example.test/assessed/1", soup, soup.get_text(separator="\n", strip=True))

        self.assertIsNone(listing["age_min_months"])
        self.assertIsNone(listing["age_max_months"])

    def test_single_age_fallback_reads_age_section(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">10 Weaner Steers</div>
            <ap-read-more field-id="Location" text="ROMA, QLD"></ap-read-more>
            <div>Age</div>
            <div>18 Months</div>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_commercial_listing("https://example.test/assessed/2", soup, soup.get_text(separator="\n", strip=True))

        self.assertEqual(listing["age_min_months"], 18)
        self.assertEqual(listing["age_max_months"], 18)

    def test_accreditation_tokens_do_not_match_inside_words(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">10 Weaner Steers</div>
            <ap-read-more field-id="Location" text="ROMA, QLD"></ap-read-more>
            <div>Accreditation(s)</div>
            <div>European cattle program</div>
            <div>Ben Nevis bloodline</div>
            <div>Delivery</div>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_commercial_listing("https://example.test/assessed/3", soup, soup.get_text(separator="\n", strip=True))

        self.assertFalse(listing["is_EU"])
        self.assertFalse(listing["is_NE"])

    def test_accreditation_scan_is_bounded_before_late_page_text(self):
        filler = "\n".join(f"<div>Line {i}</div>" for i in range(15))
        html = f"""
        <html>
          <body>
            <div class="text-headline-sm font-medium">10 Weaner Steers</div>
            <ap-read-more field-id="Location" text="ROMA, QLD"></ap-read-more>
            <div>Accreditation(s)</div>
            {filler}
            <div>EU</div>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_commercial_listing("https://example.test/assessed/4", soup, soup.get_text(separator="\n", strip=True))

        self.assertFalse(listing["is_EU"])


if __name__ == "__main__":
    unittest.main()
