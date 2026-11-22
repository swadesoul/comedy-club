# MAESTRO Comedy Club — genuine GPT Live One first take

**Date:** November 22, 2026. **Status:** successful controlled opening-take capture; private human review. **Not a finished 3-minute routine, not broadcast.**

## Verified source and recording

- Owner specifically authorized **one** $0.05 maximum test. The server-only runner completed a **single** OpenAI Primary Live WebSocket session, with model explicitly confirmed by provider: `gpt-live-1.1`. No paid retry.
- Exact provider session ID retained in the owner-private receipt and RESINGLAB project generation metadata. Provider session reported `usage.seconds: 24` and `reason: close_requested`.
- Captured **24.98 seconds** of audio, 24 kHz mono PCM16 WAV, sha256 `9811a576d77c8aff6edac2b651cd8b78f60ee2aff2dc60bce8e3269c8d11d5b9`. The mono MP3 export is 25.032 seconds container duration, sha256 `d11781f1dbe117187b700dcdaccdd0d7c2abdc55c87ef7c076fcf34693ab5b81`.
- Technical audio scan: max peak about −6.96 dBFS; zero NaN and Inf audio values.
- OpenAI session billing usage was 24 seconds. **Estimated** charge is roughly $0.02 at $0.05 per minute; provider did not supply a final USD invoice, and a budget limit in local code cannot replace a platform-enforced account billing cap.
- Private B2 upload: `comedy/review/<owner>/<routine>/smart-house-gpt-live-1.1-first-take-unreviewed.mp3`, SHA256 verified. Real B2 ranged readback returned HTTP 206 and an MP3 header.
- Recorded as one real `resinglab.resinglab_generations` `spoken_word` generation with provider `openai`, model `gpt-live-1.1`, completed generation state and metadata stating **needs_review / not published**.
- Private studio endpoint `GET /comedy-api/live-take/<routine-id>` is restricted to authenticated authorized owner, returns a short-lived B2 URL. Other-tenant direct access denied; unauthenticated HTTP access returns 401.
- Existing Smart House private RESINGLAB V3 full master, original approved script and source production receipts are **unchanged**. No radio or MAESTRO MIX station injection, no public catalog audio and no adult-content change.

## Listener access and next-stage quality control

Owner: sign in to https://themaestroradio.com/comedy-studio/ and open **Saved routines** → *The Smart House That Snitched on Me* → **Review GPT Live One take (25s)**. The control is separate from the longer original **Review audio** button. It only previews the authentic opening take.

Founder listening review must assess character consistency, pacing, natural comedic delivery and script fidelity. This is not proof of a finished full routine. Once satisfied and a **new budget** is authorized, record the remaining sections separately through the same auditable live sessions and FFmpeg-assemble with the room-first laugh, liner, realistic audience and light mic ambience. Do not replay or spend again based on this one-time approval.

## Technical verification

- Original recording WAV confirmed 24 kHz mono, 24.98 s; MP3 verified 25.032 s.
- 26/26 foundation tests passed, including Live capture identity, sample framing, required signed closure, budget rejection, and owner-only review route.
- Studio routes on both MAESTRO RADIO and SWADEBASE returned HTTP 200. Unauthenticated private endpoint returned 401; public catalog still returned zero approved routines.
- Source: `engine/gpt-live-capture.mjs`, `scripts/run-gpt-live-take.mjs`, `engine/comedy_studio.py`, and `studio/production.html`.
- Live deploy rollback (if needed): `/opt/swadebase/backups/comedy-live-one-private-review-20261122T110316Z/`. Restore both prior backend module and studio HTML; restart only `maestro-factory.service` after lock coordination and smoke tests. Leave media and database records intact.
