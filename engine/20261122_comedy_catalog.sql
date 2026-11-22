-- Maestro Comedy Club durable catalog, separate from artist/music entities.
-- Additive. Backend service role accesses private drafts; anon access gets no grants.
BEGIN;
CREATE TABLE IF NOT EXISTS maestroradio.comedy_comedians (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 owner_id uuid,
 slug text NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9-]{2,64}$'),
 display_name text NOT NULL CHECK (length(display_name) BETWEEN 2 AND 120),
 biography text NOT NULL DEFAULT '',
 artwork_path text,
 default_rating text NOT NULL DEFAULT 'PG' CHECK(default_rating IN ('PG','PG-13','R')),
 status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','in_development','published','retired')),
 rights_confirmed boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS maestroradio.comedy_routines (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 owner_id uuid NOT NULL,
 comedian_id uuid NOT NULL REFERENCES maestroradio.comedy_comedians(id),
 title text NOT NULL CHECK(length(title) BETWEEN 3 AND 200),
 script text NOT NULL CHECK(length(script) BETWEEN 20 AND 16000),
 rating text NOT NULL CHECK(rating IN ('PG','PG-13','R')),
 state text NOT NULL DEFAULT 'draft' CHECK(state IN ('draft','script_approved','rendering','needs_review','approved','published','retired')),
 audio_b2_key text,
 duration_ms integer CHECK(duration_ms BETWEEN 1000 AND 180000),
 audio_reviewed_at timestamptz,
 rights_confirmed boolean NOT NULL DEFAULT false,
 station_id uuid,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 CONSTRAINT comedy_published_media_check CHECK(
   state <> 'published' OR (audio_b2_key IS NOT NULL AND duration_ms IS NOT NULL
     AND audio_reviewed_at IS NOT NULL AND rights_confirmed)
 )
);
CREATE INDEX IF NOT EXISTS comedy_routines_public_idx
 ON maestroradio.comedy_routines(comedian_id,created_at DESC)
 WHERE state='published';
ALTER TABLE maestroradio.comedy_comedians ENABLE ROW LEVEL SECURITY;
ALTER TABLE maestroradio.comedy_routines ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON maestroradio.comedy_comedians FROM PUBLIC,anon,authenticated;
REVOKE ALL ON maestroradio.comedy_routines FROM PUBLIC,anon,authenticated;
COMMIT;
-- Required grants for the existing private backend service role only.
GRANT SELECT,INSERT,UPDATE ON maestroradio.comedy_comedians, maestroradio.comedy_routines TO service_role;
NOTIFY pgrst,'reload schema';
