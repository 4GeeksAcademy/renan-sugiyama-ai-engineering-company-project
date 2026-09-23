# Project Conventions and Runtime Proposal

## Overview

This document summarizes the conventions already established in the repository and includes a proposal to improve the monorepo’s runtime and dependency management model.

---

## Conventions already established in the codebase

### 1) Folder-by-responsibility organization

The repository is organized by domain and responsibility rather than by feature or application type.

Top-level folders include:

- `services/` — backend APIs and workers
- `uis/` — frontend apps and user interfaces
- `data/` — datasets, pipelines, and processing
- `agents/` — AI agents and assistants
- `skills/` — reusable AI capabilities
- `mcps/` — Model Context Protocol servers
- `workflows/` — automation and orchestration
- `packages/` — shared reusable libraries
- `shared/` — loose shared assets
- `docs/` — cross-cutting documentation
- `infra/` — infrastructure and deployment
- `scripts/` — helper automation scripts
- `internal/` — internal developer tools

This reflects a clear project convention: each folder owns a single layer of responsibility.

### 2) Descriptive, lowercase naming

The codebase follows a simple naming convention based on clarity and consistency:

- lowercase folder names
- descriptive domain names
- short, readable names that map to real responsibilities
- package names following a scoped pattern such as `@repo/shared-types`

Examples from the repo include:

- `services`
- `agents`
- `data`
- `shared`
- `packages/shared`

This supports discoverability and keeps the project easy to navigate.

### 3) Separation of concerns

The repo is intentionally structured to avoid mixing responsibilities in the same layer.

Examples:

- UI logic lives in `uis/`
- API logic lives in `services/`
- Data transformation lives in `data/`
- AI logic lives in `agents/` and `skills/`
- Deployment concerns live in `infra/`
- Cross-system flows live in `workflows/`

This is a strong architectural pattern and is explicitly reinforced by the repo guidance.

### 4) Shared code as reusable modules

The project already expects common logic and domain contracts to be centralized in a shared package rather than duplicated across apps.

This is represented by the package structure:

- `packages/shared/package.json`
- `packages/shared/types/index.ts`

This creates a convention of shared, typed domain models and modular dependency boundaries.

### 5) Documentation-first structure

The project strongly encourages README files as part of each major layer. The repository is designed so that every new application, service, agent, workflow, or project area is documented in its own folder documentation.

This creates a practical convention:

- each major component should explain its purpose
- each major component should describe technology and run instructions
- the repo remains understandable without needing to inspect every file immediately

### 6) Explicit and typed contracts

The shared types file reflects a convention toward explicit, typed definitions.

Examples include:

- `Id`
- `BaseEntity`

This suggests a broader preference for type clarity and domain contracts instead of loosely structured data objects.

---

## Proposal: Standardize a root runtime and dependency contract

### Problem

The repository is well organized by layer, but it lacks a single explicit runtime contract at the root. The project has clear architectural separation, yet there is no obvious root-level orchestration model for local development, dependency management, or service startup.

This creates a practical gap:

- it is unclear which commands start the monorepo
- there is no single dependency management standard visible at the root
- apps and services may drift into inconsistent startup patterns
- onboarding becomes harder as more components are added

### Why this should be improved

A monorepo with multiple layers benefits from a clear operational model. Without a root runtime contract, teams may duplicate tooling, create inconsistent environment setup, and lose clarity when new services are added.

### Proposal

Define a repository-wide standard with the following rules:

1. One root-level dependency manager and lockfile should define the workspace toolchain.
2. One root-level command should start the local development environment.
3. Each service or app should have its own local entry point, but the root should orchestrate them consistently.
4. Environment variables and config should follow a single convention across services.
5. The root documentation should clearly specify startup order, runtime assumptions, and local dependencies.
6. Naming of runtime scripts and services should remain consistent with the repo’s folder-level conventions.

### Expected benefits

- easier onboarding
- clearer local development setup
- fewer duplicate or conflicting dependency patterns
- cleaner scaling as new apps and services emerge
- consistent developer experience across all project layers

### Scope

This proposal is about the repository’s developer experience and operational architecture. It does not require changing the business logic or the existing folder structure.

---

## Recommended direction

The project already demonstrates a strong conceptual architecture. The next improvement should focus on making that architecture operationally consistent at the root so the monorepo is easier to run, maintain, and extend.
