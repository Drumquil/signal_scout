"""
inspect_multi_user_validation.py

Inspect Google Sheets log/listings rows for the dummy multi-user validation
users and report duplicate / overlap characteristics.
"""

from collections import Counter, defaultdict
from sheets_client import open_spreadsheet

SPREADSHEET_NAME = "drumquil_scout"
LOG_TAB = "cattle_scout_log"
LISTINGS_TAB = "cattle_scout_listings"
TARGET_USERS = {"dummy_multi_a", "dummy_multi_b", "dummy_batch_a", "dummy_batch_b", "tom_steers"}


def connect_sheet():
    return open_spreadsheet(SPREADSHEET_NAME)


def summarize_tab(rows, tab_name):
    if not rows:
        print(f"{tab_name}: empty")
        return

    header = rows[0]
    body = rows[1:]
    filtered = [row for row in body if len(row) >= 2 and row[0].strip() in TARGET_USERS]

    print(f"\n{tab_name}")
    print(f"  matching rows: {len(filtered)}")

    per_user = Counter(row[0].strip() for row in filtered)
    for user_id in sorted(per_user):
        print(f"  {user_id}: {per_user[user_id]}")

    url_pairs = [(row[0].strip(), row[1].strip()) for row in filtered if len(row) >= 2]
    pair_counts = Counter(url_pairs)
    dup_pairs = [pair for pair, count in pair_counts.items() if count > 1]
    print(f"  duplicate (user_id, url) pairs: {len(dup_pairs)}")
    if dup_pairs:
        dup_by_user = Counter(user_id for user_id, _ in dup_pairs)
        for user_id in sorted(dup_by_user):
            print(f"    duplicate pairs for {user_id}: {dup_by_user[user_id]}")

    urls_by_user = defaultdict(set)
    for row in filtered:
        if len(row) >= 2:
            urls_by_user[row[0].strip()].add(row[1].strip())

    pairs = [
        ("dummy_multi_a", "dummy_multi_b"),
        ("dummy_batch_a", "dummy_batch_b"),
    ]
    for left, right in pairs:
        if left in urls_by_user and right in urls_by_user:
            overlap = urls_by_user[left] & urls_by_user[right]
            print(f"  overlap {left} vs {right}: {len(overlap)} urls")
            sample = sorted(overlap)[:5]
            for url in sample:
                print(f"    {url}")

    print(f"  headers: {header[:4]} ...")


def main():
    spreadsheet = connect_sheet()
    log_rows = spreadsheet.worksheet(LOG_TAB).get_all_values()
    listings_rows = spreadsheet.worksheet(LISTINGS_TAB).get_all_values()

    summarize_tab(log_rows, LOG_TAB)
    summarize_tab(listings_rows, LISTINGS_TAB)


if __name__ == "__main__":
    main()
