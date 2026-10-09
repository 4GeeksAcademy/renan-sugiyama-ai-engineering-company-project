#!/bin/sh
set -eu

(cd website && exec ./node_modules/.bin/next dev --hostname 0.0.0.0 --port 3000) &
website_pid=$!

(cd backoffice/dashboard && exec ./node_modules/.bin/next dev --hostname 0.0.0.0 --port 3001) &
dashboard_pid=$!

trap 'kill "$website_pid" "$dashboard_pid" 2>/dev/null || true' INT TERM
wait