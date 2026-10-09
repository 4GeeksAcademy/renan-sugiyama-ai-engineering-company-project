---
name: "frontend-react-best-practices"
description: "Defines the standard for frontend development in the monorepo, including state management, data fetching, CSS modules, and folder structure."
glob: "**/src/**/*.{ts,tsx,js,jsx,css,module.css}"
---

## Purpose

This skill defines the default frontend development standards for React applications in this monorepo. It applies to UI work in the `uis/` area and any React module that is part of a feature.

## Core decisions

### 1) Zustand for client state

Use Zustand for local, UI-driven client state that is not server-owned and does not need to be cached across network responses.

Do:

- keep UI state in stores when it is shared across components
- use small, purpose-driven stores rather than a single global store
- separate persisted UI state from server-fetched data
- prefer selectors and small store slices

Do not:

- put server data into Zustand as the primary source of truth
- duplicate query data in local state when TanStack Query already owns it
- create large "god stores" with unrelated state

### 2) TanStack Query for server data and server state

Use TanStack Query for all asynchronous server state management:

- data fetching
- mutation flows
- loading and error states
- cache invalidation
- optimistic updates when appropriate
- polling or refetching strategies

Do:

- define query keys with stable, predictable naming
- keep the data-fetching logic in hooks or API modules
- handle loading, error, and empty states in the UI
- invalidate related queries after mutations

Do not:

- fetch data directly inside a component whenever a shared hook or service can encapsulate it
- duplicate server state in component local state if it already exists in the query cache
- ignore stale data and cache invalidation after writes

### 3) CSS Modules for styling

Use CSS Modules for component-level styling instead of global CSS classes.

Do:

- name classes by component and intent
- keep styles close to the component or feature they serve
- create small, reusable styling primitives when necessary
- use CSS Modules for local scoping and lower risk of collisions

Do not:

- spread CSS classes across many unrelated files
- rely on global selectors for component-specific styling
- mix layout logic and business logic into the same styles

### 4) Use `useCallback` and `useMemo` only when necessary

Memoization should be a deliberate optimization, not default behavior.

Do:

- use `useCallback` when passing stable function references to child components or effect dependencies
- use `useMemo` when a computed value is expensive and reused across renders
- profile and justify memoization before using it broadly

Do not:

- wrap every function or object in `useCallback` and `useMemo`
- optimize prematurely before a real performance issue exists
- memoize values that are cheap to recompute and do not affect render performance

### 5) React best practices

Follow these core principles:

- keep components small and focused on one responsibility
- prefer composition over deeply nested prop drilling
- derive values instead of storing redundant state
- keep business logic outside render-heavy components when possible
- use stable keys for list rendering
- handle accessibility basics: labels, focus states, semantic markup, keyboard interaction
- prefer typed data models and explicit props over any/loose object usage
- avoid hidden side effects inside render

### 6) Data flow rules

- server data: TanStack Query
- client-only UI state: Zustand
- reusable utilities: `lib/` or `utils/`
- API contract logic: `api/` or `services/`
- UI-only components: `components/`
- page-level orchestration: `pages/` or `features/`

## Recommended folder structure

A typical frontend structure should be:

```txt
src/
  api/
    client.ts
    incidents.ts
  components/
    Button/
      Button.tsx
      Button.module.css
    IncidentCard/
      IncidentCard.tsx
      IncidentCard.module.css
  features/
    incidents/
      components/
      hooks/
      store/
      types/
      utils/
  hooks/
    useIncidentFilters.ts
  lib/
    formatters.ts
    validators.ts
  pages/
    DashboardPage.tsx
    IncidentDetailPage.tsx
  store/
    uiStore.ts
  styles/
    tokens.css
  types/
    index.ts
  App.tsx
  main.tsx
```

## Interpretation for this repo

The project already follows a folder-by-responsibility model. The frontend app should keep that convention and avoid mixing responsibilities inside the same file or folder.

- `api/` contains network calls and data-fetching adapters
- `components/` contains presentational and reusable UI primitives
- `features/` groups domain-feature logic and related files
- `hooks/` contains reusable logic and custom hooks
- `lib/` contains generic utilities and supporting functions
- `pages/` contains top-level route screens
- `store/` contains Zustand stores for client state
- `types/` contains shared app interfaces and contracts
- CSS Modules stay close to the component or feature they style

## Verification

A frontend change is compliant only if it follows this pattern:

- server state is handled by TanStack Query
- client-only state is handled by Zustand
- styling uses CSS Modules
- optimization is justified and not overused
- the folder structure remains consistent with the project’s responsibility-based organization
