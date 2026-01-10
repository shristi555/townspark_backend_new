from rest_framework import serializers
from .models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_initials = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "user_name",
            "user_initials",
            "rating",
            "feedback",
            "designation",
            "created_at"
        ]

    def get_user_initials(self, obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        if first_name and last_name:
            return f"{first_name[0]}{last_name[0]}".upper()
        return first_name[0].upper() if first_name else "U"
