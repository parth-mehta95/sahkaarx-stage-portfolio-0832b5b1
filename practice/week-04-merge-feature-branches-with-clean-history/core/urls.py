"""
Core application URL mappings.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_discovery, name='index-discovery'),
    path('health/', views.health_check, name='health-check'),
    path('ping/', views.ping, name='ping'),
]
