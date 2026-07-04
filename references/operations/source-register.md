**DRUMQUIL SIGNAL**

Signal Scout Source Register

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Working Register** |
| --- | --- | --- |

## 1. Purpose

This register converts the platform and agent research into an operational source list for Signal Scout.

Use this file as the working control sheet for source expansion decisions. It answers:

1. what the source is;
2. how valuable it is;
3. what the legal posture looks like right now;
4. whether we need permission;
5. what the next action is.

This is a living operational document. Update it whenever:

- a new source is identified;
- terms are re-checked;
- permission status changes;
- a parser is prototyped;
- a source is approved, deferred, or dropped.

## 2. Status Keys

### Build Priority

| Value | Meaning |
| --- | --- |
| `P1` | Important near-term source or enabling channel |
| `P2` | Useful secondary source |
| `P3` | Long-tail or monitor-only source |

### Legal Risk

| Value | Meaning |
| --- | --- |
| `RED` | Do not scrape without written permission |
| `AMBER` | Permission-first; limited internal research only |
| `GREEN` | Authorised/opt-in path or relatively low-friction facts-only source |

### Source Status

| Value | Meaning |
| --- | --- |
| `active` | Already used in product/runtime |
| `research` | Investigated but not yet actioned |
| `outreach` | Needs permission or relationship contact |
| `prototype` | Safe enough to test internally or with permission |
| `hold` | Defer for now |
| `drop` | Not worth pursuing at present |

## 3. Master Register

