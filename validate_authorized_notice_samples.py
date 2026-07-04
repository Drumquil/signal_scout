"""
validate_authorized_notice_samples.py
Drumquil Signal — authorised notice sample validator

Checks ingestion-ready JSON records in authorized_notice_samples/ and reports
whether they look safe for the authorised_notice_proto source.
"""

import json
from pathlib import Path


SAMPLES_DIR = Path("authorized_notice_samples")
REQUIRED_FIELDS = {
    "source",
    "source_type",
    "source_record_id",
    "permission_status",
    "url",
    "title",
    "sale_name",
    "listing_type",
    "listing_category",
}


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def validate_record(path):
    payload = load_json(path)
    missing = sorted(field for field in REQUIRED_FIELDS if not payload.get(field))
    warnings = []

    if payload.get("listing_type") not in {"commercial", "stud"}:
        warnings.append(f"unexpected listing_type={payload.get('listing_type')!r}")

    if payload.get("listing_category") not in {"commercial", "breeding_female", "cow_calf_unit", "bull"}:
        warnings.append(f"unexpected listing_category={payload.get('listing_category')!r}")

    if payload.get("state") in (None, "", "Unknown"):
        warnings.append("state missing or unknown")

    return missing, warnings


def main():
    if not SAMPLES_DIR.exists():
        print("Sample directory does not exist.")
        return

    sample_files = sorted(SAMPLES_DIR.glob("*.json"))
    if not sample_files:
        print("No normalised authorised notice samples found.")
        return

    failures = 0
    for path in sample_files:
        missing, warnings = validate_record(path)
        if missing:
            failures += 1
            print(f"FAIL {path.name}: missing {', '.join(missing)}")
            continue

        if warnings:
            print(f"WARN {path.name}: {'; '.join(warnings)}")
        else:
            print(f"OK   {path.name}")

    print(f"Validated sample files: {len(sample_files)}. Hard failures: {failures}.")


if __name__ == "__main__":
    main()
