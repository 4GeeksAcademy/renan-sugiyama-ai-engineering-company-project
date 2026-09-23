---
title: "Separation of concerns"
description: "Keep business, UI, data, AI, and infrastructure logic in separate layers to avoid coupling and keep the system maintainable."
applicationType: Always
---

## Applies to

- new source files under `services/`, `uis/`, `data/`, `agents/`, `skills/`, `mcps/`, `workflows/`, `packages/`, and `infra/`
- new modules, features, and service boundaries across the repo
- code that defines business logic, API logic, workflows, or external integrations

## Do

- Place UI concerns under `uis/`.
- Place backend and API logic under `services/`.
- Place data processing and storage logic under `data/`.
- Place AI assistants under `agents/`.
- Place reusable AI guidance under `skills/`.
- Place external tool and protocol integrations under `mcps/`.
- Place workflow automation under `workflows/`.
- Place shared contracts and libraries under `packages/`.
- Place deployment and runtime concerns under `infra/`.

## Do not

- Do not couple business logic directly into UI components.
- Do not place data pipelines inside the API layer unless they are part of the service contract.
- Do not duplicate domain logic across app layers.
- Do not place external integration logic inside unrelated folders.
- Do not mix infrastructure concerns with application logic in the same module.

## Verification

A change is compliant only if each module belongs to a single responsibility layer and does not mix business, UI, data, AI, or infrastructure concerns in the same implementation.
