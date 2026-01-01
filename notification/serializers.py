from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'event', 'title', 'description', 'created_at', 'is_read', 'related_id']
        read_only_fields = ['id', 'user', 'event', 'title', 'description', 'created_at', 'related_id']
