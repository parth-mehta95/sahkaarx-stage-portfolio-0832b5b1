"""
Top-level URL routing table for Capstone Backend Project.
Week 04 Practice Module: Implement Multiple Feature Branches with Atomic Commits.
"""

from pathlib import Path
from django.contrib import admin
from django.urls import path, include

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Modular endpoint routing based on enabled feature branches
if (BASE_DIR / 'authentication' / 'urls.py').exists():
    urlpatterns.append(path('api/auth/', include('authentication.urls')))

if (BASE_DIR / 'database_models' / 'urls.py').exists():
    urlpatterns.append(path('api/models/', include('database_models.urls')))

if (BASE_DIR / 'api_endpoints' / 'urls.py').exists():
    urlpatterns.append(path('api/v1/', include('api_endpoints.urls')))
