# Signal Scout Twilio Status Callback Implementation Plan

## Purpose

This plan turns WhatsApp delivery from a black box into an observable beta
workflow.

The goal is to answer three operational questions clearly:

1. was a message created successfully by Signal Scout?
2. did Twilio actually send and deliver it?
3. if a tester says "nothing came through", is that a matching problem, a send
   problem, or a delivery problem?

## Current Runtime Position

As of 20 June 2026:

- `cattle_scout.py` sends WhatsApp messages in two places:
  `send_watching_alert()` and `send_alert()`
- both call `client.messages.create(...)`
- neither passes `status_callback=...`
- neither stores the returned `MessageSid`
- the current Google Sheets contract has no dedicated message-dispatch or
  message-status tab

That means Signal Scout can say "send attempted" but cannot currently prove
delivery cleanly per tester.

## Recommended Beta-Phase Design

Keep this simple and additive.

Add three operational pieces:

1. one manual tracker tab for tester state
2. one append-only dispatch tab written by the runtime immediately after
   `messages.create(...)`
3. one append-only status-event tab written by a Twilio webhook endpoint

This gives you:

- manual visibility of who should be live
- a record that Signal Scout asked Twilio to send a specific message
- a separate record of what Twilio later reported happened

## Recommended Google Sheets Tabs

### 1. `beta_operator_tracker`

Purpose:

- manual operator control surface for the 3-5 tester cohort

Starter template:

- import `docs/beta_operator_tracker_template.csv` into a new tab named
  `beta_operator_tracker`

### 2. `twilio_message_dispatch`

Purpose:

- one row per outbound WhatsApp message created by Signal Scout

Recommended columns:

| Col | Header | Meaning |
|---|---|---|
| A | `message_sid` | Twilio `MessageSid` returned by `messages.create()` |
| B | `user_id` | Signal Scout config user |
| C | `twilio_to` | recipient WhatsApp destination |
| D | `alert_kind` | `WATCHING` or `ALERT` |
| E | `listing_url` | listing URL tied to the alert |
| F | `listing_title` | listing title |
| G | `run_timestamp` | local runtime timestamp |
| H | `twilio_initial_status` | status on create response if present |
| I | `test_mode` | `TRUE`/`FALSE` |
| J | `message_preview` | short first-line preview for human inspection |
| K | `error_code` | local send exception code if available |
| L | `error_message` | local send exception message if available |

### 3. `twilio_message_status`

Purpose:

- append-only Twilio callback event log

Recommended columns:

| Col | Header | Meaning |
|---|---|---|
| A | `logged_at` | when the webhook wrote the row |
| B | `message_sid` | Twilio `MessageSid` |
| C | `message_status` | `queued`, `sent`, `delivered`, `read`, `failed`, etc. |
| D | `to` | destination number |
| E | `from` | sender number |
| F | `channel` | `whatsapp` if derivable |
| G | `error_code` | Twilio error code if present |
| H | `error_message` | Twilio error message if present |
| I | `raw_payload_json` | raw callback payload serialized as JSON |
| J | `source_ip` | optional request source IP |

## Minimal Architecture

### Runtime side

`cattle_scout.py` should:

1. send the message
2. capture the returned `message.sid`
3. append one row to `twilio_message_dispatch`
4. print the SID locally for operator visibility

### Webhook side

A very small FastAPI service should:

1. receive Twilio status callbacks at `/twilio/status-callback`
2. validate the Twilio request signature
3. append the callback event to `twilio_message_status`
4. return `200 OK` quickly

### Operator side

Tom should:

1. use `beta_operator_tracker` to know who is meant to be live
2. use `twilio_message_dispatch` to confirm Signal Scout created the message
3. use `twilio_message_status` to confirm whether Twilio delivered it

## Concrete Runtime Changes

## Step 1 - add environment variables

Add these optional environment variables:

```text
TWILIO_STATUS_CALLBACK_URL=
TWILIO_STATUS_CALLBACK_ENABLED=FALSE
```

Notes:

- signature validation uses the existing `TWILIO_AUTH_TOKEN`
- keep callbacks optional so local work is not blocked before deployment

## Step 2 - centralize outbound send logic

Refactor both `send_watching_alert()` and `send_alert()` to use one helper,
for example:

```python
send_whatsapp_message(
    *,
    body,
    twilio_to,
    user_id,
    alert_kind,
    listing_url,
    listing_title,
)
```

That helper should:

1. create the Twilio client
2. build `messages.create(...)`
3. include `status_callback=TWILIO_STATUS_CALLBACK_URL` when enabled
4. capture the returned message object
5. append a dispatch row with `message.sid`
6. return the message SID or `None`

