# Firecrawl Allowed-Use Checklist

## Purpose

This note defines where Firecrawl may help Signal Scout technically, and where
it does not change the project's legal or permission posture.

Use this together with:

- `references/operations/source-register.md`
- `references/operations/ai-content-pipeline-research-review-for-signal-scout.md`
- `docs/strategy.md`

## Bottom Line

Firecrawl can help Signal Scout fetch or extract more data from difficult pages,
especially JavaScript-rendered sources.

It does **not** make a restricted source legally usable by itself.

For Signal Scout, Firecrawl is a technical option only after the source's
permission and terms posture is acceptable for the planned use case.

## What Firecrawl Is Good For

Potentially useful cases:

- JS-rendered sale pages where `requests` + `BeautifulSoup` is insufficient
- noisy public pages where markdown extraction is cleaner than raw HTML
- source-specific prototyping where a richer extractor may save engineering time
- controlled testing of public sources already marked safe enough to prototype

## What Firecrawl Does Not Solve

Firecrawl does not solve:

- lack of permission
- restrictive terms of use
- login walls or paid access rights
- source objections to automated extraction
- the project rule against scraping `RED` sources without written approval

If a source is `RED` or still clearly `AMBER permission-first`, Firecrawl does
not move it into an approved state.

## Signal Scout Allowed Use

Firecrawl is acceptable only when all of the following are true:

1. The source is not `RED` in the register.
2. The intended use remains facts-only and link-back-oriented.
3. The page is public or otherwise authorised for the relevant access path.
4. A simpler method is not clearly better.
5. The source has been reviewed as a real candidate worth testing.

Examples that may be acceptable:

- a future JS-rendered but permission-cleared agent sale page
- a public cattle-sale notice page where parser prototyping is explicitly
  allowed or low-risk
- an approved source where Playwright or Firecrawl is needed to read content

## Signal Scout Not Allowed Use

Do not use Firecrawl for:

- The Herd Online without written approval
- Agora Livestock where the source register remains partnership-only
- any login-gated cattle platform without explicit sanction
- any source where the main reasoning is "the tool can technically get it"

## Decision Order Before Firecrawl

Always prefer the cheapest reliable path first:

1. authorised email or direct notice
2. RSS or Atom feed
3. plain HTML via `requests` + `BeautifulSoup`
4. Playwright for JS-rendered public pages
5. Firecrawl when browser execution or cleaner extraction is still needed

This keeps Firecrawl as a fallback or targeted accelerator, not the default.

## Per-Source Checklist

Before using Firecrawl on any source, answer all of these:

1. What is the source name?
2. What is the current source-register risk level?
3. Is the source public, login-gated, or partner-only?
4. Do we already have a better authorised path, such as email, PDF, or feed?
5. Why did plain HTML parsing fail or become too brittle?
6. Would Playwright be enough without a managed service?
7. What exact facts are we trying to extract?
8. Are we keeping attribution and original link-back?
9. What would make us stop using this source?

If these answers are weak or unclear, do not use Firecrawl yet.

## Recommended Signal Scout Position

Use Firecrawl only when:

- the source is already a realistic candidate under our permission-first model;
- the page shape genuinely needs a heavier extractor;
- the expected value is high enough to justify extra complexity.

For the current beta stage, Firecrawl is more relevant to later source
expansion than to the live AuctionsPlus path.

## Good Repo-Level Rule

Signal Scout should treat Firecrawl as:

- `allowed for approved source-specific prototyping`
- `not approved as a blanket scraping shortcut`

## Suggested Register Notes

When Firecrawl is being considered for a source, add notes such as:

- `JS-rendered candidate; test Playwright before Firecrawl`
- `Firecrawl only if permission is confirmed`
- `managed extractor not justified at current source value`
- `authorised email path preferred over Firecrawl`
