\set ON_ERROR_STOP on
\getenv telemetry_owner_password TELEMETRY_OWNER_PASSWORD
\getenv telemetry_ingest_password TELEMETRY_INGEST_PASSWORD

BEGIN;

CREATE ROLE telemetry_owner
    LOGIN PASSWORD :'telemetry_owner_password'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE telemetry_ingest
    LOGIN PASSWORD :'telemetry_ingest_password'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

ALTER DATABASE telemetry OWNER TO telemetry_owner;
REVOKE ALL ON DATABASE telemetry FROM PUBLIC;
GRANT CONNECT ON DATABASE telemetry TO telemetry_ingest;

ALTER SCHEMA public OWNER TO telemetry_owner;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

SET LOCAL ROLE telemetry_owner;

CREATE TABLE public.telemetry_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    service TEXT NOT NULL,
    tags JSONB NOT NULL CHECK (
        jsonb_typeof(tags) = 'object'
        AND tags ? 'event_id'
        AND jsonb_typeof(tags -> 'event_id') = 'string'
    ),
    level TEXT NOT NULL CHECK (level IN ('info', 'error'))
);

CREATE INDEX telemetry_events_timestamp_idx ON public.telemetry_events (timestamp);
CREATE INDEX telemetry_events_event_type_idx ON public.telemetry_events (event_type);
CREATE INDEX telemetry_events_tags_gin_idx ON public.telemetry_events USING GIN (tags);
CREATE UNIQUE INDEX telemetry_events_event_id_uidx
    ON public.telemetry_events ((tags ->> 'event_id'));

REVOKE ALL ON TABLE public.telemetry_events FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO telemetry_ingest;
GRANT INSERT ON TABLE public.telemetry_events TO telemetry_ingest;
GRANT SELECT (id, tags) ON TABLE public.telemetry_events TO telemetry_ingest;
GRANT USAGE ON SEQUENCE public.telemetry_events_id_seq TO telemetry_ingest;

COMMIT;