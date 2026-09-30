"""
Top-level URL configuration for backend project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Administration portal
    path('admin/', admin.site.urls),

    # Core system endpoints (health, ping, service discovery)
    path('', include('core.urls')),

    # Tasks domain REST API endpoints
    path('api/tasks/', include('tasks.urls')),
]
