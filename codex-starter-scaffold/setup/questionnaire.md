# Workspace Setup Questionnaire

Fill this out before adapting the scaffold to a new project.

## Project Identity

1. What is the product or project name?
2. What does it do in one or two sentences?
3. What is the current top priority?
4. What work is explicitly deferred for now?

## Source Of Truth

5. Which files are the live runtime entry points?
6. Which docs should Codex read first by default?
7. Which docs are task-specific references?
8. Which folders are historical or background only?

## Safety

9. What validations prove a change is safe?
10. Which files or paths must never move casually because scripts, operators, or tooling depend on them?
11. Are there secrets, generated files, or sensitive folders that need `.gitignore` protection?

## Routing

12. What recurring task types deserve explicit routing in `CONTEXT.md`?
13. Which stage contracts need domain-specific instructions beyond the default scaffold?
