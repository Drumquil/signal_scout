# Python App Setup Questionnaire

Fill this out before adapting the scaffold to a new Python project.

## Project Identity

1. What is the project name?
2. What does the app do in one or two sentences?
3. What is the current top priority?
4. What work is explicitly deferred for now?

## Source Of Truth

5. What are the primary Python entry points?
6. Where is the main source root: `src/`, package root, or another layout?
7. Which docs should Codex read first by default?
8. Which docs are task-specific references?
9. Which folders are historical or background only?

## Validation

10. What is the preferred Python executable or environment path?
11. What is the smallest syntax check command used here?
12. What is the narrowest useful test command?
13. What focused script or runtime command best proves behavior safely?

## Safety

14. Which files or paths must never move casually because imports, scripts, operators, or tooling depend on them?
15. Are there secrets, generated files, caches, or local databases that need `.gitignore` protection?
16. Are there migrations, persistent state files, or external integrations that require extra caution?

## Routing

17. What recurring task types deserve explicit routing in `CONTEXT.md`?
18. Which stage contracts need domain-specific instructions beyond the default scaffold?
