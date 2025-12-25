from rest_framework import serializers
from .models import Issue, IssueImage, IssueComment


class IssueCommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="commented_by.email", read_only=True)

    class Meta:
        model = IssueComment
        fields = ["id", "user", "text", "created_at"]


class IssueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueImage
        fields = ["id", "image"]


class IssueSerializer(serializers.ModelSerializer):
    images = IssueImageSerializer(many=True, read_only=True)
    comments = IssueCommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    reported_by = serializers.CharField(source="reported_by.email", read_only=True)

    # for upload - now required with validation
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10,
        error_messages={
            'required': 'At least one image is required.',
            'min_length': 'At least one image is required.',
            'max_length': 'Maximum 10 images allowed.'
        }
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "is_resolved",
            "reported_by",
            "images",
            "uploaded_images",
            "comments",
            "likes_count",
            "created_at",
        ]

    def create(self, validated_data):
        images = validated_data.pop("uploaded_images", [])
        request = self.context["request"]

        issue = Issue.objects.create(reported_by=request.user, **validated_data)

        IssueImage.objects.bulk_create(
            [IssueImage(issue=issue, image=image) for image in images]
        )

        return issue