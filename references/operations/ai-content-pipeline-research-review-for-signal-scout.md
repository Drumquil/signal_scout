# AI Content Pipeline Research Review for Signal Scout

Reviewed on 22 June 2026 against:
`C:/Users/Drumquil/Documents/Claude/claude-projects/cop-pipline/reference/ai_content_pipeline_research_v1_0.md`

## Purpose

This note captures the parts of the external research document that are likely
to help Signal Scout expand beyond the current AuctionsPlus-first runtime.

It is a supporting reference only. It does not replace the active source of
truth in:

- `docs/CURRENT_STATE.md`
- `docs/auctionsplus-selector-reference.md`
- `docs/strategy.md`

## Bottom Line

The external document is useful, but mostly for **future source expansion**
rather than the current AuctionsPlus scraper.

Why:

- Signal Scout's current AuctionsPlus path already works with static HTML via
  `requests` + `BeautifulSoup`.
- The research is strongest on **blocked sources, JS-rendered sources,
  newsletter-to-feed workarounds, and source-routing patterns**.
- Those findings fit Phase 2 and authorised-source expansion more than the
  current beta blocker list.

## What Is Directly Useful for Signal Scout

### 1. Keep AuctionsPlus on the current parser-first path

The research recommends heavier tools such as Playwright and managed scraping
services for JS-rendered or blocked pages. That does **not** justify changing
the AuctionsPlus runtime today, because our own selector reference already
confirms the required catalogue fields are present in static HTML.

Signal Scout implication:

- Keep `cattle_scout.py` on `requests.Session()` + `BeautifulSoup` for
  AuctionsPlus unless the live site behaviour changes.
- Optimise within the current path before adding browser automation.

### 2. Reuse the existing `source_type` architecture for Phase 2 expansion

The external document's "source-type routing" recommendation maps well to the
runtime direction already visible in `cattle_scout.py`.

Signal Scout implication:

- Continue treating each source as a separate ingestion module.
- Keep discovery and scraping logic source-specific, but normalise to the same
  listing shape.
- Classify future sources explicitly, for example:
  - `auction_listing`
  - `email_notice`
  - future `rss_notice`
  - future `html_page`
  - future `playwright_page`
  - future `api_feed`

This is relevant when adding agent websites, The Herd Online alternatives, or
authorised publisher inputs.

### 3. Add a source-triage checklist before building any new scraper

The best reusable idea in the document is the fetch-order decision framework.
For every future source, test the cheapest path first:

1. Does the source already offer an authorised email/newsletter path?
2. Does it expose RSS or another feed?
3. Is the content available in plain HTML?
4. Is the page JS-rendered and therefore a Playwright candidate?
5. Is there a public API or structured dataset instead of a webpage?

Signal Scout implication:

- Apply this triage before writing code for any new platform or agent site.
- This supports the strategy rule that expansion should stay
  permission-first.

### 4. Playwright is a Phase 2 tool, not a default dependency

The document's Playwright guidance is relevant for sources like:

- The Herd Online
- JS-heavy catalogue pages
- dynamic agent or saleyard portals

Signal Scout implication:

- Use Playwright only when a target source genuinely requires JS execution.
- Keep it outside the main AuctionsPlus-first runtime until a real source
  proves the need.
- If introduced, isolate it behind a source-specific fetch function rather than
  mixing browser logic into the whole runtime.

### 5. Authorised notice intake may be more efficient than scraping

The document strongly favours feed/newsletter ingestion when available because
it avoids scraper brittleness and anti-bot issues.

Signal Scout implication:

- This supports the current authorised notice pathway already scaffolded in
  `authorized_notice_raw/`, `transform_authorized_notices.py`, and
  `validate_authorized_notice_samples.py`.
- For some sources, subscription or permissioned inbox intake may be a better
  build than HTML scraping.

### 6. Prefer deterministic intermediate structures when source count grows

The document argues for named JSON intermediate files and schema-validated
outputs in multi-stage AI pipelines.

Signal Scout implication:

- This is not an immediate beta priority for the current scrape-filter-alert
  loop.
- It may become useful if Signal Scout later adds:
  - AI-assisted source classification
  - summarisation of notices
  - multi-stage enrichment for sparse non-AuctionsPlus sources

## What Is Lower Relevance Right Now

These ideas are sound in their original context but are not first-order needs
for the current beta:

- Claude Code Routines
- newsletter-style digest assembly
- schema-validated LLM triage stages
- Gmail MCP and other interactive MCP-heavy workflows
- no-code orchestration comparisons

Signal Scout is currently a **listing-monitoring runtime**, not a newsletter or
editorial pipeline.

## Suggested Working Rule for Future Source Expansion

Before building any new source module, classify the source into one of these
paths:

