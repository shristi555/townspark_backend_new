from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'fullname', 'email', 
            'phone_no', 'address', 'password', 
            'profile_pic', 'created_at'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        # Use create_user to ensure the password gets hashed!
        user = User.objects.create_user(**validated_data)
        return user