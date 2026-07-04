import unittest

from source_parser_spikes import (
    extract_money_cents,
    parse_rma_html,
    parse_stockplace_detail_html,
    parse_stockplace_html,
)


STOCKPLACE_HTML = """
<html>
  <body>
    <article class="listing-card">
      <h3><a href="/stock/livestock-for-sale/listing/800-crossbred-flatback-heifers-280-kg-21912">800 crossbred flatback heifers. 280 kg</a></h3>
      <div class="location">Richmond, QLD</div>
      <p>No. of Head: 800</p>
      <p>Breed: Composite</p>
      <p>Stock Type: Heifers</p>
      <p>Av. Weight (kg): 280</p>
      <p>Price Type: Per Kg</p>
      <p>$3.90 per kg</p>
      <p>Good quality feeder or breeding heifers</p>
    </article>
    <article class="listing-card">
      <h3><a href="/stock/livestock-order-wanted-to-buy/listing/100-steers-12345">100 steers wanted</a></h3>
      <div class="location">Roma, QLD</div>
      <p>Order filled</p>
    </article>
    <article class="listing-card">
      <h3><a href="/stock/livestock-for-sale/listing/quality-vendor-bred-young-cows-and-calves-8th-may-2026-55555">Quality vendor bred young cows and calves - Auctions Plus 8th May 2026</a></h3>
      <p>Strong cows and calves line with no direct listing fields.</p>
    </article>
    <article class="listing-card">
      <h3><a href="/stock/livestock-for-sale/listing/4-decks-of-brahman-and-crossbred-yearling-steers-88888">4 decks of Brahman and Crossbred yearling steers with all the hard work done.</a></h3>
      <div class="location">Cloncurry, QLD</div>
      <p>Breed: Brahman Cross</p>
      <p>Stock Type: Yearling Steers</p>
    </article>
  </body>
</html>
"""

STOCKPLACE_DETAIL_HTML = """
<html>
  <body>
    <h1>96 Droughtmaster Backgrounder Steers</h1>
    <div class="location">Cloncurry, QLD</div>
    <p>No. of Head: 96</p>
    <p>Breed: Droughtmaster</p>
    <p>Stock Type: Backgrounder Steers</p>
    <p>Av. Weight (kg): 312</p>
    <p>Price Type: Per Kg</p>
    <p>$3.45 per kg</p>
    <p>Well-grown backgrounder line ready to move on.</p>
  </body>
</html>
"""

RMA_HTML = """
<html>
  <body>
    <h2>Feature</h2>
    <div class="section">
      <article class="sale-card">
        <h3><a href="/sales/cattle/26919">Binnaway Store Sale</a></h3>
        <p>Binnaway, NSW 2395</p>
        <p>Friday, 29th May 2026 09:00am</p>
        <p>David Grant Livestock Agency 02 6842 7963</p>
      </article>
    </div>
    <h2>Auction</h2>
    <div class="section">
      <article class="sale-card">
        <h3><a href="/sales/cattle/26920">32 Feeder Steers</a></h3>
        <p>Tylden, VIC 3444</p>
        <p>Friday, 29th May 2026 09:00am</p>
        <p>Michael White 0407501212</p>
      </article>
    </div>
    <h2>Wanted</h2>
    <div class="section">
      <article class="sale-card">
        <h3><a href="/sales/cattle/26921">Wanted Cattle</a></h3>
      </article>
    </div>
  </body>
</html>
"""


class SourceParserSpikeTests(unittest.TestCase):
    def test_extract_money_cents_infers_ambiguous_units_by_magnitude(self):
        self.assertEqual(extract_money_cents("$4.50"), (4.5, None))
        self.assertEqual(extract_money_cents("$450"), (None, 450.0))
        self.assertEqual(extract_money_cents("$3.90 per kg"), (390.0, None))
        self.assertEqual(extract_money_cents("$1,200 per head"), (None, 1200.0))

    def test_parse_stockplace_html_filters_wanted_and_extracts_listing_fields(self):
        records, summary = parse_stockplace_html(STOCKPLACE_HTML, "https://www.stockplace.com.au/stock", scraped_at="2026-06-27T00:00:00+00:00")

        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(records[0]["source_name"], "Stockplace Marketing")
        self.assertEqual(records[0]["source_record_id"], "21912")
        self.assertEqual(records[0]["num_head"], 800)
        self.assertEqual(records[0]["breed"], "Composite")
        self.assertEqual(records[0]["class"], "heifer")
        self.assertEqual(records[0]["sex"], "heifer")
        self.assertEqual(records[0]["avg_weight_kg"], 280.0)
        self.assertEqual(records[0]["price_c_kg"], 390.0)
        self.assertEqual(records[0]["state"], "QLD")
        self.assertEqual(records[1]["source_record_id"], "88888")
        self.assertIsNone(records[1]["num_head"])
        self.assertEqual(records[1]["class"], "yearling")
        self.assertEqual(records[1]["state"], "QLD")

    def test_parse_stockplace_html_filters_prose_noise_and_auction_plus_reference_cards(self):
        records, _summary = parse_stockplace_html(STOCKPLACE_HTML, "https://www.stockplace.com.au/stock", scraped_at="2026-06-27T00:00:00+00:00")

        record_ids = {record["source_record_id"] for record in records}
        self.assertNotIn("55555", record_ids)
        self.assertNotIn("12345", record_ids)

    def test_parse_stockplace_detail_html_extracts_clean_detail_fields(self):
        record = parse_stockplace_detail_html(
            STOCKPLACE_DETAIL_HTML,
            "https://www.stockplace.com.au/stock/livestock-for-sale/listing/96-droughtmaster-backgrounder-steers-99999",
            scraped_at="2026-06-27T00:00:00+00:00",
        )

        self.assertEqual(record["listing_title"], "96 Droughtmaster Backgrounder Steers")
        self.assertEqual(record["num_head"], 96)
        self.assertEqual(record["breed"], "Droughtmaster")
        self.assertEqual(record["class"], "backgrounder")
        self.assertEqual(record["sex"], "steer")
        self.assertEqual(record["avg_weight_kg"], 312.0)
        self.assertEqual(record["price_c_kg"], 345.0)
        self.assertEqual(record["state"], "QLD")

    def test_parse_rma_html_preserves_sections_and_skips_wanted(self):
        records, summary = parse_rma_html(RMA_HTML, "https://www.rma.com.au/sales/cattle", scraped_at="2026-06-27T00:00:00+00:00")

        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(records[0]["source_name"], "RMA Network")
        self.assertEqual(records[0]["source_record_id"], "26919")
        self.assertEqual(records[0]["listing_mode"], "feature")
        self.assertEqual(records[0]["state"], "NSW")
        self.assertEqual(records[1]["source_record_id"], "26920")
        self.assertEqual(records[1]["num_head"], 32)
        self.assertEqual(records[1]["class"], "feeder")
        self.assertEqual(records[1]["sex"], "steer")
        self.assertEqual(records[1]["state"], "VIC")


if __name__ == "__main__":
    unittest.main()
