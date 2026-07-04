# Signal Scout

Signal Scout is a Drumquil Signal beta product for monitoring Australian cattle sale listings, filtering lots against buyer criteria, and sending WhatsApp alerts for matching opportunities. The current build focuses on AuctionsPlus as the first source, with multi-user Google Sheets configuration, per-user deduplication, form-based onboarding, and a two-stage WATCHING/ALERT pipeline.

The repo now also contains an authorised-source intake lane for future opt-in email/PDF sources:
- raw mailbox exports or manually curated notice batches go in `authorized_notice_raw/`
- `transform_authorized_notices.py` converts them into ingestion-ready JSON
- `authorized_notice_samples/` feeds the opt-in `authorised_notice_proto` source in `cattle_scout.py`

Current project state, beta gates, schemas, and selector references live in `docs/`.
