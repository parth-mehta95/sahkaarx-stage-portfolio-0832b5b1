# Branching Strategy & Atomic Commit Standards

## 1. Overview & Objectives

In modern backend engineering, a clean, readable Git history is essential for bisecting regressions, generating automated changelogs, conducting effective code reviews, and maintaining long-term software maintainability.

This document outlines the **Branching Strategy** and **Atomic Commit Conventions** implemented for Week 04 in the Capstone Django Backend Service.

---

## 2. Feature Branch Taxonomy

| Branch Name | Scope / Responsibility | Base Branch | Merge Target | Commits |
| :--- | :--- | :--- | :--- | :--- |
| `feature/auth-setup` | JWT Token generation, authentication views, user profiles, and security tests | `main` | `main` | 3 Atomic Commits |
| `feature/database-models` | Workspace & Project models, schema validations, migrations, and model tests | `main` | `main` | 3 Atomic Commits |
| `feature/api-endpoints` | REST serializers, project viewsets, pagination, filtering, and API tests | `main` | `main` | 3 Atomic Commits |

---

## 3. Atomic Commit Principles

Each commit in a feature branch must satisfy the three golden rules of atomic commits:

1. **Single Responsibility**: Each commit makes exactly one logical change.
2. **Self-Contained & Compilable**: The test suite must pass at each commit point. The repository is never left in a broken intermediate state.
3. **Revertible**: If a bug is introduced in a specific commit, that single commit can be reverted via `git revert <hash>` without breaking other unrelated features.

### Atomic Progression Pattern

For each feature branch, commits follow a predictable progression:
- **Commit 1 (Configuration & Base)**: Scaffold configuration, tokens, or base models.
- **Commit 2 (Implementation & Logic)**: Business logic, serializers, views, or migrations.
- **Commit 3 (Verification & Tests)**: Automated test suite asserting end-to-end functionality.

---

## 4. Conventional Commit Message Specification

All commit messages adhere to the **Conventional Commits 1.0.0** format:

```text
<type>(<scope>): <short imperative description>

[optional body explaining motivation and architectural decisions]
- Bullet point summarizing file or functional change
- Bullet point summarizing validations or behavior
```

### Commit Types:
- `feat`: A new feature introduced to the codebase
- `test`: Adding or correcting tests with no production code changes
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `docs`: Documentation updates or additions
- `chore`: Maintenance tasks, dependencies, or configuration updates

---

## 5. Conflict-Free Merge Protocol

To ensure all feature branches merge cleanly to `main` without conflicts:
- Each feature branch isolates its modifications within a dedicated modular package (`authentication/`, `database_models/`, `api_endpoints/`).
- The project settings (`backend/settings.py`) and top-level URLs (`backend/urls.py`) use decoupled module discovery, preventing simultaneous edits to central registration files.
- Merges are performed using explicit non-fast-forward merges (`git merge --no-ff`) to preserve branch topology and review history.
