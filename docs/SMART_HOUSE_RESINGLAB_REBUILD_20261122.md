# Smart House — ReSingLab spoken-word rebuild (2026-11-22)

## Render history verified

Approved script: `routines/001-smart-house-that-snitched.md`. Source record: `docs/PILOT_001_REAL_AUDIO_RECEIPT.md`.

- **V1:** Local Kokoro voice performances; a small number of solo-laughter recordings repeated. 179.952-second stereo MP3, owner reported unconvincing audience and dry microphone. The original B2 media object is preserved.
- **V2 experiment:** Earlier FFT crowd-layer attempt was abandoned after the server became resource constrained; NO finished V2 file exists.
- **ReSingLab V3:** Actual rebuilt audio made from original local voice stems using streaming FFmpeg editing. An existing ReSingLab user-owned spoken-word project and generation record were created, without using paid Replicate voice credits.

## Production changes

- Source theater audience: Soundeffects4You / Freesound clip 231258, real stereo crowd recording, published **CC0** (https://freesound.org/people/Soundeffects4You/sounds/231258/). Distinct non-overlapping crowd passages support punchlines, instead of recycling a single person's laugh.
- Every show should begin with in-progress audience laughter. This master starts with 3.35 seconds of actual crowd laughter followed by the established five-second station liner.
- Subtle stage microphone reverb on voices: 47, 83 and 129 ms low-wet reflections. Original fictional comedian identity is maintained.
- Separate announcer, comedian, male/female audience participants, refrigerator and group response. Laughter follows written punchline cues.
- Result: stereo MP3 **165.117 seconds raw / 165.168 seconds container**, 160 kbps, **3,303,885 bytes**, SHA256 `88d6bbc4b4b4f077f344b23d2bb0ff3f23a00087923eab7f6a09cdc2375f41dd`.
- New B2 media is stored under private `comedy/review/<owner>/<routine>/`, with receipt and ranged readback. The original object is retained. The existing MAESTRO Comedy Club routine points to V3 with status `needs_review`, not published.
- ReSingLab `resinglab_projects` has an actual `spoken_word` project; `resinglab_generations` has the V3 completed generation and B2 provenance. The ReSingLab record's metadata says publication is pending human review.

## Provider and QA truth

**This is a ReSingLab spoken-word audio remix of existing Kokoro CPU voice stems, NOT GPT Live One.** The existing RESINGLAB text-to-speech edge function uses **Replicate Kokoro** (paid). A verified GPT Live One recorded performance route remains pending; do not substitute its name for a different model. No external generation credits were spent for V3.

No public or radio production, no MAESTRO Mix placement and no R-rated routing changes have been authorized. Human listening approval and realistic-crowd QA are outstanding. User can open the existing MAESTRO Comedy Studio, select Smart House and click *Review audio* to hear V3 privately.
