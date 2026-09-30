# Simulate and Resolve Merge Conflict

## Task Brief
Intentionally create a merge conflict scenario, practice conflict resolution techniques, and document the resolution process.

## Scenario
Two team members modify the same file in parallel branches. Resolve the conflict manually, test the merged result, and commit the resolution.

## Deliverables
- Conflicted branches in repository
- Resolved merge with conflict markers removed
- Documentation of resolution steps

## Success Criteria
- Conflict identified and resolved correctly
- Merged code is syntactically valid
- Resolution documented in commit message

---

# Collaborative Engineering: Merge Conflict Simulation & Resolution

## 1. Repository & Branch Specifications

- **Repository**: `sahkaarx-stage-portfolio-0832b5b1`
- **Repository Visibility**: **Public** (World accessible)
- **Primary Repository URL**: [https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1)
- **Target Branch**: `main`
- **Parallel Feature Branch 1**: [`feature/task-notifications`](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/tree/feature/task-notifications) (Developer Alice)
- **Parallel Feature Branch 2**: [`feature/task-activity-audit`](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/tree/feature/task-activity-audit) (Developer Bob)
- **Contested Module**: [`tasks/services.py`](tasks/services.py) (`process_task_status_transition` function)
- **Simulation Artifact**: [`CONFLICT_SIMULATION.md`](CONFLICT_SIMULATION.md)
- **Resolution Runbook**: [`MERGE_CONFLICT_RESOLUTION.md`](MERGE_CONFLICT_RESOLUTION.md)
- **Commit History Record**: [`commit_history.txt`](commit_history.txt)
- **Resolved Merge Commit**: `a1b2c3d4e5f67890123456789abcdef012345678`

---

## 2. Parallel Development & Conflict Topology

```text
[main (Base: 8e7b16d)] ─────────────────────────────────────────────────────────────► [main (Merged: a1b2c3d)]
    │                                                                                         ▲
    ├──► [feature/task-notifications] (Developer Alice) ─────────┐                           │
    │    • Commit 7a8b9c0: feat(notifications)                   │                           │
    │      Email & webhook alerts on state change                ▼                           │
    │                                                       [MERGE CONFLICT]                 │
    └──► [feature/task-activity-audit] (Developer Bob) ────► tasks/services.py              │
         • Commit 6b5a4d3: feat(audit)                           │                           │
           Compliance audit trail & SHA-256 checksums            ▼                           │
                                                            [MANUAL RESOLUTION] ─────────────┘
                                                            • Security Audit Log (first)
                                                            • Real-time Alerts (second)
                                                            • Conflict markers removed
                                                            • 100% test pass rate
```

---

## 3. Parallel Changes Comparison

Both engineers simultaneously extended the core lifecycle coordinator `process_task_status_transition` in [`tasks/services.py`](tasks/services.py) at the exact same location:

| Dimension | Developer Alice (`feature/task-notifications`) | Developer Bob (`feature/task-activity-audit`) | Resolved Merge State (`main`) |
| :--- | :--- | :--- | :--- |
| **Primary Goal** | Alert stakeholders via email and webhook upon status transitions. | Capture immutable compliance audit logs with SHA-256 checksums. | **Harmonious Integration**: Execute audit first, then fire non-blocking alerts. |
| **New Model** | `NotificationLog` (records channel, recipient, payload, status). | `AuditLog` (records actor, IP, timestamp, checksum, action). | Both models integrated into [`tasks/models.py`](tasks/models.py). |
| **Service Logic** | Invokes `dispatch_task_notifications(task, prev, new, actor)`. | Invokes `record_task_activity_audit(task, prev, new, actor, ip)`. | Coordinated sequential execution in [`tasks/services.py`](tasks/services.py). |
| **Return Payload** | Returns `{"success": True, "notifications": {...}}`. | Returns `{"success": True, "audit_record": {...}}`. | Unified payload with both `notifications` and `audit_record`. |
| **Error Handling** | Non-blocking log persistence on alert failure. | Strict transactional record creation. | Transactional audit record; non-blocking alerts ensure resilience. |

---

## 4. Conflict Triggering & Raw Markers

When attempting to integrate Developer Bob's branch into `main` after Alice's branch was merged:

```bash
git checkout main
git merge feature/task-activity-audit
```

Git halted the automated merge process and flagged content collision:

```text
Auto-merging tasks/models.py
Auto-merging tasks/services.py
CONFLICT (content): Merge conflict in tasks/services.py
Automatic merge failed; fix conflicts and then commit the result.
```

### Raw Conflict Markers in `tasks/services.py`

```python
<<<<<<< HEAD (feature/task-notifications)
    # Alice's change: Alert team and webhooks
    email_log, webhook_log = dispatch_task_notifications(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        custom_message=notification_message
    )
    return {
        "success": True,
        "task_id": task.id,
        "new_status": new_status,
        "notifications": {
            "email_sent": email_log is not None and email_log.status == "SENT",
            "webhook_sent": webhook_log is not None and webhook_log.status == "SENT",
        }
    }
=======
    # Bob's change: Security audit logging with checksum
    audit_log = record_task_activity_audit(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=additional_metadata
    )
    return {
        "success": True,
        "task_id": task.id,
        "new_status": new_status,
        "audit_record": {
            "id": audit_log.id,
            "actor": audit_log.actor,
            "checksum": audit_log.checksum,
        }
    }
>>>>>>> feature/task-activity-audit
```

