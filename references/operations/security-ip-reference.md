**DRUMQUIL SIGNAL**

Cybersecurity & IP Reference

| **Version: 1.1** | **Date: 18 May 2026** | **Author: Tom Flanagan** |
| --- | --- | --- |

# 1. Purpose

This document defines the cybersecurity and intellectual property protection approach for Drumquil Signal. It covers immediate actions (now complete), ongoing discipline, and the architecture decisions that protect both the business and its users.

Two perspectives matter: protecting Drumquil Signal IP from external parties (including AI tool providers), and protecting user data once the tool is multi-user. Both are addressed.

v1.1 update (18 May 2026): The immediate-actions credential rotation in Section 2 is now complete. Section 2 has been restructured as a completion log. The ongoing-discipline rules remain in force in Section 4. A new Section 10 documents the credential rotation log for future reference.

# 2. Section 2 â€” Immediate Actions: COMPLETED 18 May 2026

All immediate actions identified in v1.0 have been executed. The original list is preserved below as a completion log.

Context: The Twilio auth token and Google service account credentials hardcoded in cattle_scout.py were visible in earlier Claude chat history and were treated as compromised. Both have been rotated at their respective providers and the old credentials revoked.

| **#** | **Action** | **Status** | **Completed** |
| --- | --- | --- | --- |
| 1 | Regenerate Twilio auth token. Old token automatically invalidated. | **DONE** | 18 May 2026 |
| 2 | Create new Google service account JSON key in drumquil-scout project. Delete old key (immediately revoked). | **DONE** | 18 May 2026 |
| 3 | Replace google_credentials.json on disk with newly downloaded file. | **DONE** | 18 May 2026 |
| 4 | Move credentials out of cattle_scout.py source code into .env file (see Section 4). | **DONE** | 18 May 2026 |
| 5 | Add .env to .gitignore. | **DONE** | 18 May 2026 |
| 6 | Turn off training data use for all AI tools (see Section 3). | In progress | â€” |

Result: cattle_scout.py v1.7 no longer contains any hardcoded credentials. All credentials are read from a .env file at runtime via python-dotenv. The .env file is excluded from any future git repository via .gitignore. Both test scripts (test_sheets.py, test_twilio.py) follow the same pattern.

Action 6 (AI tool privacy settings) is the only outstanding item from the original immediate-actions list. Status to be confirmed and logged in Section 10 when complete.

# 3. AI Tool Privacy Settings

Every AI tool used in this project has settings that control whether your conversations are used to train future models. Turn these off for all tools.

## Claude (claude.ai)

Settings â†’ Privacy â†’ "Help improve Claude" â†’ turn OFF.

This setting controls whether Anthropic uses your conversations to train future Claude models. With it off, conversations are still accessible to Anthropic for safety review and abuse detection but are not used for training.

For sensitive work (Cattle Model formulas, commercial strategy): use Claude API access via console.anthropic.com rather than claude.ai. API requests are not used for training by default and there is no ambiguity. Cost is modest (~$20â€“50/month for the volume Tom would use).

## Other AI tools

Apply equivalent privacy settings to: ChatGPT (Settings â†’ Data Controls â†’ Improve the model for everyone OFF), GitHub Copilot (Settings â†’ Copilot â†’ Allow GitHub to use my code snippets OFF), Cursor (Settings â†’ Privacy Mode ON).

Generally, default to API access over web chat access for any tool handling sensitive content. APIs typically have stricter no-training defaults.

# 4. Credentials Management â€” Current Operating Pattern

As of v1.7 of cattle_scout.py, the .env file + python-dotenv pattern is the standing approach for all credentials. This section documents that pattern as the operational baseline.

## Setup (one-time)

Install python-dotenv: pip install python-dotenv

Create a file named .env in the same folder as cattle_scout.py. Contents:

TWILIO_ACCOUNT_SID=AC...

TWILIO_AUTH_TOKEN=...

TWILIO_FROM=whatsapp:+14155238886

TWILIO_TO=whatsapp:+61XXXXXXXXX

