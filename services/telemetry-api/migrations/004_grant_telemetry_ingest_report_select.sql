\set ON_ERROR_STOP on

BEGIN;

SET LOCAL ROLE telemetry_owner;

GRANT SELECT (event_type, timestamp, tags)
    ON TABLE public.telemetry_events TO telemetry_ingest;

COMMIT;