**DRUMQUIL SIGNAL**

Australian Cattle Agents, Websites, and Newsletter Channels

| **Version: 1.0** | **Date: 31 May 2026** | **Status: Reference** |
| --- | --- | --- |

## 1. Purpose

This document maps the agent-side source landscape for Signal Scout: branch websites, sale calendars, market reports, downloadable sale-entry PDFs, and opt-in email/newsletter channels that may become a higher-trust second layer beyond platform scraping.

This is not a perfect registry of every cattle agent in Australia. The market is too fragmented for a single-pass guarantee. It is instead a best-effort operational inventory of the most relevant patterns and high-value targets identified during the current research pass.

## 2. Why Agent Sources Matter

Platform scraping alone will never cover the full Australian cattle market.

Agent-controlled sources matter because they often publish:

- store sale calendars;
- early sale-entry PDFs;
- branch-specific sale dates;
- special sale notices;
- market reports;
- subscriber alerts before or alongside broader platform publication.

For Signal Scout, authorised agent channels may become the safest and highest-signal expansion path after AuctionsPlus.

## 3. Decision Rubric

| Decision | Meaning |
| --- | --- |
| `RED - agreement required` | Explicit anti-automation terms or clearly proprietary channel where ingestion should not occur without permission. |
| `AMBER - permission-first` | Public information exists, but it is commercially sensitive, terms are incomplete, or copying/reuse risk remains. Suitable for discussion and limited internal research only. |
| `GREEN - authorised feed path` | The source is naturally designed for opted-in receipt or authorised sharing, such as a newsletter signup or agent-provided PDF feed. |

## 4. High-Value Source Patterns

| Pattern | Typical data shape | Value to Signal Scout | Preferred legal posture |
| --- | --- | --- | --- |
| Branch livestock pages | sale days, branch contacts, venue, categories | medium | public-page review + permission if production use expands |
| Downloadable sale-date PDFs | dates, sale names, venue, schedule | medium | usually acceptable for facts-only capture, still permission-first commercially |
| Sale-entry PDFs | lot counts, account names, breed, sex, age, est. weights | very high | best with agent consent |
| Market reports | sale results and pricing commentary | low for pre-sale matching, high for intelligence | public summarisation only |
| Email alerts / newsletters | upcoming sale notice, curated opportunities, attached catalogues | very high | best path if opt-in and authorised |

## 5. Current Target Inventory

