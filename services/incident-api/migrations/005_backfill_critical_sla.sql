UPDATE incidents
SET sla_target_at = strftime('%Y-%m-%dT%H:%M:%f+00:00', datetime(created_at, '+24 hours'))
WHERE severity = 'critical' AND sla_target_at IS NULL;
