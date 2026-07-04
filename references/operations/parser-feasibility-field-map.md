**DRUMQUIL SIGNAL**

Parser Feasibility Field Map

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Working Reference** |
| --- | --- | --- |

## 1. Purpose

This file is a compact companion to the parser feasibility shortlist.

It maps the parser-first sources against the fields Signal Scout is most likely to extract, so parser design can start from a realistic shared schema instead of improvising source by source.

## 2. Field Coverage Matrix

| Field | Stockplace | Sullivan | GDL | CIAA | RMA | Quality |
| --- | --- | --- | --- | --- | --- | --- |
| `listing_title` | strong | medium | strong | strong | strong | medium |
| `sale_name` | weak | strong | strong | strong | strong | strong |
| `sale_type` | medium | strong | strong | strong | strong | strong |
| `sale_date` | weak | strong | medium | medium | medium | medium |
| `sale_time` | weak | medium | weak | medium | weak | medium |
| `venue` | weak | strong | medium | medium | medium | strong |
| `location` | strong | strong | strong | strong | strong | strong |
| `head_count` | strong | medium | medium | medium | weak | medium |
| `class_breakdown_raw` | weak | strong | weak | medium | weak | weak |
| `breed` | strong | weak | medium | medium | weak | medium |
| `stock_type` | strong | medium | medium | medium | medium | medium |
| `avg_weight_kg` | strong | weak | weak | medium | weak | weak |
| `asking_price` | weak | weak | weak | strong | weak | weak |
| `price_type` | strong | weak | weak | medium | weak | weak |
| `status` | strong | medium | weak | medium | strong | weak |
| `contact_name` | weak | strong | medium | strong | medium | medium |
| `contact_phone` | weak | strong | medium | strong | strong | medium |
| `catalogue_url` | weak | strong | weak | weak | weak | weak |
| `online_bidding_url` | medium | strong | weak | weak | weak | weak |
| `subscribe_path` | weak | weak | weak | weak | weak | strong |

## 3. Interpretation

Best direct-listing source:
- `Stockplace`

Best sale-notice source:
- `Sullivan`

Best network sales aggregator:
- `RMA`

Best pricing/for-sale collective:
- `CIAA`

Best outreach-plus-parser hybrid:
- `Quality`

Best Queensland expansion candidate after first spikes:
- `GDL`
