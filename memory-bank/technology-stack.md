# Technology Stack

## Current project structure

The repository is organized as a monorepo with clear separation by responsibility:

- `services/` for backend APIs and workers
- `uis/` for user-facing apps
- `data/` for datasets and pipelines
- `agents/` for AI agents
- `skills/` for reusable AI capabilities
- `mcps/` for MCP servers
- `workflows/` for automation orchestration
- `packages/` for shared reusable modules
- `shared/` for loose shared assets
- `infra/` for deployment and infrastructure
- `docs/` for cross-project documentation

## Existing technologies and conventions reflected in the repo

### Shared code and contracts

The project already includes a shared package:

- `packages/shared/package.json`
- `packages/shared/types/index.ts`

This indicates a TypeScript-first approach for shared models and contracts.

### Frontend: incident back office

The incident-management back office is implemented under `uis/backoffice` as a
TypeScript React application.

- React and React DOM for the component-based UI.
- TypeScript for the application entrypoint, component props, API responses,
  form payloads, and UI state models.
- Vite for local development and production builds.
- React Router for the incident queue, creation, and detail routes.
- Zustand for local UI state such as filters, pagination, and toast messages.
- TanStack Query for API requests, server-state caching, and invalidation after
  incident mutations.
- Prettier through the VS Code workspace formatter for TypeScript, TSX, and CSS
  files on save.

The back office consumes the centralized FastAPI service through its incident,
catalog, summary, assignment, lifecycle, and audit endpoints. Its local
commands are:

```bash
npm install
npm run dev
npm run typecheck
npm run build
```

### Intended runtime model

The repository guidance suggests a centralized backend service and recommends a single entry point for company services. The intended backend is described as a FastAPI service, even though the implementation has not yet been created.

### Intended AI and automation model

The project is designed to support:

- AI agents in `agents/`
- reusable agent capabilities in `skills/`
- external integrations via MCP servers in `mcps/`
- automation and workflow orchestration in `workflows/`

### Data and evaluation model

The repository anticipates a data pipeline model:

- raw data
- processing pipelines
- cleaned intermediate outputs
- evaluation datasets

## Current implementation status

The repository now contains a working incident-management slice, although it is
not yet a complete company-wide application stack. The following parts remain
outside the current implementation:

- root `docker-compose.yml`
- root package manager configuration
- working AI agent runtime

Implemented for the incident-management scope:

- FastAPI incident service under `services/api`
- SQLite persistence and catalog repair migrations
- TypeScript React back office under `uis/backoffice`
- Shared TypeScript incident contracts under `packages/shared`
- API contract tests and frontend typecheck/build scripts

## Expected technology direction

The project supports a modern AI engineering architecture with a combination of:

- Python backend services (FastAPI expected)
- TypeScript React frontends and shared contracts/packages
- Vite-based frontend tooling
- React Router for client-side navigation
- Zustand for local UI state
- TanStack Query for server state and API cache management
- LLM-based AI agents and skills
- workflow orchestration tools
- datasets and evaluation pipelines
- modular infrastructure and deployment configs
