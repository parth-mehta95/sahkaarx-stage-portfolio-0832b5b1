"""
API views for the Tasks domain application.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Task, TaskCategory
from .serializers import TaskSerializer, TaskCategorySerializer
from .services import TaskService
from utils.constants import HttpStatusCodes
from utils.pagination import StandardResultsSetPagination


class TaskListCreateAPIView(APIView):
    """
    API view to list tasks with query filters, or create a new task.
    Supports filtering by ?status= and ?priority=.
    """
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        queryset = Task.objects.select_related('category', 'assigned_to').all()

        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.lower())

        priority_filter = request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter.lower())

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = TaskSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Task successfully created.",
                    "data": TaskSerializer(task).data
                },
                status=HttpStatusCodes.CREATED
            )
        return Response(
            {
                "success": False,
                "error_code": "VALIDATION_FAILED",
                "message": "Task data validation failed.",
                "details": serializer.errors
            },
            status=HttpStatusCodes.BAD_REQUEST
        )


class TaskDetailAPIView(APIView):
    """
    API view to retrieve, update, or delete a task by reference_id or id.
    """

    def get_object(self, lookup):
        if lookup.isdigit():
            return get_object_or_404(Task.objects.select_related('category', 'assigned_to'), id=int(lookup))
        return get_object_or_404(Task.objects.select_related('category', 'assigned_to'), reference_id=lookup)

    def get(self, request, lookup):
        task = self.get_object(lookup)
        return Response({"success": True, "data": TaskSerializer(task).data}, status=HttpStatusCodes.OK)

    def patch(self, request, lookup):
        task = self.get_object(lookup)
        status_update = request.data.get('status')
        if status_update and status_update != task.status:
            task = TaskService.update_task_status(task, status_update)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            updated_task = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Task successfully updated.",
                    "data": TaskSerializer(updated_task).data
                },
                status=HttpStatusCodes.OK
            )
        return Response(
            {
                "success": False,
                "error_code": "VALIDATION_FAILED",
                "message": "Invalid update parameters.",
                "details": serializer.errors
            },
            status=HttpStatusCodes.BAD_REQUEST
        )

    def delete(self, request, lookup):
        task = self.get_object(lookup)
        ref_id = task.reference_id
        task.delete()
        return Response(
            {
                "success": True,
                "message": f"Task {ref_id} deleted successfully."
            },
            status=HttpStatusCodes.OK
        )


class TaskMetricsAPIView(APIView):
    """
    API endpoint returning aggregated task metrics and lifecycle statistics.
    """

    def get(self, request):
        metrics = TaskService.get_task_metrics()
        return Response({"success": True, "data": metrics}, status=HttpStatusCodes.OK)


class TaskCategoryListCreateAPIView(APIView):
    """
    API view to list or create task categories.
    """

    def get(self, request):
        categories = TaskCategory.objects.all()
        serializer = TaskCategorySerializer(categories, many=True)
        return Response({"success": True, "data": serializer.data}, status=HttpStatusCodes.OK)

    def post(self, request):
        serializer = TaskCategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {"success": True, "message": "Category created.", "data": TaskCategorySerializer(category).data},
                status=HttpStatusCodes.CREATED
            )
        return Response(
            {"success": False, "error_code": "VALIDATION_FAILED", "details": serializer.errors},
            status=HttpStatusCodes.BAD_REQUEST
        )
