#!/usr/bin/env bash
# Starts every backend service and every UI. Stop everything with Ctrl+C.
#
# Stop a single service by port (the others keep running):
#   kill $(lsof -ti :8001)    # inventory-api
#   kill $(lsof -ti :5173)    # inventory-manager
# Ports: telemetry 8000, inventory 8001, dashboard-aggregator 8002, auth 8003,
#        incident 8004, website 3000, dashboard 3001, inventory UI 5173, incident UI 5174
#
# Free all ports after a crash or closed terminal:
#   kill $(lsof -ti :8000,:8001,:8002,:8003,:8004,:3000,:3001,:5173,:5174)
set -u
cd "$(dirname "$0")"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

pids=()
cleanup() {
  trap - INT TERM EXIT
  echo "Stopping all processes..."
  for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null; done
  wait 2>/dev/null
}
trap cleanup INT TERM EXIT

run() {
  local name="$1"; shift
  echo "Starting $name"
  "$@" 2>&1 | sed -u "s/^/[$name] /" &
  pids+=($!)
}

# Backends
run telemetry-api  python -m uvicorn app.main:app --app-dir services/telemetry-api --reload --reload-dir services/telemetry-api --port 8000
run inventory-api  python -m uvicorn app.main:app --app-dir services/inventory-api --reload --reload-dir services/inventory-api --port 8001
run dashboard-api  python -m uvicorn main:app --app-dir services/dashboard-aggregator-api --reload --reload-dir services/dashboard-aggregator-api --port 8002
run auth-api       python -m uvicorn app.main:app --app-dir services/auth-api --reload --reload-dir services/auth-api --port 8003
run incident-api   python -m uvicorn app.main:app --app-dir services/incident-api --reload --reload-dir services/incident-api --port 8004

# Frontends (run `npm install` in each project once beforehand)
run website            npm --prefix uis/website run dev # --port 3000
run dashboard          npm --prefix uis/backoffice/dashboard run dev # --port 3001
run inventory-manager  npm --prefix uis/backoffice/inventory-manager run dev -- --port 5173
run incident-manager   npm --prefix uis/backoffice/incident-manager run dev -- --port 5174

wait
