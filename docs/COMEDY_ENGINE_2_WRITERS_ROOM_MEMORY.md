# MAESTRO Comedy Engine 2.0 — Writers' Room and Memory Implementation Contract

Status: APPROVED DESIGN / DEVELOPMENT BRANCH ONLY. This document does not certify a deployed worker, active memory persistence, or broadcast.

## Canonical boundaries
- Use the existing SWADEBASE auth and tenant-scoped PostgreSQL records; no new database, service, or paid generator.
- Existing official cast IDs and public profile URLs remain stable.
- Character definitions: `config/comedian-bibles.v2.json`. Only original fictional character designs; do not imitate a real comedian's distinctive voice, performance or copyrighted routines.
- No external provider cost, bulk render or station publishing is authorized by this document.

## Data model to integrate into existing SWADEBASE / MAESTRO backend
Store normalized tenant-scoped data rather than relying on model context alone:
1. `comedy_character_bible_versions` (tenant_id, comedian_id, version, bible_json, approved_by, approved_at, created_at) with immutable approved version snapshots.
2. `comedy_recurring_characters` (tenant_id, comedian_id, character_id, canon_json, voice_asset_id nullable, status) and unique (tenant_id, comedian_id, character_id).
3. `comedy_story_continuity` (tenant_id, comedian_id, routine_id, character_id nullable, event_type, summary, canonical_status, timestamp), append-only approved events.
4. `comedy_joke_fingerprints` (tenant_id, comedian_id, routine_id, normalized_joke_hash, semantic_summary, approval_status, created_at) for no-repeat candidates; semantic similarity should trigger editorial review, not falsely assert copying.
5. `comedy_routine_production_snapshots` (tenant_id, routine_id, bible_version, script_revision, runtime_rating, profanity_policy, resolved_character_ids, cue_plan_json, approval_state, timestamps), immutable after master approval.
Create migrations only after inspecting the actual existing schema and RLS. Enforce tenant scoping and existing admin role on all writes and prevent cross-tenant retrieval.

## Rating and language rules
- PG performer: no profanity even on an R-rated slot; cannot override in request, script revisions, import, TTS, or publishing.
- PG-13 performer: may use only configured mild language; R slot does not relax a character bible restriction.
- R performer: adult language allowed, not required; explicit selected routine rating can constrain them to clean.
- Normalize profanity validation in the backend and inspect spoken-script text before dispatch; don't rely solely on prompts.
- The rating of the finished routine is the stricter of its actual content and its requested limit; never silently downgrade adult content.
- R masters must remain private unless an actual protected adult stream with applicable age/access controls is verified.

## Writers' room state machine
idea -> outline -> first_draft -> punchline_edit -> voice_character_review -> director_cues -> profanity_rights_qa -> owner_script_approval -> render_authorization -> rendered_stems -> mix_qa -> owner_audio_review -> approved_master -> optional_maestro_staging -> broadcast_verification.
Every transition records who approved it and what assets were used. A rejection returns only affected sections to the prior editing stage. No unapproved auto-publishing or unbounded paid retries.

## Structured script contract
Use an array of `beats` with `beat_id`, `speaker_id`, `dialogue`, `delivery_direction`, `setup_or_punchline`, `callback_to_beat_id`, `audience_cue` (optional), and `max_pause_ms`. Audience cues specify intensity, section (front/middle/rear), reaction class, and whether delayed; they are editorial suggestions until word-level speech end times are measured.
Explicitly mark recurring-character occurrences and summarize approved canon additions after approval, not from unreviewed model output.

## Stage and sound
- Open with varied residual laughter, not the same clip on every episode.
- Separate comedian voice, recurring character voices, individual crowd-work responders, front/middle/rear audience beds, ambience, and mic/room effects.
- Align laughter start after the actual measured final punchline word, allow natural decay, and make room for silence and recovery.
- Use natural stereo width and subtle short stage-mic reverb; preserve intelligibility and avoid 1-voice-sounding cloned laughter.
- Reuse licensed/owned crowd assets and partial voice regeneration to minimize provider spend.

## Memory retrieval and write policy
Read: pull approved comedian bible, relevant approved character canon, prior *approved* jokes/callbacks, and newest approved story continuity, all tenant-scoped. Generate a small bounded context rather than loading full transcripts. Write: create proposed memories with provenance during drafting; commit canon and joke fingerprints ONLY after script/audio approval. Failed or discarded routines never become canon. Preserve version history and allow founder corrections to supersede canon without deleting production provenance.

## Required tests before merging
1. PG comedian + R routine does not permit cursing, even on import or rewrite.
2. Adult comedian + PG routine produces clean speech and content review.
3. Character ID remains identical across consecutive approved episodes.
4. Previous joke candidate receives a repetition warning; no auto rejection without editorial review.
5. No continuity memory from an unapproved or abandoned draft is returned as canon.
6. Cross-tenant memory requests and writes are forbidden.
7. Actual punchline timing controls laugh alignment; timing does not mask the last word.
8. 10-routine batch planning cannot dispatch vendor spend without authorization.
9. R audio cannot route to public/clean MAESTRO stations.
10. Existing Smart House pilot, public catalog, auth and draft-save paths remain unaffected.

## Next implementation gate
Review current SQL migrations and `engine/comedy_studio.py`, then implement RLS-backed memory endpoints and adapter-aware prompt assembly in the existing service. Add unit/integration tests. Do not merge, deploy or claim working audio until all required checks pass and the owner approves produced audio.
