# Signal Scout Beta Feedback Process

## Purpose

This defines the working feedback loop for a supervised beta cohort of 3-5 real
testers.

The goal is not to build a complex support system.
The goal is to learn quickly, keep tester experience smooth, and catch issues
before they become trust-breaking.

## Default Feedback Channel

Use direct WhatsApp replies and short follow-up conversations first.

Recommended default:

- primary channel: direct WhatsApp with Tom
- secondary channel: short phone call if a tester has something more detailed
  to explain
- internal record: one concise operator log per tester

Do not add heavy tooling before this simple loop is exercised consistently.

## Feedback Moments

Collect feedback at five moments:

### 1. Agreement and onboarding

Ask after the tester has agreed and received the setup form:

- Was the form clear?
- Was anything hard to answer?
- Did the buying categories make sense?

### 2. Activation and delivery confirmation

Ask after setup is completed and the tester should now be reachable:

- Did the setup explanation make sense?
- Did you receive the onboarding / confirmation message?
- Is WhatsApp the right place for these alerts?

### 3. First alert feedback

Ask after the first real alert or first few alerts:

- Did this feel relevant?
- Was anything obviously wrong?
- Was the message clear enough to act on?
- What was missing?

### 4. Outcome feedback

Ask after a real buying decision or sale event:

- Did the alert make you inspect the lot?
- Did it make you attend, bid, or buy?
- Was the lot actually within your target?
- Would you want more alerts like this or fewer?

### 5. Reliability feedback

Ask whenever delivery appears uncertain:

- Have alerts arrived consistently?
- Did anything come through late or not at all?
- Did any message thread or joining step feel confusing?

## Core Questions To Capture

For each meaningful alert cycle, try to capture:

1. Was the alert relevant?
2. If not, why not?
3. If yes, what made it relevant?
4. Did the user inspect the lot?
5. Did the user attend, bid, or buy?
6. Was anything important missing from the alert?
7. Was any criteria behaviour surprising?
8. Did delivery or timing feel unreliable?

## Minimum Operator Log

Until a dedicated feedback store exists, log feedback manually in concise notes.

Minimum fields:

- tester name
- tester status: invited / agreed / form submitted / activated / live / paused
- date
- listing or alert reference
- feedback type: onboarding / delivery / relevance / missed match / purchase
  outcome / pause request
- short note
- resulting action for product, config, or communication
- owner
- due date if follow-up is required

Suggested note format:

```text
Tester:
Status:
Date:
Listing/alert reference:
Feedback type:
What they said:
Action taken / follow-up:
Owner:
Due:
```

## Operator Workflow

Use this sequence for each tester:

### 1. Invite

- send the outreach message
- record invitation date
- record whether the tester agreed

### 2. Intake

- confirm the tester submitted the live form
- preview their response with `transform_form_response.py --dry-run`
- append the config only after the preview looks correct
- record their config as `ready`

### 3. Channel validation

- confirm they can receive the setup / confirmation WhatsApp message
- if using Twilio Sandbox, confirm they joined correctly and know to report any
  delivery drop
- mark channel status as `confirmed`

### 4. Supervised activation

- move the tester to `live`
- monitor the first meaningful alert cycle
- log any delivery or matching issue immediately

### 5. Follow-up

- send the first check-in within 24 hours of activation or first alert
- send the sale-cycle follow-up after a genuine chance to inspect lots
- record whether the tester is still engaged

### 6. Adjust or pause

- update config if their brief changes
- pause alerts if trust is dropping or delivery is unstable
- reactivate only after the blocker is understood

## Lightweight Automation To Add

These are the first useful automations, in order:

### 1. Delivery-state logging

Use Twilio delivery status callbacks so each outbound message can be recorded as:

- queued
- failed
- sent
- delivered
- read

This is the highest-value automation because it separates matching problems from
delivery problems.

### 2. Tester state tracker

Maintain one simple operator tracker for:

- tester name
- invitation status
- form submitted
- config written
- WhatsApp confirmed
- first alert received
- feedback received
- still active yes/no

Google Sheets is enough for this in beta.

Starter template:

- import `docs/beta_operator_tracker_template.csv` into a tab named
  `beta_operator_tracker`

### 3. Follow-up reminders

Create reminders for:

- no form submission after invitation
- no WhatsApp confirmation after activation
- no first check-in sent within 24 hours
- no feedback recorded after first alert

### 4. Exception flags

Raise an operator flag when:

- a tester reports no messages received
- a message status is failed
- a tester gets repeated off-target alerts
- a tester requests criteria changes

Twilio implementation detail:

- use `docs/twilio-status-callback-implementation-plan.md` as the concrete build
  order for delivery-state logging

## Paste-Ready Follow-Up Prompts

Use these scripts rather than improvising the first pass.

### After onboarding

```text
Quick setup check:

Was the form clear?
Was anything hard to answer?
Did the buying categories make sense?
```

### After activation

```text
Quick delivery check:

You should now be set up for beta alerts.
Did the setup make sense and did this message come through clearly?
```

### After the first alert

```text
Quick alert check:

Did this feel relevant?
Was anything obviously wrong?
Was the message clear enough to act on?
What was missing, if anything?
```

### After a real sale decision

```text
Quick outcome check:

Did this alert make you inspect the lot?
Did it affect whether you attended, bid, or bought?
Was the lot actually within your target?
Would you want more alerts like this or fewer?
```

### If delivery seems uncertain

```text
Quick check:

Have alerts been coming through consistently on WhatsApp?
If anything has been delayed, missing, or confusing, let me know directly.
```

## What Counts As Strong Beta Evidence

Strong evidence is not "they said it sounds good."

Strong evidence looks like:

- a tester changed behaviour because of an alert
- a tester said an alert saved them time
- a tester identified a repeated false-positive pattern
- a tester flagged missing information that clearly matters to buying decisions
- a tester reported delivery was smooth and trustworthy
- a tester wants to keep using the product

## Immediate Fix Triggers

Escalate and fix quickly if a tester reports:

- clearly wrong category matching
- repeated irrelevant alerts
- confusing wording that undermines trust
- onboarding confusion that blocks setup
- missed alerts that should obviously have matched under current logic
- messages not arriving consistently
- a broken Twilio join / reply / delivery path

## Cohort Review Rhythm

Run a short operator review at least twice weekly during the first 3-5 tester
cohort.

Check:

- who is invited
- who is live
- who has not received a first alert yet
- who has not replied yet
- which issues are matching problems
- which issues are delivery problems
- which product changes are now recurring

## Exit Condition For Early Beta

The first narrow beta phase is doing its job when:

- at least 3 real testers have been onboarded cleanly
- at least 2 testers have responded meaningfully
- the main confusion points are known
- the main false-positive patterns are known
- delivery friction is understood
- at least one tester reports genuine value, not just interest
