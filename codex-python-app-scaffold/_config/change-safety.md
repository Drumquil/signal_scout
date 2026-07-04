# Change Safety

## Non-Negotiables

- Do not move Python entry points, package roots, settings files, or active docs
  without updating every affected path and verifying the result.
- Do not rename modules or packages casually; import-path churn can cause broad regressions.
- Do not convert the repo into a stage-output-driven runtime unless that is the
  explicit task.
- Use the narrowest validation that proves the change.
- Favor small, reversible edits over broad cleanup.

## Python Path Preservation Checklist

Before moving or renaming any existing Python file or folder:

1. Search for references with `rg`.
2. Update imports, scripts, docs, test paths, and operator notes together.
3. Re-run the smallest affected checks such as `py_compile`, a narrow `pytest` target, or a focused script run.
4. Confirm the new location improves clarity enough to justify migration risk.

## Environment Safety

- Treat `.env`, secret files, API credentials, and local databases as sensitive.
- Prefer `.env.example` or docs updates over editing real secret material.
- If the repo lacks ignore rules for sensitive files or generated artifacts, add them deliberately.

## Source Improvement Principle

If the same manual fix is needed repeatedly, update the source instruction,
contract, test, or reference file rather than repeatedly patching outputs.
