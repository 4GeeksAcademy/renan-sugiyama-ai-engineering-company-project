---
title: "Folder organization by responsibility"
description: "Create and maintain a single-purpose repository layout so each top-level folder has one clear responsibility."
applicationType: Always
---

## Applies to

- repository root directories
- newly created project folders
- any new subfolder added under the repo
- folder names that define services, apps, data, AI, infrastructure, or shared assets

## Do

- Place backend APIs and workers under `services/`.
- Place user-facing apps under `uis/`.
- Place datasets, ETL jobs, and processed outputs under `data/`.
- Place AI agents under `agents/`.
- Place reusable AI capabilities under `skills/`.
- Place MCP servers under `mcps/`.
- Place automation workflows under `workflows/`.
- Place shared libraries under `packages/`.
- Place loose shared assets under `shared/`.
- Place deployment and infrastructure files under `infra/`.
- Place cross-project documentation under `docs/`.
- Place small helper scripts under `scripts/`.
- Place structured internal tools under `internal/`.

## Do not

- Do not place UI code, backend code, data code, and AI code in the same directory.
- Do not store APIs in `uis/`.
- Do not store frontends in `services/`.
- Do not store datasets in `agents/`.
- Do not store infrastructure files in `data/`.
- Do not create a new top-level folder without assigning it a single responsibility.

## Verification

A change is compliant only if each new or moved component matches one of the allowed top-level folders above and does not mix responsibilities across layers.