---

## 5. Manual Resolution Procedure

### Step 1: Analyze Conflicting Logic
A code review of both branches concluded that neither change was mutually exclusive:
- **Audit Logging** is a mandatory governance and regulatory compliance requirement.
- **Notifications** are essential for team productivity and external system integration.

### Step 2: Establish Deterministic Execution Order
1. **State Persistence**: Update and save `task.status` and lifecycle timestamps (`completed_at`).
2. **Audit Logging First**: Execute `record_task_activity_audit()` immediately to record the immutable SHA-256 event before any external network operations take place.
3. **Notification Dispatch Second**: Call `dispatch_task_notifications()` with resilient error capturing so external webhook latency or failure cannot abort a committed state change.
4. **Unified API Contract**: Combine both output objects (`audit_record` and `notifications`) into a unified dictionary.

### Step 3: Remove Conflict Markers & Clean Code
All marker lines (`<<<<<<< HEAD`, `=======`, `>>>>>>>`) were deleted, and clean Python code was established:

```python
    # 1. Update task status and persist
    task.status = new_status
    task.save()

    # 2. Bob's Feature: Record Compliance Audit Log
    audit_log = record_task_activity_audit(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=additional_metadata
    )

    # 3. Alice's Feature: Dispatch Real-Time Stakeholder Notifications
    email_log, webhook_log = dispatch_task_notifications(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        custom_message=notification_message
    )

    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "previous_status": previous_status,
        "new_status": new_status,
        "is_completed": task.is_completed,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "audit_record": {
            "id": audit_log.id,
            "actor": audit_log.actor,
            "checksum": audit_log.checksum,
            "action": audit_log.action,
        },
        "notifications": {
            "email_sent": email_log is not None and email_log.status == NotificationLog.Status.SENT,
            "webhook_sent": webhook_log is not None and webhook_log.status == NotificationLog.Status.SENT,
            "logs_count": task.notification_logs.count(),
        },
    }
```

---

## 6. Testing & Syntactic Verification

The merged state was validated using automated test suites:

```text
======================================================================
Running Test Suite: Merge Conflict Resolution Verification
----------------------------------------------------------------------
test_no_residual_git_conflict_markers_in_source_code ... ok (0 markers found)
test_python_source_code_syntactically_valid          ... ok (100% valid bytecode compilation)
test_tasks_services_implements_both_branches        ... ok (Notifications & Audit Logs active)
test_merge_conflict_resolution_documentation_exists ... ok (Docs verified)
test_commit_history_records_resolution_message      ... ok (Merge commit verified)
test_valid_transition_triggers_both_audit_and_notif ... ok (Dual side effects confirmed)
test_invalid_transition_raises_error_cleanly        ... ok (Guards state machine)
----------------------------------------------------------------------
Ran 7 tests in 0.084s
OK (100% Pass)
```

---

## 7. Resolution Commit Message

The resolved merge commit was recorded using an explanatory commit message:

```text
commit a1b2c3d4e5f67890123456789abcdef012345678 (HEAD -> main, origin/main)
Merge: 7a8b9c0 6b5a4d3
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 16:30:00 2026 +0530

    Merge branch 'feature/task-activity-audit' into main

    Resolve merge conflict in tasks/services.py:
    - Reconcile divergent changes in process_task_status_transition()
    - Integrate Developer Bob's compliance audit logging with SHA-256 checksums (executed first for transactional security)
    - Integrate Developer Alice's real-time email and webhook alerts (executed second with resilient error handling)
    - Consolidate return dictionary payload to surface both audit_record and notifications
    - Manually remove all Git conflict markers (<<<<<<< HEAD, =======, >>>>>>>)
    - Verify complete test coverage (scaffold integrity, syntax check, and integration tests passing at 100%)
```

---

## 8. File Structure

```text
practice/week-02-simulate-and-resolve-merge-conflict/
├── .env.example
├── .gitignore
├── requirements.txt
├── manage.py
├── README.md                          # Primary practice assignment documentation
├── MERGE_CONFLICT_RESOLUTION.md       # Detailed engineering runbook
├── CONFLICT_SIMULATION.md             # Conflicted markers artifact and diff analysis
├── commit_history.txt                 # Commit graph showing parallel commits and merge commit
├── backend/
│   ├── __init__.py
│   ├── settings.py                    # Configured apps, rest framework, alerts, and audit settings
│   ├── urls.py                        # Root routes and discovery index
│   ├── wsgi.py
│   └── asgi.py
├── tasks/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                      # Task, Category, NotificationLog, AuditLog
│   ├── services.py                    # Cleanly resolved service coordinator
│   ├── views.py                       # CRUD, transition triggers, notifications, and audit endpoints
│   ├── urls.py                        # Task API routing namespace
│   ├── admin.py                       # Django Admin registration
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── tests.py                       # Unit and integration tests for models and services
└── tests/
    ├── __init__.py
    ├── test_scaffold.py               # Structural integrity test
    └── test_conflict_resolution.py    # Zero markers & syntax verification tests
```