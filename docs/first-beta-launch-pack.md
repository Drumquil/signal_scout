# Signal Scout Beta Launch Pack

## Purpose

This is the operator runbook for the first trusted tester and the first small
beta cohort after that.

Use this document together with:

1. `docs/beta-user-guide.md`
2. `docs/beta-feedback-process.md`
3. `docs/prelaunch-checklist.md`

This pack exists to keep the first `TEST_MODE` switch controlled and reversible,
then help scale to a supervised cohort of 3-5 testers without losing
discipline.

## First Tester Profile

Choose one person only.

Preferred traits:

- personally known to Tom
- likely to reply plainly rather than politely
- relevant to current AuctionsPlus coverage
- comfortable using WhatsApp
- willing to inspect real lots during the first 7-10 days

Avoid as the first tester:

- anyone expecting polished paid-product behaviour
- anyone needing multiple buying profiles immediately
- anyone who is hard to reach during the first live alert cycle

## Cohort Shape After The First Tester

Only expand after the first tester pass is understandable and controlled.

Recommended cohort size:

- 3-5 active testers total

Recommended mix:

- 1 commercial-focused buyer
- 1 breeding-heifer or breeding-cow buyer
- 1 broader restocker brief
- optional 1-2 additional testers only if Tom can still supervise feedback and
  delivery personally

Avoid:

- onboarding all 5 at once on the same day
- mixing in people who expect polished paid-product support
- letting delivery uncertainty stack up across multiple testers before it is
  understood

## Launch Pack Contents

Each tester should receive:

1. the short outreach message
2. the live Google Form link
3. the beta guide
4. the note that feedback will happen by direct WhatsApp reply with Tom

Internally, Tom should have ready:

1. this launch pack
2. each tester's submitted form response
3. a manual feedback log or tracker
4. the exact checklist below for the `TEST_MODE` flip and cohort rollout
5. a clear Twilio decision: Sandbox-supervised or upgraded sender path

## Paste-Ready Outreach Message

Send this before the tester fills the form:

```text
Hi [Name] - I'm running a very small beta of Signal Scout, a tool that watches cattle sale listings and sends a WhatsApp alert when a lot looks like it may match a buyer's brief.

It is still an early beta, so I'm starting with a small group of trusted people who will tell me plainly when something is useful, confusing, or wrong.

If you're happy to help, I'll send a short form so I can set up your buying criteria, then you'll receive alerts and reply with quick feedback when something comes through.

No pressure if now is not a good time.
```

## Paste-Ready Onboarding Message

Send this immediately after the tester agrees:

```text
Thanks - here is the short setup form:
[insert live form link]

Once you've filled it in, I'll load your criteria and send you a short guide so you know what the alerts mean.

For this beta pass, the most helpful feedback is simple:
- relevant / not relevant
- what looked right or wrong
- whether it made you inspect, attend, bid, or buy
```

## Paste-Ready Launch-Day Message

Send this after the form has been transformed into config and before live sends
start:

```text
You're now set up in the Signal Scout beta.

You'll receive WhatsApp messages when a lot appears to match the buying brief you submitted.

`WATCHING` means an early heads-up.
`ALERT` means the lot passed the current checks using the information available at the time.

Please treat each message as a prompt to inspect the source listing, not as a recommendation to buy.

If something looks useful, confusing, wrong, or if messages seem to stop arriving, just reply directly here.
That feedback is part of the beta.
```

## Twilio Decision Before Real Tester Rollout

Make this decision explicitly before activating any external tester.

### Option A - stay on Twilio Sandbox briefly

Use this only for a tightly supervised first pass.

Requirements:

- tester has joined the Sandbox successfully
- tester has received a confirmation message
- tester understands to tell Tom immediately if messages stop
- Tom is available to monitor delivery closely
- no more than 1-2 testers are live on the Sandbox at once unless delivery is
  already proving stable

Risks:

- tester must join the Sandbox correctly
- Sandbox sessions expire and may need rejoin
- outbound messaging rules are more restrictive
- this is not a production-grade experience

### Option B - upgrade Twilio and register a proper WhatsApp sender

This is the recommended path before a 3-5 tester cohort if budget and setup
timing allow.

Benefits:

- lower onboarding friction
- cleaner sender experience
- less risk that beta users think the product is broken when the issue is
  actually Sandbox state
- better base for repeatable testing and later paid rollout

Recommendation:

- first tester can be done on Sandbox only if supervised closely
- upgrade before expanding to 3-5 testers unless the Sandbox pass is proving
  clearly reliable in practice

## Operator Checklist Before `TEST_MODE = False`

Do not switch live sending on until every item below is true.

### Tester and channel readiness

- first tester has explicitly agreed to participate
- tester has submitted the live Google Form
- tester's WhatsApp number is confirmed in the form response
- tester can receive WhatsApp messages through the chosen Twilio path
- tester has received the beta guide and launch-day message
- tester knows to reply directly if messages stop arriving

### Twilio and delivery readiness

- Twilio path decision is explicit: Sandbox or upgraded sender
- if Sandbox is being used, the tester has joined successfully and a live test
  message has been confirmed
- if an upgraded sender is being used, sender setup and destination reachability
  are confirmed
- delivery status visibility is available in Twilio Console at minimum
- message failure handling is decided before go-live
  if a message fails, Tom checks status immediately and follows up with the
  tester directly

### Runtime and config readiness

- latest `TEST_MODE` run completed without unexpected write or matching issues
- `python -m unittest test_transform_form_response_contract.py` passes locally
- tester form response has been transformed into config successfully
- tester submission has been previewed first with
  `python transform_form_response.py --row <n> --dry-run`
