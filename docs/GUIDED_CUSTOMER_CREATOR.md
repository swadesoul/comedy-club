# Create Your Own Comedy Club — Guided Customer Setup

**Status 2026-11-21:** Companion ChatGPT Skill packaged separately as `comedy-club-creator`. This file is the versioned workflow contract for app integration. The customer onboarding UI and payment/generation integration are not live until tested.

## Customer journey (one question per stage)

1. **Club identity:** propose 3 club names, show name, use (family podcast, stand-up, radio, business, comedy special), select own name or custom.
2. **Look and imagery:** offer default cinematic club look, **upload own logo**, **upload stage/interior inspiration**, **upload character/host photo** (only with rights and any applicable performer consent). Accept .png/.jpg/.webp. Persist approved original to existing scoped B2 assets; never store bytes or secrets in prompts.
3. **Stage and audience:** select audience size 25/50/100 for the $99 standard tier. Choose room acoustics, laughter intensity, spontaneous-looking crowd replies, and audience personalities. Audience size is an acoustic simulation, not 100 separately generated individual speakers.
4. **Original cast:** guide creation of 2 comedian personas (name, mood, point of view, age-range presentation, and consent-safe original voice). Include 3 recurring fictional audience speakers; never clone a celebrity or impersonate someone without consent.
5. **Content:** PG, PG-13, or R internal category per routine; adult category stays out of general/underage distribution. Set duration up to 180s including reusable 5s intro.
6. **Routines:** write with AI, paste, import owned .txt, or pick an original story premise; flag opening seed, escalation, callback, final reveal, and reaction cues. Save source/rights and versioned revisions.
7. **Automated production:** select up to 10 routines, view a generated manifest and estimated usage, plan at zero cost. Actual RESINGLAB TTS and audience stems require authorized capped dispatch. Use existing SWADEBASE queue and durable receipts; no automatic spending from preview controls.
8. **Review and release:** inspect final voice/laughter lanes; listen, fix targeted timing, approve master; optional stage in a permitted MAESTRO comedy library only. Staging is not broadcasting.

## Skill intake and export
The current standalone Skill supports one-at-a-time conversation questions and outputs a `comedy-club-creator-v1` manifest with club, rights-confirmed assets, room, cast, rating policy, liner, routines, batch, cost authorization, and publish approval. The packaged Skill validates manifests locally. Product code should verify the exact schema again server-side; client answers are never grant or payment authority.

## Commercial package — proposed entitlements
**$250 one-time setup + $99/month**, 1 branded club, 2 original comedians, 1 announcer, 3 fictional recurring crowd-work audience voices, max 100 seats, 10 finished audio routines per billing cycle, max 3m each and 30m combined, two partial audio corrections, 5GiB live customer media. Batch planning is free of model cost. Third-party credit cost is not waived by customer membership. See `docs/CREATOR_STUDIO_COMMERCIAL_OFFER.md` for details and upgrade proposals.

## Architecture
The `swadesoul/comedy-club` repo is canonical for domain templates and customer configuration. Deploy only after existing SWADEBASE identity/tenant adapter, existing RESINGLAB speech renderer and existing MAESTRO station library paths are integrated and tested. Do not duplicate a database, scheduler, provider adapter or admin identity. Do not auto-publish uploaded photos or imported copyrighted material.

## Deployment status
Source-only. No live customer checkout, onboarding route, provider rendering or radio broadcast certification is claimed by this file.
