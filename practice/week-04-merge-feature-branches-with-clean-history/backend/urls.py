"""
Top-level URL routing table for Capstone Backend Project.
Week 04 Practice Module: Merge Feature Branches with Clean History.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/models/', include('database_models.urls')),
    path('api/v1/', include('api_endpoints.urls')),
]
