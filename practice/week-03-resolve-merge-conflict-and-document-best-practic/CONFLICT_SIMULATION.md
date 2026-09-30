# Merge Conflict Simulation & Resolution Walkthrough

This document simulates, step-by-step, the intentional merge conflict created between two parallel engineering feature branches:
1. `feature/task-rate-limiting` (Developer Claire)
2. `feature/task-retry-policy` (Developer Dave)

Both engineers modified the same execution pipeline coordinator (`execute_task_pipeline`) within [`tasks/services.py`](tasks/services.py).

---

## 1. Branch Simulation Topology

```text
[main (Base: c39ebec)] ────────────────────────────────────────────────────────► [main (Merged: e5f6a7b)]
    │                                                                                       ▲
    ├──► [feature/task-rate-limiting] (Claire) ────────────────┐                           │
    │    • Commit 1a2b3c4: feat(rate-limit)                    │                           │
    │      Token-bucket throttling & quota protection          ▼                           │
    │                                                     [MERGE CONFLICT]                 │
    └──► [feature/task-retry-policy] (Dave) ─────────────► tasks/services.py              │
         • Commit 5d6e7f8: feat(retry)                         │                           │
           Exponential backoff & dead-letter queue             ▼                           │
                                                          [MANUAL RESOLUTION] ─────────────┘
                                                          • Step 1: Rate Limit Check
                                                          • Step 2: Retry Interceptor
                                                          • Step 3: Unified Response
                                                          • Conflict markers removed
```

---

## 2. Step 1: Branch Creation from Main

Both engineers created their feature branches from `main` (commit `c39ebec`):

```bash
# Developer Claire
git checkout main
git checkout -b feature/task-rate-limiting

# Developer Dave
git checkout main
git checkout -b feature/task-retry-policy
```

---

## 3. Step 2: Claire's Implementation (`feature/task-rate-limiting`)

Claire introduced client throughput throttling in [`tasks/services.py`](tasks/services.py) and added `RateLimitLog` in [`tasks/models.py`](tasks/models.py):

```python
# Commit: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
# Author: Claire Engineer <claire.engineer@example.com>
# Message: feat(rate-limit): enforce client quota and token bucket throttling

def execute_task_pipeline(task: Task, client_identifier: str = "internal-service", **kwargs):
    # Claire's logic: Fast fail if rate limit exceeded
    is_allowed, info, log = check_rate_limit(client_identifier, max_requests=60)
    if not is_allowed:
        return {
            "success": False,
            "status_code": 429,
            "reason": "RATE_LIMIT_EXCEEDED",
            "rate_limit": info,
        }

    task.status = Task.STATUS_COMPLETED
    task.save()
    return {"success": True, "rate_limit": info, "task": task.to_dict()}
```

Claire committed and pushed her branch, and merged it into `main`:

```bash
git checkout main
git merge --no-ff feature/task-rate-limiting -m "feat(rate-limit): merge rate limiting into main"
```

---

## 4. Step 3: Dave's Parallel Implementation (`feature/task-retry-policy`)

Simultaneously, Dave implemented exponential backoff and dead-letter routing in [`tasks/services.py`](tasks/services.py) and added `RetryPolicyLog` in [`tasks/models.py`](tasks/models.py):

```python
# Commit: 5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e
# Author: Dave Engineer <dave.engineer@example.com>
# Message: feat(retry): implement exponential backoff and dead-letter queue routing

def execute_task_pipeline(task: Task, client_identifier: str = "internal-service", **kwargs):
    # Dave's logic: Guard execution with retry policy
    success, retry_result, logs = execute_with_retry_policy(
        task=task,
        action_func=execute_internal_action,
        max_attempts=3,
        base_backoff_ms=200,
    )
    if not success:
        task.status = Task.STATUS_FAILED
        task.save()
        return {
            "success": False,
            "status_code": 500,
            "reason": "DEAD_LETTER",
            "retry_policy": retry_result,
        }

    return {"success": True, "retry_policy": retry_result, "task": task.to_dict()}
```

Dave committed his changes to `feature/task-retry-policy`:

```bash
git add tasks/
git commit -m "feat(retry): implement exponential backoff and dead-letter queue routing"
```

---

## 5. Step 4: Merge Attempt & Conflict Triggering

Dave attempts to merge `feature/task-retry-policy` into updated `main`:

```bash
git checkout main
git merge feature/task-retry-policy
```

Git automatically halts the merge due to conflicting changes on the same lines of [`tasks/services.py`](tasks/services.py):

```text
Auto-merging tasks/models.py
Auto-merging tasks/services.py
CONFLICT (content): Merge conflict in tasks/services.py
Automatic merge failed; fix conflicts and then commit the result.
```

---

## 6. Step 5: Raw Conflict Markers in `tasks/services.py`

When inspecting the contested block in [`tasks/services.py`](tasks/services.py):