- tester config rows look correct in Sheets
- only intended beta tester profiles are active; dummy/self-test profiles stay
  inactive unless deliberately re-enabled for validation
- no known trust-breaking bug is unresolved

### Immediate Post-Form `TEST_MODE` Run

Use this immediately after a tester submits the form, before waiting for the
next scheduled GitHub Actions run:

1. Preferred preview shortcut:
   `python run_post_form_check.py --row <n>`
2. Or preview the new response manually:
   `python transform_form_response.py --row <n> --dry-run`
3. If the preview matches the tester brief, write the config:
   `python transform_form_response.py --row <n>`
4. Preferred safe scrape shortcut after the config write:
   `python run_post_form_check.py --row <n> --run-scout --target-user-id <user_id>`
5. Or run one supervised local scrape in safe mode:

```powershell
$env:TEST_MODE = "TRUE"
$env:MAX_PAGES = "5"
$env:SCRAPE_WORKERS = "4"
$env:REQUEST_DELAY = "1"
$env:LISTING_CACHE_TTL_SECONDS = "10800"
$env:TARGET_USER_ID = "<user_id>"
python .\cattle_scout.py
```

If running from GitHub instead, use **Actions > Signal Scout > Run workflow**
with `test_mode=TRUE`, `max_pages=5`, `scrape_workers=4`, and
`request_delay=1`, then set `target_user_id` to the new tester's `user_id`.
Treat `test_mode=FALSE` as a separate deliberate go-live decision.

### Operator readiness

- Tom is available to monitor the first live alert cycle
- direct WhatsApp feedback channel is active
- manual feedback log destination has been prepared
- tester tracker exists with invitation, config, delivery, and feedback status
- rollback decision is clear: switch `TEST_MODE` back to `True` immediately if a
  trust-breaking issue appears

## Exact `TEST_MODE` Flip Sequence

Use this order on the intentional go-live run:

1. Confirm the checklist above is fully true.
2. Confirm the tester has already received the guide and knows replies should go
   directly to Tom.
3. Switch `TEST_MODE` to `False`.
4. Run the live runtime intentionally for the first tester window.
5. Watch the first send closely.
6. Log the first meaningful outcome in the feedback notes.
7. If a trust-breaking issue appears, switch `TEST_MODE` back to `True` before
   the next run.

## Cohort Rollout Sequence For 3-5 Testers

Do not activate a full cohort in one jump.

Use this order:

1. onboard and supervise tester 1
2. confirm first delivery path is understandable
3. confirm at least one meaningful alert cycle is observed cleanly
4. activate tester 2
5. activate tester 3 only after testers 1 and 2 are stable enough to support
   more load on Tom's attention
6. add testers 4 and 5 only if delivery, feedback handling, and config updates
   still feel controlled

Recommended pace:

- no more than 1 new tester per day
- ideally 2-3 days between tester 1 and tester 3 unless everything is very
  stable

## Cohort Checklist For Each New Tester

Use this checklist every time:

- tester agreed explicitly
- form submitted
- response previewed with `--dry-run`
- config rows written correctly
- WhatsApp delivery confirmed
- beta guide sent
- launch-day message sent
- first follow-up reminder scheduled
- tester added to the operator tracker
- rollback path clear if their experience degrades trust

## Common Failure Points To Watch

These are the issues most likely to make beta feel rough:

- tester never completes the form
- form answer is valid but writes an unintended config shape
- WhatsApp message path is not actually confirmed before live use
- tester receives no alerts and assumes the product is inactive
- tester receives off-target alerts and does not say so
- Tom changes config without logging it, then loses track of why behaviour
  changed
- too many testers are live before delivery behaviour is understood

## Minimum Operator Tracker Fields

Track at least:

- tester name
- phone number
- invitation date
- agreed yes/no
- form submitted yes/no
- config previewed yes/no
- config written yes/no
- WhatsApp confirmed yes/no
- guide sent yes/no
- live yes/no
- first alert seen yes/no
- feedback received yes/no
- current risk or blocker

## First 24-Hour Follow-Up Script

Send after the first real alert or, if no alert arrives yet, after the first day
live:

```text
Quick beta check-in:

Was setup clear?
If you've seen any alerts yet, did they feel relevant?
Was anything confusing, obviously off, or missing?

Even a short reply is useful.
```

## First Sale-Cycle Follow-Up Script

Send after the tester has had a real chance to inspect sale listings:

```text
Quick follow-up on the beta alerts:

Did any alert make you inspect a lot?
Did any feel off-target?
Was there anything you wished the alert told you before you clicked through?
Did any alert affect whether you attended, bid, or bought?
```

## Reliability Follow-Up Script

Send if delivery confidence is uncertain:

```text
Quick check:

Have alerts been coming through consistently on WhatsApp?
If anything has been delayed, missing, or confusing, let me know directly.
```

## What Is Still Missing Before The First Intentional Live Send

As of 20 June 2026, these items still need to be true in practice before the
first trusted tester run:

- first tester chosen and confirmed
- live form submitted by that tester
- tester successfully reachable in the chosen WhatsApp path
- manual feedback log started
- Tom ready to supervise the first live cycle
- deliberate moment chosen for the `TEST_MODE` flip

The dedicated authorised-source mailbox is not required for this first tester
launch.

## Success Condition For This Pack

This pack has done its job when:

- the tester is onboarded without confusion
- the first live send is deliberate and monitored
- feedback is captured in the first alert cycle
- the repo has evidence about what to tighten before and during the first 3-5
  tester cohort
