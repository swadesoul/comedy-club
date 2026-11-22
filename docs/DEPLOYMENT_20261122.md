# Comedy Club live release report — 2026-11-22 UTC

## Verified now
- Server: swadesoul Hostinger. Source repo: `swadesoul/comedy-club`, main.
- Routes: both `themaestroradio.com` and `swadebase.cloud`, `/comedy-club/`, `/comedy-studio/`, `/comedy-api/public`.
- Existing MAESTRO private factory (`maestro-factory.service` on 127.0.0.1:8033) extended by `comedy_studio.py`; no new listener API host or payment system.
- Self-hosted PostgreSQL tables added: `comedy_comedians`, `comedy_routines`, `comedy_assets`, `comedy_batch_plans` under existing `maestroradio` schema; RLS and restrictive grants.
- Six registered original cast profiles are marked `in_development`; one approved script attached to founder owner identity; one *real* original audio master staged privately for review.
- Public JSON returns six profiles and **zero publicly released audio**. No demo array remains in public page source. Six original SVG illustrations and one original logo SVG installed.
- 16 automated Node validation tests passed. Actual headless Chromium rendered six real profiles on MAESTRO public route. Private read/write/media endpoints require bearer; unsigned attempts return 401.
- Real Backblaze upload checksum/readback and private ranged MP3 retrieval verified. 179.952-second mastered MP3 output passed file/duration/peak checks; subjective listening review still pending.
- Legacy `/comedy-studio-preview/` redirects to `/comedy-studio/`; no mock/placeholder studio public routes.
- **No public or adult station added, no radio schedule or Maestro Mix reels changed, no customer payment products activated.**

## Outstanding live release gates
Real customer session visual QA, first image upload via actual signed-in browser, production worker execution for 10 routines, human listening review, commercial Stripe recurring setup/fulfillment and real station staging/airplay. These are not certified. No mock data or fake audio inserted to conceal open gates.

## Recovery
- Existing radio sources, playlists, PWA and music streams are unchanged.
- Nginx backups: `/opt/swadebase/backups/comedy-api-20261122T094228Z`, `/opt/swadebase/backups/comedy-studio-live-20261122T094713Z` (check actual generated directories), and `/opt/swadebase/backups/comedy-remove-preview-20261122T095151Z`.
- Original pre-adapter factory handler reproducible from `/opt/swadebase/backups/comedy-api-ROLLBACK_FACTORY.py`; do not overwrite newer unrelated work while restoring. Roll back selectively, validate `nginx -t` and restore/restart only the affected factory if necessary.
- Preserve tables, licensed media assets, and author records on rollback; do not delete real customer content.
