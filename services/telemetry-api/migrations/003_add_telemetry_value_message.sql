\set ON_ERROR_STOP on

BEGIN;

SET LOCAL ROLE telemetry_owner;

ALTER TABLE public.telemetry_events
    ADD COLUMN value DOUBLE PRECISION,
    ADD COLUMN message TEXT;

COMMIT;