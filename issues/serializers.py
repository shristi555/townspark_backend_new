from rest_framework import serializers
from .models import (
    Issue,
    IssueImage,
    IssueComment,
    IssueProgress,
    IssueProgressImage,  # NEW
    IssueCategory,
)


# class IssueCategorySerializer(serializers.ModelSerializer):
#     """Serializer for issue categories."""

#     class Meta:
#         model = IssueCategory
#         fields = ["id", "name", "description"]


class IssueCommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="commented_by.email", read_only=True)

    class Meta:
        model = IssueComment
        fields = ["id", "user", "text", "created_at"]


class IssueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueImage
        fields = ["id", "image", "created_at"]


class IssueProgressImageSerializer(serializers.ModelSerializer):
    """Serializer for progress images."""

    class Meta:
        model = IssueProgressImage
        fields = ["id", "image", "created_at"]


class IssueProgressSerializer(serializers.ModelSerializer):
    """Serializer for creating progress updates with images."""

    updated_by = serializers.SerializerMethodField()
    issue_id = serializers.IntegerField(write_only=True)
    images = IssueProgressImageSerializer(many=True, read_only=True)  # NEW
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        max_length=10,
        help_text="Optional images for progress update (max 10)",
    )

    class Meta:
        model = IssueProgress
        fields = [
            "id",
            "issue_id",
            "title",
            "description",
            "updated_by",
            "images",  # NEW - for reading
            "uploaded_images",  # NEW - for writing
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_by", "images"]

    def get_updated_by(self, obj):
        return {
            "id": obj.updated_by.id,
            "email": obj.updated_by.email,
            "first_name": obj.updated_by.first_name,
            "last_name": obj.updated_by.last_name,
        }

    def create(self, validated_data):
        issue_id = validated_data.pop("issue_id")
        uploaded_images = validated_data.pop("uploaded_images", [])  # NEW

        issue = Issue.objects.get(id=issue_id)
        validated_data["issue"] = issue
        validated_data["updated_by"] = self.context["request"].user

        # Create progress update
        progress = super().create(validated_data)

        # Create associated images
        if uploaded_images:
            IssueProgressImage.objects.bulk_create(
                [
                    IssueProgressImage(progress=progress, image=image)
                    for image in uploaded_images
                ]
            )

        return progress


class IssueProgressGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving progress updates (read-only)."""

    updated_by = serializers.SerializerMethodField()
    images = IssueProgressImageSerializer(many=True, read_only=True)  # NEW

    class Meta:
        model = IssueProgress
        fields = [
            "id",
            "issue_id",
            "title",
            "description",
            "updated_by",
            "images",  # NEW
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_by", "images"]

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
    Accepts category ID or creates category by name if it doesn't exist.
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

    category = serializers.CharField()

    latitude = serializers.DecimalField(
        max_digits=13,
        decimal_places=10,
        required=False,
        allow_null=True,
        coerce_to_string=False,
    )
    longitude = serializers.DecimalField(
        max_digits=13,
        decimal_places=10,
        required=False,
        allow_null=True,
        coerce_to_string=False,
    )

    # category_id = serializers.PrimaryKeyRelatedField(
    #     queryset=IssueCategory.objects.all(),
    #     source="category",
    #     required=False,
    #     allow_null=True,
    #     write_only=True,
    # )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "latitude",
            "longitude",
            "uploaded_images",
        ]

    def validate_latitude(self, value):
        """Validate latitude is within valid range."""
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError(
                    "Latitude must be between -90 and 90 degrees."
                )
        return value

    def validate_longitude(self, value):
        """Validate longitude is within valid range."""
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError(
                    "Longitude must be between -180 and 180 degrees."
                )
        return value

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
    progress_updates = IssueProgressGetSerializer(many=True, read_only=True)  # CHANGED

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "latitude",
            "longitude",
            "is_resolved",
            "is_archived",
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
    progress_updates = IssueProgressGetSerializer(many=True, read_only=True)  # CHANGED

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "address",
            "latitude",
            "longitude",
            "is_resolved",
            "is_archived",
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
    Accepts category ID or name.
    """

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=IssueCategory.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )
    category_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, write_only=True
    )

    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "category_id",
            "category_name",
            "address",
            "is_resolved",
        ]

    def update(self, instance, validated_data):
        category_name = validated_data.pop("category_name", None)

        if category_name and not validated_data.get("category"):
            category, _ = IssueCategory.objects.get_or_create(name=category_name)
            validated_data["category"] = category

        return super().update(instance, validated_data)
