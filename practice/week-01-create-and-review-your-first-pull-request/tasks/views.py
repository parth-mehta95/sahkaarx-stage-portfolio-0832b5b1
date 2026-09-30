"""
Views for the tasks application.
"""

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Task


def health_check(request: HttpRequest) -> JsonResponse:
    """Service health check endpoint for tasks app."""
    return JsonResponse({
        "app": "tasks",
        "status": "healthy",
        "ready": True,
        "scaffold": "Django App via Feature PR",
    })


@require_http_methods(["GET", "POST"])
@csrf_exempt
def task_list(request: HttpRequest) -> JsonResponse:
    """List all tasks or create a new task."""
    if request.method == "GET":
        tasks = Task.objects.all().values(
            'id', 'title', 'description', 'status', 'priority', 'is_completed', 'created_at'
        )
        return JsonResponse({
            "status": "success",
            "count": len(tasks),
            "data": list(tasks)
        }, safe=False)

    # POST - Create new task
    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title', '').strip()
        if not title:
            return JsonResponse({"error": "Field 'title' is required."}, status=400)

        task = Task.objects.create(
            title=title,
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
        )
        return JsonResponse({
            "status": "created",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
            }
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)


@require_http_methods(["GET", "PUT", "DELETE"])
@csrf_exempt
def task_detail(request: HttpRequest, task_id: int) -> JsonResponse:
    """Retrieve, update, or delete an existing task."""
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": f"Task with id {task_id} not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        })

    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode('utf-8'))
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'status' in data:
                task.status = data['status']
                task.is_completed = (task.status == 'completed')
            if 'priority' in data:
                task.priority = data['priority']
            task.save()
            return JsonResponse({"status": "updated", "id": task.id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # DELETE
    task.delete()
    return JsonResponse({"status": "deleted", "id": task_id})
