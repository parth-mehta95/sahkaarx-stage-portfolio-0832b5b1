"""
URL route definitions for Tasks domain API endpoints.
"""

from django.urls import path
from .views import (
    TaskListCreateAPIView,
    TaskDetailAPIView,
    TaskMetricsAPIView,
    TaskCategoryListCreateAPIView,
)

urlpatterns = [
    path('', TaskListCreateAPIView.as_view(), name='task-list-create'),
    path('metrics/', TaskMetricsAPIView.as_view(), name='task-metrics'),
    path('categories/', TaskCategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('<str:lookup>/', TaskDetailAPIView.as_view(), name='task-detail'),
]