| Source | Coverage / type | Useful public signals found | Newsletter / email path | Legal posture | Build note |
| --- | --- | --- | --- | --- | --- |
| Nutrien Ag Solutions | National agency network | livestock sales calendar and branch sale content | explicit `Livestock Sales Alert` signup found | `GREEN - authorised feed path` for opt-in email; `AMBER` for general scraping | One of the strongest candidates for authorised ingestion. |
| Elders | National agency network | branch cattle sale pages and downloadable sale-date PDFs found | no formal livestock alert confirmed in this pass | `AMBER - permission-first` | Strong source for branch calendars and sale-date docs. Direct permission would help. |
| AWN | National independent agency network | livestock sales, sales calendar, stock-for-sale, market reports | no dedicated buyer alert found in this pass | `AMBER - permission-first` | Strong candidate because it has a real sales calendar and listing layer, but may also route listings through AuctionsPlus and FarmGate. |
| Ray White Rural & Livestock | National agency network | strong livestock network positioning and event/news layer | no structured buyer-alert program confirmed in this pass | `AMBER - permission-first` | Worth tracking, but current evidence suggests more network/brand content than clean cattle listing inventory. |
| GDL (Grant Daniel Long) | Queensland-primary agency network | featured livestock sales on-site | no dedicated alert path confirmed in this pass | `AMBER - permission-first` | Good Queensland candidate for direct sale-page parsing. |
| RLX - Regional Livestock Exchanges | Eastern Australian exchange network | public sale pages with online presence and selected online bidding paths | no newsletter path confirmed in this pass | `AMBER - permission-first` | Important exchange-layer source, but not a conventional agent website. |
| Ian Weir & Son | Northern Rivers / Lismore | public market reports and sale notices | no dedicated newsletter confirmed in this pass | `AMBER - permission-first` | Very relevant regional source; likely useful for local physical sales intelligence. |
| Donovan Livestock & Property | Grafton / Northern Rivers | public market reports and downloadable PDFs | no newsletter confirmed in this pass | `AMBER - permission-first` | Good regional PDF/report source. |
| Farrell McCrohon | Grafton / Clarence region | sale-entry PDF example found | no newsletter confirmed in this pass | `AMBER - permission-first` | Important because it shows pre-sale entry documents can exist in parseable form. |
| Stockplace Marketing | North West Queensland | direct livestock-for-sale pages and individual cattle listings | no dedicated newsletter confirmed in this pass | `AMBER - permission-first` | Strong regional candidate with on-site cattle listings rather than just reports. |
| Sullivan Livestock & Rural Services | Gympie / Queensland | structured upcoming sale pages with cattle counts, classes and linked catalogues | no dedicated newsletter confirmed in this pass | `AMBER - permission-first` | Very useful pattern for parsing physical and special sale information. |
| Forbes Livestock & Agency Co | Central West NSW | cattle market reports, sale details, AuctionsPlus references | weekly newsletter signup explicitly promoted | `AMBER - permission-first` | One of the better independent-agent candidates because it combines reports, sale content and newsletter distribution. |
| Rodwells | Victoria / southern NSW | livestock business confirmed, branch network and major selling-centre access | no alert path confirmed in this pass | `AMBER - incomplete review` | Real livestock business, but structured public listing depth still unclear. |
| KMWL | Central West NSW | market reports and livestock sales presence | Facebook-led updates noted on-site | `AMBER - permission-first` | More useful as a regional information source than a clean listing-origin platform at this stage. |
| JJ Dresser & Co | Cowra / Central Tablelands NSW | sale dates, livestock sales, market updates | no newsletter path confirmed in this pass | `AMBER - permission-first` | Good structured regional sale-information source. |
| RMA Network | VIC, NSW, QLD collective | cattle sales pages, upcoming sales, feature sales, agistment and market-report style content | no newsletter path confirmed in this pass | `AMBER - permission-first` | Strong collective source because it aggregates multiple independent agencies in one place. |
| CIAA | South Australian independent-agent collective | livestock-for-sale section, auction pages, member directory | no email alert path confirmed in this pass | `AMBER - permission-first` | Valuable SA collective with genuine live for-sale inventory. |
| SAL | South Australian network | livestock services and strong agency footprint | no newsletter path confirmed in this pass | `AMBER - permission-first` | Relevant, though likely overlapping with Nutrien / Platinum / CIAA channels. |
| Quality Livestock | SA and VIC | saleyard pages, stock-for-sale, SMS subscribe / mailing-list hooks | mailing-list / SMS subscribe path confirmed | `AMBER - permission-first` | Good candidate because it has both public sale structure and a direct subscriber pathway. |
| Ray White Rural branches | National / regional | possible livestock/sale pages, not deeply reviewed here | newsletter path not confirmed | `AMBER - incomplete review` | Worth a later national-branch review. |
| Local independent agents | Regional fragmented market | often have WordPress pages, Facebook posts, PDF uploads | varies | `AMBER - source-by-source` | These may be the best physical-sale coverage layer, but require manual sourcing. |

## 6. Source Notes

### 6.1 Nutrien Ag Solutions

Why it matters:
- National scale.
- Existing livestock sales calendar and event pages.
- Explicit opt-in alert product already exists.

What was found:
- A live `Livestock Sales Alert` signup page inviting users to receive updates on stock for sale and upcoming auctions.
- Corporate online-services terms that explicitly prohibit automated scripts collecting information from the technology.

Signal Scout implication:
- Do not treat Nutrien's website as a free general scrape target.
- Do treat Nutrien alert emails as a strong candidate for authorised ingestion if subscribed legitimately and used within the scope of permission.

Best use:
- dedicated authorised mailbox receives Nutrien alert emails;
- parser extracts factual listing metadata and attachment links;
- Signal Scout stores structured facts and links back to source.

### 6.2 Elders

Why it matters:
- National footprint and deep cattle-market coverage.
- Branch pages often expose sale days and local cattle-sale information.

What was found:
- Public branch pages with recurring sale schedules.
- Downloadable cattle sale date PDFs on some branch pages.
- General website terms page located, but no explicit anti-scraping clause surfaced in the snippet reviewed during this pass.

Signal Scout implication:
- Good candidate for public branch/schedule intelligence.
- For systematic extraction at scale, direct permission is still preferable.

### 6.3 Ian Weir & Son

Why it matters:
- Strong relevance to the Northern Rivers physical saleyard ecosystem already in project scope.

What was found:
- Public market-report pages with sale dates, commentary, categories, and agent contact numbers.

