"""
transform_authorized_notices.py
Drumquil Signal — authorised notice intake normaliser

Converts manually exported authorised email / PDF notice metadata from
authorized_notice_raw/ into ingestion-ready JSON records in
authorized_notice_samples/.

The raw format is intentionally simple so Tom can export or curate source
material without needing direct mailbox integration first.
"""

import json
import re
from pathlib import Path


RAW_DIR = Path("authorized_notice_raw")
OUTPUT_DIR = Path("authorized_notice_samples")

REQUIRED_BATCH_FIELDS = {"source_name", "source_type", "permission_status", "records"}
REQUIRED_RECORD_FIELDS = {"title"}


def slugify(value):
    text = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return text or "record"


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def ensure_directories():
    RAW_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)


def validate_batch(payload, path):
    missing = sorted(field for field in REQUIRED_BATCH_FIELDS if field not in payload)
    if missing:
        raise ValueError(f"{path.name}: missing batch field(s): {', '.join(missing)}")
    if not isinstance(payload["records"], list) or not payload["records"]:
        raise ValueError(f"{path.name}: records must be a non-empty list")


def build_normalized_record(batch, record, batch_path, record_index):
    missing = sorted(field for field in REQUIRED_RECORD_FIELDS if not record.get(field))
    if missing:
        raise ValueError(
            f"{batch_path.name} record {record_index}: missing record field(s): {', '.join(missing)}"
        )

    feed_meta = batch.get("feed_meta") if isinstance(batch.get("feed_meta"), dict) else None
    source_url = (
        record.get("source_url")
        or record.get("entry_link")
        or batch.get("source_url")
        or (feed_meta or {}).get("entry_link")
        or batch.get("catalogue_url")
        or f"file://{batch_path.resolve().as_posix()}"
    )
    catalogue_url = record.get("catalogue_url") or batch.get("catalogue_url") or source_url
    message_id = batch.get("message_id") or (feed_meta or {}).get("entry_id") or batch_path.stem
    external_id = record.get("external_id") or f"{message_id}-{record_index:02d}"
    listing_category = record.get("listing_category") or "commercial"
    listing_type = record.get("listing_type") or "commercial"
    title = record["title"].strip()
    notes_parts = [part for part in [record.get("notes_raw"), batch.get("body_text")] if part]

    normalized = {
        "source_name": batch["source_name"],
        "source": slugify(batch["source_name"]),
        "source_type": batch["source_type"],
        "source_record_id": external_id,
        "permission_status": batch["permission_status"],
        "source_confidence": record.get("source_confidence", batch.get("source_confidence")),
        "sender_email": batch.get("sender_email"),
        "received_at": batch.get("received_at"),
        "message_id": message_id,
        "attachment_name": None,
        "catalogue_url": catalogue_url,
        "url": source_url,
        "feed_meta": feed_meta,
        "title": title,
        "sale_name": record.get("sale_name") or batch.get("subject") or title,
        "sale_date": record.get("sale_date") or "",
        "listing_type": listing_type,
        "listing_category": listing_category,
        "catalogue_pending": bool(record.get("catalogue_pending", False)),
        "vendor": record.get("vendor") or record.get("agent_name") or batch.get("source_name"),
        "pre_auction_text": record.get("pre_auction_text") or "",
        "num_head": record.get("num_head"),
        "num_calves": record.get("num_calves"),
        "state": record.get("state") or "Unknown",
        "location": record.get("location") or "Location unknown",
        "class": record.get("class") or record.get("stock_type") or "",
        "sex": record.get("sex"),
        "breed": record.get("breed") or "Unknown",
        "breed_groups": record.get("breed_groups") or [],
        "horn_status": record.get("horn_status"),
        "store_condition": record.get("store_condition"),
        "temperament": record.get("temperament"),
        "avg_weight_kg": record.get("avg_weight_kg"),
        "weight_at_assessment_kg": record.get("weight_at_assessment_kg"),
        "weight_min": record.get("weight_min"),
        "weight_max": record.get("weight_max"),
        "weight_range_kg": record.get("weight_range_kg"),
        "delivery_adjustment_pct": record.get("delivery_adjustment_pct"),
        "liveweight_gain_per_day": record.get("liveweight_gain_per_day"),
        "dressing_pct": record.get("dressing_pct"),
        "fat_score": record.get("fat_score"),
        "age_min_months": record.get("age_min_months"),
        "age_max_months": record.get("age_max_months"),
        "hours_off_feed": record.get("hours_off_feed"),
        "assessment_date": record.get("assessment_date"),
        "is_EU": record.get("is_EU", False),
        "is_NE": record.get("is_NE", False),
        "is_LPA": record.get("is_LPA", False),
        "is_MSA": record.get("is_MSA", False),
        "has_WHP": record.get("has_WHP", False),
        "HGP_free": record.get("HGP_free"),
        "lifetime_traceable_pct": record.get("lifetime_traceable_pct"),
        "price_per_head": record.get("price_per_head"),
        "price_c_kg": record.get("price_c_kg"),
        "sale_type_pricing": record.get("sale_type_pricing"),
        "notes_raw": "\n\n".join(notes_parts) if notes_parts else None,
        "input_type": batch["source_type"],
        "raw_file": batch_path.name,
    }

    attachments = batch.get("attachments") or []
    if attachments:
        first_attachment = attachments[0]
        if isinstance(first_attachment, dict):
            normalized["attachment_name"] = first_attachment.get("file_name")

    return normalized


def write_record(normalized):
    sale_date = normalized.get("sale_date") or "undated"
    file_name = (
        f"{slugify(normalized['source'])}"
        f"__{sale_date}"
        f"__{slugify(normalized['title'])}"
        f"__{slugify(normalized['source_record_id'])}.json"
    )
    output_path = OUTPUT_DIR / file_name
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(normalized, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    return output_path


def main():
    ensure_directories()

    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        print("No raw authorised notice files found.")
        return

    written = 0
    for raw_file in raw_files:
        payload = load_json(raw_file)
        validate_batch(payload, raw_file)

        for index, record in enumerate(payload["records"], start=1):
            normalized = build_normalized_record(payload, record, raw_file, index)
            output_path = write_record(normalized)
            print(f"Wrote normalised notice: {output_path}")
            written += 1

    print(f"Normalised records written: {written}")


if __name__ == "__main__":
    main()
