# Change Safety

## Non-Negotiables

- Do not move `cattle_scout.py`, `transform_form_response.py`, validation
  scripts, or active docs without updating every affected path and verifying the
  result.
- Do not convert the repo into a stage-output-driven runtime unless that is the
  explicit task.
- Use the narrowest validation that proves the change.
- Favor small, reversible edits over broad cleanup.

## Path Preservation Checklist

Before moving or renaming any existing file:

1. Search for path references with `rg`.
2. Update docs, scripts, imports, and operational notes together.
3. Re-run the narrowest affected checks.
4. Confirm the new location improves clarity enough to justify migration risk.

## Source Improvement Principle

If the same manual fix is needed repeatedly, update the source instruction,
contract, or reference file rather than repeatedly patching outputs.
