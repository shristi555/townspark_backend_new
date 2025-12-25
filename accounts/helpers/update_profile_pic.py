from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

# from accounts.serializers import ProfilePictureSerializer

from rest_framework import serializers
from accounts.models import User
import os


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("profile_pic",)

    def validate_profile_pic(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image must be under 5MB.")

        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")

        return value

    def update(self, instance, validated_data):
        if instance.profile_pic and "profile_pic" in validated_data:
            if os.path.isfile(instance.profile_pic.path):
                os.remove(instance.profile_pic.path)

        return super().update(instance, validated_data)


class UpdateProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        return self._update_picture(request)

    def patch(self, request):
        return self._update_picture(request)

    def _update_picture(self, request):
        serializer = ProfilePictureSerializer(
            request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Profile picture updated successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
