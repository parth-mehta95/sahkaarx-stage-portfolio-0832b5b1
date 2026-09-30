"""
URL configuration for tasks application.
"""

from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list_create, name="task-list-create"),
    path("<int:task_id>/", views.task_detail, name="task-detail"),
    path("categories/", views.category_list_create, name="category-list-create"),
    path("categories/<int:category_id>/", views.category_detail, name="category-detail"),
    path("health/", views.task_health_check, name="task-health"),
]
