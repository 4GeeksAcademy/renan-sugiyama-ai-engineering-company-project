# AGENTS.md

This repository is a multi-service monorepo. Agents must operate within the established project context and avoid modifying authoritative project documentation or protected runtime assets without explicit approval from the developer.

## Required memory-bank reads at the start of each session

At the beginning of every working session, the agent must read the following files in order before making changes:

1. `memory-bank/project-brief.md` — business context, project goals, and problem definition.
2. `memory-bank/tech-context.md` — technical constraints, stack, and implementation context.
3. `memory-bank/project-progress.md` — current project status, milestones, and active tasks.
4. `memory-bank/visual-design-system.md` — design conventions and product UX guidance.

If the agent is working on a specific feature or service, it may read the corresponding implementation files afterward, but the memory-bank files above are mandatory before any code edits or commit preparation.

## Mandatory workflow before each commit

Before every commit, the agent must complete all of the following steps in order:

1. Review the working tree and confirm exactly which files changed.
2. Re-read the relevant memory-bank context and confirm the change still matches the business, technical, and design intent of the project.
3. Run the smallest relevant validation available for the affected scope (for example: targeted tests, linting, or static checks for the edited area).
4. Verify the diff for unintended edits, especially in protected files and documentation.
5. Confirm that no protected folder or file was modified without explicit approval.
6. Only then prepare a commit with a clear, specific message summarizing the change.

The agent must not skip any of these steps before committing.

## Protected files and folders

The following files and folders are read-only unless the developer explicitly confirms a modification:

- `memory-bank/`
- `CONTEXT.md`
- `CONTEXT.es.md`
- `README.md`
- `README.es.md`
- `PROJECT_CONVENTIONS.md`
- `company-choice.md`
- `docs/spec/`
- `services/**/migrations/`
- `AGENTS.md`

The agent must also avoid changing any root-level product, planning, or architectural documentation that defines the monorepo direction unless explicitly approved.

## Default operating rule

When in doubt, read first, ask for confirmation before editing protected documentation, and keep the change scope minimal and aligned with the approved project direction.
