"""
REST API view endpoints for projects, workspaces, and metrics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from database_models.models import Workspace, Project
from .serializers import (
    WorkspaceSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer
)
from .pagination import StandardResultsSetPagination
from .filters import filter_projects_queryset


class WorkspaceListView(APIView):
    """
    List active workspaces.
    """
    def get(self, request):
        workspaces = Workspace.objects.filter(is_active=True)
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectListCreateView(APIView):
    """
    List projects with pagination and filters, or create a new project.
    """
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        queryset = Project.objects.filter(is_deleted=False).select_related('workspace').prefetch_related('tags')
        filtered_qs = filter_projects_queryset(queryset, request.query_params)

        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(filtered_qs, request)
        serializer = ProjectListSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProjectDetailSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    """
    Retrieve, update or soft-delete a project by ID.
    """
    def _get_project(self, pk):
        try:
            return Project.objects.get(pk=pk, is_deleted=False)
        except Project.DoesNotExist:
            return None

    def get(self, request, pk):
        project = self._get_project(pk)
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        project = self._get_project(pk)
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectDetailSerializer(project, data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        project = self._get_project(pk)
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectDetailSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = self._get_project(pk)
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        project.is_deleted = True
        project.save(update_fields=['is_deleted'])
        return Response({'message': f'Project {pk} successfully archived.'}, status=status.HTTP_200_OK)


class ProjectStatsView(APIView):
    """
    Aggregated project metrics grouped by status and priority.
    """
    def get(self, request):
        total = Project.objects.filter(is_deleted=False).count()
        by_status = dict(
            Project.objects.filter(is_deleted=False)
            .values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        by_priority = dict(
            Project.objects.filter(is_deleted=False)
            .values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )

        return Response({
            'total_projects': total,
            'by_status': by_status,
            'by_priority': by_priority,
        }, status=status.HTTP_200_OK)
