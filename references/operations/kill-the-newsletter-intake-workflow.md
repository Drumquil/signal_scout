# Kill the Newsletter Intake Workflow

## Purpose

This note defines how Signal Scout can use Kill the Newsletter as an
authorised email-to-Atom intake path for cattle-agent alerts, newsletters, and
sale updates.

This is an operations guide, not a legal override. It should be used together
with:

- `references/operations/authorised-intake-ops.md`
- `references/operations/source-register.md`
- `references/operations/permission-email-drafts.md`

## Bottom Line

Kill the Newsletter is suitable for Signal Scout when:

- Tom subscribes legitimately to a source's existing email updates;
- the source is naturally sending the update to subscribed recipients;
- Signal Scout uses the resulting Atom feed for facts-only ingestion;
- the source is not objecting and is not being bypassed around a clear access
  restriction.

Kill the Newsletter is not a substitute for permission where the source
register still marks a source as permission-first or `RED`.

## What Kill the Newsletter Changes

It changes the transport path, not the content rights.

Instead of:

`agent email -> human inbox`

Signal Scout can use:

`agent email -> Kill the Newsletter inbox -> private Atom feed -> Signal Scout intake`

This is useful because it gives:

- a stable feed URL per subscription;
- a machine-readable feed structure;
- less manual mailbox export work for recurring alerts.

## Allowed Use Cases

Use Kill the Newsletter when all of the following are true:

1. The source already distributes emails or newsletters to subscribers.
2. The subscription is legitimate and opt-in.
3. The feed is used for factual extraction, alert discovery, or sample
   collection.
4. Source attribution and deep-linking remain intact.
5. The feed URL is treated as private operational infrastructure.

Strong examples:

- Nutrien livestock sales alerts sent to an opted-in address
- Elders branch sale updates where signup is offered normally
- agent newsletters that announce sale dates, store sales, catalogue releases,
  and linked PDF notices

## Do Not Use It For

Do not use Kill the Newsletter to:

- bypass a source that has clearly refused automated use;
- access login-gated or paid-only material;
- republish full newsletter text as a substitute for the source;
- share the private Atom feed publicly;
- assume that a feed subscription equals blanket permission for any later
  production use.

If a source is `RED` in the source register, Kill the Newsletter does not
change that status.

## Signal Scout Workflow

### 1. Create the feed

1. Go to Kill the Newsletter.
2. Create a newsletter inbox for the source.
3. Save:
   - the generated subscription email address
   - the private Atom feed URL
   - the source name
   - the signup page URL
   - the subscription date

Record that in the subscription register.

### 2. Subscribe legitimately

1. Use the generated Kill the Newsletter email address when signing up.
2. Complete any normal signup flow that the source expects.
3. If the source uses manual approval, preserve that context in the register.
4. If the source requires reply-based confirmation and the flow cannot be
   completed, treat the source as not solved by Kill the Newsletter.

### 3. Wait for the first real email

Before any parser work:

1. confirm the first real email arrives in the feed;
2. confirm the feed entry contains enough source facts to be useful;
3. check whether the feed consistently carries:
   - title
   - sent date
   - source link
   - summary/body text
   - PDF or catalogue links where relevant

### 4. Convert to Signal Scout raw notice input

Once a real feed item exists:

1. export the source facts into
   `references/operations/authorized_notice_batch_template.json` shape;
   use `authorized_notice_raw/ktn_atom_item_template.json` as the smallest
   checked-in example;
2. place the batch file in `authorized_notice_raw/`;
3. run:

```powershell
C:\Users\Drumquil\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\transform_authorized_notices.py
C:\Users\Drumquil\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\validate_authorized_notice_samples.py
```

4. review output in `authorized_notice_samples/`.

Checked-in examples:

- `authorized_notice_raw/ktn_atom_item_template.json`
- `authorized_notice_raw/ktn_atom_item_multi_record_template.json`
- `authorized_notice_samples/ktn_atom_item_normalized_example.json`

### 5. Decide whether the source is parser-worthy

Good signs:

- consistent sale/update format
- stable links to catalogue, PDF, or sale page
- enough facts for `WATCHING`-grade records
- no obvious objection from the source

Weak signs:

- highly promotional content with little cattle metadata
- inconsistent formatting across sends
- missing links or attachment references
- signup flow depends on unsupported email replies

## Suggested Register Notes for Kill the Newsletter Sources

When a source is being tested through Kill the Newsletter, add notes such as:

- `authorised email path under test via Kill the Newsletter`
- `Atom feed captured; waiting for first real sale alert`
- `reply-based confirmation blocked; feed path not viable`
- `feed useful for WATCHING-only sale notice extraction`

## Operational Guardrails

1. Treat every Atom feed URL as a secret.
2. Do not commit live feed URLs to git.
3. Preserve source attribution in every downstream record.
4. Keep the original source link whenever present.
5. Stop using the feed immediately if the source objects or changes terms in a
   way that makes the use inappropriate.

## Recommended First Sources

Best current candidates from the source register:

1. `Nutrien Ag Solutions alerts`
2. selected `Elders` branch updates
3. later approved regional-agent notice streams

## Practical Decision Rule

Use Kill the Newsletter when it reduces manual handling of a source that is
already willingly emailing updates to subscribers.

Do not use it as a workaround for a source that still needs permission for the
underlying use case.