| Source | Source class | Coverage | Build priority | Legal risk | Permission needed? | Source status | Best ingestion path | Terms review date | Current owner | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AuctionsPlus | platform | national | `P1` | `AMBER` | yes, before scale/paid | `active` | public-page parser already in use | 31 May 2026 | Tom / product | Keep beta stable and seek written comfort before commercial scale |
| The Herd Online | platform | national | `P1` | `RED` | yes | `outreach` | partnership / permission / licence | 31 May 2026 | Tom / product | Do not build scraper; prepare permission request |
| On The Box / Up For Bids | platform | national | `P1` | `AMBER` | yes | `outreach` | permission-led parser or partner feed | 31 May 2026 | Tom / product | Identify current trading brand/contact path and prepare outreach |
| StockLive | platform | national | `P1` | `AMBER` | yes | `outreach` | permission-led parser / data relationship | 31 May 2026 | Tom / product | Add to first-round platform outreach |
| Southern Livestock Exchange | exchange / livestream auction | SA-based with online bidding access | `P2` | `AMBER` | likely yes | `research` | exchange-page parser or direct feed | 31 May 2026 | Tom / product | Verify data shape and whether online sale data is exposed directly or through a third-party bidding layer |
| Cattlesales | platform | national | `P1` | `AMBER` | yes | `outreach` | permission-led classifieds parser | 31 May 2026 | Tom / product | Add to first-round platform outreach |
| Nutrien Ag Solutions alerts | newsletter / email | national | `P1` | `GREEN` for opt-in email, `AMBER` for scraping | likely no for subscribed alerts, yes for broader web extraction | `prototype` | dedicated mailbox + email/attachment parser | 31 May 2026 | Tom / ops | Create mailbox and subscribe legitimately to sales alerts |
| Nutrien livestock-for-sale pages | agent website / listings | national | `P2` | `AMBER` | yes for systematic production extraction | `research` | listings-page parser or approved feed | 31 May 2026 | Tom / ops | Distinguish between public listings, sales calendar, and alert-email pathways |
| Nutrien branch pages | agent website | national | `P2` | `AMBER` | yes for systematic production extraction | `research` | branch-page and calendar parser | 31 May 2026 | Tom / ops | Review whether calendars alone justify parser work |
| Elders branch pages | agent website | national | `P1` | `AMBER` | yes, ideally | `research` | branch-page + sale-date PDF parser | 31 May 2026 | Tom / ops | Start branch-level inventory for cattle-heavy regions |
| Elders livestock pages / Livestock Now | agent website / newsletter | national | `P2` | `AMBER` | yes, ideally | `research` | branch-page, article, or newsletter ingestion | 31 May 2026 | Tom / ops | Separate sale-calendar data from general livestock content and newsletter material |
| Elders sale-date PDFs | pdf | national / branch-level | `P1` | `AMBER` | ideally yes | `prototype` | PDF schedule parser | 31 May 2026 | Tom / ops | Capture 3-5 sample PDFs and assess consistency |
| AWN livestock pages | agent network / sales calendar | national | `P2` | `AMBER` | yes, ideally | `research` | sales-calendar parser, listings-page parser, or market-report ingestion | 31 May 2026 | Tom / ops | Hybrid candidate: good calendar/listing entry points, but likely needs outreach and branch-level mapping before full parser build |
| Ray White Rural & Livestock | agent network | national | `P2` | `AMBER` | yes, ideally | `hold` | event page / network listing parser, plus social-led follow-up | 31 May 2026 | Tom / ops | Mostly outreach/network candidate unless stronger direct listing inventory is confirmed |
| GDL (Grant Daniel Long) | agent website / sales listings | Queensland-primary | `P2` | `AMBER` | yes, ideally | `prototype` | featured livestock sales parser | 31 May 2026 | Tom / ops | Strong parser candidate with repeated featured sale cards and cattle sale detail pages |
| Ian Weir & Son | agent website | Northern Rivers | `P1` | `AMBER` | yes for systematic reuse | `research` | branch-page / report parser | 31 May 2026 | Tom / ops | Add to regional agent outreach list |
| Donovan Livestock & Property | agent website / pdf | Northern Rivers / Grafton | `P1` | `AMBER` | yes for systematic reuse | `research` | market-report + PDF parser | 31 May 2026 | Tom / ops | Add to regional agent outreach list |
| Farrell McCrohon sale-entry PDFs | pdf | Grafton / Clarence | `P1` | `AMBER` | yes, strongly preferred | `prototype` | sale-entry PDF parser | 31 May 2026 | Tom / ops | Use as first physical-sale PDF parsing sample |
| Stockplace Marketing | regional agent website / listings | North West Queensland | `P2` | `AMBER` | yes, ideally | `prototype` | direct listing-page parser | 31 May 2026 | Tom / ops | Strong parser candidate with repeated on-site listing fields and status metadata |
| Sullivan Livestock & Rural Services | regional agent website / sales pages | Gympie / Queensland | `P2` | `AMBER` | yes, ideally | `prototype` | upcoming-sales parser + linked catalogue handling | 31 May 2026 | Tom / ops | Strong parser candidate for sale schedules, yarding counts and linked catalogues |
| Forbes Livestock & Agency Co | regional agent website / newsletter | Central West NSW | `P2` | `AMBER` | yes, ideally | `research` | market-report parser, upcoming-sales parser, newsletter signup | 31 May 2026 | Tom / ops | Better as hybrid parser/newsletter candidate than pure listing-origin parser |
| Rodwells | regional agency network | Victoria / southern NSW | `P3` | `AMBER` | yes, ideally | `hold` | contact-led or branch-led approach only | 31 May 2026 | Tom / ops | Livestock business confirmed, but no strong structured public cattle listing layer surfaced yet |
| Kevin Miller Whitty Lennon & Co (KMWL) | regional agent website / reports | Central West NSW | `P2` | `AMBER` | yes, ideally | `hold` | market-report parser and sale-info extraction | 31 May 2026 | Tom / ops | Better outreach/market-intel candidate than parser-first source at this stage |
| JJ Dresser & Co | regional agent website / sale info | Cowra / Central Tablelands NSW | `P2` | `AMBER` | yes, ideally | `research` | sale-info parser and market update extraction | 31 May 2026 | Tom / ops | Hybrid candidate with sale pages plus VIP email list |
| RMA Network | agency collective / sale network | VIC, NSW, QLD | `P2` | `AMBER` | yes, ideally | `prototype` | sales-page parser | 31 May 2026 | Tom / product | Strong parser candidate because cattle sales are exposed as repeated public sale cards with contact metadata |
| CIAA | state collective / exchange-linked listings | South Australia | `P2` | `AMBER` | yes, ideally | `prototype` | livestock-for-sale parser and market page extraction | 31 May 2026 | Tom / product | Strong parser candidate with public live for-sale inventory and auction-market pages |
| SAL (South Australian Livestock) | state agency network | South Australia | `P2` | `AMBER` | yes, ideally | `hold` | livestock-page and regional network mapping | 31 May 2026 | Tom / ops | Better treated as network/outreach layer; likely overlaps with CIAA and Nutrien channels |
| Quality Livestock | regional agency network | SA and VIC | `P2` | `AMBER` | yes, ideally | `prototype` | saleyard page parser, stock-for-sale parser, SMS/newsletter path | 31 May 2026 | Tom / ops | Strong parser candidate with public sale structure plus subscriber hooks |
| FarmGate Auctions | platform | national | `P2` | `AMBER` | yes | `hold` | permission-led platform parser | 31 May 2026 | Tom / product | Keep in secondary queue after top platform outreach |
| LocalAg | platform | national / broad ag | `P3` | `AMBER` | yes | `hold` | low-priority marketplace parser | 31 May 2026 | Tom / product | Revisit only if cattle inventory looks stronger |
| Agora Livestock | platform | national | `P2` | `RED` | yes | `hold` | partnership only | 31 May 2026 | Tom / product | No scrape work; only revisit for commercial conversation |
| Farm Tender | platform | national / broad ag | `P3` | `RED` | yes | `drop` | partnership only | 31 May 2026 | Tom / product | Not worth current effort for cattle expansion |
| AgTrader | platform | national / broad ag | `P3` | `AMBER` | likely yes | `hold` | occasional classifieds parser | 31 May 2026 | Tom / product | Keep as watchlist item |
| Farmbuy Livestock | marketplace / stud and auction listings | national | `P2` | `AMBER` | likely yes | `research` | listings-page parser or approved content use | 31 May 2026 | Tom / product | Review terms and content ownership model before using as source rather than directory |
| The Sale Yards | marketplace / saleyard comparison | Queensland-focused | `P3` | `AMBER` | likely yes | `hold` | comparison / quote source only | 31 May 2026 | Tom / product | Useful more for saleyard intelligence than live buyer-alert inventory |
| RLX - Regional Livestock Exchanges | exchange network | eastern Australia | `P2` | `AMBER` | yes, ideally | `research` | sale-calendar / sale-detail parser, potentially third-party bidding linkout | 31 May 2026 | Tom / product | Map which RLX sales expose structured public sale details vs links to StockLive or AuctionsPlus |
| Ray White Rural branch sites | agent website | national / branch-level | `P2` | `AMBER` | yes, ideally | `research` | branch-page / sale notice parser | 31 May 2026 | Tom / ops | Run later branch-by-branch inventory |
| Local independent agents | agent website / email / pdf | regional fragmented | `P1` in target regions | `AMBER` | yes, ideally | `research` | email + PDF + branch-page mix | 31 May 2026 | Tom / ops | Build regional target list by saleyard first, agent second |
| LivestockHub / similar | platform | unclear | `P3` | `AMBER` | unknown | `hold` | unknown | 31 May 2026 | Tom / product | Verify existence, listing density and terms before doing anything |
| Fivestock / emerging niche sites | platform | unclear | `P3` | `AMBER` | unknown | `hold` | unknown | 31 May 2026 | Tom / product | Monitor only |

