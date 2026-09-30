"""
URL routing patterns for tasks application.
"""

from django.urls import path
from tasks import views

app_name = 'tasks'

urlpatterns = [
    # Task CRUD and search
    path('', views.task_list_create_view, name='task-list-create'),
    path('<int:task_id>/', views.task_detail_view, name='task-detail'),

    # Resolved conflict transition trigger
    path('<int:task_id>/transition/', views.task_transition_view, name='task-transition'),

    # Dual-feature logs endpoints
    path('notifications/', views.notification_log_list_view, name='notification-logs'),
    path('audit-logs/', views.audit_log_list_view, name='audit-logs'),

    # Category endpoints
    path('categories/', views.category_list_create_view, name='category-list-create'),
]
