# Signal Scout Source Integration Architecture

## Purpose

This document turns the multi-source intake plan into an implementation-facing
architecture for the next 12 months.

It is the reference point for adding new source modules without disturbing the
live AuctionsPlus beta path.

Use with:

- `cattle_scout.py`
- `references/operations/source-register.md`
- `references/operations/parser-specs-top-three.md`
- `references/operations/kill-the-newsletter-intake-workflow.md`
- `references/operations/firecrawl-allowed-use-checklist.md`

## Core Runtime Backbone

Keep this pattern as the permanent ingestion boundary:

`discover_items -> scrape_item -> normalise_shared_listing -> match users`

Rules:

- each source module owns discovery and extraction for its own source
- each source returns a sparse dict that can be normalised into the shared
  listing shape
- buyer matching must not branch on source-specific parser logic
- one source failure must degrade that source only, not the whole run

## Two-Contract Model

### 1. Raw source contract

Source-specific intake payloads preserve provenance and unstructured facts.

Examples:

- mailbox-derived email notice JSON
- Kill the Newsletter Atom-item export JSON
- sale-entry PDF extraction JSON
- HTML parser raw capture

The raw contract may contain source-specific blocks such as:

- `feed_meta`
- `attachments`
- `class_breakdown_raw`
- `catalogue_url`
- `online_bidding_url`

### 2. Normalized shared listing contract

Every source must map into the shared-listing shape expected by
`normalise_shared_listing()` and the downstream runtime.

Rules:

- unknown fields remain `None`
- source provenance must survive normalization
- rich sources can fill many fields
- sparse sources may still be valid for `WATCHING`-grade matching

## Approved Source Families

Standardize new sources into these families:

- `auction_listing`
- `email_notice`
- `email_attachment_pdf`
- `sale_entry_pdf`
- `sale_calendar_pdf`
- `agent_direct_listing`
- `agent_sale_notice`
- `agency_network_sale_index`
- `api_feed`
- later `js_page`

Use these families to choose parser behavior, source confidence defaults, and
rollout expectations. Do not let each new source invent its own ad hoc source
type unless the family list is clearly insufficient.

## Matching and Alerting Rules

### Rich listing sources

Examples:

- AuctionsPlus
- direct listing pages with enough cattle fields

Allowed outcomes:

- `WATCHING`
- `ALERTED`

### Sparse notice sources

Examples:

- email notice
- sale-entry PDF
- sale calendar item
- network sales card

Allowed outcome by default:

- `WATCHING`

Upgrade to richer alerting only when the source proves it can reliably provide
enough factual detail to support the existing buyer criteria safely.

### Excluded objects

Do not ingest these into the buyer-match feed as listing records:

- generic market reports
- commentary-only newsletters
- broad news digests
- duplicate directory pages with no usable sale signal

## Source Confidence Defaults

Use these starting ranges:

| Source family | Suggested confidence |
|---|---|
| `auction_listing` | `0.9` |
| `agent_direct_listing` | `0.45-0.6` |
| `email_notice` | `0.35-0.5` |
| `email_attachment_pdf` / `sale_entry_pdf` | `0.4-0.55` |
| `agency_network_sale_index` | `0.45-0.6` |
| `js_page` | inherit from source quality, not extractor sophistication |

These are starting defaults only. Raise or lower them once real sample quality
is known.

## Reliability Stack

Use the ingestion stack in this order:

1. direct mailbox or mailbox-forward path
2. Kill the Newsletter as optional adapter
3. manual raw JSON fallback
4. plain HTML parsing
5. Playwright for approved JS-rendered pages
6. Firecrawl only when approved and still necessary

Rules:

- Kill the Newsletter is a convenience transport, not the backbone
- keep manual raw JSON intake available even after automation grows
- Firecrawl and Playwright are source-specific tools, not platform-wide defaults
- the approved path must be chosen per source, not once globally

## First 12-Month Build Sequence

### Phase 1 - intake foundation

- stabilize raw authorized-notice contract
- keep `authorised_notice_proto` file-based
- preserve provenance through normalization
- define which sparse sources are `WATCHING`-only

### Phase 2 - durable authorized notices

- use direct mailbox as the long-term operator path
- use Kill the Newsletter as an optional adapter for subscribed sources
- validate first with `Nutrien Ag Solutions alerts`
- then test selected `Elders` branch updates and PDFs

### Phase 3 - parser-first non-platform sources

- `Stockplace`
- `RMA`
- `Sullivan`
- `Farrell McCrohon`
- `Elders sale-date PDFs`

Output target:

- normalized JSON first
- no Sheet writes or live alerts until source quality is proven

### Phase 4 - broader coverage

- `GDL`
- `CIAA`
- `Quality`
- `AWN`
- `Forbes`
- regional relationship path: `Ian Weir`, `Donovan`, `Farrell McCrohon`

### Phase 5 - heavy extractor lane

- use `Playwright` first for approved JS-rendered pages
- use `Firecrawl` only when simpler approved paths are still insufficient
- keep this lane outside the live AuctionsPlus path

## Platform Expansion Lane

Keep platform expansion separate from parser-first agent-site work.

Current platform queue:

- `StockLive`
- `On The Box / Up For Bids`
- `Cattlesales`
- later `The Herd Online` only if permission posture changes

Rules:

- treat `StockLive` as an active platform-outreach candidate, not a scrape-first build
- do not mix platform-permission work into the beta-safe parser lane
- only move a platform into implementation once the source register posture supports it

## Implementation Guardrails

1. `RED` sources stay off the build path without written approval.
2. `AMBER` sources stay within the source-register posture and ops rules.
3. Every downstream alert must preserve attribution and link-back.
4. New source modules must be disableable individually.
5. New source modules must not require buyer-filter rewrites to function.
