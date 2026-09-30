"""
Routing for REST API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('workspaces/', views.WorkspaceListView.as_view(), name='api-workspaces-list'),
    path('projects/', views.ProjectListCreateView.as_view(), name='api-projects-list-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='api-project-detail'),
    path('projects/stats/', views.ProjectStatsView.as_view(), name='api-projects-stats'),
]
