# Back-office applications

The incident manager and inventory manager are existing Vite projects; the
operations dashboard uses Next.js App Router. New standalone frontend
applications must use Next.js App Router and TypeScript. Each package has its
own dependencies, build output, API configuration, and development server.

## Incident manager

```sh
cd incident-manager
npm install
npm run dev
```

## Inventory manager

````sh
cd inventory-manager
npm install
npm run dev
```# Nexova incident back office

TypeScript React back office for phase 4 of the incident-management plan. It uses Vite, React Router, Zustand for UI state, and TanStack Query for server state and cache invalidation.

## Run locally

1. Install frontend dependencies: `npm install`.
2. Start the API from the repository root: `.venv/bin/uvicorn app.main:app --app-dir services/incident-api --reload`.
3. Start the UI: `npm run dev`.
4. Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

The UI sends `X-Backoffice-User: local-user` by default. Create that active local user in the API database before using protected endpoints:

```sql
INSERT OR IGNORE INTO backoffice_users (id, role) VALUES ('local-user', 'backoffice');
````

Set `window.INCIDENT_API_URL` before loading `app.tsx` when the API is hosted elsewhere.
