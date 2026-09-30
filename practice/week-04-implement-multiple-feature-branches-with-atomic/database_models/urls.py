"""
URL routing for database models introspection.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('schema/', views.model_schema_info, name='models-schema-info'),
]
