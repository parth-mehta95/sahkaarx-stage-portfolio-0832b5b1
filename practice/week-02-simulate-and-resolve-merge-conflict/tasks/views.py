"""
Views and API endpoints for tasks application.

Exposes CRUD operations, status transition triggers invoking the resolved service layer,
and query endpoints for notification logs and compliance audit logs.
"""

import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
from django.utils.dateparse import parse_date

from tasks.models import Task, Category, NotificationLog, AuditLog
from tasks.services import process_task_status_transition, TaskTransitionError

MAX_PAGE_SIZE = 100


def get_client_ip(request) -> str:
    """Extract client IP address from standard and reverse-proxy headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


@csrf_exempt
def task_list_create_view(request):
    """
    List tasks with filtering and pagination, or create a new task.
    GET /api/tasks/
    POST /api/tasks/
    """
    if request.method == "GET":
        queryset = Task.objects.select_related("category").all()

        # Filtering
        status_filter = request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())

        priority_filter = request.GET.get("priority")
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter.upper())

        category_slug = request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        search_query = request.GET.get("q")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # Pagination clamping
        try:
            page = int(request.GET.get("page", 1))
            page_size = min(int(request.GET.get("page_size", 20)), MAX_PAGE_SIZE)
            if page_size < 1:
                page_size = 20
        except ValueError:
            page, page_size = 1, 20

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = []

        return JsonResponse({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "page_size": page_size,
            "results": [t.to_dict() for t in page_obj],
        })

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponseBadRequest(
                json.dumps({"error": "INVALID_JSON", "message": "Malformed JSON payload"}),
                content_type="application/json"
            )

        title = data.get("title", "").strip()
        if not title:
            return HttpResponseBadRequest(
                json.dumps({"error": "VALIDATION_ERROR", "field": "title", "message": "Title is required"}),
                content_type="application/json"
            )

        description = data.get("description", "").strip()
        status = data.get("status", Task.Status.TODO).upper()
        priority = data.get("priority", Task.Priority.MEDIUM).upper()
        assignee_email = data.get("assignee_email", "").strip()

        category = None
        category_slug = data.get("category_slug")
        if category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if not category:
                return HttpResponseBadRequest(
                    json.dumps({
                        "error": "CATEGORY_NOT_FOUND",
                        "message": f"Category with slug '{category_slug}' does not exist"
                    }),
                    content_type="application/json"
                )

        due_date = None
        raw_due_date = data.get("due_date")
        if raw_due_date:
            due_date = parse_date(raw_due_date)

        task = Task.objects.create(
            title=title,
            description=description,
            category=category,
            status=status if status in Task.Status.values else Task.Status.TODO,
            priority=priority if priority in Task.Priority.values else Task.Priority.MEDIUM,
            assignee_email=assignee_email,
            due_date=due_date
        )

        return JsonResponse(task.to_dict(), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def task_detail_view(request, task_id):
    """
    Retrieve, update, or delete a task.
    GET /api/tasks/<id>/
    PUT / PATCH /api/tasks/<id>/
    DELETE /api/tasks/<id>/
    """
    task = Task.objects.select_related("category").filter(id=task_id).first()
    if not task:
        return JsonResponse({"error": "NOT_FOUND", "message": f"Task #{task_id} not found"}, status=404)

    if request.method == "GET":
        return JsonResponse(task.to_dict())

    elif request.method in ["PUT", "PATCH"]:
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponseBadRequest(
                json.dumps({"error": "INVALID_JSON", "message": "Malformed JSON payload"}),
                content_type="application/json"
            )

        if "title" in data:
            task.title = data["title"].strip()
        if "description" in data:
            task.description = data["description"].strip()
        if "priority" in data and data["priority"].upper() in Task.Priority.values:
            task.priority = data["priority"].upper()
        if "assignee_email" in data:
            task.assignee_email = data["assignee_email"].strip()
        if "due_date" in data:
            task.due_date = parse_date(data["due_date"]) if data["due_date"] else None

        task.save()
        return JsonResponse(task.to_dict())

    elif request.method == "DELETE":
        task.delete()
        return JsonResponse({"deleted": True, "task_id": task_id}, status=200)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


@csrf_exempt
def task_transition_view(request, task_id):
    """
    Trigger a lifecycle transition using the resolved merge conflict service.
    POST /api/tasks/<id>/transition/
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    task = Task.objects.filter(id=task_id).first()
    if not task:
        return JsonResponse({"error": "NOT_FOUND", "message": f"Task #{task_id} not found"}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest(
            json.dumps({"error": "INVALID_JSON", "message": "Malformed JSON payload"}),
            content_type="application/json"
        )

    new_status = data.get("new_status", "").upper()
    if not new_status or new_status not in Task.Status.values:
        return HttpResponseBadRequest(
            json.dumps({
                "error": "INVALID_STATUS",
                "message": f"Invalid status '{new_status}'. Choices: {Task.Status.values}"
            }),
            content_type="application/json"
        )

    actor = data.get("actor", "system")
    ip_addr = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "api-client/1.0")
    custom_msg = data.get("message")
    meta = data.get("metadata", {})

    try:
        result = process_task_status_transition(
            task=task,
            new_status=new_status,
            actor=actor,
            ip_address=ip_addr,
            user_agent=user_agent,
            notification_message=custom_msg,
            additional_metadata=meta
        )
        return JsonResponse(result, status=200)
    except TaskTransitionError as err:
        return HttpResponseBadRequest(
            json.dumps({"error": "TRANSITION_DISALLOWED", "message": str(err)}),
            content_type="application/json"
        )


def notification_log_list_view(request):
    """
    List notification logs generated by Developer Alice's feature.
    GET /api/tasks/notifications/
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    queryset = NotificationLog.objects.select_related("task").all()
    task_id = request.GET.get("task_id")
    if task_id:
        queryset = queryset.filter(task_id=task_id)

    channel = request.GET.get("channel")
    if channel:
        queryset = queryset.filter(channel=channel.upper())

    logs = [log.to_dict() for log in queryset[:100]]
    return JsonResponse({
        "feature": "task-notifications",
        "author": "Developer Alice",
        "count": len(logs),
        "results": logs,
    })


def audit_log_list_view(request):
    """
    List tamper-evident audit logs generated by Developer Bob's feature.
    GET /api/tasks/audit-logs/
    """
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    queryset = AuditLog.objects.select_related("task").all()
    task_id = request.GET.get("task_id")
    if task_id:
        queryset = queryset.filter(task_id=task_id)

    action = request.GET.get("action")
    if action:
        queryset = queryset.filter(action=action.upper())

    logs = [log.to_dict() for log in queryset[:100]]
    return JsonResponse({
        "feature": "task-activity-audit",
        "author": "Developer Bob",
        "count": len(logs),
        "results": logs,
    })


@csrf_exempt
def category_list_create_view(request):
    """List or create categories."""
    if request.method == "GET":
        categories = [c.to_dict() for c in Category.objects.all()]
        return JsonResponse({"count": len(categories), "results": categories})

    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return HttpResponseBadRequest(
                json.dumps({"error": "INVALID_JSON"}),
                content_type="application/json"
            )

        name = data.get("name", "").strip()
        if not name:
            return HttpResponseBadRequest(
                json.dumps({"error": "VALIDATION_ERROR", "message": "Name is required"}),
                content_type="application/json"
            )

        color_hex = data.get("color_hex", "#3B82F6")
        description = data.get("description", "")
        category = Category.objects.create(name=name, color_hex=color_hex, description=description)
        return JsonResponse(category.to_dict(), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])
