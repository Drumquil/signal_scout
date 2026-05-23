"""
inspect_fields.py
Drumquil Signal — Field Structure Inspector

Fetches a single AuctionsPlus assessed listing and dumps:
  1. All field-id attributes found in the raw HTML
  2. Raw HTML context around breed, fat score, and weight fields
  3. Page size (to detect JS-shell vs full static HTML)
  4. Whether expandable section content is in the static HTML at all

Run this against a LIVE assessed listing URL — paste a current URL from
the AuctionsPlus browse page into the URL variable below.

Author: Tom Flanagan
"""

import requests
from bs4 import BeautifulSoup
import re

# ── PASTE A LIVE ASSESSED LISTING URL HERE ──────────────────────────────────
URL = "https://auctionsplus.com.au/auctions/cattle/weaner-yearling-sale/32-feeder-steers/assessed/127843-317641/browse"
# ────────────────────────────────────────────────────────────────────────────

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def main():
    print(f"Fetching: {URL}")
    response = requests.get(URL, headers=HEADERS, timeout=15)
    print(f"Status: {response.status_code}  |  Page size: {len(response.text):,} bytes")

    if response.status_code != 200:
        print("ERROR: Non-200 response. Check the URL is a live listing.")
        return

    if len(response.text) < 5000:
        print("WARNING: Page is very small — likely a JS shell. "
              "Field data may not be in static HTML.")

    soup = BeautifulSoup(response.text, "html.parser")
    raw  = response.text

    # ── 1. All field-id attributes ───────────────────────────────────────────
    section("ALL field-id ATTRIBUTES IN PAGE")
    fields = soup.find_all(attrs={"field-id": True})
    if fields:
        for f in fields:
            print(f"  field-id={f.get('field-id')!r:25s}  "
                  f"tag={f.name:20s}  "
                  f"text-attr={f.get('text','')[:60]!r}  "
                  f"inner={f.get_text(strip=True)[:60]!r}")
    else:
        print("  NONE FOUND — field-id attributes not present in static HTML")

    # ── 2. Breed field — raw HTML context ────────────────────────────────────
    section("RAW HTML AROUND BREED-RELATED CONTENT (first 8 matches)")
    breed_terms = re.compile(
        r'angus|hereford|breed|sire|dam', re.IGNORECASE
    )
    matches = list(breed_terms.finditer(raw))
    for m in matches[:8]:
        ctx = raw[max(0, m.start()-200):m.end()+200]
        print(f"\n  --- match: {m.group()!r} at pos {m.start()} ---")
        print(repr(ctx))

    # ── 3. Fat score — raw HTML context ──────────────────────────────────────
    section("RAW HTML AROUND FAT SCORE CONTENT (first 5 matches)")
    fat_terms = re.compile(r'fat.{0,8}score|fat_score|fatScore', re.IGNORECASE)
    for m in list(fat_terms.finditer(raw))[:5]:
        ctx = raw[max(0, m.start()-200):m.end()+200]
        print(f"\n  --- match: {m.group()!r} at pos {m.start()} ---")
        print(repr(ctx))

    # ── 4. Weight range — raw HTML context ───────────────────────────────────
    section("RAW HTML AROUND WEIGHT RANGE CONTENT (first 5 matches)")
    wt_terms = re.compile(r'low.{0,5}high|weight.{0,10}range|min.{0,5}max', re.IGNORECASE)
    for m in list(wt_terms.finditer(raw))[:5]:
        ctx = raw[max(0, m.start()-200):m.end()+200]
        print(f"\n  --- match: {m.group()!r} at pos {m.start()} ---")
        print(repr(ctx))

    # ── 5. Expandable/accordion component markers ─────────────────────────────
    section("EXPANDABLE COMPONENT MARKERS (accordion, collapse, expand, v-show)")
    expand_terms = re.compile(
        r'accordion|collapse|v-show|v-if|x-show|:open|expandable', re.IGNORECASE
    )
    expand_matches = list(expand_terms.finditer(raw))
    print(f"  Found {len(expand_matches)} expandable markers in raw HTML")
    for m in expand_matches[:5]:
        ctx = raw[max(0, m.start()-100):m.end()+100]
        print(f"\n  --- {m.group()!r} at pos {m.start()} ---")
        print(repr(ctx))

    # ── 6. Vue / JS component tags that may contain field data ───────────────
    section("VUE / WEB COMPONENT TAGS (ap-, vue, custom elements)")
    vue_tags = soup.find_all(re.compile(r'^ap-|^vue-', re.IGNORECASE))
    if vue_tags:
        for tag in vue_tags[:20]:
            print(f"  <{tag.name}  attrs={dict(tag.attrs)}  "
                  f"inner={tag.get_text(strip=True)[:80]!r}>")
    else:
        print("  No ap- or vue- prefixed elements found")

    # ── 7. Any element with 'breed' in its attributes or class ───────────────
    section("ELEMENTS WITH 'breed' IN ATTRS OR CLASS")
    breed_els = soup.find_all(lambda t: any(
        'breed' in str(v).lower() for v in t.attrs.values()
    ))
    if breed_els:
        for el in breed_els[:10]:
            print(f"  tag={el.name}  attrs={el.attrs}  "
                  f"inner={el.get_text(strip=True)[:80]!r}")
    else:
        print("  None found")

    # ── 8. Rendered text — first 100 meaningful lines ────────────────────────
    section("RENDERED PAGE TEXT (first 100 non-empty lines)")
    lines = [l.strip() for l in soup.get_text(separator="\n").split("\n") if l.strip()]
    for i, line in enumerate(lines[:400], 1):
        print(f"  {i:3d}  {line}")

    print(f"\n{'='*70}")
    print("Inspection complete.")


if __name__ == "__main__":
    main()