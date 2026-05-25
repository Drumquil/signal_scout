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

## Notes
- `.gitignore` already ignores `.env` and `google_credentials.json`.
- If git refuses commands with “dubious ownership”, run:
  - `git config --global --add safe.directory "C:/Users/Drumquil/Documents/Codex/Drumquil Signal/Signal Scout"`
