"""
URL routing configuration for the tasks application.
"""

from django.urls import path
from tasks import views

app_name = "tasks"

urlpatterns = [
    path('tasks/', views.task_list_create_view, name='task_list_create'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('tasks/pipeline/execute/', views.execute_pipeline_view, name='execute_pipeline'),
    path('tasks/rate-limits/', views.rate_limit_logs_view, name='rate_limit_logs'),
    path('tasks/retry-logs/', views.retry_policy_logs_view, name='retry_policy_logs'),
]
