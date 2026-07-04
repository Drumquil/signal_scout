"""
source_parser_spikes.py
Drumquil Signal - standalone parser spikes for candidate non-AuctionsPlus sources

These parsers are intentionally separate from the live Signal Scout runtime.
They fetch or read public source pages, emit normalised JSON records to stdout,
and never write to Google Sheets or send alerts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

SOURCE_CONFIG = {
    "stockplace": {
        "sample_url": "https://www.stockplace.com.au/stock",
        "parser": "parse_stockplace_html",
    },
    "rma": {
        "sample_url": "https://www.rma.com.au/sales/cattle",
        "parser": "parse_rma_html",
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_whitespace(value: str | None) -> str | None:
    if value is None:
        return None
    return re.sub(r"\s+", " ", value).strip()


def clean_text(node) -> str:
    if node is None:
        return ""
    return normalize_whitespace(node.get_text(" ", strip=True)) or ""


def extract_labelled_fields(node) -> dict[str, str]:
    labelled = {}
    for row in node.find_all(string=re.compile(":")):
        raw = normalize_whitespace(str(row))
        if not raw or ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        labelled[key.strip().lower()] = value.strip()
    return labelled


def extract_money_cents(value: str | None) -> tuple[float | None, float | None]:
    text = normalize_whitespace(value)
    if not text:
        return None, None
    match = re.search(r"\$?\s*([\d,]+(?:\.\d+)?)", text)
    if not match:
        return None, None
    amount = float(match.group(1).replace(",", ""))
    if "per kg" in text.lower() or "c/kg" in text.lower():
        if "$" in text:
            return round(amount * 100, 2), None
        return amount, None
    if "per head" in text.lower() or "/head" in text.lower():
        return None, amount
    if amount < 100:
        return amount, None
    return None, amount


def derive_state(location: str | None) -> str | None:
    if not location:
        return None
    match = re.search(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", location.upper())
    return match.group(1) if match else None


def derive_head_count(title: str | None, field_value: str | None = None) -> int | None:
    if field_value:
        match = re.search(r"\b(\d{1,5})\b", field_value)
        if match:
            return int(match.group(1))

    if not title:
        return None

    title_text = normalize_whitespace(title) or ""
    if re.match(r"^\d{1,3}\s*(?:deck|decks)\b", title_text, re.IGNORECASE):
        return None
    if re.match(r"^\d{1,3}\s*deck\s+line\b", title_text, re.IGNORECASE):
        return None

    leading_match = re.match(
        r"^(\d{1,4})\b(?=.*\b(steers?|heifers?|cows?|bulls?|calves?|weaners?|yearlings?)\b)",
        title_text,
        re.IGNORECASE,
    )
    if leading_match:
        return int(leading_match.group(1))

    x_of_x_match = re.match(
        r"^(\d{1,3})\s*x\s*(\d{1,3})\b(?=.*\b(cows?|calves?)\b)",
        title_text,
        re.IGNORECASE,
    )
    if x_of_x_match:
        return int(x_of_x_match.group(1))

    return None


def derive_sex_and_class(title: str | None, stock_type: str | None = None) -> tuple[str | None, str | None]:
    text = " ".join(filter(None, [title, stock_type])).lower()

    sex = None
    for token, value in [
        ("steer", "steer"),
        ("heifer", "heifer"),
        ("cow", "cow"),
        ("bull", "bull"),
        ("mixed", "mixed"),
    ]:
        if token in text:
            sex = value
            break

    listing_class = ""
    for token, value in [
        ("station mated", "station mated"),
        ("feeder", "feeder"),
        ("backgrounder", "backgrounder"),
        ("weaner", "weaner"),
        ("yearling", "yearling"),
        ("store", "store"),
        ("prime", "prime"),
        ("breeder", "breeder"),
        ("cow", "cow"),
        ("heifer", "heifer"),
        ("steer", "steer"),
        ("bull", "bull"),
    ]:
        if token in text:
            listing_class = value
            break

    return sex, listing_class


def parse_date_text(value: str | None) -> str:
    text = normalize_whitespace(value) or ""
    if not text:
        return ""
    # Preserve source text for now rather than overfitting parser assumptions.
    return text


def is_stockplace_listing_href(href: str | None) -> bool:
    if not href:
        return False
    href_lower = href.lower()
    return "/stock/" in href_lower and "/listing/" in href_lower


def is_cattle_text(text: str | None) -> bool:
    text_lower = (text or "").lower()
    return any(
        token in text_lower
        for token in [
            "steer",
            "heifer",
            "cow",
            "bull",
            "calf",
            "cattle",
            "weaner",
            "yearling",
            "backgrounder",
            "feeder",
            "station mated",
            "ptic",
            "joined",
        ]
    )


def is_meaningful_title(title: str | None) -> bool:
    text = normalize_whitespace(title) or ""
    if not text or text.lower() == "unknown":
        return False
    if len(text) < 8:
        return False
    return is_cattle_text(text)


def looks_like_location_line(text: str | None) -> bool:
    line = normalize_whitespace(text) or ""
    if not line:
        return False
    if re.search(r"\b(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b", line.upper()):
        return True
    return bool(re.search(r"^[A-Z][A-Za-z .'-]+,\s*[A-Z][A-Za-z .'-]+$", line))


def derive_location(card, title: str | None) -> str | None:
    location_node = card.find(attrs={"class": re.compile("location", re.I)})
    if location_node:
        location = clean_text(location_node)
        if location:
            return location

    title_text = normalize_whitespace(title) or ""
    for line in card.stripped_strings:
        normalized_line = normalize_whitespace(line)
        if not normalized_line or normalized_line == title_text:
            continue
        if ":" in normalized_line:
            continue
        if looks_like_location_line(normalized_line):
            return normalized_line

    return None


def extract_detail_title(soup: BeautifulSoup) -> str | None:
    for selector in ["h1", "h2", "h3"]:
        heading = soup.find(selector)
        title = clean_text(heading)
        if is_meaningful_title(title):
            return title
    for link in soup.find_all("a", href=re.compile(r"/stock/")):
        title = clean_text(link)
        if is_meaningful_title(title):
            return title
    return None


def extract_detail_notes(soup: BeautifulSoup, title: str | None) -> str | None:
    title_text = normalize_whitespace(title) or ""
    note_candidates = []
    for para in soup.find_all(["p", "div"]):
        text = clean_text(para)
        if not text or text == title_text:
            continue
        if ":" in text and len(text) < 60:
            continue
        note_candidates.append(text)
    if not note_candidates:
        return None
    return note_candidates[0]


def parse_stockplace_detail_html(html: str, source_url: str, scraped_at: str | None = None) -> dict | None:
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = scraped_at or now_iso()
    labelled = extract_labelled_fields(soup)
    title = extract_detail_title(soup)
    breed = labelled.get("breed")
    stock_type = labelled.get("stock type")
    sex, listing_class = derive_sex_and_class(title, stock_type)
    location = derive_location(soup, title)

    avg_weight = None
    if labelled.get("av. weight (kg)"):
        weight_match = re.search(r"(\d+(?:\.\d+)?)", labelled["av. weight (kg)"])
        if weight_match:
            avg_weight = float(weight_match.group(1))

    price_type = labelled.get("price type")
    price_c_kg = None
    price_per_head = None
    if price_type:
        price_hint = None
        for line in soup.stripped_strings:
            normalized_line = normalize_whitespace(line)
            if normalized_line and "$" in normalized_line:
                price_hint = normalized_line
                break
        price_c_kg, price_per_head = extract_money_cents(price_hint)

    notes_raw = extract_detail_notes(soup, title)

    return {
        "source_name": "Stockplace Marketing",
        "source_type": "agent_direct_listing",
        "source_url": source_url,
        "scraped_at": scraped_at,
        "listing_title": title,
        "listing_status": None,
        "listing_mode": "for_sale",
        "listing_category": "commercial",
        "sale_name": title,
        "sale_type": "for_sale",
        "sale_date": "",
        "sale_time": "",
        "venue": None,
        "location": location,
        "state": derive_state(location),
        "num_head": derive_head_count(title, labelled.get("no. of head")),
        "class": listing_class,
        "sex": sex,
        "breed": breed,
        "breed_groups": [],
        "avg_weight_kg": avg_weight,
        "weight_min": None,
        "weight_max": None,
        "weight_range_kg": None,
        "asking_price": None,
        "price_type": price_type,
        "price_c_kg": price_c_kg,
        "price_per_head": price_per_head,
        "agent_name": "Stockplace Marketing",
        "agent_branch": None,
        "contact_name": None,
        "contact_phone": None,
        "contact_email": None,
        "catalogue_url": None,
        "online_bidding_url": None,
        "notes_raw": notes_raw,
        "class_breakdown_raw": None,
    }


def merge_stockplace_record(base_record: dict, detail_record: dict | None) -> dict:
    if not detail_record:
        return base_record
    merged = dict(base_record)
    for key, value in detail_record.items():
        if value in (None, "", [], {}):
            continue
        merged[key] = value
    return merged


def build_stockplace_record(card, source_url: str, scraped_at: str) -> dict | None:
    text = clean_text(card)
    if not text:
        return None

    title_link = card.find("a", href=re.compile(r"/stock/"))
    title = clean_text(title_link) if title_link else clean_text(card.find(["h2", "h3", "h4"]))
    href = title_link.get("href") if title_link else None
    detail_url = urljoin(source_url, href) if href else source_url

    if not is_stockplace_listing_href(href):
        return None

    record_id = None
    if href:
        match = re.search(r"-(\d+)(?:/)?$", href)
        if match:
            record_id = match.group(1)

    status = None
    for candidate, normalized in [
        ("s o l d", "sold"),
        ("sold", "sold"),
        ("under offer", "under_offer"),
        ("order filled", "order_filled"),
        ("order filling", "order_filling"),
        ("available", "available"),
    ]:
        if candidate in text.lower():
            status = normalized
            break

    listing_mode = "for_sale"
    if "wanted" in text.lower() or "order" in text.lower():
        listing_mode = "wanted"
    elif "auctionsplus" in text.lower():
        listing_mode = "auction_plus_reference"

    labelled = extract_labelled_fields(card)

    num_head = derive_head_count(title, labelled.get("no. of head"))
    breed = labelled.get("breed")
    stock_type = labelled.get("stock type")
    sex, listing_class = derive_sex_and_class(title, stock_type)

    avg_weight = None
    if labelled.get("av. weight (kg)"):
        weight_match = re.search(r"(\d+(?:\.\d+)?)", labelled["av. weight (kg)"])
        if weight_match:
            avg_weight = float(weight_match.group(1))

    price_c_kg = None
    price_per_head = None
    price_type = labelled.get("price type")
    if price_type:
        price_hint = None
        for line in card.stripped_strings:
            normalized_line = normalize_whitespace(line)
            if normalized_line and "$" in normalized_line:
                price_hint = normalized_line
                break
        price_c_kg, price_per_head = extract_money_cents(price_hint)

    location = derive_location(card, title)

    notes_raw = clean_text(card.find("p")) or None

    structured_signal_count = sum(
        1
        for value in [
            labelled.get("no. of head"),
            breed,
            stock_type,
            labelled.get("av. weight (kg)"),
            price_type,
            location,
        ]
        if value
    )

    if listing_mode in {"wanted", "auction_plus_reference"}:
        return None
    if not is_meaningful_title(title):
        return None
    if not is_cattle_text(" ".join(filter(None, [title, stock_type, breed, notes_raw]))):
        return None
    if structured_signal_count < 2:
        return None

    return {
        "source_name": "Stockplace Marketing",
        "source_type": "agent_direct_listing",
        "source_url": detail_url,
        "source_record_id": record_id,
        "scraped_at": scraped_at,
        "permission_status": "permission_first",
        "terms_risk_level": "AMBER",
        "listing_title": title or None,
        "listing_status": status or "unknown",
        "listing_mode": listing_mode,
        "listing_category": "commercial",
        "sale_name": title or None,
        "sale_type": "for_sale",
        "sale_date": "",
        "sale_time": "",
        "venue": None,
        "location": location,
        "state": derive_state(location),
        "num_head": num_head,
        "class": listing_class,
        "sex": sex,
        "breed": breed,
        "breed_groups": [],
        "avg_weight_kg": avg_weight,
        "weight_min": None,
        "weight_max": None,
        "weight_range_kg": None,
        "asking_price": None,
        "price_type": price_type,
        "price_c_kg": price_c_kg,
        "price_per_head": price_per_head,
        "agent_name": "Stockplace Marketing",
        "agent_branch": None,
        "contact_name": None,
        "contact_phone": None,
        "contact_email": None,
        "catalogue_url": None,
        "online_bidding_url": None,
        "notes_raw": notes_raw,
        "class_breakdown_raw": None,
    }


def parse_stockplace_html(
    html: str,
    source_url: str,
    scraped_at: str | None = None,
    detail_fetcher=None,
) -> tuple[list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = scraped_at or now_iso()
    records = []
    skipped = 0

    cards = soup.find_all(["article", "div", "li"])
    for card in cards:
        link = card.find("a", href=re.compile(r"/stock/"))
        if not link:
            continue
        record = build_stockplace_record(card, source_url, scraped_at)
        if not record:
            skipped += 1
            continue
        if detail_fetcher and record.get("source_url"):
            try:
                detail_html = detail_fetcher(record["source_url"])
            except Exception:
                detail_html = None
            if detail_html:
                detail_record = parse_stockplace_detail_html(detail_html, record["source_url"], scraped_at=scraped_at)
                record = merge_stockplace_record(record, detail_record)
        if record["listing_mode"] == "wanted" or record["listing_status"] in {"sold", "order_filled"}:
            skipped += 1
            continue
        if record["state"] is None and not record["location"]:
            skipped += 1
            continue
        records.append(record)

    summary = {
        "source": "stockplace",
        "sample_url": source_url,
        "scraped_at": scraped_at,
        "record_count": len(records),
        "skipped": skipped,
    }
    return records, summary


def parse_card_contacts(card_text: str) -> tuple[str | None, str | None]:
    phone_matches = re.findall(r"(?:\+?61|0)\d[\d\s]{7,}", card_text)
    phones = "; ".join(normalize_whitespace(match) for match in phone_matches) if phone_matches else None
    return None, phones


def extract_rma_title(card) -> str | None:
    for selector in ["h4.sortable", "h4", "h3", "h2"]:
        heading = card.select_one(selector) if "." in selector else card.find(selector)
        title = clean_text(heading)
        if title and title.lower() != "view sale":
            return title
    return None


def extract_rma_agent_name(card) -> str | None:
    contact_block = card.find(string=re.compile(r"Contact", re.IGNORECASE))
    if contact_block:
        container = contact_block.parent.parent if getattr(contact_block, "parent", None) and getattr(contact_block.parent, "parent", None) else None
        if container:
            bold = container.find("b")
            if bold:
                return clean_text(bold) or None
    bold = card.find("b")
    return clean_text(bold) or None


def build_rma_record(card, section_name: str, source_url: str, scraped_at: str) -> dict | None:
    title_link = card.find("a", href=re.compile(r"/sales/cattle/\d+/?$"))
    title = extract_rma_title(card) or (clean_text(title_link) if title_link else clean_text(card.find(["h2", "h3", "h4"]) or card))
    href = title_link.get("href") if title_link else None
    detail_url = urljoin(source_url, href) if href else source_url
    record_id = None
    if href:
        match = re.search(r"/(\d+)(?:/)?$", href)
        if match:
            record_id = match.group(1)

    text = clean_text(card)
    location = None
    location_match = re.search(r"\b[A-Za-z .'-]+,\s*(NSW|QLD|VIC|SA|WA|TAS|NT|ACT)(?:\s+\d{4})?\b", text)
    if location_match:
        location = normalize_whitespace(location_match.group(0))

    sale_date = ""
    sale_time = ""
    date_match = re.search(
        r"((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\d{1,2}(?:st|nd|rd|th)?\s+\w+(?:\s+\d{4})?)",
        text,
        re.IGNORECASE,
    )
    if date_match:
        sale_date = normalize_whitespace(date_match.group(1)) or ""
    time_match = re.search(r"\b(\d{1,2}:\d{2}\s*(?:am|pm)|\d{1,2}\s*(?:am|pm))\b", text, re.IGNORECASE)
    if time_match:
        sale_time = normalize_whitespace(time_match.group(1)) or ""

    sex, listing_class = derive_sex_and_class(title, section_name)
    num_head = derive_head_count(title)
    _, contact_phone = parse_card_contacts(text)
    agent_name = extract_rma_agent_name(card)

    return {
        "source_name": "RMA Network",
        "source_type": "agency_network_sale_index",
        "source_url": detail_url,
        "source_record_id": record_id,
        "scraped_at": scraped_at,
        "permission_status": "permission_first",
        "terms_risk_level": "AMBER",
        "listing_title": title or None,
        "listing_status": "upcoming_sale" if section_name.lower() != "wanted" else "closed",
        "listing_mode": section_name.lower().replace(" ", "_"),
        "listing_category": "commercial",
        "sale_name": title or None,
        "sale_type": section_name.lower().replace(" ", "_"),
        "sale_date": sale_date,
        "sale_time": sale_time,
        "venue": None,
        "location": location,
        "state": derive_state(location),
        "num_head": num_head,
        "class": listing_class,
        "sex": sex,
        "breed": None,
        "breed_groups": [],
        "avg_weight_kg": None,
        "weight_min": None,
        "weight_max": None,
        "weight_range_kg": None,
        "asking_price": None,
        "price_type": None,
        "price_c_kg": None,
        "price_per_head": None,
        "agent_name": agent_name,
        "agent_branch": None,
        "contact_name": agent_name,
        "contact_phone": contact_phone,
        "contact_email": None,
        "catalogue_url": None,
        "online_bidding_url": None,
        "notes_raw": text or None,
        "class_breakdown_raw": None,
    }


RMA_SECTION_NAMES = {"feature", "for sale", "auction", "wanted"}


def is_rma_section_heading(node) -> bool:
    if not getattr(node, "name", None):
        return False
    if node.name not in {"h1", "h2", "h3"}:
        return False
    return clean_text(node).lower() in RMA_SECTION_NAMES


def iter_rma_sections(soup: BeautifulSoup) -> Iterable[tuple[str, list[object]]]:
    for heading in soup.find_all(["h1", "h2", "h3"]):
        section_name = clean_text(heading)
        if section_name.lower() not in RMA_SECTION_NAMES:
            continue

        section_cards = []
        seen = set()
        for element in heading.next_elements:
            if element is heading:
                continue
            if is_rma_section_heading(element):
                break
            if not getattr(element, "name", None):
                continue
            for card in iter_rma_cards_in_container(element):
                card_id = id(card)
                if card_id in seen:
                    continue
                seen.add(card_id)
                section_cards.append(card)

        if section_cards:
            yield section_name, section_cards


def iter_rma_cards_in_container(container) -> Iterable[object]:
    seen = set()

    for card in container.find_all(class_=re.compile(r"card__content", re.I)):
        card_id = id(card)
        if card_id not in seen:
            seen.add(card_id)
            yield card

    for link in container.find_all("a", href=re.compile(r"/sales/cattle/\d+/?$")):
        card = link.find_parent(class_=re.compile(r"card__content", re.I))
        if not card:
            card = link.find_parent(["article", "div", "li"])
        if not card:
            continue
        card_id = id(card)
        if card_id not in seen:
            seen.add(card_id)
            yield card


def parse_rma_html(html: str, source_url: str, scraped_at: str | None = None) -> tuple[list[dict], dict]:
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = scraped_at or now_iso()
    records = []
    skipped = 0
    seen_keys = set()

    for section_name, cards in iter_rma_sections(soup):
        for card in cards:
            record = build_rma_record(card, section_name, source_url, scraped_at)
            if not record:
                skipped += 1
                continue
            if record["listing_mode"] == "wanted":
                skipped += 1
                continue
            title_lower = (record["listing_title"] or "").lower()
            if not any(token in title_lower for token in ["steer", "heifer", "cow", "bull", "sale", "cattle"]):
                skipped += 1
                continue
            dedup_key = (
                record["source_record_id"]
                or record["source_url"]
                or (record["listing_title"], record["contact_phone"], record["sale_date"])
            )
            if dedup_key in seen_keys:
                skipped += 1
                continue
            seen_keys.add(dedup_key)
            records.append(record)

    summary = {
        "source": "rma",
        "sample_url": source_url,
        "scraped_at": scraped_at,
        "record_count": len(records),
        "skipped": skipped,
    }
    return records, summary


def load_html(input_file: str | None, url: str) -> str:
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")

    import requests

    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def main():
    parser = argparse.ArgumentParser(description="Run standalone source parser spikes.")
    parser.add_argument("--source", choices=sorted(SOURCE_CONFIG.keys()), required=True)
    parser.add_argument("--input-file", help="Optional local HTML file to parse instead of fetching.")
    parser.add_argument("--url", help="Optional URL override. Defaults to the source sample URL.")
    args = parser.parse_args()

    config = SOURCE_CONFIG[args.source]
    url = args.url or config["sample_url"]
    html = load_html(args.input_file, url)

    parser_fn = globals()[config["parser"]]
    records, summary = parser_fn(html, url)

    print(json.dumps({"summary": summary, "records": records}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
