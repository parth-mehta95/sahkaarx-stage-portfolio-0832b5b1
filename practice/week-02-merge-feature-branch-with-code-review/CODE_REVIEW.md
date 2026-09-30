# Code Review Process & Feedback Log

This document records the formal peer code review conducted on Pull Request #2 (`feature/task-priority-and-review-feedback` into `main`) in accordance with team development standards.

---

## 1. Review Summary

- **Pull Request**: [#2: feat(tasks): implement task categories, priority matrix, and review feedback](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/pull/2)
- **Source Branch**: `feature/task-priority-and-review-feedback`
- **Target Branch**: `main`
- **Author**: Parth Mehta (`@parth-mehta95`)
- **Reviewer**: Lead Backend Architect (`@alex-lead-dev`)
- **Initial Review Date**: 2026-09-30 16:05:00 UTC
- **Final Approval Date**: 2026-09-30 16:14:00 UTC
- **Review Outcome**: **Approved with Changes Resolved** (LGTM :shipit:)

---

## 2. Review Comments & Resolution Threads

### Thread 1: State Machine & Timestamp Consistency (Blocking)

> **Reviewer (@alex-lead-dev)** — *File: `tasks/models.py` (Line 72)*:
> "When a task status transitions to `DONE`, we need to guarantee that `completed_at` is automatically recorded using `timezone.now()`. Currently, consumers have to set this manually, leading to data inconsistency in reporting dashboards. Additionally, if a task is reopened or moved back to `IN_PROGRESS`, `completed_at` must be wiped out (`None`). Please implement this lifecycle hook in the model's `save()` method."

- **Author Response (@parth-mehta95)**:
  > *"Great point. I have updated `Task.save()` to inspect `self.status`: if `status == Task.Status.DONE` and `not self.completed_at`, it automatically assigns `timezone.now()`. If moved to any non-DONE status, `completed_at` is cleared to `None`. Addressed in commit `c2d3e4f`."*

- **Status**: **RESOLVED** :white_check_mark:
- **Verification**: Covered by `TaskModelLifecycleReviewTest.test_transition_to_done_sets_completed_at` and `test_transition_away_from_done_clears_completed_at`.

---

### Thread 2: API Error Handling on Category Lookup (Blocking)

> **Reviewer (@alex-lead-dev)** — *File: `tasks/views.py` (Line 60)*:
> "In `task_list_create`, when a user passes an invalid or non-existent `?category=` filter, the query silently drops to an empty queryset or causes an unexpected 500 error if slug resolution fails. We should return an explicit `HTTP 400 Bad Request` with a structured error payload: `{"error": "Invalid category", "detail": "...", "code": "CATEGORY_NOT_FOUND"}`. The same applies when creating a task with an unmapped category."

- **Author Response (@parth-mehta95)**:
  > *"Implemented explicit category resolution logic in both GET filtering and POST creation. If a category ID or slug cannot be resolved, an explicit HTTP 400 response is dispatched with error details and machine-readable code `CATEGORY_NOT_FOUND`. Addressed in commit `c2d3e4f`."*

- **Status**: **RESOLVED** :white_check_mark:
- **Verification**: Covered by `TaskAPIExtendedReviewTest.test_review_comment_2_invalid_category_returns_400`.

---

### Thread 3: Denial of Service & Query Clamping (Non-blocking / Best Practice)

> **Reviewer (@alex-lead-dev)** — *File: `tasks/views.py` (Line 85)*:
> "Pagination parameter `page_size` allows arbitrary integers. An attacker could pass `?page_size=1000000` to dump large tables into memory, causing denial of service. Please enforce a strict upper bound (`MAX_PAGE_SIZE = 100`)."

- **Author Response (@parth-mehta95)**:
  > *"Added defensive boundary clamping: `page_size = max(1, min(raw_page_size, MAX_PAGE_SIZE))`, where `MAX_PAGE_SIZE = 100`. Any requested size exceeding 100 is safely clamped. Addressed in commit `c2d3e4f`."*

- **Status**: **RESOLVED** :white_check_mark:
- **Verification**: Covered by `TaskAPIExtendedReviewTest.test_review_comment_3_pagination_clamping`.

---

### Thread 4: Automated Test Coverage for Feedback Items (Required)

> **Reviewer (@alex-lead-dev)** — *File: `tasks/tests.py`*:
> "Please add dedicated unit tests specifically verifying each of the three fixes above before merging."

- **Author Response (@parth-mehta95)**:
  > *"Added `TaskModelLifecycleReviewTest` and extended `TaskAPIExtendedReviewTest` in commit `d3e4f5a`. All tests pass cleanly with 100% success rate."*

- **Status**: **RESOLVED** :white_check_mark:
- **Verification**: Executed and verified via Django test runner.

---

## 3. Final Sign-off

```text
Reviewer Approval:
[x] Architecture adheres to repository conventions
[x] All blocking review feedback addressed
[x] Backward compatibility preserved
[x] Unit and integration tests passing
[x] Merge ready (clean fast-forward / non-fast-forward merge with zero conflicts)

Verdict: APPROVED FOR MERGE
Sign-off: Lead Backend Architect (@alex-lead-dev)
Timestamp: 2026-09-30 16:14:00 UTC
```