Signal Scout implication:
- Useful for saleyard timing intelligence and agent-contact context.
- Less likely to provide structured pre-sale lot data on its own than a sale-entry PDF or email advice.

### 6.4 Donovan Livestock & Property

Why it matters:
- Regional relevance to Grafton and surrounding sales.

What was found:
- Market report pages and downloadable PDF reports for store and fat sales.

Signal Scout implication:
- More valuable for post-sale intelligence than for pre-sale matching unless paired with sale-entry material.

### 6.5 Farrell McCrohon

Why it matters:
- The strongest concrete example found of a parseable pre-sale cattle-entry PDF.

What was found:
- A public `Grafton September Store Cattle Sale` PDF containing lot-style entry information such as account/vendor line, head count, breed, sex and age descriptors.

Signal Scout implication:
- This is exactly the kind of document that could make physical saleyard sourcing viable.
- It supports a dedicated `agent_pdf` or `sale_entry_pdf` parser path in the data model.

## 7. Email Newsletter Strategy

### 7.1 Recommended operating model

Do not frame this as "link Gmail to Codex" for production.

Instead:

1. create a dedicated Google Workspace mailbox for inbound sale alerts;
2. subscribe only to agent/platform newsletters that are relevant and lawful to receive;
3. ingest emails through a controlled application path;
4. extract facts from message bodies and attachments;
5. store source URL, sender, sent date, and permission status alongside parsed data.

### 7.2 Why email may be the best expansion channel

Email alerts are often:
- earlier than public catalogue pages;
- intentionally distributed to interested buyers;
- structured enough to parse;
- easier to justify legally when received through opt-in.

### 7.3 Compliance notes for newsletter ingestion

1. Use least-privilege mailbox access.
2. Prefer a dedicated mailbox over a personal Gmail inbox.
3. Keep an internal register of what subscriptions were joined, when, and for what business purpose.
4. Preserve unsubscribe capability and sender identity metadata.
5. Avoid using harvested sender or contact details for unrelated outreach.

## 8. Physical Saleyard Lot Viability

Physical saleyard lot discovery is possible, but not uniformly.

Observed pattern:
- some sales only publish calendars and post-sale reports;
- some agents publish sale-entry PDFs;
- some useful detail lives in newsletters or attachments rather than web pages;
- the richest pre-sale detail is often agent-controlled, not saleyard-controlled.

Practical conclusion:

Signal Scout should not assume that a single national "physical sale lot" scraper exists. It will likely need a mixed strategy:

1. branch/saleyard calendars for timing;
2. agent PDFs for structured entries;
3. email newsletters for early notice;
4. direct agent relationships for anything systematic.

## 9. Build Guidance for Signal Scout

### 9.0 Focused Second-Pass Ranking

The newly confirmed agency/network candidates do not all belong in the same engineering queue. After the focused second-pass, they split into three practical groups:

| Rank | Source | Best fit | Why |
| --- | --- | --- | --- |
| `A` | Stockplace Marketing | direct parser candidate | Own stock listings with repeated structured fields (`head`, `breed`, `stock type`, `weight`, `price type`, status). |
| `A` | Sullivan Livestock & Rural Services | direct parser candidate | Strong structured upcoming-sales pages with cattle counts, classes, dates, and linked catalogues/bidding pages. |
| `A` | GDL | direct parser candidate | Home and livestock pages expose repeated featured sale cards and detail pages for cattle/private sales. |
| `A` | CIAA | direct parser candidate | Genuine `livestock for sale` inventory plus auction-market pages with sale-specific details. |
| `A` | RMA Network | direct parser candidate | Public cattle-sales pages aggregate sale cards across multiple agencies with sale/contact metadata. |
| `A` | Quality Livestock | direct parser candidate plus subscriber path | Public `stock for sale`, saleyard pages, and `SMS Subscribe` path make it both parseable and relationship-friendly. |
| `B` | AWN | hybrid parser + outreach candidate | Real sales calendar, stock-for-sale entry points and market reports exist, but some value appears to route through AuctionsPlus/FarmGate and branch-level relationships. |
| `B` | Forbes Livestock & Agency Co | hybrid parser + newsletter candidate | Good market reports, weekly sales, newsletter and AuctionsPlus linkage, but less evidence of a large standalone live on-site cattle inventory. |
| `B` | JJ Dresser & Co | hybrid sale-info + newsletter candidate | Structured sale info and a VIP email list are present, but live direct cattle inventory looks lighter than the `A` group. |
| `C` | KMWL | outreach / market-intel candidate | Strong reports and social cadence, but current site reads more as report/news and Facebook funnel than listing-origin source. |
| `C` | Ray White Rural & Livestock | outreach / network candidate | Strong network footprint, but current live evidence is more brand/event/news than direct cattle listing inventory. |
| `C` | SAL | outreach / network candidate | Real livestock footprint, but current page is mostly capability/network description and overlaps heavily with CIAA/Nutrien/Platinum channels. |
| `C` | Rodwells | watchlist / outreach candidate | Livestock business is clear, but structured public cattle listing depth is still unclear. |

