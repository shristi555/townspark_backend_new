from rest_framework import serializers
from accounts.models import User
from issues.models import Issue, IssueCategory
from issues.serializers import IssueImageSerializer

class UserSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'profile_pic']

class IssueSearchSerializer(serializers.ModelSerializer):
    reported_by_email = serializers.EmailField(source='reported_by.email', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    reported_by_id = serializers.IntegerField(source='reported_by.id', read_only=True)
    reported_by_pic = serializers.SerializerMethodField()
    images = IssueImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    def get_reported_by_pic(self, obj):
        if obj.reported_by and obj.reported_by.profile_pic:
            request = self.context.get("request")
            url = obj.reported_by.profile_pic.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'address', 
            'is_resolved', 'is_archived', 'reported_by_email', 
            'reported_by_name', 'reported_by_id', 'reported_by_pic',
            'images', 'likes_count', 'comments_count', 'created_at'
        ]

class SuggestionSerializer(serializers.Serializer):
    text = serializers.CharField()
    type = serializers.CharField()  # 'issue', 'person', 'category'
    id = serializers.IntegerField(required=False)