GOOGLE_SHEETS_CREDS_FILE=C:\path\to\google_credentials.json

## Standing rules

- The .env file is never committed to any git repository.

- The .env file is never pasted into AI chats, emails, support tickets, or any other shared channel.

- The .env file is never screenshotted; if the script's top portion is captured in a screenshot, the .env file is not in shot.

- Before sharing cattle_scout.py with anyone (including pasting into a Claude chat), verify the top of the file shows os.getenv() calls, not literal credential strings.

- .env.example is the safe-to-share template â€” committed to the repo, contains no secrets, documents the required variables.

## Code pattern

Required imports and load at top of every script that uses credentials:

from dotenv import load_dotenv

import os

load_dotenv()  # reads .env file into environment

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")

# etc.

Fail-fast check at the top of main() raises RuntimeError if any required variable is missing â€” prevents cryptic Twilio/Google errors deep in the run.

## .gitignore contents

The .gitignore file in the Cattle Scout folder must contain at minimum:

.env

google_credentials.json

*.pyc

__pycache__/

.venv/

.vscode/

# 5. Intellectual Property Protection

What can be protected, and how:

| **Asset** | **Protection approach** |
| --- | --- |
| Trademark â€” Drumquil Signal word mark | $250 per class via IP Australia. File classes 9 (software) and 42 (SaaS services). Do this once branding is finalised. |
| Trademark â€” logo | Once logo designed. Same classes. File in same application as word mark to save fees. |
| Domain name | drumquilsignal.com already owned via Porkbun. Renew annually. Consider also registering drumquilsignal.com.au, scout.com.au if available, to prevent typosquatting. |
| Copyright (automatic) | Every line of code Tom writes is automatically copyrighted to him under Australian law. No registration needed. Add Â© 2026 Drumquil Signal. All rights reserved. to every source file. |
| Trade secrets â€” Cattle Model formulas | Keep the actual weighted scoring formulas and seasonal coefficients in a document not pasted into AI chats unless necessary. Mark documents CONFIDENTIAL. |
| NDAs for collaborators | Standard 2-page mutual NDA for any conversation involving non-public details (beta users, agents, MLA, potential investors). Template from LawDepot or IP Australia. Customise parties and purpose only. |
| Open source choice | If publishing any code on GitHub, use Polyform Shield or BSL license that prevents commercial use without permission. Do NOT use MIT or Apache 2.0 for the core Cattle Scout / Cattle Model code. |
| Code repositories | Default to private repositories. Public only for documentation or clearly non-core utilities. |

## What is genuinely proprietary to Drumquil Signal

- Cattle Model: weighted scoring formulas, layer integration logic, seasonal decay coefficients, any unique calibration approaches.

- Drumquil Signal brand: name, logo, visual identity, tagline.

- Aggregation strategy: the specific approach to combining multiple platforms with a valuation layer.

- Customer relationships and producer feedback data.

- Any unique commercial agreements with MLA, agents, or processors.

## What is NOT proprietary

- The general concept of scraping listings and sending alerts.

- Two-stage filtering as a pattern.

- Google Sheets as a data store.

- Any individual open-source library (BeautifulSoup, requests, gspread, python-dotenv).

- Common UX patterns (single-column forms, inline validation).

Trying to protect the second category is futile and would waste legal effort. Protect the first category robustly.

# 6. Cybersecurity â€” Production (Multi-User)

Once the web interface is live and beta users sign in, the security model shifts. Each principle below has a security implication.

## Authentication and authorisation

- Google Sign-In for all users (no password storage).

- Whitelist on the users sheet (status = active required for sign-in).

- Per-user API keys for agent access, stored hashed (SHA-256), shown only once on generation.

- Every API endpoint verifies authentication and that the authenticated user has access to the requested resource.

## Data isolation

- Every row in profiles, alerts_log, run_requests tagged with user_email.

- Every Apps Script API query filters by Session.getActiveUser().getEmail().

- Cross-user data access impossible by design.

## Transport and storage

- HTTPS only. GitHub Pages provides automatically with Let's Encrypt.