| Path | Preferred tool | When to use |
|---|---|---|
| Authorised email/feed | mailbox or feed ingestion | source cooperates or already distributes notices |
| Plain HTML | `requests` + `BeautifulSoup` | fields are present in static HTML |
| JS-rendered public page | Playwright | content requires browser execution |
| Structured API/data feed | API client | official feed exists |
| Hard-blocked or brittle source | defer or seek permissioned pathway | avoid fragile scraping by default |

This keeps Signal Scout aligned with its current principle:
**permission-first, cheapest reliable ingestion path first**.

## Recommended Use of This Research Inside Signal Scout

Use this document when:

- prioritising Phase 2 source expansion
- deciding whether to scrape or ingest via authorised channels
- evaluating whether a candidate source needs Playwright
- designing a new source module type

Do not use this document to justify refactoring the live AuctionsPlus scraper
away from static HTML while the current approach remains reliable.

## Concrete Next Sources to Test

This shortlist applies the external research review to the existing
`references/operations/source-register.md`.

The emphasis is:

- safest authorised or low-friction prototypes first;
- at least one test in each useful ingestion shape;
- no scrape work on `RED` sources before permission.

### Test now

| Order | Source | Source register status | Why it makes the cut now | Recommended test shape |
|---|---|---|---|---|
| 1 | Nutrien Ag Solutions alerts | `prototype` | Best current authorised-ingestion candidate; aligns with the review's email-first rule | create dedicated mailbox, subscribe legitimately, capture first real samples, then test email/body/attachment normalisation |
| 2 | Farrell McCrohon sale-entry PDFs | `prototype` | Best proof that physical-sale PDF entries can be normalised without platform scraping | collect 3-5 sample PDFs and run a parser spike that extracts sale date, classes, counts, and contact details |
| 3 | Stockplace Marketing | `prototype` | Strongest direct HTML listing parser candidate; cleanest test of a true cattle-listing source beyond AuctionsPlus | public-page parser spike to JSON only, no Sheet writes |
| 4 | RMA Network | `prototype` | Best network-card aggregator test; gives broad discovery value across multiple agencies | index-page parser spike with section-aware normalisation and dedup |
| 5 | Sullivan Livestock & Rural Services | `prototype` | Best sale-notice parser test; useful where lot-level detail is incomplete but pre-sale buyer signal exists | sale-notice parser spike producing `WATCHING`-grade records only |
| 6 | Elders sale-date PDFs | `prototype` | High-value national network with a semi-structured document path that may scale if the template is consistent | capture 3-5 sample PDFs and test schedule/date extraction before any broader branch parser work |

### Outreach first, do not test-scrape yet

| Source | Why it is not in the immediate test shortlist |
|---|---|
| The Herd Online | `RED` in the register; permission or partnership comes before any scraper work |
| On The Box / Up For Bids | priority is real, but the source register still frames this as outreach-first rather than safe internal parser testing |
| StockLive | strategically important, but still permission-led in the register |
| Cattlesales | same reason; important platform, but not the safest next test |
| Agora Livestock | `RED`; partnership only |

### Parallel platform lane for the next 2 weeks

If the goal is to give two beta users more than AuctionsPlus alone, keep the
safe parser shortlist above, but run a parallel platform lane in outreach and
approval terms:

| Order | Source | Why it belongs in the near-term lane |
|---|---|---|
| 1 | StockLive | Highest-value permission-led platform add after AuctionsPlus because it broadens online and saleyard-adjacent coverage |
| 2 | On The Box / Up For Bids | Strong strategic platform if permission posture becomes workable |
| 3 | Cattlesales | Useful classifieds-style coverage if sanctioned access is available |

This lane is deliberately separate from parser-first implementation work:

- use it to prepare permission asks, contact paths, and approved ingestion
  shapes;
- do not treat it as a green light to scrape first;
- keep near-term code work focused on authorised email intake and parser-first
  sources that can produce beta-safe inventory sooner.

### Practical coverage this shortlist gives us

This set deliberately tests five different ingestion shapes:

| Shape | Source |
|---|---|
| authorised email intake | Nutrien alerts |
| PDF sale-entry parsing | Farrell McCrohon |
| direct HTML listing parser | Stockplace |
| agency-network sales aggregator | RMA |
| sale-notice / schedule parser | Sullivan |
| repeatable national PDF schedule parser | Elders sale-date PDFs |

### Recommended execution order

1. Nutrien Ag Solutions alerts
2. Farrell McCrohon sale-entry PDFs
3. Stockplace Marketing
4. RMA Network
5. Sullivan Livestock & Rural Services
6. Elders sale-date PDFs

Reasoning:

- Start with the most permission-safe and operationally cheap tests.
- Prove non-platform ingestion before adding more public-page parser surface.
- Test one clean direct-listing HTML source before broader, noisier aggregators.
- Keep `RED` platforms out of the test queue until permission status changes.
