---
title: "Dependency management and reusable modules"
description: "Centralize shared contracts and reusable logic in package-level modules instead of duplicating them across the repo."
applicationType: AutoAttached
---

## Applies to

- `package.json` files
- shared modules under `packages/`
- shared types under `packages/shared/`
- imports between `services/`, `uis/`, `agents/`, and `workflows/`
- any repeated domain model, schema, or contract used more than once

## Do

- Keep shared domain types in `packages/shared`.
- Place common contracts in `packages/` when multiple layers need the same model.
- Reuse common interfaces instead of creating parallel definitions across services and UIs.
- Keep dependencies explicit and intentional.
- Keep shared logic in a single module or package when multiple components depend on it.

## Do not

- Do not duplicate the same type or interface across unrelated services and UIs.
- Do not re-declare a shared contract in multiple places with small variations.
- Do not create hidden cross-layer dependencies without a shared package boundary.
- Do not copy logic into multiple folders when a reusable module already exists.

## Verification

A change is compliant only if shared contracts are centralized in a reusable module and duplicated logic is removed when the same model or behavior is used in multiple layers.