Recommended interpretation:

- `A` group = worth parser-design work soon.
- `B` group = good candidates for smaller parser experiments or newsletter/outreach first.
- `C` group = contact and monitor, but do not spend parser time early.

### 9.1 Source classes to add

Recommended new `source_type` values:

- `agent_branch_page`
- `sale_calendar_pdf`
- `sale_entry_pdf`
- `market_report`
- `email_notice`
- `email_attachment_pdf`

### 9.2 Fields worth storing for agent/newsletter sources

- `source_name`
- `source_url`
- `source_type`
- `sale_name`
- `sale_date`
- `venue`
- `agent_name`
- `agent_branch`
- `sender_email`
- `attachment_url`
- `lot_count`
- `vendor_or_account`
- `notes_raw`
- `permission_status`

### 9.3 Parser priorities

1. HTML sale calendar parser
2. PDF sale-entry parser
3. Email body parser
4. Market-report summariser

### 9.4 Product caution

Do not treat market reports as listing records. They are different objects and should not pollute the live buyer-match feed unless a user explicitly wants historical market intelligence.

## 10. Recommended Next Moves

### Tier 1

- Build an internal source register with `source`, `type`, `risk`, `permission`, `owner_contact`, and `review_date`.
- Start with `Nutrien`, `Elders`, `Ian Weir & Son`, `Donovan`, and `Farrell McCrohon`.

### Tier 2

- Create a dedicated inbound mailbox for authorised newsletters and sale alerts.
- Build a small normaliser for PDF/email-derived sale entries separate from the AuctionsPlus parser.

### Tier 3

- Begin relationship outreach to the most useful regional agents and ask for permission to ingest public sale-entry documents and newsletters into a buyer-alert tool that links back to the source.

### Tier 4

- Run a dedicated second-pass review of the higher-potential agency networks and collectives:
  - `AWN`
  - `GDL`
  - `Stockplace`
  - `Sullivan`
  - `Forbes Livestock`
  - `RMA`
  - `CIAA`
  - `Quality Livestock`

Focused second-pass result:

- `Parser-first`: `Stockplace`, `Sullivan`, `GDL`, `CIAA`, `RMA`, `Quality`
- `Hybrid`: `AWN`, `Forbes`, `JJ Dresser`
- `Outreach/newsletter-first`: `KMWL`, `Ray White Rural & Livestock`, `SAL`, `Rodwells`

## 11. Reviewed Sources

Primary sources reviewed or relied on in this pass:

- Nutrien livestock sales alert: `https://www.nutrienagsolutions.com.au/livestock/livestock-sales-alert`
- Nutrien online services terms: `https://www.nutrienagsolutions.com.au/terms-and-conditions-privacy-policy/Online-Services-Terms-of-use`
- Elders website terms: `https://elders.com.au/website-terms-and-conditions/`
- Elders VLE Leongatha page: `https://elders.com.au/our-services/our-branches/vic/victorian-livestock-exchange-leongatha-market`
- Elders Strathalbyn cattle sale dates page: `https://elders.com.au/our-services/our-branches/sa/elders-strathalbyn`
- Elders Strathalbyn sale-dates PDF: `https://elders.com.au/content/dam/eld/documents/other-documents/strathalbyn_cattle_sales.pdf`
- Ian Weir and Son market report: `https://ianweirandson.com.au/listings/off-the-rails-lismore-cattle-market-report/`
- Donovan market reports: `https://donovanlivestock.com.au/livestock-sales/market-reports/`
- Farrell McCrohon sale-entry PDF example: `https://farrellmccrohon.com.au/wp-content/uploads/2018/03/STORE-SALE-ENTRIES-SEPT-2025.pdf`

Related compliance references relevant to newsletter ingestion:

- Google Workspace API user data and developer policy: `https://developers.google.com/gmail/api/policy`
- OAIC personal information guidance: `https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/handling-personal-information/what-is-personal-information`
- ACMA spam guidance: `https://www.acma.gov.au/avoid-sending-spam`
