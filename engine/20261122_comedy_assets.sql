-- Uploaded customer-owned studio artwork, stored in existing Backblaze B2.
CREATE TABLE IF NOT EXISTS maestroradio.comedy_assets (
 id uuid PRIMARY KEY,
 owner_id uuid NOT NULL,
 object_key text NOT NULL UNIQUE,
 label text NOT NULL CHECK(length(label) BETWEEN 1 AND 140),
 mime_type text NOT NULL DEFAULT 'image/webp' CHECK(mime_type='image/webp'),
 bytes bigint NOT NULL CHECK(bytes BETWEEN 1 AND 5242880),
 sha256 text NOT NULL,
 consent_confirmed boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE maestroradio.comedy_assets ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON maestroradio.comedy_assets FROM PUBLIC,anon,authenticated;
GRANT SELECT,INSERT ON maestroradio.comedy_assets TO service_role;
NOTIFY pgrst,'reload schema';
