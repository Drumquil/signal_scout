# Signal Scout - Next Chat Handover

## Purpose

This handover is the current best starting point for the next Codex chat.

It captures what was completed in this session, what remains open, and what the next chat should do first without needing to reconstruct context from scratch.

The central outcome of this session is:

- Signal Scout now has a much stronger source-research base for multi-source expansion.
- The likely parser candidates and permission/outreach targets are now documented and ranked.
- The next engineering question is no longer "what sources exist?" but "how do we refactor ingestion safely before multi-source expansion makes the current runtime too slow?"

## Repo

Work in this repository:

`C:\Users\Drumquil\Documents\Codex\Drumquil Signal\Signal Scout`

## Current Product State

Signal Scout is still in beta-stabilisation mode.

The production runtime is still essentially:

- `cattle_scout.py`
- Google Sheets data layer
- Twilio WhatsApp alerts
- GitHub Actions schedule

AuctionsPlus remains the only active source in the runtime.

`TEST_MODE` remains `True`.

The first real beta tester is still not onboarded end-to-end.

## What This Session Added

### 1. Source research docs

The repo now contains a much broader source-intelligence set in `references/`, including:

- platform terms review
- agent website / newsletter review
- source register
- permission / outreach queue
- outreach log
- permission email drafts
- parser feasibility shortlist
- parser field coverage map
- parser specs for the top three parser candidates

### 2. National / regional source mapping

This session expanded and refined the source picture beyond the original shortlist.

Important source families now covered in the docs:

- major online platforms: `AuctionsPlus`, `StockLive`, `Up For Bids`, `Cattlesales`, `The Herd`, `FarmGate`, `Agora`, `Farm Tender`, `LocalAg`
- exchange/network layers: `RLX`, `Southern Livestock Exchange`, `RMA`
- major agency chains and networks: `Nutrien`, `Elders`, `AWN`, `GDL`, `Ray White Rural & Livestock`
- regional independents: `Stockplace`, `Sullivan`, `Forbes`, `KMWL`, `JJ Dresser`, `Farrell McCrohon`, `Donovan`, `Ian Weir`
- collectives / SA-heavy layers: `CIAA`, `SAL`, `Quality Livestock`

### 3. Legal / permission posture

The docs now clearly split sources into:

- `RED - agreement required`
- `AMBER - permission-first`
- `GREEN - authorised feed path`

Important current conclusions:

- `The Herd Online` should not be scraped without permission.
- `Agora Livestock` and `Farm Tender` are also effectively permission-only.
- many agent sites are more viable, especially when approached as email/PDF/feed relationships rather than silent scraping.

### 4. Outreach groundwork

The repo now includes a working outreach queue and first-pass permission drafts for:

- `The Herd Online`
- `Up For Bids`
- `StockLive`
- `Cattlesales`
- `Elders`
- `Nutrien`
- `Farrell McCrohon`
- `Donovan`
- `Ian Weir & Son`

These are documented in:

- `references/operations/permission-outreach-list.md`
- `references/operations/outreach-log.md`
- `references/operations/permission-email-drafts.md`

### 5. Parser planning

A focused second-pass was completed on the newly confirmed agency/network candidates.

The result:

- `Parser-first`: `Stockplace`, `Sullivan`, `RMA`, then `GDL`, `CIAA`, `Quality`
- `Hybrid`: `AWN`, `Forbes`, `JJ Dresser`
- `Outreach/newsletter-first`: `KMWL`, `Ray White Rural & Livestock`, `SAL`, `Rodwells`

These conclusions are now written into:

- `references/agents/cattle-agent-websites-and-newsletters.md`
- `references/operations/source-register.md`
- `references/operations/parser-feasibility-shortlist.md`
- `references/operations/parser-feasibility-field-map.md`

### 6. Top-three parser specs

Detailed first-draft parser specs were written for:

- `Stockplace`
- `Sullivan`
- `RMA`

These specs include:

- sample URLs
- parser goals
- page patterns
- extraction rules
- skip/filter logic
- normalised output contract
- mapping to the current `cattle_scout_listings` schema
- acceptance criteria for parser spikes

Primary spec file:

- `references/operations/parser-specs-top-three.md`

## Most Important New Technical Finding

The current runtime will become too slow if multi-source expansion is added on top of the current loop structure.

The reason is not only the 3-second request delay.

The deeper issue is that `cattle_scout.py` currently scrapes listings inside the per-user loop. That means the same listing pages get fetched once for each active user.

