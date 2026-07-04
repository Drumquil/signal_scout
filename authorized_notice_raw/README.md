# Authorised Notice Raw Intake

Place manually exported or manually curated authorised sale-alert inputs here.

Keep real mailbox content out of git. This folder is ignored by default except
for this README.

## Supported raw file format

Use one `.json` file per source email / notice batch.

```json
{
  "message_id": "nutrien-2026-06-14-001",
  "source_name": "Nutrien Ag Solutions",
  "source_type": "email_notice",
  "permission_status": "authorised_feed_only",
  "sender_email": "alerts@example.com",
  "received_at": "2026-06-14T08:30:00+10:00",
  "subject": "Upcoming livestock sales alert",
  "body_text": "Optional plain text body",
  "source_url": "https://example.com/source-notice",
  "catalogue_url": "https://example.com/catalogue.pdf",
  "feed_meta": {
    "feed_type": "manual_export_or_atom",
    "feed_title": "Optional feed title or inbox label",
    "entry_id": "Optional source feed entry id",
    "entry_link": "https://example.com/source-notice",
    "published_at": "2026-06-14T08:25:00+10:00",
    "ktn_inbox_label": "Optional Kill the Newsletter inbox label"
  },
  "attachments": [
    {
      "file_name": "catalogue.pdf",
      "path": "catalogues/catalogue.pdf"
    }
  ],
  "records": [
    {
      "external_id": "lot-001",
      "title": "54 Station Mated Cows",
      "sale_name": "Northern Rivers Store Sale",
      "sale_date": "2026-06-20",
      "vendor": "Example Agency",
      "location": "Casino, NSW",
      "state": "NSW",
      "class": "station mated",
      "listing_category": "breeding_female",
      "num_head": 54,
      "breed": "Angus",
      "notes_raw": "Optional extracted notes"
    }
  ]
}
```

## Notes

- `records` is required and may contain multiple opportunities from one email.
- Keep `body_text` and `notes_raw` factual and minimal.
- `feed_meta` is optional raw-only provenance for Atom or feed-derived notices.
- Use `catalogue_url` and `attachments` when the sale advice references a PDF.
- PDFs themselves can live alongside the raw JSON or in a subfolder below this
  directory; the transformer only records metadata, it does not parse PDFs yet.
- Use `ktn_atom_item_template.json` as the smallest checked-in Kill the
  Newsletter example.
