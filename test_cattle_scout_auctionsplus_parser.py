import unittest

from bs4 import BeautifulSoup

from cattle_scout import scrape_commercial_listing, scrape_stud_listing


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

    def test_stud_female_listing_is_not_forced_to_bull(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND PRUE V47</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>Female Sale</div>
              <div>Brangus female donor dam. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/the-grafton-angus-brangus-bull-female-sale/promised-land-prue-v47/listing/128488-1384685/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_type"], "stud")
        self.assertEqual(listing["listing_category"], "breeding_female")
        self.assertEqual(listing["class"], "cow")
        self.assertEqual(listing["breed"], "Brangus")
        self.assertEqual(listing["horn_status"], "polled")

    def test_bull_in_bull_female_sale_is_not_classified_as_female_from_url(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND BRANGUS BULL V12</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>The Grafton Angus Brangus Bull Female Sale</div>
              <div>Registered Brangus bull with EBV data. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/the-grafton-angus-brangus-bull-female-sale/promised-land-bull-v12/listing/128488-1384686/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_type"], "stud")
        self.assertEqual(listing["listing_category"], "bull")
        self.assertEqual(listing["class"], "bull")
        self.assertEqual(listing["breed"], "Brangus")

    def test_explicit_male_field_beats_mixed_sale_female_heading(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND V12</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <ap-read-more field-id="Sex" text="Male"></ap-read-more>
            <ap-read-more field-id="Breed" text="Brangus"></ap-read-more>
            <section>
              <div>The Grafton Angus Brangus Bull Female Sale</div>
              <div>Dam: Promise Land Cow Family. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/the-grafton-angus-brangus-bull-female-sale/promised-land-v12/listing/128488-1384687/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "bull")
        self.assertEqual(listing["class"], "bull")
        self.assertEqual(listing["sex"], "bull")

    def test_explicit_breed_field_beats_mixed_sale_breed_heading(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND PRUE V48</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <ap-read-more field-id="Sex" text="Female"></ap-read-more>
            <ap-read-more field-id="Breed" text="Angus"></ap-read-more>
            <section>
              <div>The Grafton Angus Brangus Bull Female Sale</div>
              <div>Joined Angus female. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/the-grafton-angus-brangus-bull-female-sale/promised-land-prue-v48/listing/128488-1384688/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "breeding_female")
        self.assertEqual(listing["breed"], "Angus")

    def test_breed_fallback_ignores_mixed_sale_heading_without_explicit_field(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND ANGUS PRUE V49</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>The Grafton Angus Brangus Bull Female Sale</div>
              <div>Joined female. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/the-grafton-angus-brangus-bull-female-sale/promised-land-angus-prue-v49/listing/128488-1384689/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "breeding_female")
        self.assertEqual(listing["breed"], "Angus")

    def test_location_cowra_does_not_create_cow_category_without_animal_evidence(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND V50</div>
            <ap-read-more field-id="Location" text="COWRA, Central West NSW"></ap-read-more>
            <section>
              <div>Individual animal profile. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/promise-land-genetics/promised-land-v50/listing/128488-1384690/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "stud")
        self.assertEqual(listing["class"], "unknown")

    def test_line_level_male_evidence_beats_cow_family_fallback_text(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND V52</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>Male</div>
              <div>Out of an elite cow family. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/brangus-genetics/promised-land-v52/listing/128488-1384692/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "bull")
        self.assertEqual(listing["class"], "bull")

    def test_cow_family_pedigree_text_alone_does_not_create_cow_category(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND V53</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>Out of an elite cow-family. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/brangus-genetics/promised-land-v53/listing/128488-1384694/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "stud")
        self.assertEqual(listing["class"], "unknown")

    def test_explicit_cow_calf_class_becomes_cow_calf_unit(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND PRUE V51</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <ap-read-more field-id="Sex" text="Female"></ap-read-more>
            <ap-read-more field-id="Class" text="Cow & Calf"></ap-read-more>
            <ap-read-more field-id="Breed" text="Brangus"></ap-read-more>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/brangus-female-sale/promised-land-prue-v51/listing/128488-1384691/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "cow_calf_unit")
        self.assertEqual(listing["class"], "cow-and-calf")

    def test_plural_cows_calves_text_becomes_cow_calf_unit(self):
        html = """
        <html>
          <body>
            <div class="text-headline-sm font-medium">PROMISED LAND COWS AND CALVES</div>
            <ap-read-more field-id="Location" text="GRAFTON, Northern Rivers NSW"></ap-read-more>
            <section>
              <div>Cows & Calves. Brangus. Polled.</div>
            </section>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        listing = scrape_stud_listing(
            "https://auctionsplus.com.au/auctions/cattle/brangus-female-sale/promised-land-cows-calves/listing/128488-1384693/browse",
            soup,
            soup.get_text(separator="\n", strip=True),
        )

        self.assertEqual(listing["listing_category"], "cow_calf_unit")
        self.assertEqual(listing["class"], "cow-and-calf")


if __name__ == "__main__":
    unittest.main()
