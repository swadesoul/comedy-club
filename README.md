# MAESTRO COMEDY CLUB — Studio Foundation

**Status: source-only implementation. Not deployed or connected to live speech generation/radio.**

A shared production engine for SWADEBASE Admin and MAESTRO RADIO Admin, with RESINGLAB as the creative source for voice, speech, audience stems and final audio. MAESTRO is the station, catalog, scheduling and broadcast authority. Do not duplicate their identity, storage, workers, voice service or scheduler.

## Working prototype
Open `studio/index.html`: cinematic responsive Comedy Club Studio. Choose fictional comedian, age-rating (PG, PG-13, R), room size (25/50/100/150/250), crowd work, callbacks, and duration. Write/import text routines, create multiple drafts, prepare ten-routine planning batches, preview cue timelines and download a structured per-routine production manifest. It is **offline only**; buttons do not call speech providers, consume credits or broadcast content.

`engine/comedy.mjs`: reusable pure validators and production planning with starter 5-second liner, segmented stems, crowd-response alignment, callback map and batch limits. `tests/comedy.test.mjs`: regression coverage using built-in Node test runner.

## Native integration contract (not yet built)
Mount versioned, authenticated and tenant-scoped routes into existing SWADEBASE adapter runtime; expose the same capability through MAESTRO admin. Reuse owner/tenant session checks, scoped MAESTRO staff role, existing RESINGLAB Speech/Voice Design and Backblaze B2.

- `POST /v1/comedy/routines`: ingest authored or rights-attested imported routine; preserve original and version history
- `POST /v1/comedy/batches/plan`: idempotent, no-cost plan with explicit selected settings and immutable prompt manifest
- `POST /v1/comedy/batches/{id}/authorize`: verified authorized owner and capped spend
- `POST /v1/comedy/batches/{id}/dispatch`: existing durable queue, bounded providers, no blind retry
- `GET /v1/comedy/batches/{id}`: durable status and individual outcomes
- `POST /v1/comedy/routines/{id}/approve`: listening, rights, audio, content and QA gate
- `POST /v1/comedy/routines/{id}/maestro-stage`: dedicated comedy station library, never silently schedule or change flagship

States: draft → planned → authorized → rendering → needs_review → approved → staged → scheduled. Failed/uncertain jobs stop for reconciliation. Keep original stems and script, checksums, voice consent and rights, cue sheet, callback map, provider receipts, identity and approval metadata in SWADEBASE/B2. No automatic provider dispatch or payments simply from batch planning. PG/PG-13/R are internal labels, not official film ratings; R restricted to approved adult stream, legal/platform age requirements separately enforced.

## Acceptance criteria for actual live release
- Registry and current site Bibles reconciled; same existing SWADEBASE and MAESTRO adapters reused
- Owner/tenant checks and audit log; rights and voice consent; no vendor API key in browser
- Ten routine batch crash/retry safety and explicit cost ceiling
- Per-word punchline end, audience reactions with natural decay and no masked dialogue; callbacks at end
- Five-second reusable liner; final clip ≤180 seconds including intro
- R-rated content excluded from PG/PG-13 and general queues
- Existing ReSingLab audio provider render verified, existing B2 readback verified
- Human acceptance, explicit MAESTRO station handoff and real preview/airplay checks
- Desktop, mobile, iPad Safari and rollback verified; Bibles and private What's New updated

No launch claim until these checks pass.