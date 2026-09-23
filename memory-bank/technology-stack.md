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

### Not implemented yet

The repo is currently a starter template and does not yet contain a complete runnable application stack such as:

- root `docker-compose.yml`
- root package manager configuration
- full backend service implementation
- full frontend application implementation
- working AI agent runtime

## Expected technology direction

The project is intended to support a modern AI engineering architecture with a combination of:

- Python backend services (FastAPI expected)
- TypeScript shared contracts and packages
- LLM-based AI agents and skills
- workflow orchestration tools
- datasets and evaluation pipelines
- modular infrastructure and deployment configs