Current pattern in `cattle_scout.py`:

- discover listing URLs once
- for each user:
  - for each URL:
    - fetch and parse the listing again
    - sleep again
    - evaluate filters for that user

This is acceptable for one source and one user during beta validation.
It is not a good long-term structure for:

- 2+ active users
- 2+ sources
- source growth
- more frequent schedules

## Recommendation Agreed This Session

Do **not** jump straight into full-blown infra.

Do **not** leave the current loop unchanged until after multi-source rollout.

The right path is staged:

### Near-term recommendation

Before real multi-user + multi-source expansion:

1. scrape each source once per run
2. normalise listings once per run
3. evaluate all users against the shared normalised listing set

### Long-term recommendation

Build toward:

1. source modules
2. separate ingestion from user matching
3. bounded concurrency per source
4. a small persistent local store such as SQLite
5. alerting against stored normalised records rather than live re-fetching for each user

This was judged the best long-term solution because it is:

- efficient
- low-regret
- legally safer than aggressive parallel scraping
- much cheaper than overbuilding cloud infrastructure too early

## Do We Need To Update `cattle_scout.py` Now?

Not immediately for the research/docs work.

But the next serious engineering pass should probably be a refactor spec and then a narrow refactor of `cattle_scout.py` before real multi-source rollout begins.

That refactor should happen **before**:

- multiple real beta users are active at once, and/or
- the first non-AuctionsPlus source is wired into the runtime

## Recommended Next Chat Task

The next chat should focus on the ingestion refactor plan, not on adding a new source yet.

Best next task:

Create a concrete refactor spec for `cattle_scout.py` that:

1. preserves the current AuctionsPlus beta path
2. removes duplicate per-user re-scraping
3. introduces a shared per-run normalised listing set
4. defines the smallest source-abstraction boundary that can support future source modules
5. stays simple enough to implement without destabilising beta

## Specific Next Steps For The Next Chat

Recommended sequence:

1. Read:
   - `AGENTS.md`
   - `HANDOVER.md`
   - `NEXT_CHAT_HANDOVER.md`
   - `docs/status.md`
   - `docs/schema.md`
   - `docs/strategy.md`
   - `cattle_scout.py`
   - `references/operations/source-register.md`
   - `references/operations/parser-specs-top-three.md`

2. Review the current scraping and matching loop in `cattle_scout.py`.

3. Produce a written refactor spec for:
   - scrape once, match many users
   - source module boundary
   - normalized intermediate listing object
   - compatibility with current Google Sheets tabs

4. Only after the refactor spec is sound:
   - decide whether to implement the runtime refactor next, or
   - prototype one parser spike outside the live runtime

## Suggested Implementation Order After The Refactor Spec

1. Runtime refactor:
   - scrape once per run
   - match all users against shared listings
   - add `requests.Session()` per source

2. Parser spike:
   - `Stockplace` first

3. Parser spike:
   - `RMA` second

4. Parser spike:
   - `Sullivan` third

5. Then decide whether to extend Sheets schema or add a staging layer first

## Files Added Or Updated This Session

Main files touched in this session:

- `references/platforms/australian-cattle-listing-sites-terms-review.md`
- `references/agents/cattle-agent-websites-and-newsletters.md`
- `references/operations/source-register.md`
- `references/operations/permission-outreach-list.md`
- `references/operations/outreach-log.md`
- `references/operations/permission-email-drafts.md`
- `references/operations/parser-feasibility-shortlist.md`
- `references/operations/parser-feasibility-field-map.md`
- `references/operations/parser-specs-top-three.md`
- `references/README.md`
- `NEXT_CHAT_HANDOVER.md`

## Worktree Notes

There are unrelated pre-existing local changes/untracked files in the worktree.

Do not revert them unless explicitly asked.

Known examples include:

- `.gitignore` modified
- `Cattle_Scout_Schema_Reference_v2_3.md` untracked
- `drumquil_signal_brief.md` untracked
- `references/` currently untracked as a folder

## Plain-English Summary For The Next Chat

Signal Scout now has enough source research and parser planning to stop guessing.

The next chat should not spend its energy finding more websites first.
It should turn the current single-source runtime into a structure that can safely handle future sources and multiple users without multiplying scrape time.

The core question for the next chat is:

"How do we refactor `cattle_scout.py` so Signal Scout scrapes once, normalises once, and matches many users and many future sources cleanly?"
