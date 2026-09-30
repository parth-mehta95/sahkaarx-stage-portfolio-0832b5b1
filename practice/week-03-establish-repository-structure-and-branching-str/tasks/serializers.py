"""
Django REST Framework serializers for tasks domain entities.
"""

from rest_framework import serializers
from .models import Task, TaskCategory
from utils.validators import validate_task_title, validate_future_date


class TaskCategorySerializer(serializers.ModelSerializer):
    """Serializer for TaskCategory model."""
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with field validation."""
    title = serializers.CharField(validators=[validate_task_title])
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_username = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'reference_id',
            'title',
            'description',
            'category',
            'category_name',
            'status',
            'priority',
            'assigned_to',
            'assigned_username',
            'due_date',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'reference_id', 'completed_at', 'created_at', 'updated_at']

    def validate_due_date(self, value):
        if value:
            validate_future_date(value)
        return value
