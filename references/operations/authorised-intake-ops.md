# Authorised Intake Ops

## Purpose

This file turns the authorised email/PDF intake direction into a practical
operating checklist for Signal Scout.

Use it when setting up the dedicated Google Workspace mailbox, choosing the
first subscriptions, exporting sample notices, and validating them through the
repo intake workflow.

If Kill the Newsletter is used as the transport path, also follow:

- `references/operations/kill-the-newsletter-intake-workflow.md`

## Revised Intake Setup List

Reviewed again against live official pages on 28 June 2026 and re-cut toward
the sources most relevant to current beta coverage.

Use three buckets:

- `subscribe_now`: a real self-serve email or mailing-list path appears to be
  available now
- `contact_now`: no clean self-serve subscriber path confirmed, but the source
  is still a strong authorised notice or PDF candidate
- `later_not_email_first`: useful source, but not a good first-wave email
  intake target

### Subscribe now

| Rank | Source / channel | Why it matters | Official evidence URL | Mailbox action |
| --- | --- | --- | --- | --- |
| 1 | Nutrien Ag Solutions livestock sales alerts | strongest national opted-in sale-alert path | `https://www.nutrienagsolutions.com.au/livestock/livestock-sales-alert` | subscribe immediately |
| 2 | Ramsey & Bulmer mailing list | strong regional cattle-sales source with explicit mailing-list path for upcoming sales | `https://www.ramseybulmer.com.au/` | subscribe mailbox via mailing-list form |
| 3 | APL Casino Kyogle livestock mailing list | direct livestock-page mailing-list path on a cattle-relevant regional source | `https://www.aplcasino.net.au/livestock` | subscribe mailbox via livestock-page form |
| 4 | Donovan Livestock mailing list - `Livestock Sales` | real regional list signup with livestock-sales-specific interest selection | `https://donovanlivestock.com.au/contact/` | subscribe mailbox and select `Livestock Sales` |
| 5 | Forbes Livestock weekly newsletter | active regional agency newsletter path worth testing for sale and market notices | `https://forbeslivestock.com.au/` | subscribe mailbox via homepage newsletter link |
| 6 | Quality Livestock email subscribe | explicit subscriber hook on a source with stock-for-sale and saleyard structure | `https://qualitylivestock.com.au/` | subscribe mailbox via `Email Subscribe` path |

### Contact now

| Rank | Source / channel | Why it matters | Official source URL | Mailbox action |
| --- | --- | --- | --- | --- |
| 1 | Ian Weir & Son direct sale notices | highly relevant Northern Rivers physical-sale candidate | `https://ianweirandson.com.au/contact/` | ask for direct sale notices or approved feed |
| 2 | APL Tenterfield direct livestock notices | strong regional cattle-sales source, but no clear mailing-list path confirmed | `https://www.apltenterfield.net.au/livestock-for-sale` | ask for direct sale notices or livestock email updates |
| 3 | Farrell McCrohon direct PDF / notice path | strongest known sale-entry PDF pattern for physical-sale pre-entry data | `https://farrellmccrohon.com.au/contact/` | request direct sale-entry PDF or notice emails |
| 4 | McCormack Real Estate livestock notices | active livestock page and regional relevance, but no clean self-serve email path confirmed | `https://www.mccormackrealestate.com.au/livestock` | ask for direct livestock notices or approved feed |
| 5 | Donovan direct office PDF / notice path | useful fallback if the mailing list proves too broad or late | `https://donovanlivestock.com.au/contact/` | request direct notice/PDF path in parallel with list subscription |

### Later / not email-first

| Source | Why it stays out of the first setup wave |
| --- | --- |
| RMA | strong parser candidate, but not currently a verified newsletter or email-notice source |
| Stockplace | direct listing parser candidate, but no current authorised email path confirmed |
| NRLX Casino | useful exchange/calendar layer, but not a current subscriber-first intake path |
| APL Group | useful umbrella network, but not a direct cattle-alert mailbox source |
| GNF Real Estate Prime Cattle Sales | worth re-checking later, but not cleanly verified in this pass |

### Shortest practical setup order

1. Nutrien
2. Ramsey & Bulmer
3. APL Casino Kyogle
4. Donovan mailing list
5. Forbes newsletter
6. Quality email subscribe
7. Ian Weir
8. APL Tenterfield
9. Farrell McCrohon
10. McCormack

## Mailbox Naming Recommendation

Recommended mailbox candidates:

- `alerts@<your-domain>`
- `salesalerts@<your-domain>`
- `sources@<your-domain>`

Default recommendation:

- use `alerts@<your-domain>` unless another mailbox already serves a distinct
  support or customer-alert purpose

## Mailbox Setup Checklist

1. Create the dedicated Google Workspace mailbox.
2. Enable 2FA or equivalent admin protections on the controlling admin account.
3. Do not forward the mailbox to a personal inbox by default.
4. Keep mailbox use limited to authorised source subscriptions and direct
   source-contact traffic.
5. Create one mailbox label/folder per source if convenient:
   - `Nutrien`
   - `Ramsey Bulmer`
   - `APL Casino`
   - `Forbes`
   - `Quality`
   - `Ian Weir`
   - `APL Tenterfield`
   - `Donovan`
   - `Farrell McCrohon`
   - `McCormack`
6. Keep unsubscribe capability intact for every subscribed source.
7. Record every subscription in the subscription register template.

## Exact First Actions When Back At The Computer

### Nutrien

- sign up the mailbox to the livestock sales alert channel
- log subscription date and source URL
- wait for first real alert email before doing any parser work beyond the
  current local workflow

### Ramsey & Bulmer / APL Casino / Forbes / Quality

- subscribe the mailbox through the live mailing-list or newsletter form
- log subscription date and source URL
- wait for first real notice before doing source-specific parser work

### Ian Weir / APL Tenterfield / Donovan / Farrell McCrohon / McCormack

- do not assume newsletter signup exists
- where no self-serve alert exists, use the current permission drafts and ask
  for direct notice/PDF sharing or comfort for facts-only ingestion

## Raw Notice Export Workflow

When the first real source notices arrive:

1. Export or manually summarise each source email into one raw JSON batch file
   using the template file in `references/operations/authorized_notice_batch_template.json`.
2. Place that raw JSON into `authorized_notice_raw/`.
3. Keep any actual PDF attachment outside git, optionally in a subfolder under
   `authorized_notice_raw/`.
4. Run:

```powershell
C:\Users\Drumquil\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\transform_authorized_notices.py
C:\Users\Drumquil\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\validate_authorized_notice_samples.py
```

5. Review generated records in `authorized_notice_samples/`.
6. Only after that, consider enabling:

```text
ENABLE_AUTHORIZED_NOTICE_SOURCE=TRUE
```

## Legal / Compliance Guardrails

1. Subscribe only where the source is naturally distributing alerts or has given
   permission.
2. Keep facts-only ingestion as the operating default.
3. Do not reuse photos unless explicitly permitted.
4. Preserve sender identity, sent/received date, source URL, and attachment
   metadata.
5. If a source objects, stop using that source immediately and log it.
6. Do not treat Kill the Newsletter or any other transport helper as a
   substitute for permission where the source register still says
   permission-first.

## What Codex Can Continue Doing Without Mailbox Access

- harden the JSON normalisation flow
- add parser helpers for attachment metadata
- build test fixtures from approved synthetic examples
- prepare outreach / permission registers
- run scheduled workspace checks against newly dropped raw files
