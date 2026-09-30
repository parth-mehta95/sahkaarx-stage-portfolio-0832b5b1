"""
Serializers for Projects, Workspaces, and Aggregated Statistics.
"""

from rest_framework import serializers
from database_models.models import Workspace, Project, ProjectTag


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ['id', 'name', 'slug', 'color_hex']


class WorkspaceSerializer(serializers.ModelSerializer):
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'project_count', 'created_at']

    def get_project_count(self, obj):
        return obj.projects.filter(is_deleted=False).count()


class ProjectListSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(source='workspace.name', read_only=True)
    tags = ProjectTagSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'workspace', 'workspace_name',
            'status', 'priority', 'budget', 'start_date', 'target_date',
            'tags', 'created_at', 'updated_at'
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer(read_only=True)
    workspace_id = serializers.PrimaryKeyRelatedField(
        queryset=Workspace.objects.all(), source='workspace', write_only=True
    )
    tags = ProjectTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProjectTag.objects.all(), source='tags', many=True, write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'workspace', 'workspace_id',
            'status', 'priority', 'budget', 'start_date', 'target_date',
            'tags', 'tag_ids', 'is_deleted', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date')
        target = attrs.get('target_date')
        if start and target and target < start:
            raise serializers.ValidationError({"target_date": "Target date cannot precede start date."})
        return attrs
