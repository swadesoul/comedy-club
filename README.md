# MAESTRO COMEDY CLUB

**Live database-backed public Comedy Club and authenticated producer studio.**
Production certification: **PARTIAL**. First real audio draft staged for owner listening review; no public audio or radio slot spin is released until verified and approved.

## Live product routes

- Listener catalog: https://themaestroradio.com/comedy-club/ and https://swadebase.cloud/comedy-club/
- Real Studio: https://themaestroradio.com/comedy-studio/ and https://swadebase.cloud/comedy-studio/
- Real public JSON (read-only): /comedy-api/public on both origins
- Legacy /comedy-studio-preview/ redirects to the real studio; the mock-style offline prototype was retired.

## What actually works

- The public page fetches the real SWADEBASE-hosted PostgreSQL `maestroradio.comedy_comedians` and published `comedy_routines` records through the existing MAESTRO Python factory, not hardcoded content.
- Six original official comedian personas have durable `in_development` records, distinct original illustration assets, real profile URLs and honest pre-release labels. No sample performer rows, fake plays, invented listening numbers or fake audio.
- The authorized Studio saves real script drafts, accepts .txt script imports, confirms rights, uploads JPG/PNG/WebP media (up to 5MiB) to existing Backblaze B2 after image validation, and persists up to ten selected owned scripts in a zero-credit batch plan.
- Batch manifest records chosen real comedian, rating, audience size, callback/crowd-work preferences, acoustic preset, owned art ID, and an optional real eligible MAESTRO station.
- Stations come from the actual tenant-scoped MAESTRO station library; R rated content is excluded from general-audience stations. No autopublishing.
- The first user-approved Marcus `Smart House` routine is a **real** 179.952-second stereo MP3 produced by existing local Kokoro CPU speech with separately rendered speakers and licensed public-domain/CC0 applause and laughter; stored and checksum-verified in existing B2, status `needs_review`. It is accessible only to its authorized owner in the Studio's **Review audio** control.
- 16 Node tests passed at rollout, Nginx and private MAESTRO factory checked. Unauthenticated writes return HTTP 401.

## Production source and infrastructure

- `public/index.html` + `public/comedians/*` and `public/assets/*`: listener experience and original artwork
- `studio/production.html`: real session-backed studio; no stored demo content
- `engine/comedy_studio.py`: versioned module for the **existing** private MAESTRO factory, mounted at `/comedy/*` inside its current handler (do not start a duplicate service).
- `engine/20261122_comedy_catalog.sql`, `engine/20261122_comedy_assets.sql`, `engine/20261122_comedy_batches.sql`: private database tables, owner controls, production plans and B2 media metadata. Schema belongs to existing self-hosted SWADEBASE Postgres; service role only and RLS enabled; never exposes a public write endpoint.
- `scripts/render_approved_pilot.py`: first offline zero-vendor-cost original render. Server-only voice token, never commit secrets. See `docs/PILOT_001_REAL_AUDIO_RECEIPT.md`.

## Owner and customer protections

- Production saves require valid existing sign-in and currently restricted MAESTRO administrator role; tenant-facing $250 setup/$99 recurring customer checkout is **not** launched or certified.
- No user-facing generated audio is represented as finished without actual audio file, verified provenance, acceptable timing, rights, reviewer approval and eligible station.
- Published audio must have `state=published`, source in the `comedy/approved/` B2 namespace, ownership/rights confirmation, measured duration and audio-review timestamp. R-rated masters are not exposed via public API until an actual protected adult stream is verified.
- No paid provider used for the pilot. SWADEBASE founder/admin platform charges stay exempt, but external provider costs still require caps.
- Only existing MAESTRO/AzuraCast station scheduler can schedule an approved master. No direct broadcast until station-specific human authorization. Maestro Mix uses its existing real game: it cannot feature an unreleased routine.

## Remaining acceptance gates

1. **Listen and approve or request revisions** to pilot audio; dynamic laughter timing still needs subjective review. Only then promote from B2 private review to `comedy/approved/`, set reviewer audit timestamp, publish if license/rating compliant.
2. Verify real customer login, first-time logo/photo upload, B2 retrieval, script and batch save in desktop/iPad Safari, not just server/integration tests; no claim of customer on-boarding certification yet.
3. Implement reusable multi-routine render worker via existing RESINGLAB/voice adapters, provider cost cap, durable job progress, retries and QA; currently real *batch planning* is available, not automated audio execution.
4. Implement final authenticated MAESTRO media staging and actual station playlist readback, and optional Maestro Mix reel promotion only for published approved audio.
5. Complete Stripe products, checkout, subscription entitlements and webhooks with real cancellation and usage lifecycle tests before charging any customer.
6. Obtain approval for final brand artwork/cast portraits if future images replace current original SVG illustrations.

See release record `docs/DEPLOYMENT_20261122.md` for evidence, restrictions and rollback.
