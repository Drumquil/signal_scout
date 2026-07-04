# Authorised Notice Normalised Samples

This folder holds ingestion-ready JSON records for the opt-in
`authorised_notice_proto` source in `cattle_scout.py`.

Do not commit real operational samples. This folder is ignored by default
except for this README.

## How files get here

1. Put raw exported email / PDF notice metadata in `authorized_notice_raw/`.
2. Run `transform_authorized_notices.py`.
3. The transformer writes one normalised JSON file per `records[]` entry here.
4. Optionally run `validate_authorized_notice_samples.py`.
5. Enable the source with:
   - `ENABLE_AUTHORIZED_NOTICE_SOURCE=TRUE`
   - optionally set `AUTHORIZED_NOTICE_SOURCE_DIR=authorized_notice_samples`

## Runtime expectation

Each file must contain one JSON object representing one normalised listing-like
record. The runtime reads every `.json` file in this folder when the authorised
source is enabled.

## Example fixture

`ktn_atom_item_normalized_example.json` shows the expected post-transform shape
for one Kill the Newsletter Atom-item-derived notice.
