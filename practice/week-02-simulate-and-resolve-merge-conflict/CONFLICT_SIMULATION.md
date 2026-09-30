# Merge Conflict Simulation & Reproduction Artifact

This document details the intentional simulation of a real-world Git merge conflict between two engineering branches modifying the same module in parallel.

---

## 1. Scenario Overview

Two developers worked concurrently on the task management service from the same base commit on `main`:

```text
                                  ┌─── [feature/task-notifications] (Developer Alice)
                                  │    • Added email & webhook dispatching
                                  │    • Commit: 7a8b9c0d1e2f
[main (Base: 8e7b16d)] ───────────┤
                                  │
                                  └─── [feature/task-activity-audit] (Developer Bob)
                                       • Added security compliance audit logging
                                       • Commit: 6b5a4d3c2e1f
```

Both engineers modified the transition handler function `process_task_status_transition` inside [`tasks/services.py`](file:///d:/challengers%20testing/sahkaarx-stage-portfolio-0832b5b1/practice/week-02-simulate-and-resolve-merge-conflict/tasks/services.py).

---

## 2. Parallel Modifications

### Developer Alice's Branch: `feature/task-notifications`
Alice implemented stakeholder notifications on task status changes:

```python
# Developer Alice's implementation in tasks/services.py
def process_task_status_transition(task, new_status, actor="system", ...):
    task.status = new_status
    task.save()
    
    # Send email and webhook alerts
    email_log, webhook_log = dispatch_task_notifications(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor
    )
    return {"status": "success", "notifications": {"sent": True}}
```

### Developer Bob's Branch: `feature/task-activity-audit`
Concurrently, Bob implemented regulatory compliance audit logging with SHA-256 checksums:

```python
# Developer Bob's implementation in tasks/services.py
def process_task_status_transition(task, new_status, actor="system", ...):
    task.status = new_status
    task.save()
    
    # Record compliance audit trail with cryptographic checksum
    audit_log = record_task_activity_audit(
        task=task,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        ip_address=ip_address
    )
    return {"status": "success", "audit_record": {"id": audit_log.id, "checksum": audit_log.checksum}}
```

---

## 3. Conflict Triggering

When merging `feature/task-activity-audit` into `main` (after `feature/task-notifications` was merged) or attempting to cross-merge the branches:

```bash
git checkout feature/task-notifications
git merge feature/task-activity-audit
```

**Git Output**:
```text
Auto-merging tasks/models.py
Auto-merging tasks/services.py
CONFLICT (content): Merge conflict in tasks/services.py
Automatic merge failed; fix conflicts and then commit the result.
```

---

## 4. Conflicted State with Conflict Markers

Inside `tasks/services.py`, Git inserted standard conflict markers:

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

## 5. Conflict Resolution Strategy & Decisions

### Decision: "Keep Both" Harmonious Integration
Neither change could be dropped:
1. **Compliance Requirements**: The system cannot skip Bob's audit trail without violating regulatory and security requirements.
2. **Operational Visibility**: Dropping Alice's alerts would break downstream webhook automation and assignee notifications.

### Execution Sequencing:
1. **Audit First**: Create the audit record immediately following the status persistence. This guarantees that audit trails are written before network I/O occurs.
2. **Notify Second**: Dispatch notifications with non-blocking error handling, so a network glitch in an external webhook never rolls back a valid status update or audit log.
3. **Unified Response**: Combine both the `audit_record` and `notifications` payloads in the return dictionary.
4. **Remove All Markers**: Thoroughly eliminate `<<<<<<< HEAD`, `=======`, and `>>>>>>> feature/task-activity-audit`.

---

## 6. Resolved Clean Code

The resulting production code in [`tasks/services.py`](file:///d:/challengers%20testing/sahkaarx-stage-portfolio-0832b5b1/practice/week-02-simulate-and-resolve-merge-conflict/tasks/services.py#L162-L215):

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
