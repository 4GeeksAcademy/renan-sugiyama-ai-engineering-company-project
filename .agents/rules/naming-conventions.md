---
title: "Naming conventions"
description: "Use stable, lowercase, descriptive names for folders, packages, apps, and services so the project remains easy to navigate and maintain."
applicationType: Always
---

## Applies to

- folder names at any level of the repo
- package names
- service names
- app names
- module names that represent a project component

## Do

- Use lowercase names for folders and project names.
- Use descriptive names that reflect the component responsibility.
- Use short, readable names such as `services`, `agents`, `data`, `docs`, and `infra`.
- Use domain-oriented names for subfolders and modules.
- Keep naming consistent across apps, services, and packages.
- Use valid package naming patterns such as `@repo/shared-types` when a package name is required.

## Do not

- Do not use uppercase letters in repo folder names.
- Do not use vague names such as `misc`, `stuff`, `temp`, or `utils` unless there is a very clear reason.
- Do not use names that hide the component purpose.
- Do not mix naming styles across the same layer of the project.

## Verification

A name is compliant only if it is lowercase, descriptive, and consistent with the role of the component in the repository.
