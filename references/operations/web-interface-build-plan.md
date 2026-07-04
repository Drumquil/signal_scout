**DRUMQUIL SIGNAL**

Cattle Scout — Web Interface Build Plan

| **Version: 1.0** | **Date: May 2026** | **Author: Tom Flanagan** |
| --- | --- | --- |

# **1. Purpose**

This document defines the architecture and build plan for the Cattle Scout web-based configuration interface. It locks design decisions, scope, and sequence so that build can begin in a new chat without re-relitigating prior conversations.

The interface eliminates Google Sheets as the user-facing config layer, enables sharing with beta producers, and establishes the architectural foundation for future agent-accessibility and multi-platform aggregation.

# **2. Locked Architectural Decisions**

| **Decision** | **Position** |
| --- | --- |
| **Frontend** | Static HTML + Tailwind CSS (CDN) + vanilla JavaScript. No React. Hosted on GitHub Pages. |
| **Backend** | Google Apps Script web app, JSON API, bound to new master sheet (separate from Tom's personal drumquil_scout sheet). |
| **Auth** | Google Sign-In via Apps Script Session.getActiveUser(). Email whitelist in users tab for beta. |
| **Domain** | scout.drumquilsignal.com (subdomain via Porkbun DNS pointing to GitHub Pages). |
| **Mobile** | Mobile-first design via Tailwind responsive utilities. Same codebase serves desktop and phone. |
| **Data store** | Single master Google Sheet with multi-user tabs. Migrate to PostgreSQL on paid backend when justified. |
| **Run-now** | Button writes flag to run_requests tab. GitHub Actions cron polls every 5 minutes. |
| **Validation** | Inline form validation. Reward early, punish late: errors trigger onBlur, clear onChange, required-field checks onSubmit. |
| **Agent-accessibility** | API-first backend design. Per-user API keys for agent access. MCP-ready architecture from day one. |
| **IP ****&**** copyright** | © 2026 Drumquil Signal copyright notice on every source file and in app footer. |
| **Credentials** | Never in source code. .env file for local Python. Apps Script PropertiesService for backend secrets. |

# **3. UX Design Principles**

User audience: 50-65 year old producers with varying tech comfort. Principles below apply throughout the build.

| **Principle** | **Implementation** |
| --- | --- |
| **Touch targets** | Minimum 48px height for primary actions. Generous spacing between tappable elements. Tested on phone in poor light, one-handed. |
| **Font sizes** | Base 16px minimum body text. Labels 14px minimum. Headings 20-24px. No 12px text anywhere. |
| **Plain language** | Buttons say what they do ("Save profile" not floppy disk icon). No jargon. No clever wording. |
| **Error messages** | Explain how to fix the problem with current values. "Maximum weight must be greater than minimum weight (currently 300kg max, 400kg min)". |
| **Discoverability** | Every action visible as a button. Gestures (swipe, pull-to-refresh, long-press) supported as accelerators on top of visible buttons. No gesture-only actions. |
| **Defaults** | New user lands on screen with one obvious next action. New profiles open with sensible pre-filled defaults so users can save a working profile without understanding every field. |
| **Confirmation** | Destructive actions (delete profile) require explicit confirmation. Non-destructive actions are one-click. |
| **Feedback** | Every action produces visible confirmation. Save → green tick + "Profile saved". Run requested → "Run queued, results within 5 minutes". |
| **Loading states** | All async operations show loading indicators. No silent freezes. |

# **4. Data Model**

Single master Google Sheet named drumquil_scout_master with the following tabs:

## **Tab: users**

Columns: email (primary key), name, whatsapp_number, status (active/disabled/pending), date_joined, api_key_hash, last_login

## **Tab: profiles**

Columns: profile_id (UUID), user_email (FK), profile_name, active (boolean), category (commercial/breeding_female/cow_calf/bull), criteria (JSON blob containing all filter fields), created_at, updated_at

Using a JSON blob for criteria keeps the schema flexible as new filter fields are added. Apps Script can parse and validate it server-side; the web form constructs and edits the JSON.

## **Tab: alerts_log**

Columns: alert_id, user_email, profile_id, listing_url, listing_data (JSON), status (WATCHING/ALERTED), user_response (PASS/WATCH/BID/null), platform (auctionsplus/herdonline/etc), logged_at, responded_at

## **Tab: run_requests**

Columns: request_id, user_email, requested_at, status (pending/running/complete/failed), completed_at, alerts_generated

## **Tab: audit**

Columns: audit_id, user_email, action, target, timestamp, ip_address. Every write operation logs an audit row.

# **5. API Design (API-First, Agent-Ready)**

Every operation the web UI performs is a JSON API call. Same endpoints serve future MCP wrapper for agent access. Authentication via Google Sign-In session token (web UI) or X-API-Key header (agents).

| **Endpoint** | **Purpose** | **Type** |
| --- | --- | --- |
| **GET /api/profiles** | List authenticated user's profiles | Read |
| **GET /api/profiles/{id}** | Get single profile detail | Read |
| **POST /api/profiles** | Create new profile | Write |
| **PUT /api/profiles/{id}** | Update existing profile | Write |
| **DELETE /api/profiles/{id}** | Delete profile (soft delete — sets active=false) | Write |
| **GET /api/watching** | List current WATCHING listings for user | Read |
| **GET /api/alerts** | List ALERTED listings with response history | Read |
| **POST /api/alerts/{id}/response** | Mark response (PASS/WATCH/BID) | Write |
| **POST /api/run** | Request a run | Write |
| **GET /api/run/status** | Check status of pending/running requests | Read |
| **GET /api/user** | Get authenticated user profile | Read |
| **PUT /api/user** | Update user profile (name, whatsapp_number) | Write |

Read endpoints can be granted to agents freely. Write endpoints may require additional user confirmation when called by an agent. This distinction is enforced in the auth layer, not the endpoint logic.

# **6. Page Wireframes**

## **Page 1: Sign in**

Single page. Drumquil Signal logo. Google Sign-In button. Below: "By signing in you accept the Terms of Use and Privacy Policy." Whitelist check runs server-side. Non-whitelisted users see message with email contact to request access.

## **Page 2: Home — My Profiles**

Header: user name + sign-out. Body: list of profiles as cards. Each card shows profile name, category badge, active/paused toggle (large switch), last-run summary (e.g. "3 watching, 0 alerted this week"), and three buttons: Edit, Duplicate, Delete. Top of page: "+ New Profile" primary action button. Bottom nav (mobile): Home / Watching / Alerts / Settings.

## **Page 3: Profile Editor**

Single-column form with collapsible sections to manage cognitive load:

• Basics (always open): profile name, active toggle, states multi-select chips, sale types multi-select chips.

• Cattle Type (always open): tab strip — Commercial / Breeding Females / Cow & Calf / Bulls. Tab selection drives which subsequent sections are visible.

• Filter Criteria (visible per cattle type): classes, breeds, min/max head, min/max weight, mob evenness, fat score range, age range. Slider inputs for ranges where possible. Sliders simultaneously display numeric value next to them.

• Accreditations (always open): EU, NE, WHP toggles with plain-language descriptions.

• Price (always open): max price per head (optional).

• Vendors (collapsed by default): preferred / excluded vendor lists.

• Bull EBVs (collapsed by default within Bulls tab, currently blank pending breed selection).

Save button sticky at bottom of viewport on mobile, always visible. Save disabled until all validation errors clear. Cancel button returns to Home without saving (with unsaved-changes confirmation).

## **Page 4: Watching Queue**

List of all WATCHING listings across user's active profiles. Each row: listing title, head count, location, sale date, profile that matched, View on AuctionsPlus link, and three response buttons PASS / WATCH / BID. PASS removes from queue. Pull-to-refresh and visible refresh button both supported.

## **Page 5: Alert History**

Read-only log of ALERTED listings with user responses. Filterable by profile, by response, by date range. Foundation for future learning (e.g. "you usually PASS on Hereford crosses — should we deprioritise?").

## **Page 6: Run Now**

Single primary button: "Run Cattle Scout Now". Tap → button disables, shows "Run queued, results within 5 minutes". When complete, button re-enables and shows "Last run: X alerts at HH:MM". User also receives WhatsApp notification on completion.

## **Page 7: Settings**

Account: name, WhatsApp number, sign out. API keys: generate, copy, revoke (for agent access). Notifications: WhatsApp on/off, time-of-day window. Account deletion: full data export + delete (GDPR-style).

# **7. Security Architecture**

Security is a first-class design concern from day one. Each architecture decision below has a security implication noted.

| **Concern** | **Approach** |
| --- | --- |
| **Credentials** | Never in source code. Apps Script PropertiesService for all secrets. .env for local Python. |
| **HTTPS only** | GitHub Pages provides automatically via Let's Encrypt. No HTTP fallback. |
| **Authentication** | Google Sign-In for humans. X-API-Key header for agents. API keys stored hashed (SHA-256), not plaintext. |
| **Authorisation** | Every endpoint verifies session/key and checks user has access to requested resource. No anonymous endpoints. |
| **Input validation** | Every endpoint validates payload shape, size, and field constraints. Reject malformed JSON. Reject oversized payloads (>100KB). |
| **Rate limiting** | Per-user per-day limits on write endpoints. Run-requests capped at 10/user/day during beta. Apps Script natural quotas as outer layer. |
| **Audit logging** | Every write operation logs to audit tab: user, action, target, timestamp, IP if available. |
| **Data export** | Users can export all their data (profiles, alerts, audit history) as JSON via Settings. |
| **Account deletion** | Users can request full deletion. Sets status=deleted, soft-deletes all rows. Hard delete after 30 days. |
| **Vulnerability disclosure** | Email tom@drumquilsignal.com. Document publicly once contact established. |
| **Incident response** | Plan documented separately: credential compromise, data exposure, scraper detection. Run-book to be created before beta launch. |

# **8. Source-Abstraction Refactor (Phase 2 Dependency)**

The web interface depends on the underlying scraper being source-abstracted before multi-platform support can be exposed in the UI. Refactor must precede or run parallel to the web build.

Common Listing schema (Python dataclass):

• Source metadata: platform, url, scraped_at

• Listing identity: title, sale_name, sale_date, vendor, agent

• Location: location_string, state, postcode_if_available

• Cattle: category, class, breed, num_head, num_calves, age_min_months, age_max_months

• Physical: avg_weight_kg, weight_range_kg, fat_score

• Accreditations: is_EU, is_NE, has_WHP

• Price: price_per_head, price_c_kg

• Status: catalogue_pending

Each platform_scrapers/<platform>.py module exposes a single function get_listings(config) returning List[Listing]. Main script aggregates across all configured platforms, deduplicates by (platform, listing_id), then applies common filter/valuation/alert logic.

# **9. Build Sequence**

| **Week** | **Deliverables** |
| --- | --- |
| **Week 1** | Data model, Apps Script API, authentication. Master sheet created with all tabs. Apps Script web app deployed with all endpoints stubbed and returning correct response shape. Google Sign-In and whitelist working. Audit logging working. API documentation written in parallel. |
| **Week 2** | Frontend skeleton. GitHub Pages repo with Tailwind CDN, base layout, sign-in page, profiles list page. Mobile-first throughout, tested on actual phone. scout.drumquilsignal.com DNS configured. |
| **Week 3** | Profile editor. Full form with all sections, collapsibles, multi-select chips, sliders. Inline validation following reward-early-punish-late pattern. Save flow with proper error handling. |
| **Week 4** | Watching queue and alert history. Both read-only views first. Then add PASS/WATCH/BID buttons. Gesture support (swipe, pull-to-refresh) on top of visible buttons. |
| **Week 5** | Run-now button and Python script integration. Modify cattle_scout.py to be multi-user-aware. Modify to check run_requests flag. Set up GitHub Actions cron schedule. End-to-end test. |
| **Week 6** | Beta launch. Add 2-3 producer friends to whitelist. Write 1-page user guide. Set up feedback channel (shared WhatsApp group or similar). Monitor closely for first 2 weeks. |

# **10. Cost Analysis**

| **Item** | **Cost** |
| --- | --- |
| **GitHub Pages hosting** | Free (forever for static sites) |
| **Google Apps Script** | Free (within standard quotas) |
| **Google Sheets data store** | Free (within standard quotas) |
| **GitHub Actions cron** | Free (2000 minutes/month for public repos) |
| **Domain (drumquilsignal.com)** | Already owned via Porkbun |
| **Twilio WhatsApp sandbox** | Free (50 messages/day shared during beta — binding constraint) |
| **Total during build + beta** | $0/month ongoing |
| **Twilio production WhatsApp (5+ users)** | ~$5/month base + per-message |
| **Render/Fly.io backend (20+ users)** | $5-7/month |
| **PostgreSQL (Render bundled free tier)** | Free initially |
| **Cloudflare WAF (production)** | Free tier |
| **Trademark registration (one-time)** | $250 per class via IP Australia |

# **11. Decisions Still Required Before Week 1**

• Visual design and branding. Logo, colour palette, typography. Drumquil Signal has no brand assets yet. Recommend simple text-based logo with one accent colour for v1, professional brand design in parallel as separate workstream.

• Beta user list. 2-3 producer friends to invite. Names, contact, tech comfort level. Their constraints shape final design decisions.

• Terms of Use and Privacy Policy. Need basic versions before any beta user signs in. Standard SaaS templates customised for Drumquil Signal context. Lawyer review recommended before any paid users.

• Initial sensible defaults for new profile. Pre-filled values that make a working profile. Tom's current values are a reasonable starting point.

• Brand voice and tone for UI copy. Buttons, error messages, confirmations. Should sound like Drumquil Signal speaking to a producer peer — direct, no jargon, no marketing fluff.

# **12. Instructions for Starting Build Chat**

Paste at the top of the new build chat:

Starting Cattle Scout Web Interface build. Read the Web Interface Build Plan v1.0, Project State Document v1.3, Australian Platforms Reference v1.0, and Cybersecurity Reference v1.0 first. Current task: Week 1 — data model and Apps Script API. Locked decisions in the Build Plan are not to be re-relitigated.

*© 2026 Drumquil Signal. All rights reserved.  |  Cattle Scout Web Interface Build Plan v1.0  |  May 2026*