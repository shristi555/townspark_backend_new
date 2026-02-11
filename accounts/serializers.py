from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from djoser.serializers import UserSerializer as BaseUserSerializer


def base_name_validator(value, field_name):
    #     we use regex to allow only letters, numbers, underscores, and hyphens in the base name
    import re

    pattern = r"^[a-zA-Z0-9_-]+$"
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            f"{field_name} can only contain letters, numbers, underscores, and hyphens."
        )
    return value


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for user registration.

    **Request Format (JSON):**
    {
        "first_name": string (required),
        "last_name": string (optional),
        "email": string (required),
        "phone_number": string (optional),
        "password": string (required),
        "terms": boolean (optional)
    }
    """

    terms = serializers.BooleanField(write_only=True, required=False)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "terms",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": False},
            "phone_number": {"required": False},
        }

    def validate_email(self, value):
        """Ensure email is unique and valid."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    # def validate_phone_number(self, value):
    #     """Ensure phone number is unique."""
    #     if User.objects.filter(phone_number=value).exists():
    #         raise serializers.ValidationError(
    #             "A user with this phone number already exists."
    #         )
    #     return value


class UserSerializer(BaseUserSerializer):
    """
    Serializer for user data retrieval.
    """

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "is_staff",
        ]
        read_only_fields = ["id", "email", "is_active", "is_staff"]

    # Full name is a read-only field that concatenates first_name and last_name
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        profile_pic_url = obj.profile_pic.url if obj.profile_pic else None

        if profile_pic_url and request:
            return request.build_absolute_uri(profile_pic_url)

        return profile_pic_url


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        User = get_user_model()

        # Check if email exists
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": {"email": f'Provided email "{email}" not found. '}}
            )

        if not user_obj.is_active:
            raise serializers.ValidationError({"detail": "Account is inactive."})

        # passowrd check is handled by super class
        # super().validate(attrs)
        # if we pass wrong password it will raise ValidationError
        try:
            data = super().validate(attrs)
        except serializers.ValidationError:
            # If parent fails, it means the password was wrong
            # (since we already checked email exists above) only possible failure is in password
            raise serializers.ValidationError(
                {"detail": {"password": "Password is incorrect for given email."}}
            )

        # 3. Add Custom Data
        data["user"] = user_obj.get_user_info()

        return data