## 4. Recommended First-Wave Test Queue

This is the concrete next-source test order that best matches current legal
posture, product value, and the ingestion-path review saved in
`references/operations/ai-content-pipeline-research-review-for-signal-scout.md`.

| Order | Source | Why now |
| --- | --- | --- |
| 1 | AuctionsPlus hardening | Current beta source; still the base system |
| 2 | Dedicated authorised alert mailbox | Unlocks the safest next-source test path and enables legitimate sample capture |
| 3 | Nutrien alert emails | Best authorised national ingestion candidate; tests the email-notice path without scraper risk |
| 4 | Farrell McCrohon sample PDF parser | Best proof that physical sale-entry PDFs can become structured `WATCHING` inputs |
| 5 | Stockplace Marketing parser spike | Strongest direct HTML cattle-listing parser candidate in the current register |
| 6 | RMA Network parser spike | Best agency-network sales aggregator test with broad discovery value |
| 7 | Sullivan Livestock parser spike | Strongest sale-notice parser candidate for pre-sale signals and class breakdowns |
| 8 | Elders sale-date PDF parser spike | High-value national network test if template consistency is good enough |
| 9 | Regional agent outreach set (`Ian Weir`, `Donovan`, `Farrell McCrohon`) | Likely fastest relationship path to target-region physical-sale coverage |
| 10 | Platform outreach set (`The Herd`, `On The Box`, `StockLive`, `Cattlesales`) | Necessary before platform expansion can happen cleanly; not immediate test-scrape candidates |
| 11 | RLX / Southern Livestock Exchange mapping | Important exchange-layer mapping, but probably mediated by platform permissions or third-party bidding layers |
| 12 | High-signal second-wave parser set (`GDL`, `CIAA`, `Quality`, `AWN`, `Forbes`) | Extend geographic and source-shape coverage after the first parser spikes are proven |

## 5. Tool Policy Notes

### Kill the Newsletter

Signal Scout may use Kill the Newsletter for legitimate opted-in source emails
where the source is already distributing updates to subscribers and the
downstream use remains facts-only with attribution and link-back.

It does not override `RED` or permission-first source status.

See:

- `references/operations/kill-the-newsletter-intake-workflow.md`
- `references/operations/authorised-intake-ops.md`

### Firecrawl

Firecrawl may be used as a source-specific technical extractor for approved or
acceptable candidate sources, especially if a page is JS-rendered or difficult
to parse with simpler methods.

It does not make restricted sources legally usable by itself.

See:

- `references/operations/firecrawl-allowed-use-checklist.md`
- `references/operations/ai-content-pipeline-research-review-for-signal-scout.md`

## 6. Source Intake Checklist

Use this checklist before adding any new line to the product backlog:

1. Record source name and source class.
2. Save source URL and terms URL.
3. Record review date.
4. Classify legal risk (`RED`, `AMBER`, `GREEN`).
5. Record whether the source is public, login-gated, email-based, or partner-only.
6. Decide the likely ingestion path.
7. Set a concrete next action.
8. Assign an owner.

## 7. Notes for Future Conversion to Spreadsheet

This register is deliberately shaped so it can later become a Sheet or Airtable table with the same columns.

Suggested future columns to add once outreach begins:

- `contact_name`
- `contact_email`
- `first_contact_date`
- `last_contact_date`
- `reply_status`
- `approved_use_case`
- `parser_status`
- `sample_docs_captured`
- `go_live_decision`
