from rest_framework import serializers
from .models import ScrapingTask


class ScrapingTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for ScrapingTask model.
    
    Used for displaying task details in API responses.
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ScrapingTask
        fields = [
            'id',
            'task_id',
            'task_type',
            'task_type_display',
            'status',
            'status_display',
            'search_query',
            'item_id',
            'item_url',
            'created_at',
            'completed_at',
            'duration',
            'error_message',
        ]
        read_only_fields = fields
    
    def get_duration(self, obj):
        """
        Calculate duration of task in seconds.
        
        Returns None if task is not yet complete.
        """
        if obj.completed_at and obj.created_at:
            delta = obj.completed_at - obj.created_at
            return delta.total_seconds()
        return None


class ScrapingTaskDetailedSerializer(serializers.ModelSerializer):
    """
    More detailed serializer including additional helper fields.
    """
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    is_complete = serializers.SerializerMethodField()
    is_successful = serializers.SerializerMethodField()
    is_failed = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = ScrapingTask
        fields = [
            'id',
            'task_id',
            'task_type',
            'task_type_display',
            'status',
            'status_display',
            'search_query',
            'item_id',
            'item_url',
            'created_at',
            'completed_at',
            'duration',
            'error_message',
            'is_complete',
            'is_successful',
            'is_failed',
        ]
        read_only_fields = fields
    
    def get_is_complete(self, obj):
        return obj.is_complete()
    
    def get_is_successful(self, obj):
        return obj.is_successful()
    
    def get_is_failed(self, obj):
        return obj.is_failed()
    
    def get_duration(self, obj):
        """Calculate duration of task in seconds."""
        if obj.completed_at and obj.created_at:
            delta = obj.completed_at - obj.created_at
            return delta.total_seconds()
        return None