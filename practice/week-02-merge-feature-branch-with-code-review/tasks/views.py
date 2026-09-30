"""
Views and API endpoint handlers for the tasks application.

Implements CRUD endpoints, query filtering, pagination clamping, and explicit
validation error responses incorporated from Team Lead Code Review feedback.
"""

import json
from datetime import datetime
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Task, Category

# Review Comment #3 Fix: Enforce strict pagination clamping to prevent resource exhaustion
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _parse_json_body(request):
    """Safely parse request JSON body or return None on malformed payload."""
    try:
        if not request.body:
            return {}
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@csrf_exempt
def task_list_create(request):
    """
    Handle GET (listing tasks with filtering & pagination) and
    POST (creating new task with validation).
    """
    if request.method == "GET":
        queryset = Task.objects.select_related("category").all()

        # 1. Filter by Status
        status_param = request.GET.get("status")
        if status_param:
            valid_statuses = [choice[0] for choice in Task.Status.choices]
            if status_param.upper() in valid_statuses:
                queryset = queryset.filter(status=status_param.upper())
            else:
                return JsonResponse({
                    "error": "Invalid status filter",
                    "valid_options": valid_statuses,
                    "provided": status_param
                }, status=400)

        # 2. Filter by Priority
        priority_param = request.GET.get("priority")
        if priority_param:
            valid_priorities = [choice[0] for choice in Task.Priority.choices]
            if priority_param.upper() in valid_priorities:
                queryset = queryset.filter(priority=priority_param.upper())
            else:
                return JsonResponse({
                    "error": "Invalid priority filter",
                    "valid_options": valid_priorities,
                    "provided": priority_param
                }, status=400)

        # 3. Filter by Category (Review Comment #2 Fix: Explicit 400 on invalid category)
        category_param = request.GET.get("category")
        if category_param:
            category_obj = None
            if category_param.isdigit():
                category_obj = Category.objects.filter(id=int(category_param)).first()
            if not category_obj:
                category_obj = Category.objects.filter(slug__iexact=category_param).first()

            if not category_obj:
                return JsonResponse({
                    "error": "Invalid category",
                    "detail": f"Category '{category_param}' does not exist.",
                    "code": "CATEGORY_NOT_FOUND"
                }, status=400)

            queryset = queryset.filter(category=category_obj)

        # 4. Search Filter (Title & Description)
        search_query = request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        # 5. Review Comment #3 Fix: Clamped Pagination to prevent DoS query exhaustion
        try:
            raw_page_size = int(request.GET.get("page_size", DEFAULT_PAGE_SIZE))
            page_size = max(1, min(raw_page_size, MAX_PAGE_SIZE))
        except (ValueError, TypeError):
            page_size = DEFAULT_PAGE_SIZE

        paginator = Paginator(queryset, page_size)
        page_num = request.GET.get("page", 1)

        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []

        results = [task.to_dict() for task in page_obj]

        return JsonResponse({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number if hasattr(page_obj, "number") else 1,
            "page_size": page_size,
            "results": results,
        }, status=200)

    elif request.method == "POST":
        payload = _parse_json_body(request)
        if payload is None:
            return JsonResponse({"error": "Malformed JSON payload"}, status=400)

        title = payload.get("title", "").strip()
        if not title:
            return JsonResponse({
                "error": "Validation failed",
                "field_errors": {"title": "Title is required and cannot be blank."}
            }, status=400)

        # Category resolution with review validation fix
        category_val = payload.get("category") or payload.get("category_id") or payload.get("category_slug")
        category_instance = None
        if category_val:
            if isinstance(category_val, int) or (isinstance(category_val, str) and category_val.isdigit()):
                category_instance = Category.objects.filter(id=int(category_val)).first()
            if not category_instance and isinstance(category_val, str):
                category_instance = Category.objects.filter(slug__iexact=category_val).first()

            if not category_instance:
                return JsonResponse({
                    "error": "Validation failed",
                    "field_errors": {"category": f"Category '{category_val}' not found."}
                }, status=400)

        status_val = payload.get("status", Task.Status.TODO).upper()
        if status_val not in [c[0] for c in Task.Status.choices]:
            return JsonResponse({
                "error": "Validation failed",
                "field_errors": {"status": f"Invalid status '{status_val}'."}
            }, status=400)

        priority_val = payload.get("priority", Task.Priority.MEDIUM).upper()
        if priority_val not in [c[0] for c in Task.Priority.choices]:
            return JsonResponse({
                "error": "Validation failed",
                "field_errors": {"priority": f"Invalid priority '{priority_val}'."}
            }, status=400)

        due_date_val = None
        if payload.get("due_date"):
            try:
                due_date_val = datetime.strptime(payload["due_date"], "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({
                    "error": "Validation failed",
                    "field_errors": {"due_date": "Due date must be in YYYY-MM-DD format."}
                }, status=400)

        task = Task.objects.create(
            title=title,
            description=payload.get("description", "").strip(),
            category=category_instance,
            status=status_val,
            priority=priority_val,
            due_date=due_date_val,
        )

        return JsonResponse({
            "message": "Task created successfully",
            "task": task.to_dict()
        }, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def task_detail(request, task_id):
    """Retrieve, update, or delete a specific task."""
    try:
        task = Task.objects.select_related("category").get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found", "task_id": task_id}, status=404)

    if request.method == "GET":
        return JsonResponse(task.to_dict(), status=200)

    elif request.method in ["PUT", "PATCH"]:
        payload = _parse_json_body(request)
        if payload is None:
            return JsonResponse({"error": "Malformed JSON payload"}, status=400)

        if "title" in payload:
            new_title = payload["title"].strip()
            if not new_title:
                return JsonResponse({"error": "Title cannot be empty"}, status=400)
            task.title = new_title

        if "description" in payload:
            task.description = payload["description"].strip()

        if "status" in payload:
            new_status = payload["status"].upper()
            if new_status not in [c[0] for c in Task.Status.choices]:
                return JsonResponse({"error": f"Invalid status '{new_status}'"}, status=400)
            task.status = new_status

        if "priority" in payload:
            new_priority = payload["priority"].upper()
            if new_priority not in [c[0] for c in Task.Priority.choices]:
                return JsonResponse({"error": f"Invalid priority '{new_priority}'"}, status=400)
            task.priority = new_priority

        if "due_date" in payload:
            if payload["due_date"]:
                try:
                    task.due_date = datetime.strptime(payload["due_date"], "%Y-%m-%d").date()
                except ValueError:
                    return JsonResponse({"error": "Due date must be in YYYY-MM-DD format"}, status=400)
            else:
                task.due_date = None

        if "category" in payload or "category_id" in payload:
            cat_val = payload.get("category") or payload.get("category_id")
            if cat_val is None:
                task.category = None
            else:
                cat_obj = None
                if isinstance(cat_val, int) or (isinstance(cat_val, str) and cat_val.isdigit()):
                    cat_obj = Category.objects.filter(id=int(cat_val)).first()
                if not cat_obj and isinstance(cat_val, str):
                    cat_obj = Category.objects.filter(slug__iexact=cat_val).first()

                if not cat_obj:
                    return JsonResponse({"error": f"Category '{cat_val}' not found"}, status=400)
                task.category = cat_obj

        task.save()
        return JsonResponse({
            "message": "Task updated successfully",
            "task": task.to_dict()
        }, status=200)

    elif request.method == "DELETE":
        task_id_cached = task.id
        task.delete()
        return JsonResponse({
            "message": f"Task {task_id_cached} deleted successfully",
            "task_id": task_id_cached
        }, status=200)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


@csrf_exempt
def category_list_create(request):
    """List all categories or create a new category."""
    if request.method == "GET":
        categories = Category.objects.prefetch_related("tasks").all()
        return JsonResponse({
            "count": categories.count(),
            "results": [c.to_dict() for c in categories]
        }, status=200)

    elif request.method == "POST":
        payload = _parse_json_body(request)
        if payload is None:
            return JsonResponse({"error": "Malformed JSON payload"}, status=400)

        name = payload.get("name", "").strip()
        if not name:
            return JsonResponse({"error": "Category name is required"}, status=400)

        if Category.objects.filter(name__iexact=name).exists():
            return JsonResponse({"error": f"Category '{name}' already exists"}, status=400)

        category = Category.objects.create(
            name=name,
            slug=payload.get("slug", "").strip(),
            description=payload.get("description", "").strip(),
            color_hex=payload.get("color_hex", "#3B82F6").strip()
        )
        return JsonResponse({
            "message": "Category created successfully",
            "category": category.to_dict()
        }, status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def category_detail(request, category_id):
    """Retrieve, update, or delete a specific category."""
    try:
        category = Category.objects.prefetch_related("tasks").get(id=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found", "category_id": category_id}, status=404)

    if request.method == "GET":
        return JsonResponse(category.to_dict(), status=200)

    elif request.method in ["PUT", "PATCH"]:
        payload = _parse_json_body(request)
        if payload is None:
            return JsonResponse({"error": "Malformed JSON payload"}, status=400)

        if "name" in payload:
            new_name = payload["name"].strip()
            if not new_name:
                return JsonResponse({"error": "Category name cannot be empty"}, status=400)
            category.name = new_name

        if "description" in payload:
            category.description = payload["description"].strip()

        if "color_hex" in payload:
            category.color_hex = payload["color_hex"].strip()

        category.save()
        return JsonResponse({
            "message": "Category updated successfully",
            "category": category.to_dict()
        }, status=200)

    elif request.method == "DELETE":
        cat_id_cached = category.id
        category.delete()
        return JsonResponse({
            "message": f"Category {cat_id_cached} deleted successfully"
        }, status=200)

    return HttpResponseNotAllowed(["GET", "PUT", "PATCH", "DELETE"])


def task_health_check(request):
    """Health check endpoint providing status overview and task counts."""
    from django.db import connection

    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    counts = {
        status_choice[0]: Task.objects.filter(status=status_choice[0]).count()
        for status_choice in Task.Status.choices
    }

    return JsonResponse({
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "task_counts": counts,
        "total_tasks": Task.objects.count(),
        "total_categories": Category.objects.count(),
        "service": "tasks-service-week-02"
    }, status=200 if db_ok else 503)
