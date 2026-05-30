# Signal Scout — Handover (Codex)

## Source of truth (working repo)
- `C:\Users\Drumquil\Documents\Codex\Drumquil Signal\Signal Scout`

## Knowledge Library (KL) — keep out of git
- `C:\Users\Drumquil\Documents\Drumquil\Drumquil Signal\Signal Scout KL Files`
- Folders created: `00_INBOX`, `01_ACTIVE`, `02_ARCHIVE`, `03_EXPORTS`, `04_REFERENCES`

## Secrets (keep out of git + out of KL)
- Secrets folder: `C:\Users\Drumquil\Secrets\signal_scout`
- Store Google service account key here:
  - `C:\Users\Drumquil\Secrets\signal_scout\google_credentials.json`
- `.env` lives in the repo root but must never be committed:
  - `C:\Users\Drumquil\Documents\Codex\Drumquil Signal\Signal Scout\.env`

## External data
- Treat `drumquil_scout.xlsx` as external/reference data (do not commit).
  - Suggested location: `C:\Users\Drumquil\Documents\Drumquil\Drumquil Signal\Signal Scout KL Files\01_ACTIVE\drumquil_scout.xlsx`

## KL download workflow (Claude → local)
- Download new items into: `C:\Users\Drumquil\Documents\Drumquil\Drumquil Signal\Signal Scout KL Files\00_INBOX`
- Triage + move:
  - Current/active → `01_ACTIVE`
  - Outdated/superseded → `02_ARCHIVE`
  - Claude exports/snapshots → `03_EXPORTS`
  - External reference material → `04_REFERENCES`
- Record the final path of key active files in:
  - `C:\Users\Drumquil\Documents\Drumquil\Drumquil Signal\Signal Scout KL Files\KL_INDEX.md`

## Tomorrow start checklist
- Open repo in VS Code/Codex: `C:\Users\Drumquil\Documents\Codex\Drumquil Signal\Signal Scout`
- Activate venv (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Quick sanity checks:
  - `python test_sheets.py`
  - `python test_twilio.py`

## Notes
- `.gitignore` already ignores `.env` and `google_credentials.json`.
- If git refuses commands with “dubious ownership”, run:
  - `git config --global --add safe.directory "C:/Users/Drumquil/Documents/Codex/Drumquil Signal/Signal Scout"`

## Current state (docs)
- Project status: `docs/status.md` (updated 30 May 2026)
- Beta gates/checklist: `docs/prelaunch-checklist.md` (updated 30 May 2026)