```python
def execute_task_pipeline(
    task: Task,
    client_identifier: str = "internal-service",
    action_payload: Optional[Dict[str, Any]] = None,
    max_rate_limit: int = 60,
    max_retries: int = 3,
) -> Dict[str, Any]:
<<<<<<< HEAD (feature/task-rate-limiting in main)
    # Claire's rate limiting logic
    is_allowed, rate_limit_info, rate_log = check_rate_limit(
        client_identifier=client_identifier,
        endpoint="/api/tasks/pipeline/execute/",
        max_requests=max_rate_limit,
    )
    if not is_allowed:
        return {
            "success": False,
            "status_code": 429,
            "reason": "RATE_LIMIT_EXCEEDED",
            "message": f"Execution request rate limit of {max_rate_limit} requests/window exceeded.",
            "rate_limit": rate_limit_info,
            "task": task.to_dict(),
        }
=======
    # Dave's retry policy logic
    success, retry_result, retry_logs = execute_with_retry_policy(
        task=task,
        action_func=pipeline_action,
        max_attempts=max_retries,
        base_backoff_ms=100,
    )
    if not success:
        task.status = Task.STATUS_FAILED
        task.save()
        return {
            "success": False,
            "status_code": 500,
            "reason": "RETRY_EXHAUSTED_DEAD_LETTER",
            "retry_policy": retry_result,
            "task": task.to_dict(),
        }
>>>>>>> feature/task-retry-policy
```

---

## 7. Step 6: Conflict Analysis & Manual Resolution Strategy

### Why Did Git Conflict?
- Git's three-way merge algorithm compares the common ancestor (Base commit `c39ebec`) against both branch heads.
- Both branches modified lines within the exact same function body (`execute_task_pipeline`), altering the control flow and return statements.
- Git cannot deduce whether rate limiting should precede retry handling or replace it entirely.

### Resolution Architecture:
1. **Execute Rate Limiting First (Claire)**:
   Checking client quotas before consuming execution worker threads protects server resources against denial-of-service or runaway loops. If rate-limited, return HTTP 429 immediately.
2. **Execute Retry Policy Second (Dave)**:
   If the quota check succeeds, wrap the execution inside the exponential backoff retry loop.
3. **Consolidate Output Payload**:
   Combine `rate_limit` metadata and `retry_policy` metadata into the final JSON dictionary.
4. **Remove All Conflict Markers**:
   Strip out `<<<<<<< HEAD`, `=======`, and `>>>>>>> feature/task-retry-policy`.

### Resolved Code Implementation:
The unified code as written in [`tasks/services.py`](tasks/services.py):

```python
def execute_task_pipeline(
    task: Task,
    client_identifier: str = "internal-service",
    action_payload: Optional[Dict[str, Any]] = None,
    max_rate_limit: int = 60,
    max_retries: int = 3,
) -> Dict[str, Any]:
    action_payload = action_payload or {}

    # Step 1: Claire's Rate Limiting Check (Evaluated first to protect capacity)
    is_allowed, rate_limit_info, rate_log = check_rate_limit(
        client_identifier=client_identifier,
        endpoint="/api/tasks/pipeline/execute/",
        max_requests=max_rate_limit,
    )

    if not is_allowed:
        return {
            "success": False,
            "status_code": 429,
            "reason": "RATE_LIMIT_EXCEEDED",
            "message": f"Execution request rate limit of {max_rate_limit} requests/window exceeded.",
            "rate_limit": rate_limit_info,
            "retry_policy": None,
            "task": task.to_dict(),
        }

    # Step 2: Dave's Exponential Backoff & Retry Execution
    def pipeline_action(t: Task) -> Dict[str, Any]:
        with transaction.atomic():
            t.status = Task.STATUS_IN_PROGRESS
            t.save()
            # Execute business logic
            action_type = action_payload.get("action_type", "standard_process")
            if action_type == "simulate_transient_failure":
                raise RuntimeError("Transient pipeline worker timeout simulated.")
            t.status = Task.STATUS_COMPLETED
            t.save()
            return {"task_id": t.id, "action_type": action_type, "status": t.status}

    success, retry_result, retry_logs = execute_with_retry_policy(
        task=task,
        action_func=pipeline_action,
        max_attempts=max_retries,
        base_backoff_ms=100,
    )

    if not success:
        task.status = Task.STATUS_FAILED
        task.save()

    # Step 3: Unified Response Payload
    return {
        "success": success,
        "status_code": 200 if success else 500,
        "reason": "SUCCESS" if success else "RETRY_EXHAUSTED_DEAD_LETTER",
        "rate_limit": rate_limit_info,
        "retry_policy": retry_result,
        "retry_logs_count": len(retry_logs),
        "task": task.to_dict(),
    }
```

---

## 8. Step 7: Staging and Completing the Merge Commit

```bash
# Verify no residual conflict markers
git diff | grep -E '<<<<<<<|=======|>>>>>>>'

# Stage resolved files
git add tasks/models.py tasks/services.py

# Commit merge resolution
git commit -m "Merge branch 'feature/task-retry-policy' into main

Resolve merge conflict in tasks/services.py:
- Harmonize execute_task_pipeline() by ordering Claire's rate limiting before Dave's retry policy
- Rate limit validation fast-fails with HTTP 429 to protect backend capacity
- Retry policy handles transient execution failures with exponential backoff and dead-letter routing
- Consolidate telemetry payload with both rate_limit and retry_policy fields
- Cleanly excise all conflict markers (<<<<<<<, =======, >>>>>>>)
- Verify 100% test pass rate across unit and integration suites"

# Push resolved main branch to GitHub
git push origin main
```
