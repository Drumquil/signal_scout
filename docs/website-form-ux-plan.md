# Website and Onboarding UX Plan

## Purpose

Build a simple Signal Scout web presence and replace the current Google Form
with a buyer onboarding flow that feels clear, fast, and professionally guided.

This is the next product layer after the runtime proves it can scrape quickly,
classify breeding-female opportunities correctly, and run safely for the first
tester.

## UX Principles

- Ask questions in buyer language, not config language.
- Show the buyer what their alert profile means before they submit.
- Prefer guided choices with examples over long open text fields.
- Keep advanced filters optional and collapsible.
- Make WhatsApp delivery expectations explicit before activation.
- Preserve the current config contract until a deliberate schema migration.

## Website MVP

- First screen: usable onboarding entry, not a marketing landing page.
- Short explanation of what Signal Scout watches and what an alert means.
- Clear beta disclaimer: alerts are prompts to inspect listings, not buying
  recommendations.
- Operator-friendly admin handoff: each submission should still be previewed
  with `transform_form_response.py --dry-run` before config write.

## Form Overhaul

- Split onboarding into sections:
  buyer details, region, stock type, breed, lot size, physical filters,
  accreditation/quality filters, delivery confirmation.
- Use conditional questions:
  commercial classes only when commercial stock is selected, breeding-female
  filters only when breeding females or CAF are selected, bull filters only
  when bulls are selected.
- Add a final plain-English profile summary:
  "You will receive alerts for 1-30 Brangus/Ultrablack cows or cow-calf units
  in NSW, 3-6 years old, polled required."
- Keep duplicate submissions as the temporary multi-profile workaround until
  the post-beta profile model is designed.

## Build Sequence

1. Finish runtime sprint validation with offline tests and one supervised
   `TEST_MODE=TRUE` run.
2. Review the current Google Form fields against real first-tester friction.
3. Draft the replacement question flow.
4. Build the website/onboarding UI against the existing config schema.
5. Add an operator preview step before any submission writes to Sheets.
6. Only then consider direct automatic activation.

## Open Decisions

- Whether the first website is public beta-facing or private invite-only.
- Whether form responses continue through Google Sheets or move to an app
  backend.
- Whether users can edit profiles themselves during beta, or whether Tom stays
  in the loop for every change.