## Step 3 - pass user context into send functions

Current send functions only receive `listing` and `twilio_to`.

Update them to also receive:

- `user_id`
- `alert_kind`

This keeps the dispatch row attributable to the correct tester.

## Step 4 - append dispatch rows

Add a helper in `cattle_scout.py`, for example:

```python
def log_twilio_dispatch(worksheet, row):
    worksheet.append_row(row, value_input_option="RAW", table_range="A1")
```

Use the same `table_range="A1"` discipline already used elsewhere in the
project.

## Concrete Webhook Service Plan

## Recommended file

Add a small standalone file such as:

`twilio_status_webhook.py`

Why standalone:

- keeps webhook concerns separate from the scrape runtime
- easier to host independently
- easier to test with one endpoint and one responsibility

## Recommended stack

- FastAPI
- Uvicorn
- `twilio.request_validator.RequestValidator`
- `gspread`
- existing Google service account credentials

## Endpoint contract

### `POST /twilio/status-callback`

Expected behavior:

1. read form-encoded Twilio payload
2. validate `X-Twilio-Signature`
3. extract key fields
4. append event row to `twilio_message_status`
5. return plain `200 OK`

## Fields to capture from Twilio callback

At minimum:

- `MessageSid`
- `MessageStatus`
- `To`
- `From`
- `ErrorCode`
- `ErrorMessage`

Capture the full payload too so future debugging does not depend on a narrow
field list.

## Recommended deployment pattern

Use a tiny hosted endpoint on:

- Render
- Railway
- or another always-on small web host

Requirements:

- public HTTPS URL
- environment variables for Google creds path and Twilio auth token
- low-latency response

Do not host the callback inside a machine or process that only runs during the
scheduled scrape.

Twilio needs a stable public endpoint.

## Recommended implementation sequence

### Phase 1 - observability only

Goal:

- prove delivery visibility before adding any automation beyond logging

Work:

1. create `beta_operator_tracker`
2. add `twilio_message_dispatch`
3. add `twilio_message_status`
4. deploy webhook
5. wire `status_callback` into send helper
6. run one controlled real send

Success looks like:

- one dispatch row appears when a message is created
- later status rows appear for the same `message_sid`

### Phase 2 - operator workflow

Goal:

- make delivery issues visible without manual console checking

Work:

1. add simple filtered views in Sheets
2. highlight failed statuses
3. add a column in `beta_operator_tracker` for `delivery_health`
4. update the operator runbook to check callback logs daily

### Phase 3 - automation

Goal:

- reduce manual chasing

Work:

1. mark failed deliveries automatically in a tracker field or companion sheet
2. trigger follow-up reminders when:
   no WhatsApp confirmation exists
   first alert was sent but no feedback was logged
   repeated failures appear for one tester

## Recommended Sheet Views

In `beta_operator_tracker`:

- `Invited not submitted`
- `Config ready not live`
- `Live no first alert`
- `Live no feedback`
- `Blocked or delivery risk`

In `twilio_message_status`:

- `Failed`
- `Delivered`
- `Read`
- `No final status yet`

## Testing Plan

### Local code checks

1. unit-test the helper that builds dispatch rows
2. unit-test callback payload parsing
3. unit-test signature validation behavior with a mocked validator

### Manual beta checks

1. send one test WhatsApp message to Tom
2. confirm a dispatch row is written
3. confirm callback rows arrive
4. confirm the same `message_sid` appears in both places
5. confirm a tester tracker row can now be audited against actual delivery data

## Failure Modes To Expect

Plan for these explicitly:

- Twilio message created but callback never arrives
  likely webhook URL, hosting, or signature issue
- callback arrives but cannot be linked to tester context
  dispatch row is missing or `message_sid` was not stored
- tester says "nothing came through" but callback says delivered
  likely user-side thread, mute, or Sandbox confusion
- message creation fails before SID exists
  log local exception to dispatch sheet with blank SID

## Recommended Definition Of Done

This plan is complete enough for beta when:

- every outbound WhatsApp message gets a dispatch row
- every Twilio callback gets a status row
- failed deliveries are visible within minutes
- Tom can answer "what happened to this tester's alert?" without guessing

## Immediate Next Build Order

If you want to implement this incrementally, do it in this order:

1. import `docs/beta_operator_tracker_template.csv` into Google Sheets
2. add `twilio_message_dispatch` and `twilio_message_status` tabs
3. refactor `cattle_scout.py` send logic into one helper
4. store `message.sid` to the dispatch tab
5. deploy the webhook
6. wire `status_callback`
7. test one real supervised send
