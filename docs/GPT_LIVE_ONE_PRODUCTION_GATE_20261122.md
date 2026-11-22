# Smart House — GPT Live One recording gate (2026-11-22)

## Verified state

Smart House remains private, marked `needs_review`, and has **not** been re-recorded with GPT Live One. The latest actual recording in RESINGLAB is V3 (165.117 seconds of Kokoro-origin voice stems and authentic licensed crowd reactions). It must never be relabeled as GPT Live One.

## Reused infrastructure

- The canonical approved script is `routines/001-smart-house-that-snitched.md` (do not replace it without approval).
- `engine/gpt-live-capture.mjs` is the recording ledger for the **primary GPT-Live WebSocket**, validating the resolved model and session ID and preserving output PCM16LE audio as a real WAV with SHA256 and provider usage. It refuses output without a clean terminal `session.closed` event.
- `scripts/run-gpt-live-take.mjs` is a **server-only** paid-session adapter with a 5–30-second hard session limit. It selects `gpt-live-1.1` by default (or exact `gpt-live-1` when available), fixes mono PCM16 at 24kHz, and sends a spoken cue through the audio-first API. **Never include its API key, cost controls or runner in the public browser.**
- `scripts/test_gpt_live_assembly.py` verifies two-part FFmpeg assembly on existing audio, not GPT-Live generation.
- Retain existing RESINGLAB spoken-word project, B2 media and admin role enforcement; no new service stack, station, or billable client API.

## Configuration and cost safeguards

OpenAI official primary Live API: `wss://api.openai.com/v1/live/sessions`. First send `session.start` with model, output voice, and PCM 24kHz format. Then wait for `session.started` and stream real PCM input using `session.input_audio.append`. Collect `session.output_audio.delta` bytes in arrival order. Send `session.close`; require acknowledged `session.closed` before claiming recording is complete. Avoid the legacy Realtime `response.output_audio.delta` event and avoid using Replicate Kokoro as a proxy.

**Important:** The owner has not authorized an external-vendor spend amount for this session. Under SWADEBASE standing rule 13 the vendor spend allowance is **$0**. The runner must not be executed in paid mode until the owner explicitly authorizes a small, bounded amount (recommend one test <= $0.05). The technical session duration is capped in code at 30 seconds with a cost ceiling; actual provider usage and billing may differ and must be reconciled from the final event, not guessed.

Example preparatory, no-charge run:

`node scripts/run-gpt-live-take.mjs --dry-run`

Paid mode needs all of: the server-only OpenAI credential, `COMEDY_LIVE_PAID_APPROVED=YES`, `COMEDY_LIVE_MAX_USD` as an explicitly authorized dollar cap <= $0.10, `COMEDY_LIVE_MAX_SECONDS` <= 30, `COMEDY_LIVE_CUE_FILE` containing a real licensed spoken audio cue, `COMEDY_LIVE_SCRIPT_FILE` with the authorized single scene, and a private output directory. Never start a session in response to opening a public page or planning a batch.

## Acceptance plan

1. After explicit cost approval, do **one** <=30-second GPT Live One take of an original Marcus opening scene, preserving the provider-resolved model/session provenance. Abort on provider errors, missing audio, missing closure or over-limit audio.
2. Human-listen to genuine performance cadence and mic sound. If unsuitable, do not retry without further owner authorization.
3. For approved segments, repeat under separately accounted limits. Preserve distinct stage voice/crowd reply tracks, place real venue laughter at zero seconds, then the five-second station liner, and apply short subtle mic reflections without burying the script.
4. FFmpeg-assemble and QA the finished <=180-second master; store to private B2 review path, update the existing ReSingLab spoken-word project with true provider/model/usage data, and require founder listening approval.
5. Only after approval allow authorized MAESTRO station selection; no automatic airplay or Maestro Mix reel insertion.

## Evidence

- `node --test tests/*.test.mjs`: **23 passed**, including no-spend dry-run, missing cost-authorization refusal, resolved-model checks, PCM WAV roundtrip and FFmpeg split/rejoin safety.
- No production GPT Live recording, Live session ID, OpenAI voice invoice, customer charge, station publication, or new public media was created in this change.
- Source documentation: https://developers.openai.com/api/reference/resources/live/primary-websocket