- Apps Script PropertiesService stores all backend secrets, not in code.

- Production-stage: PostgreSQL with row-level security if migrating off Google Sheets.

## Defensive measures

- Input validation on every endpoint: shape, size, field constraints.

- Rate limiting per user per day on write endpoints.

- Audit log of every write action (user, action, target, timestamp, IP).

- Cloudflare in front of production backend for DDoS protection (free tier sufficient).

## Account security (Tom's accounts)

- 2FA enabled on: Anthropic, GitHub, Google, Twilio, Porkbun, Cloudflare, any other admin account.

- Password manager for unique passwords across all services (Bitwarden free or 1Password).

- Recovery codes for 2FA stored offline (printed or in encrypted backup).

# 7. Incident Response Plan

Run-book to follow if security incidents occur. Develop in full before beta launch.

## Credential compromise

1. Identify which credential. 2. Rotate immediately (regenerate at provider). 3. Update .env or PropertiesService. 4. Audit logs for unauthorised use. 5. Notify affected users if any. 6. Post-mortem documented in Section 10.

## Data exposure (user data leaked or accessed inappropriately)

1. Stop the bleeding (block the access vector). 2. Identify scope (which users, what data). 3. Notify affected users within 24 hours. 4. Notify OAIC if mandatory under Notifiable Data Breaches scheme. 5. Post-mortem documented and shared with affected users.

## Scraper detection or blocking

1. Stop the scraper for that platform immediately. 2. Contact the platform directly to discuss whether a sanctioned arrangement is possible. 3. Do not attempt to circumvent. 4. If no sanctioned arrangement possible, accept the block â€” that source is removed from Cattle Scout.

## Service outage

1. Identify cause. 2. Restore service. 3. Communicate status to beta users via WhatsApp group. 4. Post-mortem documented.

# 8. Privacy and Data Handling

## User data collected

- Email (from Google Sign-In).

- Name (user-provided).

- WhatsApp number (user-provided).

- Buying criteria profiles (user-created).

- Alert history and responses.

- Audit log entries.

## User data NOT collected

- No payment information (no payments in beta).

- No address, phone (other than WhatsApp), or other PII beyond above.

- No tracking cookies or analytics beyond what's necessary for the service.

## Privacy commitments to users

- Data is used only to provide the Cattle Scout service.

- Data is not sold or shared with third parties.

- Data export available at any time via Settings.

- Account deletion available at any time; full data hard-deleted after 30 days.

- Users notified within 24 hours of any data exposure incident.

## Australian compliance

- Privacy Act 1988 applies if Drumquil Signal annual revenue exceeds $3M (not yet relevant).

- Notifiable Data Breaches scheme applies regardless of revenue if dealing with sensitive information (limited applicability â€” cattle buying criteria are not sensitive).

- Spam Act 2003 applies to WhatsApp alerts â€” users must opt in (handled at sign-up) and have unsubscribe pathway (handled in Settings).

# 9. Living Document

This document is updated whenever:

- A new tool or service is added to the stack.

- A security incident occurs (post-mortem appended to Section 10).

- Australian regulations change relevant compliance requirements.

- The user model changes (e.g. moving from beta to paid).

- A credential rotation occurs (logged in Section 10).

# 10. Credential Rotation Log

Every credential rotation is recorded here, regardless of cause (compromise, scheduled rotation, staff change, etc.).

| **Date** | **Credential** | **Reason** | **Action** |
| --- | --- | --- | --- |
| 18 May 2026 | Twilio Auth Token | Token visible in earlier chat history â€” treated as compromised. | Generated secondary token, promoted to primary, deleted old primary. |
| 18 May 2026 | Google service account key (drumquil-scout / cattle-scout) | JSON key path and contents visible in earlier chat history â€” treated as compromised. | Created new JSON key, replaced on disk, deleted old key via Google Cloud Console. |

Outstanding action: AI tool privacy settings (Section 3) â€” to be confirmed and logged here when complete.

*Â© 2026 Drumquil Signal. All rights reserved.  |  Cybersecurity **&** IP Reference v1.1  |  18 May 2026*

