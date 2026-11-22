-- Persistent owner-approved batch planning; no speech-provider dispatch.
CREATE TABLE IF NOT EXISTS maestroradio.comedy_batch_plans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL,
  request_id uuid NOT NULL,
  routine_ids uuid[] NOT NULL CHECK(cardinality(routine_ids) BETWEEN 1 AND 10),
  prompt_manifest jsonb NOT NULL,
  status text NOT NULL DEFAULT 'planned' CHECK(status IN ('planned','authorized','rendering','needs_review','completed','failed','cancelled')),
  external_spend_authorized boolean NOT NULL DEFAULT false,
  provider_spend_cap_cents integer NOT NULL DEFAULT 0 CHECK(provider_spend_cap_cents >= 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (owner_id,request_id),
  CHECK (external_spend_authorized=false OR provider_spend_cap_cents>0)
);
ALTER TABLE maestroradio.comedy_batch_plans ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON maestroradio.comedy_batch_plans FROM PUBLIC,anon,authenticated;
GRANT SELECT,INSERT,UPDATE ON maestroradio.comedy_batch_plans TO service_role;
NOTIFY pgrst,'reload schema';
