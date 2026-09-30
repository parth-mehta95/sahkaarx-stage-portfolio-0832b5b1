"""
REST Views for Task Domain, Pipeline Execution, Rate Limiting, and Retry Policy Diagnostics.
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from tasks.models import Task, Category, RateLimitLog, RetryPolicyLog
from tasks.services import execute_task_pipeline, check_rate_limit


@csrf_exempt
def task_list_create_view(request):
    """GET /api/tasks/ or POST /api/tasks/"""
    if request.method == "GET":
        qs = Task.objects.select_related("category").all()

        status_filter = request.GET.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        priority_filter = request.GET.get("priority")
        if priority_filter:
            qs = qs.filter(priority=priority_filter.upper())

        page = int(request.GET.get("page", 1))
        page_size = min(int(request.GET.get("page_size", 10)), 100)

        paginator = Paginator(qs, page_size)
        current_page = paginator.get_page(page)

        return JsonResponse({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "page": page,
            "results": [t.to_dict() for t in current_page],
        })

    elif request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        title = payload.get("title", "").strip()
        if not title:
            return JsonResponse({"error": "Field 'title' is required"}, status=400)

        category_id = payload.get("category_id")
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return JsonResponse({"error": f"Category ID {category_id} not found"}, status=404)

        task = Task.objects.create(
            title=title,
            description=payload.get("description", "").strip(),
            status=payload.get("status", Task.STATUS_PENDING).upper(),
            priority=payload.get("priority", Task.PRIORITY_MEDIUM).upper(),
            category=category,
            assigned_to=payload.get("assigned_to", "").strip(),
        )

        return JsonResponse(task.to_dict(), status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def task_detail_view(request, task_id):
    """GET, PUT, PATCH, DELETE /api/tasks/<task_id>/"""
    task = get_object_or_404(Task, id=task_id)

    if request.method == "GET":
        return JsonResponse(task.to_dict())

    elif request.method in ["PUT", "PATCH"]:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        if "title" in payload:
            task.title = payload["title"].strip()
        if "description" in payload:
            task.description = payload["description"].strip()
        if "status" in payload:
            task.status = payload["status"].upper()
        if "priority" in payload:
            task.priority = payload["priority"].upper()
        if "assigned_to" in payload:
            task.assigned_to = payload["assigned_to"].strip()

        task.save()
        return JsonResponse(task.to_dict())

    elif request.method == "DELETE":
        task.delete()
        return JsonResponse({"deleted": True, "task_id": task_id}, status=204)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def execute_pipeline_view(request):
    """
    POST /api/tasks/pipeline/execute/
    Executes the resolved task processing pipeline with both Rate Limiting and Retry Policy.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed. POST required."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    task_id = payload.get("task_id")
    if not task_id:
        return JsonResponse({"error": "Field 'task_id' is required"}, status=400)

    task = get_object_or_404(Task, id=task_id)
    client_identifier = payload.get("client_identifier") or request.META.get("REMOTE_ADDR", "anonymous-client")
    max_rate_limit = int(payload.get("max_rate_limit", 60))
    max_retries = int(payload.get("max_retries", 3))

    result = execute_task_pipeline(
        task=task,
        client_identifier=client_identifier,
        action_payload=payload.get("action_payload", {}),
        max_rate_limit=max_rate_limit,
        max_retries=max_retries,
    )

    return JsonResponse(result, status=result.get("status_code", 200))


def rate_limit_logs_view(request):
    """GET /api/tasks/rate-limits/"""
    qs = RateLimitLog.objects.all()
    client = request.GET.get("client")
    if client:
        qs = qs.filter(client_identifier=client)

    page = int(request.GET.get("page", 1))
    paginator = Paginator(qs, 20)
    current_page = paginator.get_page(page)

    return JsonResponse({
        "count": paginator.count,
        "results": [log.to_dict() for log in current_page],
    })


def retry_policy_logs_view(request):
    """GET /api/tasks/retry-logs/"""
    qs = RetryPolicyLog.objects.select_related("task").all()
    task_id = request.GET.get("task_id")
    if task_id:
        qs = qs.filter(task_id=task_id)

    page = int(request.GET.get("page", 1))
    paginator = Paginator(qs, 20)
    current_page = paginator.get_page(page)

    return JsonResponse({
        "count": paginator.count,
        "results": [log.to_dict() for log in current_page],
    })
