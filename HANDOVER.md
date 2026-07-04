# Signal Scout - Gold Standard Session Handover

Last updated: 2026-06-14

## Purpose

This is the best single-file starting point for a fresh Codex session.

It is designed to let the next session pick up exactly where this one stopped
without reconstructing context from chat history.

Use this file together with:

1. `AGENTS.md`
2. `docs/CODEX_BRIEF.md`
3. `docs/PROJECT_MAP.md`
4. `docs/CURRENT_STATE.md`

## Repo and Environment

### Working repo

`C:\Users\Drumquil\Documents\Codex\Drumquil Signal\Signal Scout`

### Secrets and local files

- `.env` lives in the repo root and must never be committed
- Google credentials must stay out of git
- treat live mailbox exports, real PDF notices, and raw beta-user data as local
  operational data, not repo content

### Important local intake folders

- `authorized_notice_raw/`
- `authorized_notice_samples/`

These are git-ignored except for their README files.

## Current Product Position

Signal Scout is still in beta-stabilisation mode.

The current live shape of the product is:

- AuctionsPlus-first runtime
- Google Sheets-backed multi-user config
- WhatsApp alert delivery
- Google Form -> transform -> config onboarding path
- `TEST_MODE` still `True`

Current strategic sequencing:

- beta testing comes before source-permission outreach
- source expansion stays permission-first
- demo-readiness for external source conversations comes after real beta
  feedback, not before all user testing

## What Was Accomplished In This Session

### 1. Runtime source abstraction was implemented

`cattle_scout.py` now has a real shared-source boundary:

- source discovery once per source per run
- source scraping once per source per run
- shared listing set matched across all users

AuctionsPlus remains the only enabled live source by default.

### 2. Authorised-source intake scaffold now exists

The repo now supports a controlled future email/PDF intake path:

- `authorized_notice_raw/` for raw mailbox/PDF export batches
- `transform_authorized_notices.py` to normalise raw batches
- `validate_authorized_notice_samples.py` to validate ingestion-ready records
- `authorized_notice_samples/` to hold normalised JSON records for the opt-in
  `authorised_notice_proto` source

This path is intentionally local and opt-in.
It does not connect directly to Gmail yet.

### 3. Beta-first sequence was locked in

The repo now explicitly states that the right order is:

1. finish internal validation
2. onboard one trusted real tester
3. run narrow real beta
4. tighten the product for demo-readiness
5. then begin source-permission outreach

This is captured in:

- `docs/beta-sequence.md`
- `docs/beta-user-guide.md`
- `docs/beta-feedback-process.md`

### 4. Operational source-intake materials were created

The repo now includes:

- `references/operations/authorised-intake-ops.md`
- `references/operations/authorized_subscription_register_template.csv`
- `references/operations/authorized_notice_batch_template.json`

These are the operational templates for the dedicated mailbox workflow once Tom
is ready to set it up.

### 5. Intake automation was created

A Codex app automation now exists:

- `Authorised Notice Intake Check`

Its purpose is to inspect the workspace intake folders, run the transformer and
validator when raw notice batches are present, and report whether the intake
lane looks ready for `TEST_MODE` validation.

## Current Truths The Next Session Should Assume

### Beta status

- `TEST_MODE` is still `True`
- no real external beta tester has been onboarded end to end yet
- the short beta guide and feedback process drafts now exist, but have not yet
  been exercised with a real user

### Source status

- AuctionsPlus is still the only active source in runtime
- authorised email/PDF intake is scaffolded but not live
- no dedicated Google Workspace alert mailbox has been created yet
- source-permission outreach is not the main priority until there is beta
  evidence

### Matching semantics that must stay intact

- steers must not match breeding females or CAF
- breeding heifers must not match cows
- breeding cows means females that have already calved
- CAF means cows with calves at foot only
- blank commercial sex/stage plus breeding-female selections should behave as a
  non-commercial-only profile

## Most Important Files Added or Updated Recently

### Beta sequence and user-testing files

- `docs/beta-sequence.md`
- `docs/beta-user-guide.md`
- `docs/beta-feedback-process.md`
- `docs/CURRENT_STATE.md`
- `docs/prelaunch-checklist.md`

### Authorised intake files

- `authorized_notice_raw/README.md`
- `authorized_notice_samples/README.md`
- `transform_authorized_notices.py`
- `validate_authorized_notice_samples.py`
- `references/operations/authorised-intake-ops.md`
- `references/operations/authorized_subscription_register_template.csv`
- `references/operations/authorized_notice_batch_template.json`

### Runtime files

- `cattle_scout.py`
- `transform_form_response.py`

## Immediate Next Priorities

The next session should treat these as the live priority order:

1. confirm the first trusted beta tester plan
2. prepare the exact tester onboarding message and live-send checklist
3. decide the deliberate moment to switch `TEST_MODE` to `False`
4. support the first real beta run and capture feedback cleanly
5. only in parallel, keep the dedicated mailbox / authorised-source intake lane
   ready for later use

## What The Next Session Should Not Drift Into

- do not treat source outreach as the main task before real beta evidence
- do not start broad new-source scraping work
- do not re-open the source-abstraction design unless a real bug is found
- do not overbuild a polished external platform before early beta learning

## Worktree Notes

This worktree is dirty and includes unrelated pre-existing changes and untracked
files.

Rules for the next session:

- do not revert unrelated changes
- read before editing files that already have local modifications
- assume some untracked docs and scripts were added intentionally in recent
  sessions

## Best Next Session Task

If the user wants to continue momentum, the best next task is:

Create the exact first-beta-tester launch pack:

- choose tester profile criteria
- draft the outreach / onboarding message
- define the live-send checklist for switching `TEST_MODE` off intentionally
- define the first-feedback capture script

## Exact Prompt To Start The Next Session

Use this prompt to start a fresh Codex session:

```text
Starting a fresh Signal Scout session. Read AGENTS.md, HANDOVER.md, docs/CODEX_BRIEF.md, docs/PROJECT_MAP.md, and docs/CURRENT_STATE.md first. Then continue from the current beta-first sequence without re-litigating prior decisions.

Current priority: prepare the first real beta tester launch end to end before any source-permission outreach becomes the main task.

Important current truths:
- AuctionsPlus is still the only active runtime source
- TEST_MODE is still True
- runtime source abstraction is already implemented
- authorised email/PDF intake scaffold exists but no dedicated mailbox is live yet
- beta testing comes before source outreach

Task for this session:
1. Review the current beta rollout materials in docs/beta-sequence.md, docs/beta-user-guide.md, and docs/beta-feedback-process.md
2. Turn them into an exact first-beta-tester launch pack
3. Identify anything still missing before we intentionally switch TEST_MODE to False for the first trusted tester
4. Make the next highest-value repo updates you can without waiting on external mailbox setup

Do not spend time rediscovering source lists or redesigning the source-abstraction path unless a real blocker appears.
```
