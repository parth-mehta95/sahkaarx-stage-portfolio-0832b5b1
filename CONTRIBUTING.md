# Engineering Contribution & Git Merge Conflict Best Practices Guide

Welcome to the **sahkaarx-stage-portfolio-0832b5b1** repository! This repository enforces modern engineering standards, clean Git workflows, robust code review protocols, and industry-standard conflict resolution procedures.

All contributors must review and adhere to these guidelines to ensure repository health, clean commit history, and zero production regressions.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Branching Strategy & Git Flow](#2-branching-strategy--git-flow)
3. [Commit Message Standards (Conventional Commits)](#3-commit-message-standards)
4. [Pull Request & Peer Review Lifecycle](#4-pull-request--peer-review-lifecycle)
5. [Git Conflict Resolution Runbook (5 Realistic Scenarios)](#5-git-conflict-resolution-runbook)
   - [Scenario 1: Overlapping Business Logic in Core Services](#scenario-1-overlapping-business-logic-in-core-services)
   - [Scenario 2: Divergent Database Migrations in Django ORM](#scenario-2-divergent-database-migrations-in-django-orm)
   - [Scenario 3: Dependency Version Bumps & Lockfile Collisions](#scenario-3-dependency-version-bumps--lockfile-collisions)
   - [Scenario 4: Fast-Forward vs 3-Way Merge vs Interactive Rebase](#scenario-4-fast-forward-vs-3-way-merge-vs-interactive-rebase)
   - [Scenario 5: File Rename / Refactor vs Parallel Modification (Tree Conflicts)](#scenario-5-file-rename--refactor-vs-parallel-modification-tree-conflicts)
6. [Conflict Prevention Best Practices & Git Hygiene](#6-conflict-prevention-best-practices--git-hygiene)
7. [Pre-Merge Verification Checklist](#7-pre-merge-verification-checklist)

---

## 1. Core Principles

- **Small, Atomic Pull Requests**: Keep pull requests focused on a single responsibility. Target under 400 lines of code (LOC) per PR.
- **Continuous Integration (CI) First**: Code cannot be merged into `main` unless all automated tests, linter checks, and security scans pass cleanly.
- **Transparent Communication**: If your feature touches critical core modules (e.g., service layers or pipeline coordinators), coordinate in advance with teammates touching adjacent logic.
- **No Residual Markers**: Never commit Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`). Automated pre-commit hooks and CI gates reject any code containing them.

---

## 2. Branching Strategy & Git Flow

We follow a **Trunk-Based Development** workflow supplemented with short-lived feature branches:

```text
[main] ─────────────────────────────────────────────────────────────► [Production Ready]
   │                                                              ▲
   ├──► feature/task-rate-limiting ───────────────────────────────┤ (PR #1 - Merged)
   │                                                              │
   └──► feature/task-retry-policy ──[Rebase/Sync on main]─────────┘ (PR #2 - Merged)
```

### Branch Naming Conventions

All branch names must be lowercase, hyphen-separated, and prefixed with the appropriate category:

| Prefix | Usage | Example |
| :--- | :--- | :--- |
| `feature/` | New functionality or domain model extensions | `feature/task-rate-limiting` |
| `bugfix/` | Non-critical bug corrections | `bugfix/fix-token-window-reset` |
| `hotfix/` | Urgent production fixes branching directly from main | `hotfix/security-csrf-bypass` |
| `refactor/` | Code reorganization without functional changes | `refactor/modularize-pipeline-services` |
| `test/` | Adding missing tests or enhancing test harnesses | `test/add-exponential-backoff-tests` |
| `docs/` | Documentation additions or updates | `docs/update-contributing-guide` |
| `chore/` | Maintenance, dependencies, or build config | `chore/bump-django-version` |

---

## 3. Commit Message Standards

This project adheres strictly to **Conventional Commits 1.0.0**.

### Format

```text
<type>(<scope>): <short imperative summary>

[optional multi-line body explaining motivation and technical decisions]

[optional footer(s), e.g., references, breaking changes]
```

### Allowed Types

- `feat`: A new user-facing or API feature.
- `fix`: A bug fix.
- `docs`: Documentation-only updates.
- `refactor`: Code changes that neither fix a bug nor add a feature.
- `perf`: Code changes that improve performance.
- `test`: Adding or modifying automated test suites.
- `chore`: Tooling, dependency updates, and maintenance.

### Good Commit Example

```text
feat(rate-limit): enforce client quota and token bucket throttling

- Add RateLimitLog model tracking client identifiers, window counts, and throttle states
- Implement check_rate_limit service evaluating sliding window request quotas
- Integrate rate limiting fast-fail check into execute_task_pipeline in tasks/services.py
- Expose client quota monitoring endpoint at /api/tasks/rate-limits/
- Add rate limit validation tests in tasks/tests.py
```

---

## 4. Pull Request & Peer Review Lifecycle

1. **Create Branch & Implement**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```
2. **Commit Frequently**: Make small, logical commits with clear messages.
3. **Keep Branch Synchronized**: Regularly fetch and rebase on upstream `main` to catch conflicts early:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
4. **Open Pull Request**: Include a summary of changes, motivation, test proof, and link any related issues.
5. **Review SLA**: Reviewers must provide constructive feedback within 24 business hours.
6. **Address Feedback in Commits**: Never force-push over review feedback without explanation; add follow-up commits.
7. **Clean Merge**: Merge only after receiving at least one peer approval and passing all CI checks.

---

## 5. Git Conflict Resolution Runbook

Merge conflicts are natural events in collaborative software engineering. Follow these standardized resolution playbooks across 5 common team scenarios.

---

### Scenario 1: Overlapping Business Logic in Core Services

**Context**: Two developers modify the same function or class method in `tasks/services.py` simultaneously.

```text
<<<<<<< HEAD (Branch A: Rate Limiting)
    is_allowed, info, log = check_rate_limit(client_identifier, max_requests=60)
    if not is_allowed:
        return {"success": False, "status_code": 429}
=======
    success, retry_result, logs = execute_with_retry_policy(task, max_attempts=3)
    if not success:
        return {"success": False, "status_code": 500}
>>>>>>> Branch B (Retry Policy)
```

#### Resolution Procedure:

1. **Identify the Intent of Both Changes**:
   - Branch A adds token-bucket rate limiting (capacity protection).
   - Branch B adds exponential backoff retry policies (fault resilience).
2. **Determine Architectural Ordering**:
   - Rate limiting must execute *first* to fast-fail unauthorized or abusive traffic before spinning up retry workers.
   - Retry execution must wrap the internal processing *second*.
3. **Edit the Contested File**:
   Open `tasks/services.py` in your editor. Combine both behaviors sequentially and remove the conflict markers:
   ```python
   # 1. Claire's Rate Limiting Check
   is_allowed, rate_limit_info, rate_log = check_rate_limit(
       client_identifier=client_identifier,
       max_requests=max_rate_limit,
   )
   if not is_allowed:
       return {"success": False, "status_code": 429, "rate_limit": rate_limit_info}

   # 2. Dave's Retry Policy Execution
   success, retry_result, retry_logs = execute_with_retry_policy(
       task=task,
       action_func=pipeline_action,
       max_attempts=max_retries,
   )

   # 3. Unified Telemetry Payload
   return {
       "success": success,
       "rate_limit": rate_limit_info,
       "retry_policy": retry_result,
       "task": task.to_dict(),
   }
   ```
4. **Compile and Test**:
   ```bash
   python -m py_compile tasks/services.py
   python manage.py test tests/
   ```
5. **Stage and Commit Resolution**:
   ```bash
   git add tasks/services.py
   git commit -m "Merge branch 'feature/task-retry-policy' into main - Harmonize rate limiting and retry execution"
   ```

---

### Scenario 2: Divergent Database Migrations in Django ORM

**Context**: Two parallel feature branches create new schema migrations independently, both originating from `0001_initial.py` (e.g. `0002_add_rate_limit_log.py` and `0002_add_retry_policy_log.py`).

When merging, Django flags conflicting migration leaves:
```text
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph: (0002_add_rate_limit_log, 0002_add_retry_policy_log in 'tasks').
To fix them run 'python manage.py makemigrations --merge'
```

#### Resolution Procedure:

#### Method A: Automated Migration Merge (Recommended for standard additions)
1. Run Django's built-in migration merger:
   ```bash
   python manage.py makemigrations --merge
   ```
   Django generates a new merge migration file: `tasks/migrations/0003_merge_*.py`:
   ```python
   class Migration(migrations.Migration):
       dependencies = [
           ('tasks', '0002_add_rate_limit_log'),
           ('tasks', '0002_add_retry_policy_log'),
       ]
       operations = []
   ```
2. Verify migration plan:
   ```bash
   python manage.py migrate --plan
   python manage.py migrate
   ```
3. Commit the merge migration:
   ```bash
   git add tasks/migrations/0003_merge_*.py
   git commit -m "chore(migrations): merge conflicting migration leaves in tasks"
   ```

#### Method B: Linear Re-chaining (Recommended before merging PR)
1. In the incoming feature branch, rename `0002_add_retry_policy_log.py` to `0003_add_retry_policy_log.py`.
2. Update its `dependencies` array to point to `0002_add_rate_limit_log`:
   ```python
   dependencies = [
       ('tasks', '0002_add_rate_limit_log'),
   ]
   ```
3. Test migration application cleanly from scratch:
   ```bash
   python manage.py migrate
   ```

---

### Scenario 3: Dependency Version Bumps & Lockfile Collisions

**Context**: Two branches modify `requirements.txt` or lockfiles (`poetry.lock`, `Pipfile.lock`) with conflicting library version requirements.

```text
<<<<<<< HEAD
Django>=4.2,<5.0
djangorestframework==3.14.0
pytest==7.4.0
=======
Django>=4.2,<5.1
djangorestframework==3.15.2
pytest-django>=4.5.2
>>>>>>> feature/upgrade-dependencies
```

#### Resolution Procedure:

1. **Inspect Version Bounds & Release Notes**:
   - Check if upgrading `djangorestframework` to `3.15.2` introduces breaking changes with `Django 4.2`.
   - Identify shared upper bounds (`Django>=4.2,<5.1`).
2. **Harmonize Specification**:
   Retain the modern, non-breaking superset of dependencies, sorted alphabetically:
   ```text
   Django>=4.2,<5.1
   djangorestframework>=3.14.0
   pytest>=7.4.0
   pytest-django>=4.5.2
   python-dotenv>=1.0.0
   ```
3. **Rebuild Environment & Run Test Harness**:
   ```bash
   pip install -r requirements.txt
   pytest
   ```
4. **Commit Harmonized Requirements**:
   ```bash
   git add requirements.txt
   git commit -m "build(deps): reconcile conflicting dependency versions and update test harness"
   ```

---

### Scenario 4: Fast-Forward vs 3-Way Merge vs Interactive Rebase

**Context**: Deciding when to use `git merge --no-ff` versus `git rebase origin/main`, and resolving conflicts during an interactive rebase.

#### Interactive Rebase Conflict Protocol:
When running `git rebase origin/main`, Git pauses at each conflicting commit:

```text
Auto-merging tasks/services.py
CONFLICT (content): Merge conflict in tasks/services.py
error: could not apply 5d6e7f8... feat(retry): implement retry policy
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
```

#### Step-by-Step Handling:
1. Check current status:
   ```bash
   git status
   ```
   *(You will see: `interactive rebase in progress; onto c39ebec`)*
2. Open conflicted files and resolve markers.
3. Stage resolved files:
   ```bash
   git add tasks/services.py
   ```
4. **DO NOT** run `git commit`! Instead, run:
   ```bash
   git rebase --continue
   ```
5. If conflicts occur on subsequent commits, repeat steps 2–4.
6. To abort and revert to the original state without any risk:
   ```bash
   git rebase --abort
   ```

#### Workflow Decision Matrix:

| Strategy | When to Use | Advantages | Considerations |
| :--- | :--- | :--- | :--- |
| **`git rebase origin/main`** | During active development on private feature branch. | Keeps PR commits clean and linear without intermediate merge bubbles. | Alters local commit SHAs; requires `--force-with-lease` if previously pushed. |
| **`git merge --no-ff`** | Merging completed PR into `main` branch. | Preserves PR history, reviewer sign-offs, and clear integration boundary. | Introduces a 2-parent merge commit. |
| **Squash & Merge** | Small, multi-fix PRs with messy intermediate commits. | Single cohesive commit on `main`. | Collapses detailed commit authorship if multiple people contributed. |

---

### Scenario 5: File Rename / Refactor vs Parallel Modification (Tree Conflicts)

**Context**: Engineer A refactors the codebase by moving `tasks/services.py` into a subpackage `tasks/services/pipeline.py`, while Engineer B modifies the original `tasks/services.py`.

Git flags a modify/delete tree conflict:
```text
CONFLICT (modify/delete): tasks/services.py deleted in HEAD and modified in feature/task-retry-policy.
Version feature/task-retry-policy of tasks/services.py left in tree.
```

#### Resolution Procedure:

1. **Analyze File Dispositions**:
   ```bash
   git status
   ```
2. **Apply Changes to New Target**:
   Copy the business logic updates from `tasks/services.py` into the new refactored file `tasks/services/pipeline.py`.
3. **Remove Legacy Path**:
   ```bash
   git rm tasks/services.py
   git add tasks/services/pipeline.py
   ```
4. **Verify Imports Across Repository**:
   ```bash
   grep -rn "tasks.services" tasks/ backend/ tests/
   ```
5. **Run Test Suite & Commit**:
   ```bash
   python manage.py test
   git commit -m "refactor(services): resolve tree conflict by migrating retry policy into new modular pipeline"
   ```

---

## 6. Conflict Prevention Best Practices & Git Hygiene

The best merge conflict resolution is conflict prevention. Follow these 6 golden rules:

1. **Daily Upstream Synchronization**:
   Rebase on `origin/main` daily to ensure your branch does not drift far from the team baseline:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
2. **Short-Lived Branches**:
   Target merging within 24 to 48 hours. Large, multi-week feature branches invite catastrophic merge conflicts.
3. **Modular Code Architecture**:
   Avoid 2,000-line "god classes" or files. Split code into cohesive modules (e.g., `services.py`, `selectors.py`, `validators.py`).
4. **Coordinate on High-Traffic Files**:
   Mention in standup or team chat if you are restructuring `settings.py`, core model schemas, or central routing tables.
5. **Pre-Commit Verification**:
   Install pre-commit hooks to block residual conflict markers before they can be committed:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
6. **Never Force-Push to Protected Branches**:
   Never run `git push --force` against `main` or `develop`. On feature branches, always use `git push --force-with-lease`.

---

## 7. Pre-Merge Verification Checklist

Before opening your Pull Request or marking a merge conflict resolved, complete this verification checklist:

- [ ] All Git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) are removed.
- [ ] Code compiles cleanly with zero syntax errors (`python -m py_compile ...`).
- [ ] Unit and integration test suites pass at 100% (`pytest` or `python manage.py test`).
- [ ] Database migrations are checked and plan has no conflicting heads (`python manage.py migrate --plan`).
- [ ] Commit history is atomic, follows Conventional Commits, and contains detailed merge reasoning.
- [ ] Documentation (`README.md`, docstrings, `CONTRIBUTING.md`) is updated to reflect new functionality.
