# Smart House — real 60-second owner-review sample (2026-11-23)

The owner requested an actual 60-second sample, **intro first, then audience response**, without cutting off a joke.

## Delivered

- Version: `pilot-001-sixty-second-review` (private, unreviewed).
- Opens with the existing five-second MAESTRO Comedy Club announcer intro.
- Begins audience reaction AFTER intro, 3.35 seconds.
- Includes the first three complete Marcus segments (the smart house introduction, the cheesecake/security-camera escalation, and the mortgage punchline) with shorter but complete audience reaction tails.
- Real original source recording: RESINGLAB spoken-word V3 with local Kokoro voice stems and a licensed CC0 stereo theater audience; **NOT a new GPT Live One or MOSS-TTS recording**.
- Source was edited with FFmpeg without paid voice regeneration and without truncating dialogue.
- WAV length exactly **60.000 seconds**; MP3 container **60.048 seconds** at 160kbps stereo.
- MP3 SHA256 `42dfa3bf91e2eb745b8c160f2a5b096432f650e496ab889729f7ce2623d883a1`.
- B2 private object `comedy/review/<owner>/<routine>/smart-house-60sec-intro-first-unreviewed.mp3`; checksum and authenticated byte-range readback (HTTP 206) verified.
- The previous full private master is unchanged; no public, Maestro Mix or station publication.

## Playback

Authorized founder: https://themaestroradio.com/comedy-studio/ → Saved Routines → The Smart House That Snitched on Me → **Play 60-second Smart House sample**.

The existing factory validates ownership and returns a 15-minute signed Backblaze URL; unsigned requests return HTTP 401 and other-tenant requests are denied. Both MAESTRO and SWADEBASE studio routes returned HTTP 200; headless Chromium displayed the exact new playback button and not the previous Station Not Found error.

Source: `scripts/create_smart_house_sixty_second_sample.py`, `engine/comedy_studio.py`, `studio/production.html`. The exact intro-first cue plan was updated in `engine/comedy.mjs`. 27/27 Node tests passed.

This is a safe **timing and opening-order reference**. It is not presented as the new expressive male-voice engine test, not an approved final mix, and not a guarantee that laughter passes subjective realism review.
