import json
import tempfile
import unittest
from pathlib import Path

import transform_authorized_notices as tan


class TransformAuthorizedNoticesTests(unittest.TestCase):
    def setUp(self):
        self._raw_dir = tan.RAW_DIR
        self._output_dir = tan.OUTPUT_DIR
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(self._tmpdir.name)
        tan.RAW_DIR = tmp_path / "raw"
        tan.OUTPUT_DIR = tmp_path / "out"
        tan.ensure_directories()

    def tearDown(self):
        tan.RAW_DIR = self._raw_dir
        tan.OUTPUT_DIR = self._output_dir
        self._tmpdir.cleanup()

    def write_batch(self, file_name, payload):
        path = tan.RAW_DIR / file_name
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
        return path

    def read_output(self):
        files = sorted(tan.OUTPUT_DIR.glob("*.json"))
        payloads = []
        for path in files:
            with open(path, "r", encoding="utf-8") as handle:
                payloads.append(json.load(handle))
        return files, payloads

    def test_ktn_atom_item_transforms_and_preserves_provenance(self):
        payload = {
            "source_name": "Nutrien Ag Solutions",
            "source_type": "email_notice",
            "permission_status": "authorised_feed_only",
            "sender_email": "newsletter@kill-the-newsletter.com",
            "received_at": "2026-06-27T08:30:00+10:00",
            "subject": "Nutrien livestock sales alert",
            "body_text": "Northern Rivers Store Sale summary.",
            "source_url": "https://example.com/sale",
            "catalogue_url": "https://example.com/catalogue.pdf",
            "feed_meta": {
                "feed_type": "ktn_atom_item",
                "feed_title": "Nutrien Sales Alerts",
                "entry_id": "tag:ktn:1",
                "entry_link": "https://example.com/sale",
                "published_at": "2026-06-27T08:25:00+10:00",
                "ktn_inbox_label": "nutrien-sales-alerts"
            },
            "records": [
                {
                    "external_id": "notice-1",
                    "title": "54 Station Mated Angus Cows",
                    "sale_name": "Northern Rivers Store Sale",
                    "sale_date": "2026-07-02",
                    "vendor": "Nutrien Ag Solutions",
                    "location": "Casino, NSW",
                    "state": "NSW",
                    "class": "station mated",
                    "listing_type": "commercial",
                    "listing_category": "breeding_female",
                    "num_head": 54,
                    "breed": "Angus",
                    "notes_raw": "WATCHING-grade notice"
                }
            ]
        }
        self.write_batch("ktn.json", payload)

        tan.main()
        files, outputs = self.read_output()

        self.assertEqual(len(files), 1)
        output = outputs[0]
        self.assertEqual(output["source_name"], "Nutrien Ag Solutions")
        self.assertEqual(output["message_id"], "tag:ktn:1")
        self.assertEqual(output["sender_email"], "newsletter@kill-the-newsletter.com")
        self.assertEqual(output["received_at"], "2026-06-27T08:30:00+10:00")
        self.assertEqual(output["url"], "https://example.com/sale")
        self.assertEqual(output["feed_meta"]["feed_title"], "Nutrien Sales Alerts")

    def test_multiple_records_produce_multiple_normalized_outputs(self):
        payload = {
            "source_name": "Elders",
            "source_type": "email_notice",
            "permission_status": "authorised_feed_only",
            "records": [
                {"external_id": "one", "title": "Casino Store Sale Notice"},
                {"external_id": "two", "title": "Lismore Prime Sale Notice"}
            ]
        }
        self.write_batch("multi.json", payload)

        tan.main()
        files, outputs = self.read_output()

        self.assertEqual(len(files), 2)
        self.assertEqual({item["source_record_id"] for item in outputs}, {"one", "two"})

    def test_missing_link_falls_back_to_feed_or_file_provenance(self):
        payload = {
            "source_name": "Elders",
            "source_type": "email_notice",
            "permission_status": "authorised_feed_only",
            "feed_meta": {
                "feed_type": "ktn_atom_item",
                "entry_id": "tag:ktn:2",
                "entry_link": "https://example.com/branch-update"
            },
            "records": [{"title": "Casino Store Sale Notice"}]
        }
        self.write_batch("feed-fallback.json", payload)

        tan.main()
        _, outputs = self.read_output()

        self.assertEqual(outputs[0]["url"], "https://example.com/branch-update")
        self.assertEqual(outputs[0]["message_id"], "tag:ktn:2")

    def test_file_fallback_keeps_sparse_notice_valid(self):
        payload = {
            "source_name": "Regional Agent",
            "source_type": "email_notice",
            "permission_status": "authorised_feed_only",
            "records": [
                {
                    "title": "Store Sale Notice",
                    "listing_type": "commercial",
                    "listing_category": "commercial"
                }
            ]
        }
        path = self.write_batch("file-fallback.json", payload)

        tan.main()
        _, outputs = self.read_output()

        self.assertTrue(outputs[0]["url"].startswith("file://"))
        self.assertEqual(outputs[0]["raw_file"], path.name)


if __name__ == "__main__":
    unittest.main()
