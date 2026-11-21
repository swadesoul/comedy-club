# Comedy Club Studio — Customer Offer v0.1 (2026-11-21)

**Commercial design approved in conversation:** customer-facing comedy studio upsell, **$250 one-time setup and $99/month**. This document proposes exact included entitlements and guardrails; **source specification only**. No Stripe product, payment link, customer subscription, provider dispatch, live site pricing or deployment has been created.

## Product and onboarding
Product name: **Create Your Own Comedy Club**. Customer receives a branded virtual club and production workspace powered by existing SWADEBASE Comedy Engine, RESINGLAB Speech/Voice Studio and MAESTRO RADIO for optional controlled publishing. Setup is one-time per club. Monthly plan is per club.

The **$250 setup** includes:
- One branded club identity (name, palette, logo uploaded by customer, one venue/stage layout and club description)
- Two **original** fictional comedian character briefs/profiles and their consent-safe unique voice designs
- One licensed/owned announcer profile, one five-second branded liner asset
- One simulated audience room preset with selectable sizes up to 100 seats, 3 recurring fictional audience-reply voices, and licensed/reusable laughter and ambiance stems
- One pilot routine, up to three final minutes, including production review, to verify the room and voices before subscription production
- Automatic onboarding and reusable setup choices saved to the customer's organization and entitlement

The **$99 recurring monthly plan** includes:
- One club, one studio editor seat; two comedian profiles, one announcer, and three recurring fictional audience-reply voices
- Ten **completed approved audio performances** per billing month, max 180s each including 5s reusable club liner; 30 final minutes total
- Up to 10 routines per batch request; batches create zero-cost plans, and rendering requires capped tenant allowance and explicit stage progression
- AI-assisted original writing, customer-authored script paste and permitted .txt import, comedy categories PG / PG-13 / R; callback map and audience reaction cueing
- Simulated 25/50/100-seat audience selection, directional crowd work, laughter/room ambiance, separate stems and automatic timeline suggestions
- Unlimited text edits prior to audio dispatch (subject to reasonable abuse/rate limits); two partial audio correction passes monthly after rendering. Any **new full render** beyond the included production/authorization budget must be previewed and explicitly purchased. Failed provider jobs do not charge a completed-output entitlement until reconciled
- Audio QA preview, download of approved MP3/WAV masters, private library and embeddable audio player; optional handoff for MAESTRO broadcast only after rights, human approval and station-specific eligibility
- Up to 5 GiB of stored production media while active. Export allowed; explicit retention/purge notice and reasonable cancellation grace period must be implemented before launch. No promise of perpetual backups

**Rights:** allow owned/authorized routines and original fictional character voices. No unconsented voice cloning, celebrity impersonation or promises of unrestricted copyrighted comedy use. Existing provider rights and commercial-use terms apply. R means an internal maturity label, not an MPAA film certification; gate distribution based on age, law and platform rules.

## Feature and quota counters (server enforced)
Plan key `comedy_creator_monthly_v1`.
`setup_fee_usd_cents=25000`, `recurring_fee_usd_cents=9900`, `included_routines=10`, `max_seconds_per_routine=180`, `total_final_seconds=1800`, `studio_seats=1`, `comedian_profiles=2`, `audience_reply_profiles=3`, `max_simulated_audience=100`, `storage_bytes=5368709120`, `audio_corrections=2`, `batch_size=10`.

Usage must check BOTH completed routines and finished duration; charge/settle once when verified, retain idempotency keys and provider request receipts. Keep generation attempt cap and cost cap separate; avoid infinite automatic retries. Failed renders require reconciliation and approved bounded retry. No unapproved top-ups. All creative selection presets form an immutable per-routine `prompt_manifest`; metadata stored in existing SWADEBASE tenant tables, media in existing B2 paths, access limited to paying tenant/staff.

## Optional upsells — proposed, not yet authorized checkout catalog
- **+5 routine pack:** $39 per billing cycle, max additional 15 finished minutes; no rollover unless specifically contracted.
- **Additional original comedian:** $39 one-time setup + $10/month per extra active persona; includes storage/voice ID but no extra monthly production minutes.
- **Club capacity 250:** $19/month for additional crowd acoustic presets only; does not mean 250 separately generated voice identities.
- **Second branded club:** $125 one-time + $35/month (shares parent production allowance unless upgraded).
- **Additional 10 audio minutes:** $29 per cycle (within routine maximum and approved retry costs).
- **Live listener participation:** separately scoped, moderated and usage-metered add-on, not included in standard recorded crowd work.
- **Video/animation:** quoted separately, never included in the $99 audio plan.
Publish any of these only after measured workload and pricing acceptance; initial launch could expose 'Request upgrade' without live checkout.

## Unit economics and guardrails
$99 gross monthly revenue is before applicable tax, payment processing, customer support, hosting, model usage and licensing. **Target** direct service COGS <= $20/customer/month, but this is not yet measured or certified. Reusable liners, audience sound assets, partial re-rendering and existing shared infrastructure reduce repeated spend. Do not promise margin until production instrumented: voice characters/generated, seconds output, attempts, credits/USD, storage GiB-days, delivery bandwidth, human review and refunds. Alerts: 50%, 80%, 100% of approved budget; pause at cap; founder super-admin bypasses customer billing but NOT vendor spend or provider rights/quotas.

## Billing, cancellation, rights and rollout
Reuse existing SWADEBASE/Stripe subscription adapter, not a new payments stack. Charge setup once per new club; first billing cycle may collect $349 + applicable taxes if disclosed on checkout. Avoid silently repeating setup charge on renewals, and specify treatment of cancellation/restart, trial, refunds, right to commercial distribution, and rights to source routines and generated outputs. Owner/super-admin exemption remains backend-enforced; it is not an external-vendor credit waiver.

Do not treat an anonymous purchase as authority to create a MAESTRO public station. Require account/tenant setup, payment verification, original content rights, approval, content rating and station access. Private library is default. Record all relevant acceptance, compliance and service status in the existing Bibles/What's New after release.

## Experience
Add a 'Create Your Own Comedy Club' upsell on the existing Comedy Club Studio homepage with setup vs monthly pricing clearly distinguished, transparent limits, a cinematic room builder, examples, onboarding steps and customer studio preview. Two views (owner/admin and tenant/customer) reuse the same SWADEBASE backend and scoped MAESTRO handoff. Production dashboard has draft/import, 10-item queue, staged generation, voice and laugh track lanes, preview/QA and a separate approve-and-publish control.

This document is a draft entitlement and pricing contract; verify production audio cost, customer rights, legal disclosures, checkout taxes and live subscription lifecycle before allowing real purchases.
