\set ON_ERROR_STOP on

BEGIN;

SET LOCAL ROLE telemetry_owner;

ALTER TABLE public.telemetry_events
    ALTER COLUMN service DROP NOT NULL;

COMMIT;