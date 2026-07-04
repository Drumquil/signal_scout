# Signal Scout Beta Sequence

## Purpose

This is the concrete pre-launch sequence for Signal Scout.

The goal is to:

1. validate real user value before source outreach
2. tighten the product with live beta feedback
3. reach a credible, professional demo state before approaching target sources
4. use source outreach only after there is evidence that buyers actually care

## Sequence

### Phase 0 - Internal Validation Wrap-Up

Use the current live test profile set to keep pressure on runtime behaviour
before onboarding anyone external.

Required outcomes:

- `TEST_MODE` runtime stays stable with the current active test profiles
- form -> transform -> config -> runtime path is still working end to end
- commercial / breeding-heifer / breeding-cow / CAF behaviour remains correct
- beta guide and feedback process are prepared before any external tester sees
  the product
- the first-tester launch pack exists and is ready to use

Do not wait for a polished external platform here.
This is the last internal tightening pass.

### Phase 1 - First Trusted Beta Tester

Onboard one trusted producer contact first, not a broad group.

Recommended profile of first tester:

- someone known personally
- tolerant of rough edges
- willing to reply with concrete feedback
- buying behaviour relevant to the current source coverage

Required actions:

1. tester submits the live Google Form
2. form response is transformed into config
3. tester receives the beta guide before live sends begin
4. tester is added to the feedback channel
5. live sends start intentionally by switching `TEST_MODE` to `False`

Exact operating doc for this phase:

- use `docs/first-beta-launch-pack.md`

Success criteria:

- onboarding works without manual confusion
- tester understands what alerts mean
- at least one real alert cycle is observed with feedback captured

### Phase 2 - Narrow Live Beta

Expand to 2-3 real testers only after the first tester pass is understandable
and controlled.

Focus:

- alert relevance
- false positives
- missed opportunities
- onboarding friction
- trust / clarity of wording

Track manually:

- did the user read the alert?
- did the alert cause them to inspect the lot?
- did they attend, bid, or buy?
- did they think the alert was relevant?
- what was confusing or missing?

Do not start source-permission outreach yet.
This phase is about proving buyer-side value.

### Phase 3 - Tighten for Demo Readiness

After 2-3 testers and real feedback, use the learning to tighten the product
into a professional demo state.

"Demo-ready" does not mean feature-complete.
It means:

- onboarding is coherent
- alert language is clear
- criteria behaviour is defensible
- the tool looks disciplined and trustworthy
- screenshots / live walkthrough do not feel improvised

Required outputs:

- updated beta guide
- cleaned-up current-state notes
- a short demo flow:
  form -> config -> match -> WhatsApp alert -> user interpretation

### Phase 4 - Source Outreach Preparation

Only after demo-readiness is reached should external source outreach become a
priority.

What should exist before outreach:

- screenshots or a live demo flow
- real beta evidence from trusted users
- clear "facts-only, link-back" positioning
- clarity on what the tool stores and does not store
- a shortlist of specific source asks by source type

### Phase 5 - Source Permission Outreach

Start with the sources most relevant to the current beta region and authorised
channel strategy.

Recommended first outreach wave:

1. Nutrien Ag Solutions
2. Elders
3. Farrell McCrohon
4. Donovan Livestock & Property
5. Ian Weir & Son

The goal is not "partnerships as growth."
The goal is:

- permission or comfort for email/PDF intake
- a better notice pathway than scraping
- credibility and trust

## Decision Gates

### Gate A - move from Phase 0 to Phase 1

All of these should be true:

- beta guide exists
- feedback process exists
- first-tester launch pack exists
- current runtime behaviour is stable in `TEST_MODE`
- first tester has been chosen

### Gate B - move from Phase 1 to Phase 2

All of these should be true:

- first tester onboarding succeeded
- first tester understood what the product does
- at least one real alert cycle has been observed
- no serious trust-breaking bug is unresolved

### Gate C - move from Phase 2 to Phase 3

All of these should be true:

- at least 2 real testers have given feedback
- repeated confusion points are known
- alert relevance is good enough to keep using
- feedback shows real buyer interest rather than polite curiosity

### Gate D - move from Phase 3 to Phase 4/5

All of these should be true:

- the tool can be demoed cleanly
- the value proposition is understandable in one short explanation
- beta evidence exists
- source outreach ask is specific and professional

## What Not To Do Yet

- do not chase broad source-permission outreach before real beta evidence
- do not wait for a fully polished platform before testing with real users
- do not expand the tester count too fast
- do not treat partnerships as the way to start growth
