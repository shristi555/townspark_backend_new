from rest_framework import serializers
from .models import Issue, IssueImage, IssueComment, IssueProgress


class IssueCommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="commented_by.email", read_only=True)

    class Meta:
        model = IssueComment
        fields = ["id", "user", "text", "created_at"]


class IssueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueImage
        fields = ["id", "image"]


class IssueProgressSerializer(serializers.ModelSerializer):
    updated_by = serializers.SerializerMethodField()
    issue_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IssueProgress
        fields = ["id", "issue_id", "title", "description", "updated_by", "created_at"]
        read_only_fields = ["id", "created_at", "updated_by"]

    def get_updated_by(self, obj):
        return {
            "id": obj.updated_by.id,
            "email": obj.updated_by.email,
            "first_name": obj.updated_by.first_name,
            "last_name": obj.updated_by.last_name,
        }

    def create(self, validated_data):
        issue_id = validated_data.pop("issue_id")
        issue = Issue.objects.get(id=issue_id)
        validated_data["issue"] = issue
        validated_data["updated_by"] = self.context["request"].user
        return super().create(validated_data)


class IssueProgressGetSerializer(serializers.ModelSerializer):
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = IssueProgress
        fields = ["id", "issue_id", "title", "description", "updated_by", "created_at"]
        read_only_fields = ["id", "created_at", "updated_by"]

    def get_updated_by(self, obj):
        return {
            "id": obj.updated_by.id,
            "email": obj.updated_by.email,
            "first_name": obj.updated_by.first_name,
            "last_name": obj.updated_by.last_name,
        }


class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new issues with image uploads.
    """

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10,
        error_messages={
            "required": "At least one image is required.",
            "min_length": "At least one image is required.",
            "max_length": "Maximum 10 images allowed.",
        },
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "uploaded_images",
        ]

    def create(self, validated_data):
        images = validated_data.pop("uploaded_images", [])
        request = self.context["request"]

        issue = Issue.objects.create(reported_by=request.user, **validated_data)

        IssueImage.objects.bulk_create(
            [IssueImage(issue=issue, image=image) for image in images]
        )

        return issue


class IssueListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing issues with basic information.
    """

    images = IssueImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    reported_by = serializers.CharField(source="reported_by.email", read_only=True)
    progress_updates = IssueProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "is_resolved",
            "reported_by",
            "images",
            "comments_count",
            "likes_count",
            "progress_updates",
            "created_at",
        ]


class IssueDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed issue view with comments and progress updates.
    """

    images = IssueImageSerializer(many=True, read_only=True)
    comments = IssueCommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    reported_by = serializers.CharField(source="reported_by.email", read_only=True)
    progress_updates = IssueProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "is_resolved",
            "reported_by",
            "images",
            "comments",
            "likes_count",
            "progress_updates",
            "created_at",
        ]


class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing issues.
    """

    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "category",
            "address",
            "is_resolved",
        ]
