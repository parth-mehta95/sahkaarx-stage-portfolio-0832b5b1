"""
URL routing table for core infrastructure endpoints.
"""

from django.urls import path
from .views import root_index_view, health_check_view, ping_view

urlpatterns = [
    path('', root_index_view, name='root-discovery'),
    path('health/', health_check_view, name='health-check'),
    path('ping/', ping_view, name='liveness-ping'),
]
