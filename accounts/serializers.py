from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import serializers


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
    profile_pic = serializers.ImageField(required=False, allow_null=True)
    phone_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    first_name = serializers.CharField(required=True, allow_blank=False)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "profile_pic",
        )

    def validate_phone_number(self, value):
        valid_symbols = set("0123456789+")
        if any(char not in valid_symbols for char in value):
            raise serializers.ValidationError(
                "Phone number can only contain digits and '+'"
            )
        if len(value) > 15:
            raise serializers.ValidationError(
                "Phone number must be at most 15 characters long."
            )
        return value

    def validate_first_name(self, value):
        return base_name_validator(value, "First name")

    def validate_last_name(self, value):
        return base_name_validator(value, "Last name")


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "profile_pic",
        )
        read_only_fields = ("email",)

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
            raise serializers.ValidationError({"email": "User not found."})

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
            raise serializers.ValidationError({"password": "Invalid credentials."})

        # 3. Add Custom Data
        data["user"] = user_obj.get_user_info()

        return data
