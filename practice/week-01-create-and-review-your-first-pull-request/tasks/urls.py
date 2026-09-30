"""
URL patterns for the tasks application.
"""

from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task-list'),
    path('<int:task_id>/', views.task_detail, name='task-detail'),
    path('health/', views.health_check, name='tasks-health'),
]
