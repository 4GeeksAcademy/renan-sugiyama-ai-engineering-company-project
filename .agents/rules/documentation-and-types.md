---
title: "Documentation and explicit contracts"
description: "Document each major component and define explicit contracts for exported modules, services, and shared types."
applicationType: AutoAttached
---

## Applies to

- new or existing folders that represent a major component
- exported TypeScript interfaces, types, and shared models
- README files for apps, services, agents, workflows, and datasets
- any code that defines a public contract between layers

## Do

- Add a `README.md` for each significant folder or component.
- Document the purpose, technology, and startup steps for each app or service.
- Use explicit interfaces and typed models for shared contracts.
- Use domain names for contracts, models, and shared types.
- Keep documentation aligned with the current folder structure.

## Do not

- Do not leave a major component undocumented.
- Do not expose loosely structured data objects as public contracts when a type is needed.
- Do not create undocumented exports in shared modules.
- Do not allow README files to drift away from the actual code structure.

## Verification

A change is compliant only if every significant component has documentation and every public contract is explicit, typed, and understandable to another developer without reading hidden implementation details.
